"""Unit tests for the ConstrainedDSLCompiler and modular IRCompiler stages."""

import pytest
import json

from research.compiler import (
    ConstrainedDSLCompiler,
    DSLValidationError,
    IRCompiler,
    CompilerError,
    ParserError,
    SchemaError,
    CanonicalizationError,
    SemanticError,
    TemplateError,
    ASTError
)
from research.compiler.parser import ParserStage
from research.compiler.schema import SchemaStage, ParsedIR
from research.compiler.canonicalizer import CanonicalizerStage, ValidatedIR
from research.compiler.semantic import SemanticStage, CanonicalIR
from research.compiler.templates import TemplateStage, SemanticIR
from research.compiler.ast_guard import ASTStage, GeneratedPlugin, CompilationPlan


def test_compiler_validation():
    compiler = ConstrainedDSLCompiler()

    # Safe code using allowed imports
    safe_code = """
import numpy as np
class MyPlugin:
    def convert(self, x):
        return np.array(x) * 2
"""
    assert compiler.validate_code(safe_code) is True

    # Unsafe code importing os
    unsafe_import = """
import os
class MyPlugin:
    def convert(self, x):
        return x
"""
    with pytest.raises(DSLValidationError, match="Unauthorized import"):
        compiler.validate_code(unsafe_import)

    # Unsafe code using blocked functions
    unsafe_call = """
class MyPlugin:
    def convert(self, x):
        eval("print('hello')")
        return x
"""
    with pytest.raises(DSLValidationError, match="Unauthorized function call"):
        compiler.validate_code(unsafe_call)


def test_parser_stage():
    stage = ParserStage()
    parsed = stage.execute('{"ir_version": "1.0.0", "ir_abi": 1}')
    assert parsed.data["ir_version"] == "1.0.0"

    with pytest.raises(ParserError):
        stage.execute("{broken json")


def test_schema_stage():
    stage = SchemaStage()
    
    valid_data = {
        "ir_version": "1.0.0",
        "ir_abi": 1,
        "name": "MyQuantizer",
        "strategy": "quantization.uniform.v1",
        "parameters": {"quantization_bits": 8, "symmetric": True},
        "objective": {
            "primary": "memory",
            "secondary": "latency",
            "constraints": {
                "max_accuracy_loss": 0.05,
                "max_latency_ms": 10.0
            }
        }
    }
    validated = stage.execute(ParsedIR(data=valid_data, raw_source=""))
    assert validated.data["name"] == "MyQuantizer"

    # Test invalid ir_version
    bad_version = dict(valid_data, ir_version="2.0.0")
    with pytest.raises(SchemaError, match="Unrecognized ir_version"):
        stage.execute(ParsedIR(data=bad_version, raw_source=""))


def test_canonicalizer_stage():
    stage = CanonicalizerStage()
    
    data = {"b": 2, "a": 1, "extensions": {"foo": "bar"}}
    validated = ValidatedIR(data=data)
    canonical = stage.execute(validated)
    # Check JCS lexicographical sorting
    assert canonical.canonical_json_str == '{"a":1,"b":2,"extensions":{"foo":"bar"}}'
    assert len(canonical.ir_sha256) == 64


def test_semantic_stage():
    stage = SemanticStage()
    
    base_data = {
        "strategy": "quantization.uniform.v1",
        "parameters": {"quantization_bits": 8, "symmetric": True}
    }
    canonical = CanonicalIR(
        canonical_json_bytes=b"",
        canonical_json_str="",
        ir_sha256="",
        data=base_data
    )
    semantic = stage.execute(canonical)
    assert semantic.strategy_key == "quantization.uniform.v1"

    # Test parameter bounds error
    bad_bits = {
        "strategy": "quantization.uniform.v1",
        "parameters": {"quantization_bits": 4, "symmetric": True}
    }
    bad_canonical = CanonicalIR(
        canonical_json_bytes=b"",
        canonical_json_str="",
        ir_sha256="",
        data=bad_bits
    )
    with pytest.raises(SemanticError, match="quantization_bits must be exactly 8"):
        stage.execute(bad_canonical)


def test_template_stage():
    stage = TemplateStage()
    
    data = {
        "name": "BlockQuantizer",
        "parameters": {
            "block_size": 32,
            "quantization_bits": 8,
            "symmetric": False
        }
    }
    semantic = SemanticIR(data=data, strategy_key="quantization.block.v1")
    generated = stage.execute(semantic)
    assert "class BlockQuantizer" in generated.plugin_source
    assert generated.plan.template_id == "TEMPLATE-002"
    assert len(generated.plan.registry_hash) == 64


def test_ast_stage():
    stage = ASTStage()
    plan = CompilationPlan(
        template_id="T1",
        template_version="1.0.0",
        template_abi=1,
        template_hash="",
        registry_version=1,
        registry_hash=""
    )
    
    # Safe code
    safe_code = "import numpy as np\nclass X:\n    pass"
    verified = stage.execute(GeneratedPlugin(plugin_source=safe_code, plan=plan))
    assert verified.plugin_source == safe_code

    # Unsafe code
    unsafe_code = "import os"
    with pytest.raises(ASTError, match="Unauthorized import"):
        stage.execute(GeneratedPlugin(plugin_source=unsafe_code, plan=plan))


def test_ir_compiler_pipeline():
    compiler = IRCompiler()
    
    valid_ir = """{
        "ir_version": "1.0.0",
        "ir_abi": 1,
        "name": "MyUniformQuant",
        "strategy": "quantization.uniform.v1",
        "parameters": {"quantization_bits": 8, "symmetric": true},
        "objective": {
            "primary": "memory",
            "secondary": "latency",
            "constraints": {
                "max_accuracy_loss": 0.01,
                "max_latency_ms": 2.0
            }
        }
    }"""
    
    artifact = compiler.compile_ir(valid_ir)
    assert "class MyUniformQuant" in artifact.plugin_source
    assert artifact.manifest.template_id == "TEMPLATE-001"
    assert artifact.manifest.compiler_abi == 1
    assert artifact.manifest.registry_version == 1
    assert artifact.manifest.manifest_hash is not None
    assert artifact.manifest_json is not None

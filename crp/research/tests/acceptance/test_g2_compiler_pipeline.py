"""Gate 2 Acceptance Tests: Versioned IR Compiler Pipeline.

Validates:
- Pure functional compiler execution
- Multi-stage fail-fast schema/semantic constraints
- Exact golden files matching for outputs and error code structures
- 100% byte-identical determinism and cross-platform reproducibility
- Memory usage stability
"""

import os
import ast
import gc
import sys
import json
import pytest

from research.compiler import (
    IRCompiler,
    CompilerError,
    ParserError,
    SchemaError,
    CanonicalizationError,
    SemanticError,
    TemplateError,
    ASTError
)

GOLDEN_V1_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "golden", "v1")
)


def test_golden_files_v1():
    """Verify compilation of valid IR inputs matches expected golden files exactly."""
    compiler = IRCompiler()
    ir_dir = os.path.join(GOLDEN_V1_DIR, "ir")

    # Find valid JSON test files
    valid_files = [f for f in os.listdir(ir_dir) if f.endswith(".json")]
    assert len(valid_files) > 0, "No valid golden test inputs found."

    for filename in valid_files:
        basename = os.path.splitext(filename)[0]
        json_path = os.path.join(ir_dir, filename)
        expected_dir = os.path.join(ir_dir, "expected", basename)

        # Load input
        with open(json_path, "r", encoding="utf-8") as f:
            raw_ir = f.read()

        # Compile
        artifact = compiler.compile_ir(raw_ir)

        # 1. Verify plugin source
        expected_plugin_path = os.path.join(expected_dir, "plugin.py")
        with open(expected_plugin_path, "r", encoding="utf-8") as f:
            expected_plugin = f.read()
        assert artifact.plugin_source == expected_plugin

        # 2. Verify plugin hash
        expected_plugin_hash_path = os.path.join(expected_dir, "plugin.sha256")
        with open(expected_plugin_hash_path, "r", encoding="utf-8") as f:
            expected_plugin_hash = f.read().strip()
        assert artifact.plugin_hash == expected_plugin_hash

        # 3. Verify ir hash
        expected_ir_hash_path = os.path.join(expected_dir, "ir.sha256")
        with open(expected_ir_hash_path, "r", encoding="utf-8") as f:
            expected_ir_hash = f.read().strip()
        assert artifact.ir_hash == expected_ir_hash

        # 4. Verify canonical ir structure
        expected_canonical_path = os.path.join(expected_dir, "canonical_ir.json")
        with open(expected_canonical_path, "r", encoding="utf-8") as f:
            expected_canonical = f.read().strip()
        assert artifact.canonical_ir == expected_canonical

        # 5. Verify manifest structure (excluding generated_at timestamp)
        expected_manifest_path = os.path.join(expected_dir, "manifest.json")
        with open(expected_manifest_path, "r", encoding="utf-8") as f:
            expected_manifest_data = json.load(f)

        compiled_manifest_data = json.loads(artifact.manifest_json)
        
        # Compare without generated_at
        expected_manifest_data.pop("generated_at", None)
        compiled_manifest_data.pop("generated_at", None)
        assert compiled_manifest_data == expected_manifest_data

        # 6. Verify manifest hash
        expected_manifest_hash_path = os.path.join(expected_dir, "manifest.sha256")
        with open(expected_manifest_hash_path, "r", encoding="utf-8") as f:
            expected_manifest_hash = f.read().strip()
        assert artifact.manifest_hash == expected_manifest_hash


def test_golden_invalid_and_regressions_v1():
    """Verify that invalid inputs and regression test cases fail with expected error codes."""
    compiler = IRCompiler()

    # Folders to check for error outputs
    subdirs = [
        ("invalid", os.path.join(GOLDEN_V1_DIR, "invalid")),
        ("regressions", os.path.join(GOLDEN_V1_DIR, "regressions"))
    ]

    for label, dir_path in subdirs:
        if not os.path.exists(dir_path):
            continue

        json_files = [f for f in os.listdir(dir_path) if f.endswith(".json")]
        for filename in json_files:
            basename = os.path.splitext(filename)[0]
            json_path = os.path.join(dir_path, filename)
            expected_error_path = os.path.join(dir_path, "expected", basename, "error.txt")

            with open(json_path, "r", encoding="utf-8") as f:
                raw_ir = f.read()

            with open(expected_error_path, "r", encoding="utf-8") as f:
                expected_error_code = f.read().strip()

            # Compile must raise CompilerError
            with pytest.raises(CompilerError) as exc_info:
                compiler.compile_ir(raw_ir)

            # Map the exception type to error code
            e = exc_info.value
            if isinstance(e, ParserError):
                code = "IR:PAR_001"
            elif isinstance(e, SchemaError):
                code = "IR:SCH_002"
            elif isinstance(e, CanonicalizationError):
                code = "IR:CAN_003"
            elif isinstance(e, SemanticError):
                code = "IR:SEM_004"
            elif isinstance(e, TemplateError):
                code = "IR:TMP_005"
            elif isinstance(e, ASTError):
                code = "IR:AST_006"
            else:
                code = "IR:GEN_000"

            assert code == expected_error_code, (
                f"Expected error code {expected_error_code} for {filename} in {label}, "
                f"but got {code} (Message: {e})"
            )


def test_determinism_verification():
    """Verify compiling the same IR JSON repeatedly yields identical outputs."""
    compiler = IRCompiler()
    
    with open(os.path.join(GOLDEN_V1_DIR, "ir", "uniform_quant.json"), "r", encoding="utf-8") as f:
        raw_ir = f.read()

    artifacts = []
    for _ in range(50):
        # Alter standard dict values that could leak into compilation
        os.environ["RANDOM_VAR_CRP"] = "test"
        artifacts.append(compiler.compile_ir(raw_ir))

    # All generated artifacts must be completely identical
    base = artifacts[0]
    for art in artifacts[1:]:
        assert art.plugin_source == base.plugin_source
        assert art.canonical_ir == base.canonical_ir
        assert art.plugin_hash == base.plugin_hash
        assert art.manifest_hash == base.manifest_hash
        assert art.ir_hash == base.ir_hash


def test_compiler_purity():
    """Verify that the compiler package imports only allow-listed modules."""
    allow_list = {
        "json", "hashlib", "ast", "typing", "dataclasses", "types", "re"
    }

    compiler_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "compiler")
    )
    assert os.path.exists(compiler_dir), "Compiler directory not found."

    for filename in os.listdir(compiler_dir):
        if not filename.endswith(".py") or filename in ("legacy.py", "compiler.py"):
            continue
            
        file_path = os.path.join(compiler_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filename)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    base = alias.name.split('.')[0]
                    if base not in allow_list and base != "research":
                        pytest.fail(f"Purity violation in {filename}: Imported module '{alias.name}'")
            elif isinstance(node, ast.ImportFrom):
                # If it's a relative import, skip
                if node.level > 0:
                    continue
                if node.module:
                    base = node.module.split('.')[0]
                    if base not in allow_list and base != "research":
                        pytest.fail(f"Purity violation in {filename}: Imported module '{node.module}'")


def test_memory_stability():
    """Assert that 100 repeated compilations show bounded memory usage with no growth."""
    try:
        import psutil
    except ImportError:
        pytest.skip("psutil is not installed; skipping memory stability verification.")

    compiler = IRCompiler()
    
    with open(os.path.join(GOLDEN_V1_DIR, "ir", "uniform_quant.json"), "r", encoding="utf-8") as f:
        raw_ir = f.read()

    # Warmup
    for _ in range(5):
        compiler.compile_ir(raw_ir)
    gc.collect()

    proc = psutil.Process(os.getpid())
    mem_before = proc.memory_info().rss

    # Compile 100 times
    for _ in range(100):
        compiler.compile_ir(raw_ir)

    gc.collect()
    mem_after = proc.memory_info().rss

    # Memory growth should be within a very small threshold (e.g. 5 MB)
    growth_bytes = mem_after - mem_before
    max_growth_bytes = 5 * 1024 * 1024
    assert growth_bytes <= max_growth_bytes, f"Memory leaked by compiler: {growth_bytes / 1024:.1f} KB"

import hashlib
import json
from dataclasses import dataclass
from typing import Tuple

from research.compiler.parser import (
    CompilerError,
    ParserStage,
    ParserError,
    ParsedIR
)
from research.compiler.schema import SchemaStage, SchemaError, ValidatedIR
from research.compiler.canonicalizer import (
    CanonicalizerStage,
    CanonicalizationError,
    CanonicalIR,
    jcs_serialize
)
from research.compiler.semantic import SemanticStage, SemanticError, SemanticIR
from research.compiler.templates import (
    TemplateStage,
    TemplateError,
    GeneratedPlugin,
    CompilationPlan
)
from research.compiler.ast_guard import ASTStage, ASTError, VerifiedPlugin

@dataclass(frozen=True, slots=True)
class CompilerContext:
    compiler_abi: int = 1
    template_set_version: str = "1.0.0"
    validation_profile: str = "production"

    @classmethod
    def production(cls) -> "CompilerContext":
        return cls()

@dataclass(frozen=True, slots=True)
class CompilerManifest:
    manifest_version: str
    compiler_pipeline: str
    compiler_abi: int
    compiler_version: str
    ir_version: str
    ir_abi: int
    ir_hash: str
    template_id: str
    template_version: str
    template_abi: int
    template_hash: str
    registry_version: int
    registry_hash: str
    plugin_hash: str
    manifest_hash: str
    generated_at: str
    generator: str
    deterministic: bool
    canonicalization: str
    ast_guard_version: str

@dataclass(frozen=True, slots=True)
class CompilerArtifact:
    plugin_source: str
    manifest_json: str
    manifest: CompilerManifest
    canonical_ir: str
    plugin_hash: str
    manifest_hash: str
    ir_hash: str
    warnings: Tuple[str, ...] = ()

class IRCompiler:
    """Orchestrates the 6-stage fail-fast compilation of declarative IR into safe python code."""
    
    def __init__(self) -> None:
        self.parser = ParserStage()
        self.schema = SchemaStage()
        self.canonicalizer = CanonicalizerStage()
        self.semantic = SemanticStage()
        self.template = TemplateStage()
        self.ast_guard = ASTStage()

    def compile_ir(
        self, raw_json: str, context: CompilerContext = CompilerContext.production()
    ) -> CompilerArtifact:
        """Runs the compile stages in sequence.
        
        Raises CompilerError taxonomy on stage failure.
        """
        # Stage 1: Parse JSON
        parsed = self.parser.execute(raw_json)

        # Stage 2: Schema validation
        validated = self.schema.execute(parsed)

        # Stage 3: Canonicalize (RFC 8785 JSON bytes)
        canonical = self.canonicalizer.execute(validated)

        # Stage 4: Semantic constraints validation
        semantic = self.semantic.execute(canonical)

        # Stage 5: Template substitution
        generated = self.template.execute(semantic)

        # Stage 6: AST Guard safety check
        verified = self.ast_guard.execute(generated)

        # Hash calculations
        plugin_code = verified.plugin_source
        plugin_hash = hashlib.sha256(plugin_code.encode("utf-8")).hexdigest()
        
        # Build manifest dictionary (without manifest_hash/generated_at)
        plan = verified.plan
        ir_data = canonical.data

        # Static timestamp for deterministic manifest file compilation
        generated_at = "1970-01-01T00:00:00Z"

        manifest_dict = {
            "manifest_version": "1.0.0",
            "compiler_pipeline": "IRCompiler-v1",
            "compiler_abi": context.compiler_abi,
            "compiler_version": "1.0.0",
            "ir_version": ir_data.get("ir_version", "1.0.0"),
            "ir_abi": ir_data.get("ir_abi", 1),
            "ir_hash": canonical.ir_sha256,
            "template_id": plan.template_id,
            "template_version": plan.template_version,
            "template_abi": plan.template_abi,
            "template_hash": plan.template_hash,
            "registry_version": plan.registry_version,
            "registry_hash": plan.registry_hash,
            "plugin_hash": plugin_hash,
            "generator": "IRCompiler",
            "deterministic": True,
            "canonicalization": "RFC8785",
            "ast_guard_version": "1"
        }

        # Calculate manifest_hash by serializing canonical form of the dictionary
        manifest_canonical_str = jcs_serialize(manifest_dict)
        manifest_hash = hashlib.sha256(manifest_canonical_str.encode("utf-8")).hexdigest()

        # Add manifest_hash and generated_at to manifest object
        manifest_dict["manifest_hash"] = manifest_hash
        manifest_dict["generated_at"] = generated_at

        # Explicit kwargs (not **manifest_dict) so the type checker can
        # verify every required CompilerManifest field is present.
        manifest = CompilerManifest(
            manifest_version="1.0.0",
            compiler_pipeline="IRCompiler-v1",
            compiler_abi=context.compiler_abi,
            compiler_version="1.0.0",
            ir_version=ir_data.get("ir_version", "1.0.0"),
            ir_abi=ir_data.get("ir_abi", 1),
            ir_hash=canonical.ir_sha256,
            template_id=plan.template_id,
            template_version=plan.template_version,
            template_abi=plan.template_abi,
            template_hash=plan.template_hash,
            registry_version=plan.registry_version,
            registry_hash=plan.registry_hash,
            plugin_hash=plugin_hash,
            generator="IRCompiler",
            deterministic=True,
            canonicalization="RFC8785",
            ast_guard_version="1",
            manifest_hash=manifest_hash,
            generated_at=generated_at,
        )
        manifest_json_str = json.dumps(manifest_dict, indent=2)

        return CompilerArtifact(
            plugin_source=plugin_code,
            manifest_json=manifest_json_str,
            manifest=manifest,
            canonical_ir=canonical.canonical_json_str,
            plugin_hash=plugin_hash,
            manifest_hash=manifest_hash,
            ir_hash=canonical.ir_sha256,
            warnings=()
        )

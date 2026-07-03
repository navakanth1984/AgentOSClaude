import ast
import builtins
from typing import Any
import numpy as np
import math

from research.compiler.parser import CompilerError
from research.compiler.ast_guard import ASTStage, ASTError

class DSLValidationError(CompilerError):
    """Raised when a candidate plugin fails AST/DSL safety check."""
    pass

class ConstrainedDSLCompiler:
    """AST validator and compiler that checks Python code blocks against safe plugin constraints."""
    
    def validate_code(self, source_code: str) -> bool:
        stage = ASTStage()
        from research.compiler.templates import GeneratedPlugin, CompilationPlan
        plan = CompilationPlan(
            template_id="LEGACY",
            template_version="1.0.0",
            template_abi=1,
            template_hash="",
            registry_version=1,
            registry_hash=""
        )
        try:
            stage.execute(GeneratedPlugin(plugin_source=source_code, plan=plan))
            return True
        except ASTError as exc:
            raise DSLValidationError(str(exc)) from exc

    def validate_only(self, source_code: str) -> bool:
        return self.validate_code(source_code)

    def compile_plugin(self, source_code: str, class_name: str = "QuantizedInt8DSL") -> Any:
        self.validate_code(source_code)
        
        local_scope = {}
        safe_globals = {
            "__builtins__": {
                "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict, "float": float,
                "int": int, "len": len, "list": list, "map": map, "max": max, "min": min,
                "range": range, "round": round, "set": set, "str": str, "sum": sum, "tuple": tuple,
                "zip": zip, "object": object, "super": super, "property": property,
                "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError,
                "__build_class__": builtins.__build_class__,
                "__import__": builtins.__import__
            },
            "__name__": "sandbox_plugin",
            "np": np,
            "numpy": np,
            "math": math
        }
        
        try:
            exec(source_code, safe_globals, local_scope)
        except Exception as e:
            raise DSLValidationError(f"Failed to execute candidate code compilation: {e}")

        if class_name not in local_scope:
            classes = [v for k, v in local_scope.items() if isinstance(v, type)]
            if not classes:
                raise DSLValidationError("No class definition found in candidate code.")
            return classes[0]

        return local_scope[class_name]

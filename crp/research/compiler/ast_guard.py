import ast
from dataclasses import dataclass

from research.compiler.parser import CompilerError, CompilerStage
from research.compiler.templates import GeneratedPlugin, CompilationPlan

class ASTError(CompilerError):
    """AST guard security validation failure (IR:AST_006)."""
    pass

@dataclass(frozen=True, slots=True)
class VerifiedPlugin:
    plugin_source: str
    plan: CompilationPlan

class ASTStage(CompilerStage[GeneratedPlugin, VerifiedPlugin]):
    ALLOWED_IMPORTS = {"numpy", "math", "typing"}
    BLOCKED_FUNCTIONS = {"eval", "exec", "open", "input", "globals", "locals", "compile", "dir", "vars", "getattr", "setattr"}

    def execute(self, input: GeneratedPlugin) -> VerifiedPlugin:
        """Parses the generated Python code and runs AST safety validation.
        
        Raises ASTError if any security rule is violated.
        """
        source = input.plugin_source
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            raise ASTError(f"Syntax error in generated candidate code: {exc}") from exc

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.name.split('.')[0] for alias in node.names]
                for name in names:
                    if name not in self.ALLOWED_IMPORTS:
                        raise ASTError(
                            f"Unauthorized import in candidate: '{name}'. "
                            f"Only {sorted(list(self.ALLOWED_IMPORTS))} are allowed."
                        )
            
            # Check for from imports
            if isinstance(node, ast.ImportFrom) and node.module:
                base_module = node.module.split('.')[0]
                if base_module not in self.ALLOWED_IMPORTS:
                    raise ASTError(f"Unauthorized import module in candidate: '{node.module}'")

            # Check calls to forbidden builtins
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.BLOCKED_FUNCTIONS:
                        raise ASTError(f"Unauthorized function call in candidate: '{node.func.id}'")
                elif isinstance(node.func, ast.Attribute):
                    # Prevent calling standard dunder attributes that could bypass controls
                    if node.func.attr.startswith("__") and node.func.attr.endswith("__"):
                        raise ASTError(f"Dunder attribute call blocked in candidate: '{node.func.attr}'")

        return VerifiedPlugin(plugin_source=source, plan=input.plan)

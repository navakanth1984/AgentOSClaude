from dataclasses import dataclass
from typing import Dict, Any

from research.compiler.parser import CompilerError, CompilerStage
from research.compiler.canonicalizer import CanonicalIR

class SemanticError(CompilerError):
    """Semantic domain constraints failure (IR:SEM_004)."""
    pass

@dataclass(frozen=True, slots=True)
class SemanticIR:
    data: dict
    strategy_key: str

class SemanticStage(CompilerStage[CanonicalIR, SemanticIR]):
    def execute(self, input: CanonicalIR) -> SemanticIR:
        """Validate strategy-specific parameters and semantic bounds.
        
        Raises SemanticError if constraints are violated.
        """
        data = input.data
        strategy = data["strategy"]
        parameters = data["parameters"]

        if strategy == "quantization.uniform.v1":
            # Check required params
            for p in ["quantization_bits", "symmetric"]:
                if p not in parameters:
                    raise SemanticError(f"Missing parameter '{p}' for strategy {strategy}")

            bits = parameters["quantization_bits"]
            sym = parameters["symmetric"]

            if bits != 8:
                raise SemanticError(f"quantization_bits must be exactly 8 in v1.0.0. Got {bits}")
            if not isinstance(sym, bool):
                raise SemanticError(f"symmetric must be a boolean. Got {sym}")

        elif strategy == "quantization.block.v1":
            for p in ["block_size", "quantization_bits", "symmetric"]:
                if p not in parameters:
                    raise SemanticError(f"Missing parameter '{p}' for strategy {strategy}")

            block_size = parameters["block_size"]
            bits = parameters["quantization_bits"]
            sym = parameters["symmetric"]

            if block_size not in {16, 32, 64, 128}:
                raise SemanticError(f"block_size must be in [16, 32, 64, 128]. Got {block_size}")
            if bits != 8:
                raise SemanticError(f"quantization_bits must be exactly 8 in v1.0.0. Got {bits}")
            if not isinstance(sym, bool):
                raise SemanticError(f"symmetric must be a boolean. Got {sym}")

        elif strategy == "sparsity.threshold.v1":
            for p in ["threshold", "relative"]:
                if p not in parameters:
                    raise SemanticError(f"Missing parameter '{p}' for strategy {strategy}")

            threshold = parameters["threshold"]
            relative = parameters["relative"]

            if not isinstance(threshold, (int, float)) or not (0.0 <= threshold <= 1.0):
                raise SemanticError(f"threshold must be in [0.0, 1.0]. Got {threshold}")
            if not isinstance(relative, bool):
                raise SemanticError(f"relative must be a boolean. Got {relative}")

            if relative and not (0.0 <= threshold <= 0.5):
                raise SemanticError(f"relative threshold must be in [0.0, 0.5]. Got {threshold}")

        elif strategy == "decomposition.svd.v1":
            if "target_rank" not in parameters:
                raise SemanticError(f"Missing parameter 'target_rank' for strategy {strategy}")

            target_rank = parameters["target_rank"]
            if not isinstance(target_rank, int) or not (1 <= target_rank <= 128):
                raise SemanticError(f"target_rank must be an integer in [1, 128]. Got {target_rank}")

        else:
            raise SemanticError(f"Unrecognized strategy key: {strategy}")

        return SemanticIR(data=data, strategy_key=strategy)

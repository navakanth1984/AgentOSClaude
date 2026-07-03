import re
from dataclasses import dataclass
from typing import Dict, Any

from research.compiler.parser import CompilerError, ParsedIR, CompilerStage

class SchemaError(CompilerError):
    """Schema structural layout failure (IR:SCH_002)."""
    pass

@dataclass(frozen=True, slots=True)
class ValidatedIR:
    data: dict

# Regular expression to match valid names: alphanumeric and underscores
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")

VALID_STRATEGIES = {
    "quantization.uniform.v1",
    "quantization.block.v1",
    "sparsity.threshold.v1",
    "decomposition.svd.v1"
}

VALID_OBJECTIVE_FIELDS = {"memory", "latency", "accuracy"}

class SchemaStage(CompilerStage[ParsedIR, ValidatedIR]):
    def execute(self, input: ParsedIR) -> ValidatedIR:
        """Validate structure and types of the parsed IR data.
        
        Raises SchemaError if validation fails.
        """
        data = input.data

        # Required top-level keys
        required_keys = {"ir_version", "ir_abi", "name", "strategy", "parameters", "objective"}
        missing = required_keys - data.keys()
        if missing:
            raise SchemaError(f"Missing required fields: {sorted(list(missing))}")

        # Type & value checks
        if data["ir_version"] != "1.0.0":
            raise SchemaError(f"Unrecognized ir_version: {data['ir_version']}. Must be '1.0.0'.")

        if data["ir_abi"] != 1:
            raise SchemaError(f"Unsupported ir_abi class: {data['ir_abi']}. Must be 1.")

        name = data["name"]
        if not isinstance(name, str) or not NAME_PATTERN.match(name):
            raise SchemaError(f"Invalid plugin name pattern: {name}")

        strategy = data["strategy"]
        if strategy not in VALID_STRATEGIES:
            raise SchemaError(f"Unrecognized strategy key: {strategy}")

        if not isinstance(data["parameters"], dict):
            raise SchemaError("parameters must be a JSON object.")

        # Objective check
        objective = data["objective"]
        if not isinstance(objective, dict):
            raise SchemaError("objective must be a JSON object.")

        obj_required = {"primary", "secondary", "constraints"}
        obj_missing = obj_required - objective.keys()
        if obj_missing:
            raise SchemaError(f"Missing objective fields: {sorted(list(obj_missing))}")

        primary = objective["primary"]
        secondary = objective["secondary"]
        if primary not in VALID_OBJECTIVE_FIELDS:
            raise SchemaError(f"Invalid primary objective: {primary}")
        if secondary not in VALID_OBJECTIVE_FIELDS:
            raise SchemaError(f"Invalid secondary objective: {secondary}")

        constraints = objective["constraints"]
        if not isinstance(constraints, dict):
            raise SchemaError("objective.constraints must be a JSON object.")

        const_required = {"max_accuracy_loss", "max_latency_ms"}
        const_missing = const_required - constraints.keys()
        if const_missing:
            raise SchemaError(f"Missing constraints: {sorted(list(const_missing))}")

        acc_loss = constraints["max_accuracy_loss"]
        lat_ms = constraints["max_latency_ms"]

        if not isinstance(acc_loss, (int, float)) or not (0.0 <= acc_loss <= 1.0):
            raise SchemaError(f"max_accuracy_loss must be a float in [0.0, 1.0]. Got {acc_loss}")
        if not isinstance(lat_ms, (int, float)) or lat_ms < 0.0:
            raise SchemaError(f"max_latency_ms must be a non-negative float. Got {lat_ms}")

        # Optional extensions and metadata
        if "extensions" in data and not isinstance(data["extensions"], dict):
            raise SchemaError("extensions must be a JSON object.")
        if "metadata" in data and not isinstance(data["metadata"], dict):
            raise SchemaError("metadata must be a JSON object.")

        return ValidatedIR(data=data)

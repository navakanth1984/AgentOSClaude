import hashlib
import json
from dataclasses import dataclass
from typing import Any

from research.compiler.parser import CompilerError, CompilerStage
from research.compiler.schema import ValidatedIR

class CanonicalizationError(CompilerError):
    """Canonical serialization failure (IR:CAN_003)."""
    pass

@dataclass(frozen=True, slots=True)
class CanonicalIR:
    canonical_json_bytes: bytes
    canonical_json_str: str
    ir_sha256: str
    data: dict


def _canonical_number(val: Any) -> str:
    """Format float or int according to RFC 8785 rules."""
    if isinstance(val, bool):
        # Python bool is subclass of int, check this first!
        return "true" if val else "false"
        
    if isinstance(val, int):
        return str(val)

    if isinstance(val, float):
        # Handled nan/inf check
        if val != val or val == float('inf') or val == float('-inf'):
            raise CanonicalizationError("NaN and Infinity are not valid JSON numbers.")

        # Whole float whole numbers are represented as integers in JCS
        if val.is_integer():
            return str(int(val))

        s = repr(val)
        if 'e' in s or 'E' in s:
            parts = s.lower().split('e')
            mantissa = parts[0]
            exponent = parts[1]
            # Strip positive sign and leading zeros from exponent
            exponent = exponent.replace('+', '')
            neg = '-' if exponent.startswith('-') else ''
            exp_digits = exponent.lstrip('-0')
            if not exp_digits:
                exp_digits = '0'
            s = f"{mantissa}e{neg}{exp_digits}"
        return s

    raise CanonicalizationError(f"Unsupported number type: {type(val)}")


def jcs_serialize(val: Any) -> str:
    """Recursively serialize a value strictly following RFC 8785 (JCS)."""
    if val is None:
        return "null"

    if isinstance(val, bool):
        return "true" if val else "false"

    if isinstance(val, (int, float)):
        return _canonical_number(val)

    if isinstance(val, str):
        # json.dumps handles correct JCS escapes and wrapping in double quotes
        return json.dumps(val, ensure_ascii=False)

    if isinstance(val, list):
        items = [jcs_serialize(item) for item in val]
        return "[" + ",".join(items) + "]"

    if isinstance(val, dict):
        # Sort keys lexicographically by Unicode points
        sorted_keys = sorted(val.keys())
        items = []
        for k in sorted_keys:
            items.append(f"{json.dumps(k, ensure_ascii=False)}:{jcs_serialize(val[k])}")
        return "{" + ",".join(items) + "}"

    raise CanonicalizationError(f"Unsupported type during JCS serialization: {type(val)}")


class CanonicalizerStage(CompilerStage[ValidatedIR, CanonicalIR]):
    def execute(self, input: ValidatedIR) -> CanonicalIR:
        """Canonicalize a ValidatedIR dictionary to RFC 8785 JSON bytes.
        
        Computes ir_sha256 hash. Preserves extensions.
        """
        try:
            data = input.data
            canonical_str = jcs_serialize(data)
            canonical_bytes = canonical_str.encode("utf-8")
            
            ir_sha256 = hashlib.sha256(canonical_bytes).hexdigest()
            
            return CanonicalIR(
                canonical_json_bytes=canonical_bytes,
                canonical_json_str=canonical_str,
                ir_sha256=ir_sha256,
                data=data
            )
        except Exception as exc:
            if isinstance(exc, CanonicalizationError):
                raise exc
            raise CanonicalizationError(f"Canonicalization failure: {exc}") from exc

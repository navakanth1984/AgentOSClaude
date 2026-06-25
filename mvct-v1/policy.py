"""Gate policy. The confidence threshold is an EXPERIMENTAL VARIABLE, not an
architectural law (spec section 3.2) — sweep these named policies across runs.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class GatePolicy:
    classification_required: str
    confidence_floor: float
    unlock_strategy: str = "binary"


STRICT = GatePolicy("transfer", 0.90)
RESEARCH = GatePolicy("transfer", 0.65)
BINARY = GatePolicy("transfer", 0.0)  # classification-only


def satisfies(policy: GatePolicy, classification: str, confidence: float) -> bool:
    return (
        classification == policy.classification_required
        and confidence >= policy.confidence_floor
    )

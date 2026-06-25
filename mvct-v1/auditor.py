"""The Capability Auditor: the ONLY module permitted to mint a PermissionToken.
Fail-closed — any sensor error yields no token (a governance gate must never
unlock on failure).
"""
from dataclasses import dataclass

from permission import mint_token, PermissionToken
from policy import GatePolicy, satisfies
from sensor import TransferSensor


@dataclass(frozen=True)
class AuditResult:
    token: PermissionToken | None
    classification: str
    confidence: float
    evidence: list
    reason: str


class CapabilityAuditor:
    def __init__(self, sensor: TransferSensor, policy: GatePolicy, key: bytes):
        self._sensor = sensor
        self._policy = policy
        self._key = key

    def evaluate(self, transcript: dict, current_turn: int) -> AuditResult:
        try:
            reading = self._sensor.read(transcript)
        except Exception as e:  # fail-closed: a sensor error must never unlock
            return AuditResult(None, "none", 0.0, [], f"fail-closed: sensor error ({e})")

        if satisfies(self._policy, reading.classification, reading.confidence):
            token = mint_token(
                self._key,
                classification=reading.classification,
                confidence=reading.confidence,
                current_turn=current_turn,
            )
            return AuditResult(token, reading.classification, reading.confidence,
                               reading.evidence_quotes, "unlocked: policy satisfied")

        return AuditResult(None, reading.classification, reading.confidence,
                           reading.evidence_quotes, "locked: policy not satisfied")

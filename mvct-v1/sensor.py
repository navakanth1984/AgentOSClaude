"""Single seam over transfer-detector-v0. The Auditor depends on this adapter,
not on detector.judge directly. Swap judge_fn to drop in a real-human-validated
detector later without touching any other module (addresses the over-coupling risk
and the synthetic-ceiling caveat, spec sections 2.3 / 3.1).
"""
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass(frozen=True)
class SensorReading:
    classification: str
    confidence: float
    confidence_breakdown: dict = field(default_factory=dict)
    evidence_quotes: list = field(default_factory=list)


class TransferSensor:
    def __init__(self, judge_fn: Optional[Callable[..., dict]] = None,
                 api_key: Optional[str] = None):
        if judge_fn is None:
            from detector.judge import judge_transfer
            judge_fn = judge_transfer
        self._judge = judge_fn
        self._api_key = api_key

    def read(self, transcript: dict) -> SensorReading:
        out = self._judge(transcript, api_key=self._api_key) or {}
        return SensorReading(
            classification=out.get("classification", "none"),
            confidence=float(out.get("confidence", 0.0)),
            confidence_breakdown=out.get("confidence_breakdown", {}) or {},
            evidence_quotes=out.get("evidence_quotes", []) or [],
        )

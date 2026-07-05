"""
ExecutionManifest — structured, replayable audit trail for one execution run.

Persisted as JSON so mixture/debate/auto runs can later be compared, replayed,
or fed into analytics — mirrors the audit-trail habit already used elsewhere
in this repo (CRP's Experience DB, Site Builder's generation log).
"""

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

MANIFEST_DIR = Path(__file__).parent.parent / "output" / "execution_manifests"


@dataclass
class ExecutionManifest:
    execution_id: str
    mode: str
    models: list[str]
    aggregation: Optional[str] = None
    consensus_score: Optional[float] = None
    conflicts: list[str] = field(default_factory=list)
    winner: Optional[str] = None
    cost: float = 0.0
    latency_ms: float = 0.0
    tokens: int = 0
    provider_breakdown: dict = field(default_factory=dict)
    per_model: list[dict] = field(default_factory=list)
    aggregation_trace: dict = field(default_factory=dict)
    verification: Optional[dict] = None
    final: str = ""
    timeline: list[dict] = field(default_factory=list)

    def add_event(self, label: str, **extra):
        self.timeline.append({"t": time.time(), "event": label, **extra})

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self) -> Path:
        MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
        path = MANIFEST_DIR / f"{self.execution_id}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return path


def new_manifest(mode: str, models: list[str], aggregation: Optional[str] = None) -> ExecutionManifest:
    m = ExecutionManifest(
        execution_id=uuid.uuid4().hex[:12],
        mode=mode,
        models=list(models),
        aggregation=aggregation,
    )
    m.add_event("execution_started")
    return m

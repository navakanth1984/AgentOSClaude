"""Replay a stored Experience DB run and verify decision determinism.

Spec 2a: same workload + same policy inputs => same decision, 100% of the
time. Divergence is a hard failure (R-004), reported with a field-level diff.
Telemetry timestamps are wall-clock and intentionally excluded from the
comparison; the decision (chosen, scores, rejections) is the replay contract.
"""

from __future__ import annotations

from dataclasses import dataclass

from crp_runtime.experience import ExperienceDB, StoredRun
from crp_runtime.harness import run_workload
from crp_runtime.policy import Decision
from crp_runtime.workloads import WorkloadSpec


@dataclass(frozen=True)
class ReplayResult:
    run_id: int
    deterministic: bool
    diff: str = ""


def _compare(stored: StoredRun, fresh: Decision) -> str:
    diffs: list[str] = []
    if fresh.chosen != stored.chosen:
        diffs.append(f"chosen: stored={stored.chosen!r} replay={fresh.chosen!r}")
    if fresh.scores != stored.scores:
        diffs.append(f"scores: stored={stored.scores!r} replay={fresh.scores!r}")
    if fresh.rejected != stored.rejections:
        diffs.append(
            f"rejections: stored={stored.rejections!r} replay={fresh.rejected!r}"
        )
    return "; ".join(diffs)


def replay_run(db: ExperienceDB, run_id: int) -> ReplayResult:
    stored = db.get_run(run_id)
    spec = WorkloadSpec.from_json(stored.spec_json)
    fresh = run_workload(spec, stored.constraints, stored.profile)
    diff = _compare(stored, fresh.decision)
    return ReplayResult(run_id=run_id, deterministic=not diff, diff=diff)

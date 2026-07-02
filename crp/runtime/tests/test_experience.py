import numpy as np

from crp_runtime.experience import ExperienceDB, canonical_json
from crp_runtime.harness import run_workload
from crp_runtime.policy import Constraints, Profile
from crp_runtime.workloads import WorkloadSpec

CONSTRAINTS = Constraints(
    max_memory_bytes=1 << 30, max_accuracy_loss=0.05, max_latency_ms=100.0
)
PROFILE = Profile(alpha_memory=1.0, beta_latency=1.0, gamma_accuracy=1.0)
SPEC = WorkloadSpec(
    name="synthetic_tensor", params={"rows": 64, "cols": 64, "rank": 4}, seed=7
)


def _record():
    return run_workload(SPEC, CONSTRAINTS, PROFILE)


def test_canonical_json_is_order_independent() -> None:
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})


def test_insert_and_get_roundtrip(tmp_path) -> None:
    db = ExperienceDB(tmp_path / "exp.db")
    record = _record()
    run_id = db.insert_run(record, CONSTRAINTS, PROFILE)
    stored = db.get_run(run_id)

    assert stored.spec_json == record.spec_json
    assert stored.chosen == record.decision.chosen
    assert stored.scores == record.decision.scores
    assert stored.rejections == record.decision.rejected
    assert stored.dropped == record.dropped
    assert stored.constraints == CONSTRAINTS
    assert stored.profile == PROFILE


def test_events_stored_verbatim_in_order(tmp_path) -> None:
    db = ExperienceDB(tmp_path / "exp.db")
    record = _record()
    run_id = db.insert_run(record, CONSTRAINTS, PROFILE)
    assert db.get_run(run_id).events == record.events
    assert len(record.events) > 0


def test_runs_lists_ids(tmp_path) -> None:
    db = ExperienceDB(tmp_path / "exp.db")
    ids = [db.insert_run(_record(), CONSTRAINTS, PROFILE) for _ in range(3)]
    assert db.runs() == ids

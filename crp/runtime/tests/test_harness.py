import pytest

from crp_runtime.policy import Constraints, Profile
from crp_runtime.workloads import WorkloadSpec

crp_telemetry = pytest.importorskip("crp_telemetry")

from crp_runtime.harness import run_workload  # noqa: E402

CONSTRAINTS = Constraints(max_memory_bytes=10**9, max_accuracy_loss=0.01, max_latency_ms=10.0)
PROFILE = Profile(alpha_memory=1.0, beta_latency=0.1, gamma_accuracy=100.0)


def _spec() -> WorkloadSpec:
    return WorkloadSpec(
        name="embedding_search",
        params={"n": 500, "dim": 64, "queries": 16},
        seed=99,
    )


def test_run_produces_decision_and_events() -> None:
    rec = run_workload(_spec(), CONSTRAINTS, PROFILE)
    assert rec.decision.chosen in {"dense", "int8"}
    kinds = {e[1] for e in rec.events}
    assert {1, 2} <= kinds
    assert rec.dropped == 0


def test_replay_determinism_100_percent() -> None:
    a = run_workload(_spec(), CONSTRAINTS, PROFILE)
    b = run_workload(_spec(), CONSTRAINTS, PROFILE)
    assert a.spec_json == b.spec_json
    assert a.decision.chosen == b.decision.chosen
    assert a.decision.scores == b.decision.scores
    assert a.decision.rejected == b.decision.rejected


def test_synthetic_spec_also_runs() -> None:
    spec = WorkloadSpec(
        name="synthetic_tensor",
        params={"rows": 64, "cols": 32, "rank": 4, "sparsity": 0.0},
        seed=42,
    )
    rec = run_workload(spec, CONSTRAINTS, PROFILE)
    assert rec.decision.chosen in {"dense", "int8"}

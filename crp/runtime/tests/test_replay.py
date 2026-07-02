from crp_runtime.experience import ExperienceDB
from crp_runtime.harness import run_workload
from crp_runtime.policy import Constraints, Profile
from crp_runtime.replay import replay_run
from crp_runtime.workloads import WorkloadSpec

CONSTRAINTS = Constraints(
    max_memory_bytes=1 << 30, max_accuracy_loss=0.05, max_latency_ms=100.0
)
PROFILE = Profile(alpha_memory=1.0, beta_latency=1.0, gamma_accuracy=1.0)

SYNTHETIC = WorkloadSpec(
    name="synthetic_tensor", params={"rows": 64, "cols": 64, "rank": 4}, seed=7
)
EMBEDDING = WorkloadSpec(
    name="embedding_search", params={"n": 256, "dim": 32, "queries": 4}, seed=11
)


def _insert(db: ExperienceDB, spec: WorkloadSpec) -> int:
    return db.insert_run(run_workload(spec, CONSTRAINTS, PROFILE), CONSTRAINTS, PROFILE)


def test_synthetic_replay_is_deterministic(tmp_path) -> None:
    db = ExperienceDB(tmp_path / "exp.db")
    result = replay_run(db, _insert(db, SYNTHETIC))
    assert result.deterministic, result.diff


def test_embedding_replay_is_deterministic(tmp_path) -> None:
    db = ExperienceDB(tmp_path / "exp.db")
    result = replay_run(db, _insert(db, EMBEDDING))
    assert result.deterministic, result.diff


def test_tampered_decision_detected(tmp_path) -> None:
    db = ExperienceDB(tmp_path / "exp.db")
    run_id = _insert(db, SYNTHETIC)
    db._conn.execute("UPDATE runs SET chosen = 'bogus' WHERE id = ?", (run_id,))
    db._conn.commit()
    result = replay_run(db, run_id)
    assert not result.deterministic
    assert "chosen" in result.diff

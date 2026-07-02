import numpy as np

from crp_runtime.plugins_int8 import Int8Plugin
from crp_runtime.policy import Constraints, Profile, select_representation
from crp_runtime.representations import DensePlugin, RepresentationPlugin

PLUGINS: list[RepresentationPlugin] = [DensePlugin(), Int8Plugin()]
PROFILE = Profile(alpha_memory=1.0, beta_latency=0.1, gamma_accuracy=100.0)


def _tensor() -> np.ndarray:
    return np.random.default_rng(5).standard_normal((128, 64)).astype(np.float32)


def test_memory_pressure_prefers_int8() -> None:
    t = _tensor()
    c = Constraints(max_memory_bytes=t.nbytes, max_accuracy_loss=0.01, max_latency_ms=10.0)
    d = select_representation(t, PLUGINS, c, PROFILE)
    assert d.chosen == "int8"
    assert d.scores["int8"] < d.scores["dense"]


def test_tight_accuracy_constraint_rejects_int8() -> None:
    t = _tensor()
    c = Constraints(max_memory_bytes=t.nbytes, max_accuracy_loss=1e-9, max_latency_ms=10.0)
    d = select_representation(t, PLUGINS, c, PROFILE)
    assert d.chosen == "dense"
    assert "int8" in d.rejected and "accuracy" in d.rejected["int8"]


def test_all_infeasible_falls_back_to_dense() -> None:
    t = _tensor()
    c = Constraints(max_memory_bytes=1, max_accuracy_loss=1e-12, max_latency_ms=10.0)
    d = select_representation(t, PLUGINS, c, PROFILE)
    assert d.chosen == "dense"
    assert len(d.rejected) == 2


def test_decision_is_deterministic() -> None:
    t = _tensor()
    c = Constraints(max_memory_bytes=t.nbytes, max_accuracy_loss=0.01, max_latency_ms=10.0)
    d1 = select_representation(t, PLUGINS, c, PROFILE)
    d2 = select_representation(t, PLUGINS, c, PROFILE)
    assert d1.chosen == d2.chosen
    assert d1.scores == d2.scores
    assert d1.rejected == d2.rejected


def test_decision_latency_budget_spec_2a() -> None:
    t = _tensor()
    c = Constraints(max_memory_bytes=t.nbytes, max_accuracy_loss=0.01, max_latency_ms=10.0)
    latencies = [
        select_representation(t, PLUGINS, c, PROFILE).decision_latency_ms for _ in range(50)
    ]
    mean_ms = sum(latencies) / len(latencies)
    assert mean_ms < 5.0, f"HARD FAIL spec 2a: decision latency {mean_ms:.3f} ms > 5 ms"
    if mean_ms >= 1.0:
        import pytest

        pytest.xfail(f"Target miss (not hard fail): {mean_ms:.3f} ms >= 1 ms")

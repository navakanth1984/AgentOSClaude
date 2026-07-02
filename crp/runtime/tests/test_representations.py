import numpy as np

from crp_runtime.representations import REGISTRY, DensePlugin, register


def test_dense_roundtrip_is_exact() -> None:
    rng = np.random.default_rng(3)
    t = rng.standard_normal((16, 8)).astype(np.float32)
    plugin = DensePlugin()
    converted = plugin.convert(t)
    np.testing.assert_array_equal(plugin.restore(converted), t)


def test_dense_analyze_reports_stats() -> None:
    t = np.zeros((10, 10), dtype=np.float32)
    t[0, 0] = 1.0
    stats = DensePlugin().analyze(t)
    assert stats.shape == (10, 10)
    assert 0.98 <= stats.sparsity <= 1.0
    assert stats.memory_bytes == t.nbytes


def test_dense_estimate_zero_loss() -> None:
    t = np.ones((4, 4), dtype=np.float32)
    plugin = DensePlugin()
    est = plugin.estimate(plugin.analyze(t))
    assert est.accuracy_loss == 0.0
    assert est.memory_bytes == t.nbytes


def test_registry_contains_dense() -> None:
    register(DensePlugin())
    assert "dense" in REGISTRY

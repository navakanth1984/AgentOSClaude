import numpy as np

from crp_runtime.plugins_int8 import Int8Plugin


def test_int8_roundtrip_error_is_bounded() -> None:
    rng = np.random.default_rng(11)
    t = rng.standard_normal((32, 16)).astype(np.float32)
    plugin = Int8Plugin()
    restored = plugin.restore(plugin.convert(t))
    max_abs = float(np.max(np.abs(t)))
    assert float(np.max(np.abs(restored - t))) <= max_abs / 127.0 + 1e-6


def test_int8_memory_is_quarter_of_float32() -> None:
    t = np.ones((64, 64), dtype=np.float32)
    plugin = Int8Plugin()
    est = plugin.estimate(plugin.analyze(t))
    assert est.memory_bytes == t.nbytes // 4


def test_int8_execute_matches_dense_within_tolerance() -> None:
    rng = np.random.default_rng(12)
    corpus = rng.standard_normal((50, 8)).astype(np.float32)
    queries = rng.standard_normal((4, 8)).astype(np.float32)
    plugin = Int8Plugin()
    approx = plugin.execute(plugin.convert(corpus), queries)
    exact = corpus @ queries.T
    assert np.max(np.abs(approx - exact)) < 0.15


def test_int8_zero_tensor_does_not_divide_by_zero() -> None:
    t = np.zeros((4, 4), dtype=np.float32)
    plugin = Int8Plugin()
    restored = plugin.restore(plugin.convert(t))
    np.testing.assert_array_equal(restored, t)

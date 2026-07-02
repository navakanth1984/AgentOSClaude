import numpy as np

from crp_runtime.workloads import SyntheticTensorWorkload, WorkloadSpec


def _spec() -> WorkloadSpec:
    return WorkloadSpec(
        name="synthetic_tensor",
        params={"rows": 64, "cols": 48, "rank": 4, "sparsity": 0.0},
        seed=1234,
    )


def test_spec_json_roundtrip() -> None:
    spec = _spec()
    restored = WorkloadSpec.from_json(spec.to_json())
    assert restored == spec


def test_synthetic_workload_is_deterministic() -> None:
    a = SyntheticTensorWorkload(_spec()).tensors()
    b = SyntheticTensorWorkload(_spec()).tensors()
    assert len(a) == len(b) == 1
    np.testing.assert_array_equal(a[0], b[0])


def test_synthetic_workload_respects_shape_and_rank() -> None:
    t = SyntheticTensorWorkload(_spec()).tensors()[0]
    assert t.shape == (64, 48)
    assert np.linalg.matrix_rank(t) == 4


def test_embedding_workload_deterministic_and_shaped() -> None:
    spec = WorkloadSpec(
        name="embedding_search",
        params={"n": 200, "dim": 32, "queries": 8},
        seed=7,
    )
    from crp_runtime.workloads import EmbeddingSearchWorkload

    w1, w2 = EmbeddingSearchWorkload(spec), EmbeddingSearchWorkload(spec)
    c1, q1 = w1.tensors()
    c2, q2 = w2.tensors()
    np.testing.assert_array_equal(c1, c2)
    np.testing.assert_array_equal(q1, q2)
    assert c1.shape == (200, 32) and q1.shape == (8, 32)
    top = EmbeddingSearchWorkload.top_k(c1, q1, k=5)
    assert top.shape == (8, 5)
    assert top.dtype == np.int64

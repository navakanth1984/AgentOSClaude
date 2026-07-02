"""Spec §2a: Tier-0 overhead target <5 µs, hard fail >10 µs (through Python)."""

import statistics
import time

import pytest

crp_telemetry = pytest.importorskip("crp_telemetry")

HARD_LIMIT_US = 10.0
TARGET_US = 5.0
N = 50_000


def _measure_mean_us() -> float:
    t = crp_telemetry.Telemetry(capacity=1 << 17)
    samples: list[float] = []
    for i in range(N):
        start = time.perf_counter_ns()
        t.record(kind=1, tensor_id=i, value=1.0)
        samples.append((time.perf_counter_ns() - start) / 1000.0)
        if len(t) > (1 << 16):
            t.drain(1 << 16)
    return statistics.mean(samples)


def test_tier0_hard_limit() -> None:
    mean_us = _measure_mean_us()
    print(f"\nTier-0 mean overhead via Python: {mean_us:.3f} us")
    assert mean_us < HARD_LIMIT_US, (
        f"HARD FAIL: {mean_us:.3f} us > {HARD_LIMIT_US} us (spec 2a). "
        "Update RISKS.md R-002 and stop."
    )


def test_tier0_target_soft() -> None:
    mean_us = _measure_mean_us()
    if mean_us >= TARGET_US:
        pytest.xfail(f"Target miss (not hard fail): {mean_us:.3f} us >= {TARGET_US} us")

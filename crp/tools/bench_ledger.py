"""Benchmark Ledger for CRP Tier-0 telemetry.

Measures three layers so regressions can be localized precisely:
  1. native_rust  — criterion's saved estimates for Ring::record (ns)
  2. ffi          — Python->Rust Telemetry.record() per-call overhead (us)
  3. end_to_end   — record N events + drain them through the Python API (us/event)

Each run appends one JSON line to crp/docs/benchmarks/ledger.jsonl with full
provenance: hardware, OS, Python, rustc, toolchain, and git commit.

Usage:  py -3.12 crp/tools/bench_ledger.py
"""

from __future__ import annotations

import json
import platform
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any

import crp_telemetry

REPO_ROOT = Path(__file__).resolve().parents[2]
CRITERION_ESTIMATES = (
    REPO_ROOT / "crp" / "telemetry" / "target" / "criterion" / "ring_record" / "new" / "estimates.json"
)
LEDGER = REPO_ROOT / "crp" / "docs" / "benchmarks" / "ledger.jsonl"

FFI_N = 200_000
E2E_EVENTS = 100_000
E2E_DRAIN_BATCH = 4096


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def _rustc_version(toolchain: str) -> str:
    out = subprocess.run(
        ["rustc", f"+{toolchain}", "--version"], capture_output=True, text=True
    )
    return out.stdout.strip() or out.stderr.strip()


def provenance() -> dict[str, Any]:
    return {
        "cpu": platform.processor(),
        "machine": platform.machine(),
        "os": platform.platform(),
        "python": platform.python_version(),
        "rustc": _rustc_version("stable-x86_64-pc-windows-gnu"),
        "rust_toolchain": "stable-x86_64-pc-windows-gnu",
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "build_profile": "release",
    }


def native_rust_ns() -> dict[str, float] | None:
    """Criterion point estimates for Ring::record, in nanoseconds."""
    if not CRITERION_ESTIMATES.exists():
        return None
    data = json.loads(CRITERION_ESTIMATES.read_text())
    return {
        "mean_ns": data["mean"]["point_estimate"],
        "median_ns": data["median"]["point_estimate"],
        "std_dev_ns": data["std_dev"]["point_estimate"],
    }


def _stats_us(samples: list[float]) -> dict[str, float]:
    ordered = sorted(samples)
    n = len(ordered)
    return {
        "mean_us": statistics.mean(ordered),
        "p50_us": ordered[n // 2],
        "p99_us": ordered[int(n * 0.99)],
        "std_dev_us": statistics.stdev(ordered),
        "n": float(n),
    }


def ffi_record_us() -> dict[str, float]:
    """Per-call Telemetry.record() latency through PyO3, in microseconds."""
    t = crp_telemetry.Telemetry(capacity=1 << 18)
    samples: list[float] = []
    for i in range(FFI_N):
        start = time.perf_counter_ns()
        t.record(kind=1, tensor_id=i, value=1.0)
        samples.append((time.perf_counter_ns() - start) / 1000.0)
        if len(t) > (1 << 17):
            t.drain(1 << 17)
    return _stats_us(samples)


def end_to_end_us_per_event() -> dict[str, float]:
    """Record E2E_EVENTS events and drain all of them in batches; report
    total wall time divided by event count (the runtime's real telemetry
    cost per event, producer + consumer)."""
    t = crp_telemetry.Telemetry(capacity=1 << 18)
    start = time.perf_counter_ns()
    drained = 0
    for i in range(E2E_EVENTS):
        t.record(kind=2, tensor_id=i, value=float(i))
        if i % E2E_DRAIN_BATCH == E2E_DRAIN_BATCH - 1:
            drained += len(t.drain(E2E_DRAIN_BATCH))
    while True:
        batch = t.drain(E2E_DRAIN_BATCH)
        if not batch:
            break
        drained += len(batch)
    total_us = (time.perf_counter_ns() - start) / 1000.0
    return {
        "us_per_event": total_us / E2E_EVENTS,
        "total_ms": total_us / 1000.0,
        "events": float(E2E_EVENTS),
        "drained": float(drained),
        "dropped": float(t.dropped()),
    }


def main() -> None:
    entry: dict[str, Any] = {
        "schema": 1,
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "subject": "tier0-telemetry",
        "provenance": provenance(),
        "layers": {
            "native_rust": native_rust_ns(),
            "ffi": ffi_record_us(),
            "end_to_end": end_to_end_us_per_event(),
        },
        "spec_2a": {"target_us": 5.0, "hard_limit_us": 10.0},
    }
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry, indent=2))
    print(f"\nAppended to {LEDGER}")


if __name__ == "__main__":
    main()

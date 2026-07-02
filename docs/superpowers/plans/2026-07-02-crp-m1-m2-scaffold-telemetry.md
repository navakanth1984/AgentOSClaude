# CRP Phase 0 — Plan 1/3: Scaffolding + Telemetry Foundation (Milestones 1–2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the `crp/` Python+Rust workspace with CI, and deliver a lock-free Tier-0 telemetry ring buffer (Rust + PyO3) whose per-event overhead is *measured* against the <5 µs target / 10 µs hard limit.

**Architecture:** `crp/` is a two-workspace project: a Python 3.12 package (`crp_runtime`) for orchestration and a Rust crate (`crp-telemetry`) exposing a `crp_telemetry` Python module via PyO3/maturin. The ring buffer wraps `crossbeam::queue::ArrayQueue` (battle-tested lock-free MPMC) rather than hand-rolled atomics — recorded as ADR-005. Full events are dropped (and counted) when the buffer is full; recording never blocks.

**Tech Stack:** Python 3.12, pytest, Rust stable, crossbeam, PyO3 0.22, maturin, criterion (Rust benchmarks), GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-07-02-crp-phase0-design.md` (Frozen).

## Global Constraints

- Tier-0 overhead: target < 5 µs, hard fail > 10 µs (test-enforced).
- Dropped telemetry acceptable; blocking/failing the caller is not.
- Python code must pass the repo's pyrefly pre-commit hook (Python312 interpreter). Never `--no-verify`.
- All work on branch `feat/crp-m1-scaffold-telemetry`, PR into `master`.
- New ideas → future RFCs; the frozen spec changes only for defect corrections.
- Windows 11 host; commands below are Git Bash / PowerShell-compatible.

## Follow-on plans (not in this document)

- Plan 2/3: Milestones 3–4 (replayable benchmark harness + workloads; RepresentationPlugin + Dense/Int8 + scoring policy) — written after Tier-0 budget evidence exists.
- Plan 3/3: Milestones 5–6 (Experience DB + replay tools; closed policy loop with before/after evidence).

---

### Task 1: Repository scaffold, docs skeleton, ADRs, risk register

**Files:**
- Create: `crp/README.md`, `crp/docs/SPEC.md` (pointer stub), `crp/docs/RISKS.md`,
  `crp/docs/adr/ADR-001-python-core-rust-hot-path.md`,
  `crp/docs/adr/ADR-002-sqlite-experience-db.md`,
  `crp/docs/adr/ADR-003-stable-rank-sketching.md`,
  `crp/docs/adr/ADR-004-deterministic-scoring-first.md`,
  `crp/docs/adr/ADR-005-crossbeam-arrayqueue.md`,
  `crp/docs/rfcs/INDEX.md`
- Create (empty package dirs with `.gitkeep`): `crp/plugins/.gitkeep`, `crp/benchmarks/.gitkeep`, `crp/sdk/.gitkeep`, `crp/tools/.gitkeep`

**Interfaces:**
- Produces: directory layout per spec §4 that Tasks 2–6 create files inside.

- [ ] **Step 1: Create branch**

```bash
git checkout master && git pull && git checkout -b feat/crp-m1-scaffold-telemetry
```

- [ ] **Step 2: Write README and docs**

`crp/README.md`:

```markdown
# Cognitive Runtime Platform (CRP)

Measurement-first adaptive runtime. Phase 0 scope, non-goals, success
metrics, and architecture are frozen in
[the Phase 0 design spec](../docs/superpowers/specs/2026-07-02-crp-phase0-design.md).

## Layout
- `runtime/`   — Python core (`crp_runtime` package)
- `telemetry/` — Rust `crp-telemetry` crate (Tier-0 ring buffer, PyO3)
- `plugins/`   — representation plugins (Dense, Int8; Phase 0)
- `benchmarks/`— replayable workload harness (Plan 2)
- `docs/`      — SPEC pointer, ADRs, RFCs, risk register

## Dev setup
    pip install -e ./crp[dev]
    maturin develop -m crp/telemetry/Cargo.toml --release
    pytest crp/runtime/tests -v
```

`crp/docs/SPEC.md`:

```markdown
# CRP Phase 0 Specification

The frozen Phase 0 spec lives at
`docs/superpowers/specs/2026-07-02-crp-phase0-design.md` (repo root).
This file will host the expanded SPEC as RFCs are accepted.

## Non-goals (Phase 0)
- Not an operating system kernel
- Not a scheduler replacement
- Not a tensor-network research platform
- Not a distributed runtime
- Not a production security architecture
- Not mobile-first
- Not performance-optimized beyond measured telemetry paths
```

`crp/docs/RISKS.md`:

```markdown
# CRP Risk Register

| ID | Risk | Mitigation | Status |
|---|---|---|---|
| R-001 | Python orchestration becomes bottleneck | Move hot path to Rust | Open |
| R-002 | Telemetry overhead exceeds budget | Reduce Tier-0 payload | Open |
| R-003 | Representation API proves insufficient | Version interfaces | Open |
| R-004 | Replay system diverges | Deterministic serialization | Open |
```

`crp/docs/rfcs/INDEX.md`:

```markdown
# RFC Index

| RFC | Title | Status |
|---|---|---|
| 0001 | Governance & RFC process | Stub |
| 0002 | Objective: reward + hard constraints | Stub |
| 0003 | Telemetry architecture & budgets | Stub |
| 0004 | Representation plugin interface | Stub |
```

Each ADR uses this template (fill Decision/Alternatives/Trade-offs per the
titles; content given here for ADR-001 and ADR-005, write ADR-002/003/004
in the same shape from spec §6):

`crp/docs/adr/ADR-001-python-core-rust-hot-path.md`:

```markdown
# ADR-001: Python core + Rust hot path

**Status:** Accepted 2026-07-02

**Decision:** Orchestration, policy, and plugins in Python 3.12; only the
Tier-0 telemetry ring buffer in Rust (PyO3/maturin).

**Alternatives:** pure Python (cannot meet the 10 µs hard limit under GC
pauses); pure Rust (too slow to iterate for evidence-gathering).

**Trade-offs:** two toolchains; PyO3 call overhead is part of the measured
budget, not exempt from it.
```

`crp/docs/adr/ADR-005-crossbeam-arrayqueue.md`:

```markdown
# ADR-005: crossbeam ArrayQueue instead of hand-rolled lock-free buffer

**Status:** Accepted 2026-07-02

**Decision:** The Tier-0 ring buffer wraps `crossbeam::queue::ArrayQueue`.

**Alternatives:** hand-written SPSC atomics ring (faster in theory, easy to
get subtly wrong); `std::sync::mpsc` (allocating, unbounded, can block).

**Trade-offs:** MPMC generality we don't need yet; accepted because
correctness beats micro-optimization until measurements say otherwise
(spec principle: measurement before optimization).
```

- [ ] **Step 3: Commit**

```bash
git add crp/ && git commit -m "feat(crp): scaffold repository layout, ADRs 001-005, risk register, RFC index"
```

---

### Task 2: Python workspace (`crp_runtime` package + pytest)

**Files:**
- Create: `crp/pyproject.toml`, `crp/runtime/crp_runtime/__init__.py`, `crp/runtime/tests/test_package.py`

**Interfaces:**
- Produces: installable package `crp_runtime` with `crp_runtime.__version__: str`; test root `crp/runtime/tests` used by all later Python tasks.

- [ ] **Step 1: Write failing test**

`crp/runtime/tests/test_package.py`:

```python
import crp_runtime


def test_version_present() -> None:
    assert crp_runtime.__version__ == "0.1.0"
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest crp/runtime/tests/test_package.py -v`
Expected: FAIL / error `ModuleNotFoundError: No module named 'crp_runtime'`

- [ ] **Step 3: Implement package**

`crp/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "crp-runtime"
version = "0.1.0"
description = "Cognitive Runtime Platform - Python core"
requires-python = ">=3.12"
dependencies = ["numpy>=1.26"]

[project.optional-dependencies]
dev = ["pytest>=8"]

[tool.setuptools.package-dir]
crp_runtime = "runtime/crp_runtime"

[tool.setuptools.packages.find]
where = ["runtime"]
```

`crp/runtime/crp_runtime/__init__.py`:

```python
"""CRP Python core: orchestration, policy, plugins."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Install and run test**

```bash
pip install -e ./crp[dev]
pytest crp/runtime/tests/test_package.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crp/pyproject.toml crp/runtime && git commit -m "feat(crp): crp_runtime Python package with pytest workspace"
```

---

### Task 3: Rust crate — ring buffer core (pure Rust, TDD)

**Files:**
- Create: `crp/telemetry/Cargo.toml`, `crp/telemetry/src/lib.rs`, `crp/telemetry/src/ring.rs`

**Interfaces:**
- Produces (Rust): `TelemetryEvent { timestamp_ns: u64, kind: u32, tensor_id: u64, value: f64 }`; `Ring::new(capacity: usize)`, `Ring::record(&self, ev: TelemetryEvent) -> bool` (false = dropped, never blocks), `Ring::drain(&self, max: usize) -> Vec<TelemetryEvent>`, `Ring::dropped(&self) -> u64`, `Ring::len(&self) -> usize`. Task 5 wraps these in PyO3.

- [ ] **Step 1: Crate manifest**

`crp/telemetry/Cargo.toml`:

```toml
[package]
name = "crp-telemetry"
version = "0.1.0"
edition = "2021"

[lib]
name = "crp_telemetry"
crate-type = ["cdylib", "rlib"]

[dependencies]
crossbeam = "0.8"
pyo3 = { version = "0.22", features = ["extension-module"], optional = true }

[features]
default = []
python = ["dep:pyo3"]

[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "record_overhead"
harness = false
```

- [ ] **Step 2: Write failing tests in `crp/telemetry/src/ring.rs`**

```rust
use crossbeam::queue::ArrayQueue;
use std::sync::atomic::{AtomicU64, Ordering};

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct TelemetryEvent {
    pub timestamp_ns: u64,
    pub kind: u32,
    pub tensor_id: u64,
    pub value: f64,
}

pub struct Ring {
    queue: ArrayQueue<TelemetryEvent>,
    dropped: AtomicU64,
}

#[cfg(test)]
mod tests {
    use super::*;

    fn ev(k: u32) -> TelemetryEvent {
        TelemetryEvent { timestamp_ns: 1, kind: k, tensor_id: 7, value: 0.5 }
    }

    #[test]
    fn record_then_drain_roundtrips() {
        let r = Ring::new(4);
        assert!(r.record(ev(1)));
        assert!(r.record(ev(2)));
        let out = r.drain(10);
        assert_eq!(out.len(), 2);
        assert_eq!(out[0].kind, 1);
        assert_eq!(out[1].kind, 2);
    }

    #[test]
    fn full_buffer_drops_and_counts_without_blocking() {
        let r = Ring::new(2);
        assert!(r.record(ev(1)));
        assert!(r.record(ev(2)));
        assert!(!r.record(ev(3))); // dropped, not blocked
        assert_eq!(r.dropped(), 1);
        assert_eq!(r.len(), 2);
    }

    #[test]
    fn drain_respects_max() {
        let r = Ring::new(8);
        for k in 0..5 { r.record(ev(k)); }
        assert_eq!(r.drain(3).len(), 3);
        assert_eq!(r.len(), 2);
    }
}
```

And `crp/telemetry/src/lib.rs`:

```rust
pub mod ring;
pub use ring::{Ring, TelemetryEvent};
```

- [ ] **Step 3: Run tests to verify failure**

Run: `cargo test --manifest-path crp/telemetry/Cargo.toml`
Expected: compile error — `Ring::new`, `record`, `drain`, `dropped`, `len` not defined.

- [ ] **Step 4: Implement `Ring` (append to `ring.rs`, above the tests module)**

```rust
impl Ring {
    pub fn new(capacity: usize) -> Self {
        Self { queue: ArrayQueue::new(capacity), dropped: AtomicU64::new(0) }
    }

    /// Never blocks. Returns false and counts the drop when full.
    pub fn record(&self, ev: TelemetryEvent) -> bool {
        match self.queue.push(ev) {
            Ok(()) => true,
            Err(_) => {
                self.dropped.fetch_add(1, Ordering::Relaxed);
                false
            }
        }
    }

    pub fn drain(&self, max: usize) -> Vec<TelemetryEvent> {
        let mut out = Vec::with_capacity(max.min(self.queue.len()));
        while out.len() < max {
            match self.queue.pop() {
                Some(ev) => out.push(ev),
                None => break,
            }
        }
        out
    }

    pub fn dropped(&self) -> u64 {
        self.dropped.load(Ordering::Relaxed)
    }

    pub fn len(&self) -> usize {
        self.queue.len()
    }

    pub fn is_empty(&self) -> bool {
        self.queue.is_empty()
    }
}
```

- [ ] **Step 5: Run tests to verify pass**

Run: `cargo test --manifest-path crp/telemetry/Cargo.toml`
Expected: `test result: ok. 3 passed`

- [ ] **Step 6: Commit**

```bash
git add crp/telemetry && git commit -m "feat(crp): lock-free Tier-0 telemetry ring buffer (crossbeam ArrayQueue)"
```

---

### Task 4: Criterion benchmark — measured record() overhead

**Files:**
- Create: `crp/telemetry/benches/record_overhead.rs`

**Interfaces:**
- Consumes: `Ring`, `TelemetryEvent` from Task 3.
- Produces: `target/criterion` report with mean ns/record — the first real number behind the <5 µs claim. Task 6 cites it in the benchmark report.

- [ ] **Step 1: Write benchmark**

`crp/telemetry/benches/record_overhead.rs`:

```rust
use criterion::{criterion_group, criterion_main, Criterion};
use crp_telemetry::{Ring, TelemetryEvent};

fn bench_record(c: &mut Criterion) {
    let ring = Ring::new(1 << 16);
    let ev = TelemetryEvent { timestamp_ns: 42, kind: 1, tensor_id: 7, value: 0.5 };
    c.bench_function("ring_record", |b| {
        b.iter(|| {
            if !ring.record(std::hint::black_box(ev)) {
                ring.drain(1 << 15); // keep the buffer from saturating mid-bench
            }
        })
    });
}

criterion_group!(benches, bench_record);
criterion_main!(benches);
```

- [ ] **Step 2: Run benchmark**

Run: `cargo bench --manifest-path crp/telemetry/Cargo.toml`
Expected: `ring_record  time: [...]` — record the mean; anticipated tens of ns (well under 5 µs). If mean > 5 µs, STOP and update `crp/docs/RISKS.md` R-002 before proceeding.

- [ ] **Step 3: Commit**

```bash
git add crp/telemetry/benches && git commit -m "bench(crp): criterion benchmark for Tier-0 record() overhead"
```

---

### Task 5: PyO3 bindings + maturin + Python tests

**Files:**
- Create: `crp/telemetry/src/python.rs`
- Modify: `crp/telemetry/src/lib.rs`
- Test: `crp/runtime/tests/test_telemetry.py`

**Interfaces:**
- Consumes: `Ring`, `TelemetryEvent` (Task 3).
- Produces (Python module `crp_telemetry`): `Telemetry(capacity: int)` with `.record(kind: int, tensor_id: int, value: float) -> bool` (timestamps internally, monotonic ns), `.drain(max: int) -> list[tuple[int, int, int, float]]` (timestamp_ns, kind, tensor_id, value), `.dropped() -> int`, `.__len__() -> int`. Plan 2's harness records through exactly this API.

- [ ] **Step 1: Write failing Python test**

`crp/runtime/tests/test_telemetry.py`:

```python
import pytest

crp_telemetry = pytest.importorskip("crp_telemetry")


def test_record_drain_roundtrip() -> None:
    t = crp_telemetry.Telemetry(capacity=8)
    assert t.record(kind=1, tensor_id=7, value=0.5) is True
    assert len(t) == 1
    events = t.drain(10)
    assert len(events) == 1
    ts, kind, tensor_id, value = events[0]
    assert ts > 0 and kind == 1 and tensor_id == 7 and value == 0.5


def test_full_buffer_drops_without_raising() -> None:
    t = crp_telemetry.Telemetry(capacity=2)
    assert t.record(kind=1, tensor_id=1, value=0.0)
    assert t.record(kind=2, tensor_id=2, value=0.0)
    assert t.record(kind=3, tensor_id=3, value=0.0) is False
    assert t.dropped() == 1
```

- [ ] **Step 2: Run to verify skip/failure**

Run: `pytest crp/runtime/tests/test_telemetry.py -v`
Expected: SKIPPED (`crp_telemetry` not importable) — treated as the failing state.

- [ ] **Step 3: Implement bindings**

`crp/telemetry/src/python.rs`:

```rust
use crate::ring::{Ring, TelemetryEvent};
use pyo3::prelude::*;
use std::time::Instant;

#[pyclass]
pub struct Telemetry {
    ring: Ring,
    epoch: Instant,
}

#[pymethods]
impl Telemetry {
    #[new]
    #[pyo3(signature = (capacity))]
    fn new(capacity: usize) -> Self {
        Self { ring: Ring::new(capacity), epoch: Instant::now() }
    }

    #[pyo3(signature = (kind, tensor_id, value))]
    fn record(&self, kind: u32, tensor_id: u64, value: f64) -> bool {
        let ts = self.epoch.elapsed().as_nanos() as u64;
        self.ring.record(TelemetryEvent { timestamp_ns: ts, kind, tensor_id, value })
    }

    #[pyo3(signature = (max))]
    fn drain(&self, max: usize) -> Vec<(u64, u32, u64, f64)> {
        self.ring
            .drain(max)
            .into_iter()
            .map(|e| (e.timestamp_ns, e.kind, e.tensor_id, e.value))
            .collect()
    }

    fn dropped(&self) -> u64 {
        self.ring.dropped()
    }

    fn __len__(&self) -> usize {
        self.ring.len()
    }
}

#[pymodule]
fn crp_telemetry(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Telemetry>()?;
    Ok(())
}
```

Update `crp/telemetry/src/lib.rs`:

```rust
pub mod ring;
pub use ring::{Ring, TelemetryEvent};

#[cfg(feature = "python")]
pub mod python;
```

- [ ] **Step 4: Build and run tests**

```bash
pip install maturin
maturin develop -m crp/telemetry/Cargo.toml --release --features python
cargo test --manifest-path crp/telemetry/Cargo.toml   # Rust tests still pass
pytest crp/runtime/tests/test_telemetry.py -v
```
Expected: 2 PASSED (no longer skipped).

- [ ] **Step 5: Commit**

```bash
git add crp/telemetry crp/runtime/tests/test_telemetry.py
git commit -m "feat(crp): PyO3 Telemetry bindings via maturin"
```

---

### Task 6: Python-side budget test, CI, benchmark report

**Files:**
- Create: `crp/runtime/tests/test_budget.py`, `.github/workflows/crp-ci.yml`, `crp/docs/BENCHMARK-M2.md`

**Interfaces:**
- Consumes: `crp_telemetry.Telemetry` (Task 5), criterion numbers (Task 4).
- Produces: enforced spec §2a gate (10 µs hard fail) as a pytest; CI running Rust+Python suites on `crp/**` changes; Milestone-2 benchmark report.

- [ ] **Step 1: Write budget test (this is the hard gate — it may legitimately fail)**

`crp/runtime/tests/test_budget.py`:

```python
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
```

- [ ] **Step 2: Run**

Run: `pytest crp/runtime/tests/test_budget.py -v -s`
Expected: `test_tier0_hard_limit PASSED` with the printed number; soft test PASSED or XFAIL. Record the mean.

- [ ] **Step 3: CI workflow**

`.github/workflows/crp-ci.yml`:

```yaml
name: crp-ci
on:
  pull_request:
    paths: ["crp/**", ".github/workflows/crp-ci.yml"]
  push:
    branches: [master]
    paths: ["crp/**"]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - uses: dtolnay/rust-toolchain@stable
      - name: Rust tests
        run: cargo test --manifest-path crp/telemetry/Cargo.toml
      - name: Build extension + Python tests
        run: |
          pip install maturin
          pip install -e ./crp[dev]
          maturin develop -m crp/telemetry/Cargo.toml --release --features python
          pytest crp/runtime/tests -v
```

Note: the budget test runs on shared CI runners where timing is noisy; the 10 µs hard limit still holds there by design — if CI timing proves flaky in practice, record it in RISKS.md and gate the *soft* target locally only (defect-correction level change).

- [ ] **Step 4: Write `crp/docs/BENCHMARK-M2.md`**

```markdown
# Milestone 2 Benchmark Report — Tier-0 Telemetry

Date: <fill on run day> | Host: Windows 11, <CPU model> | Build: --release

| Measurement | Value | Spec 2a verdict |
|---|---|---|
| Rust record() (criterion mean) | <n> ns | target <5 us: <pass/fail> |
| Python record() (pytest mean, N=50k) | <n> us | hard limit 10 us: <pass/fail> |
| Drop behavior under full buffer | non-blocking, counted | required: pass |

Evidence: target/criterion report + `pytest crp/runtime/tests/test_budget.py -s` output.
Conclusion: <one paragraph — is the <5 us Tier-0 budget real on this host?>
```

Fill in the actual numbers from Task 4 Step 2 and Task 6 Step 2 — no placeholders may remain at commit time.

- [ ] **Step 5: Run full suite, commit, push, PR**

```bash
cargo test --manifest-path crp/telemetry/Cargo.toml
pytest crp/runtime/tests -v
git add crp/ .github/workflows/crp-ci.yml
git commit -m "feat(crp): Tier-0 budget gate, CI workflow, Milestone-2 benchmark report"
git push -u origin feat/crp-m1-scaffold-telemetry
gh pr create --title "feat(crp): Phase 0 M1-M2 — scaffold + measured Tier-0 telemetry" --body "Implements Plan 1/3 of the frozen Phase 0 spec. Delivers workspace, ADRs 001-005, lock-free ring buffer, PyO3 bindings, measured overhead vs the 5/10 us budgets, CI.

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

---

## Self-Review (done)

- **Spec coverage:** M1 (scaffold/workspaces/CI) → Tasks 1, 2, 6; M2 (ring buffer, PyO3, budget verification) → Tasks 3–6; ADR + benchmark-report milestone exit criteria → Tasks 1, 6. Spec items for M3–M6 deliberately deferred to Plans 2–3.
- **Placeholders:** BENCHMARK-M2.md contains `<fill>` slots by design — the plan requires them filled with measured values before commit (Task 6 Step 4 states this).
- **Type consistency:** `TelemetryEvent` fields, `Ring` methods, and the Python `Telemetry` API match across Tasks 3→4→5→6.

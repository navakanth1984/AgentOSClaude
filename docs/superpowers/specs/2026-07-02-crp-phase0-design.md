# CRP Phase 0 — Design Document

- **Date:** 2026-07-02
- **Status:** Approved (user-reviewed brainstorm, refinements incorporated)
- **Project:** Cognitive Runtime Platform (CRP) — Project Genesis
- **Location:** `crp/` inside `navakanth001` (staging convention; graduates to its own repo when mature)

---

## 1. Purpose

Phase 0 delivers two artifacts in parallel:

1. **A Phase-0 architecture specification** — a concise, interface-first source-of-truth skeleton (~25–40 pages) that grows one RFC at a time. Not a speculative 300-page monolith.
2. **A measurement-first runtime implementation** — a thin vertical slice (Python core + Rust hot path) that proves the Stage 0→3 optimization pipeline on a representative AI runtime benchmark suite and populates the first Experience Database entries.

Every Phase-0 decision must be validatable, replaceable, or extensible through evidence rather than assumption.

## 2. North Star

`DONE` for Phase 0 means all of the following, demonstrated by a real run:

- ✓ The runtime measured itself (Tier-0 telemetry captured on the inference path).
- ✓ Telemetry overhead itself was measured (the <5 µs claim is a number, not an assumption).
- ✓ A representation decision was made and recorded in the Experience DB.
- ✓ That decision is replayable (same workload + same policy ⇒ same decision).
- ✓ The better representation (Dense vs Int8) was selected per workload, per the recorded evidence.
- ✓ The entire run is reproducible end-to-end from a saved run record.

Max 3 iterations per failing milestone; persistent failure means the context/design is wrong, not the effort.

## 3. Scope

### In scope (Phase 0)

- Phase-0 spec (`crp/docs/SPEC.md`), interface contracts, RFC index + 4 initial RFCs, threat-model/safety-constraint predicates.
- Runtime skeleton: telemetry (Tier 0 Rust ring buffer via PyO3, Tier 1 async sidecar, Tier 2 idle-only stubs), Representation Plugin API with exactly two plugins (Dense, Int8 quantized), deterministic scoring policy, relational SQLite Experience DB, replayable benchmark harness.
- Workload suite: local LLM inference (Ollama / small HF model) + embedding search + controlled synthetic tensor set.
- ADRs in `crp/docs/adr/` for every significant choice.

### Explicitly out of scope (RFC stubs only, no implementation)

Mobile/Android, desktop launcher, contextual bandit / learned policies, drift detection, plugin sandboxing & cryptographic verification, tensor-network representations (TT/Tucker/CP), photonic/quantum/neuromorphic anything, distributed cognition, SDK beyond internal interfaces.

## 4. Repository Layout

```
crp/
  docs/
    SPEC.md              # Phase-0 architecture spec
    interfaces/          # typed contracts (Python Protocols + Rust traits)
    rfcs/                # RFC index + documents
    adr/                 # Architecture Decision Records
  runtime/               # Python core (evolves toward production; not throwaway)
  telemetry/             # Rust crate `crp-telemetry` + PyO3 binding
  plugins/               # representation plugins (dense/, int8/)
  benchmarks/            # workload suite + replay harness
  sdk/                   # placeholder (Phase 5)
  tools/                 # dev utilities
```

Naming note: `runtime/` (not `proto/`) — this code is intended to evolve into production, not be discarded.

## 5. Architecture

### 5.1 Objective: reward + hard constraints (not one weighted equation)

Replace `J = αM + βT + γE + δA + εC + ζR` as the decision rule with a constrained optimization:

```
maximize   Reward(memory_saved, latency_gain, energy_saved, cost_saved)
subject to Latency   ≤ latency_budget
           Memory    ≤ memory_budget
           Accuracy loss ≤ accuracy_threshold
           Reliability ≥ reliability_floor
```

Weighted reward terms rank *feasible* candidates; hard constraints reject infeasible ones outright. This prevents weight-dominated objectives from ever choosing an unsafe representation. Deployment profiles (cloud/mobile/scientific/embedded) are presets of both the reward weights and the constraint bounds.

Safety constraints are machine-checkable predicates (OOM prediction, precision-loss threshold, latency violation, hardware incompatibility), not prose.

### 5.2 Representation Plugin API (defined immediately, two implementations)

Representations are plugins from day one; the abstraction is generic, not "compression":

```python
class RepresentationPlugin(Protocol):
    def analyze(self, tensor) -> TensorStats          # Stage 0 stats
    def estimate(self, stats, hw) -> RepresentationEstimate  # Stage 2 inputs
    def convert(self, tensor) -> ConvertedTensor      # Stage 3
    def execute(self, converted, op) -> ExecResult    # run workload op
    def restore(self, converted) -> Tensor            # invert conversion

@dataclass
class RepresentationResult:
    name: str
    memory_bytes: int
    latency_ms: float
    quality_score: float
    conversion_cost: float
```

Phase-0 plugins: `Dense`, `QuantizedInt8`. The registry reserves the namespace for future plugins (Sparse, TensorTrain, Tucker, …) — they implement the same interface with no API rewrite.

### 5.3 Multi-stage pipeline

- **Stage 0 — cheap stats:** shape, sparsity, variance, memory size, cache footprint.
- **Stage 1 — linear-algebra proxies:** stable rank via randomized sketch (not full SVD — ADR).
- **Stage 2 — deterministic scoring policy (no ML, no lookup table):**

```
score_dense = α·memory + β·latency
score_int8  = α·memory_saved + β·expected_latency − γ·expected_accuracy_loss
```

Fully explainable; coefficients live in the deployment profile. Learned policies (bandit) replace this only after telemetry justifies them.

- **Stage 3 — execute** the winning feasible representation; record everything.

### 5.4 Telemetry: three tiers with explicit, testable budgets

| Tier | Role | Budget |
|---|---|---|
| Tier 0 | Critical path capture → lock-free ring buffer (Rust, PyO3) | target < 5 µs, **hard limit 10 µs** (test-enforced) |
| Tier 1 | Async sidecar: sketches, stable rank, aggregation; drops events under pressure | soft budget < 10 ms per batch |
| Tier 2 | Maintenance economy: full SVD, decomposition benchmarking, DB cleanup | unlimited, **idle only** |

Inference owns compute; dropped telemetry is acceptable, dropped inference is not.

### 5.5 Experience Database — relational SQLite

Normalized schema, not one giant table:

- `runs` — run id, timestamp, git sha, config hash, replay pointer
- `workloads` — workload class, model, input spec
- `representations` — plugin, version, parameters
- `telemetry` — per-event Tier-0/1 records (FK → runs)
- `policy_decisions` — inputs, scores, constraints checked, chosen representation, confidence
- `hardware` — CPU/GPU/cache/memory-bandwidth profile
- `benchmarks` — aggregated results (FK → runs, workloads, representations)

### 5.6 Benchmark harness with replay

Every benchmark run saves its workload spec + policy config + seed so it can be replayed exactly: `run N → save workload → save policy → replay → compare against runtime v2`. Replayability is a North Star criterion, not a nice-to-have.

## 6. Spec & Governance Artifacts

- **`SPEC.md`:** mission, philosophy, layered architecture, subsystem decomposition, reward/constraint formulation, deployment profiles.
- **RFCs (Phase 0):** RFC-0001 governance & RFC process, RFC-0002 objective (reward + constraints), RFC-0003 telemetry architecture & budgets, RFC-0004 representation plugin interface. All other subsystems get numbered stubs with owners and open questions.
- **ADRs (`docs/adr/`):** ADR-001 Python core + Rust hot path (why, alternatives, trade-offs); ADR-002 SQLite (vs DuckDB); ADR-003 stable rank via sketching (vs full SVD); ADR-004 deterministic scoring before learned policy; new ADRs for every significant choice thereafter.

## 7. Technology Choices

- Python 3.12 core (pyrefly-typed, matching repo hook discipline); NumPy/PyTorch for tensor ops.
- Rust `crp-telemetry` crate, built with `cargo` + `maturin` (PyO3) — Tier-0 ring buffer only.
- SQLite for the Experience DB.
- Workloads: Ollama or a small HF transformer, an embedding-search task, synthetic tensors with controlled rank/sparsity.

## 8. Testing Strategy

- Unit tests per module; plugin conformance suite any `RepresentationPlugin` must pass.
- Budget tests: Tier-0 hard limit (10 µs) enforced as a failing test, measured on real hardware.
- Replay tests: byte-identical decision path on replayed runs.
- Constraint tests: adversarial cases where reward would pick an unsafe representation — the constraint layer must reject them.
- Integration: full Stage 0→3 run on each workload class writing to the Experience DB.

## 9. Error Handling & Safety

- Any predicate failure (OOM risk, accuracy loss beyond threshold, latency violation) ⇒ fall back to Dense (identity representation) and record the rejection.
- Telemetry overload ⇒ drop events, count drops, never block inference.
- DB write failure ⇒ inference continues; run flagged non-reproducible.

## 10. Process

- ADLC per repo standard: feature branch → implement + verify with a real run → commit (pyrefly hook) → PR into `master` → merge.
- Phase 0 decomposes into roughly: (1) scaffold + spec skeleton + ADRs, (2) plugin API + Dense/Int8, (3) Rust ring buffer + budget benchmark, (4) Experience DB + replay harness, (5) scoring policy + constraints, (6) workload suite + North-Star verification run. Each is its own branch/PR; detailed sequencing goes in the implementation plan (writing-plans).

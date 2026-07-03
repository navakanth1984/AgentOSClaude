# Project TITAN — North-Star Vision

- **Date:** 2026-07-02 (recovered and corrected 2026-07-03 — see History)
- **Status:** Vision document (aspirational; **not** a spec, **not** a commitment)
- **Relationship to CRP:** CRP is the trusted execution substrate **inside**
  TITAN, not a project TITAN grows into. TITAN owns why the platform exists
  and where it goes over years; it prescribes no implementation. CRP owns
  Gates 1–4 and everything under `crp/docs/` (Constitution, Determinism, ABI,
  IR spec, Roadmap) that governs *how* change is allowed to happen. This
  document changes only through a deliberate architectural decision — never
  as a side effect of a CRP implementation session.

## Layer model

```
Vision         — TITAN (this document): why the platform exists, multi-year
                 destination, no implementation detail.
Governance     — Constitution, Determinism, ABI, IR Spec, Roadmap: how
                 change is allowed to happen. Frozen per gate.
Implementation — CRP Gates 1-4: the trusted execution substrate.
Research       — R2 (statistical) -> R3 (LLM-assisted) -> R4 (research
                 economy) -> R5 (meta-research), staged after R1 exit.
Future         — TITAN capabilities below, entered only after RFC + evidence.
```

If a session is dedicated to TITAN, it owns vision/architecture/RFC
acceptance/gate freeze decisions and never touches production code. A CRP
implementation session owns code/tests/compiler/CI/PRs and never changes
architecture without an approved RFC. This document is the artifact that
lets both sessions stay synchronized without one absorbing the other.

---

## 1. Mission

Build a production-grade, quantum-inspired adaptive runtime capable of
automatically discovering the optimal mathematical representation for AI
workloads — measured, not assumed.

## 2. Governance rule (binding)

Every capability listed below enters the implementation **only** through the
existing RFC → ADR process in `crp/docs/`, and only after empirical evidence
from the measurement runtime justifies it. A TITAN entry is a hypothesis, not
a backlog item. If telemetry and benchmarks never justify a capability, it
never ships — that is a success of the process, not a failure of the vision.
This document does not prescribe *how* CRP implements anything; the
Constitution, Determinism spec, ABI, and IR spec do that, and they can evolve
independently of this document as long as they keep serving the mission.

## 3. The pipeline (long-term shape)

The seven-stage pipeline is already the skeleton of CRP Phase 0; TITAN only
extends what each stage can see and do.

| Stage | Name | Phase 0 (frozen) | TITAN end-state |
|---|---|---|---|
| 0 | Cheap statistics | shape, sparsity, variance | + cache locality |
| 1 | Proxy analysis | stable rank (sketched) | + effective rank, covariance decay, entropy, arithmetic intensity, bandwidth |
| 2 | Policy | deterministic scoring (reward + hard constraints) | + learned policy (contextual bandit), cloud cost, energy models |
| 3 | Representation compilation | Dense ↔ Int8 conversion | automatic conversion across all supported representations |
| 4 | Execution | local LLM inference, embedding search | full workload matrix (§5) |
| 5 | Telemetry | Tier-0 ring buffer (<5 µs), Tier-1 sidecar, Tier-2 stubs | + cache misses, FLOPs, bandwidth, GPU utilization, compression ratio, full replay |
| 6 | Learning | Experience DB (SQLite), replayable decisions | continuous policy improvement from accumulated evidence |

## 4. Representation roadmap

Each tier requires an accepted RFC before any implementation. Ordering is a
default hypothesis; evidence from earlier phases may reorder it.

| Phase | Representations | Entry evidence required |
|---|---|---|
| 0 (frozen) | Dense, Int8 | — (Phase 0 shipped: telemetry, harness, Experience DB, replay — PASS) |
| 1 | Sparse (CSR, COO), FP8 | Phase 0 benchmarks show sparsity-sensitive workloads where Dense/Int8 lose |
| 2 | Low Rank, Randomized SVD | Stage-1 stable-rank telemetry shows low effective rank in real workloads |
| 3 | Tensor Train, Matrix Product State, CP, Tucker | Phase 2 low-rank wins + workloads with higher-order structure |
| 4 | Hierarchical Matrix, Graph, Wavelet, Symbolic | Scientific/CFD/graph workloads onboarded and measured |
| 5+ | Plugin SDK opens to external/future plugins | Plugin API stable across ≥2 phases without breaking change |

## 5. Workload roadmap

Phase 0: local LLM inference, embedding search, synthetic tensors.
Later phases add, in evidence-driven order: vision, speech, graphs,
recommendation, scientific computing / CFD, multimodal. A workload is added
only when the replayable benchmark harness can reproduce it within the ±2%
reproducibility gate.

## 6. Deliverables map

| TITAN deliverable | Where it lands |
|---|---|
| Production repository | `crp/` (graduates to its own repo per staging convention) |
| Architecture documentation | `crp/docs/SPEC.md`, grown one RFC at a time |
| Benchmark suite | `crp/benchmarks/` (Plan 2) |
| Unit + integration tests | per-milestone, gated by pyrefly + CI |
| CI/CD | `.github/workflows/ci.yml`, extended per phase |
| Performance report | generated from Experience DB, per phase |
| Dashboard + visualization | future RFC (Phase 3+; web dashboard is a stretch goal) |
| Plugin SDK + developer docs | `crp/sdk/` placeholder → Phase 5 |
| Research paper | after ≥2 phases of honest empirical results (incl. negative results) |

## 7. Stretch goals (explicitly unscheduled)

Quantum-inspired contraction optimizer, adaptive bond dimension, distributed
runtime, CUDA kernels, Rust SIMD kernels, interactive benchmark explorer.
These remain outside every phase until an RFC argues for them from measured
evidence. Several are currently listed as Phase 0 **non-goals**; a non-goal
can only be revisited by an RFC that cites the data that changed the picture.

## 8. What this document is not

- Not a spec — it defines no interfaces, budgets, or acceptance criteria.
- Not a schedule — phases have entry evidence, not dates.
- Not an amendment to CRP governance — Constitution, Determinism, ABI, IR
  spec, and Roadmap win on any conflict about *how* to build; this document
  only ever answers *why* and *toward what*.

## History

- 2026-07-02 — First written (commit `784a22fc` on branch
  `feat/crp-m1-scaffold-telemetry`). That branch was superseded before
  merge and the commit never reached `master`; the file was absent from
  every ref for about a day while still recoverable from git's object
  store — a live example of why deliverables need to land on a path that
  survives branch churn, not just exist in *a* commit somewhere.
- 2026-07-03 — Recovered from `784a22fc` and corrected: relationship to
  CRP changed from "CRP grows toward TITAN" (one-layer model) to "CRP is
  the substrate inside TITAN" (five-layer model: Vision / Governance /
  Implementation / Research / Future), per external architectural review.
  Status references updated from "M1–M2 active" to reflect Phase 0 PASS
  and Gate 2 merged.

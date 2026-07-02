# CRP Phase 0 Exit Report

Date: 2026-07-03 | Commit: 487c77fced5d8caec0b1475f071028c2a14c387c | DB: `crp/experience.db` (schema v1)

## Environment

| Key | Value |
|---|---|
| cpu | AMD64 Family 25 Model 80 Stepping 0, AuthenticAMD |
| os | Windows-11-10.0.26200-SP0 |
| python | 3.12.10 |
| numpy | 2.4.2 |
| blas | scipy-openblas 0.3.31.dev |
| thread_count | 12 |
| power_profile | unrecorded |
| affinity | default |

## Hard requirements (spec section 2 / 2a)

| Criterion | Verdict |
|---|---|
| Runtime measured itself (Tier-0 events on the run path) | PASS |
| Telemetry overhead measured (BENCHMARK-M2.md: 17.7 ns / 0.238 us) | PASS |
| Representation decision recorded in Experience DB | PASS |
| Decision replayable (same inputs => same decision, 100%) | PASS |
| Better representation selected per workload, per evidence | PASS |
| Decision latency under 5 ms hard budget (max 2.505 ms) | PASS |

## Soft targets (0 / 2 met)

| Target | Verdict |
|---|---|
| Decision latency < 1 ms target — SOFT MISS (max 2.505 ms; target 1 ms, hard fail 5 ms) | MISSED |
| All Stage-0 statistics computed exactly once | MISSED |

## Known issues

- Stage-0 statistics recomputed per plugin (dominant decision-latency term; linear in plugin count) — tracked as [RFC-0005](rfcs/RFC-0005-shared-stage0-analysis.md).

## Decision-latency history (all recorded runs)

runs=4, mean=1.659 ms, p95=2.505 ms, std_dev=0.871 ms

## Recorded runs

| Run | Workload | Chosen | Decision latency | Events | Replay |
|---|---|---|---|---|---|
| 3 | synthetic_tensor | int8 | 2.505 ms | 2 | deterministic |
| 4 | embedding_search | int8 | 0.722 ms | 2 | deterministic |

Decision latencies are steady-state: one unrecorded warm-up run
precedes measurement to exclude one-time numpy/BLAS initialization.

**Phase 0 exit: PASS.** Reproduce with `py -3.12 crp/tools/phase0_exit.py` (appends new runs; the DB and ledger are append-only evidence).

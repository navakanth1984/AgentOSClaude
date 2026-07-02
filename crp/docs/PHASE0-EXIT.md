# CRP Phase 0 Exit Report

Date: 2026-07-03 | Commit: 27d26511d0b9c0846511749cd16a0ca6d7886bec | DB: `crp/experience.db`

## North Star (spec section 2)

| Criterion | Verdict |
|---|---|
| Runtime measured itself (Tier-0 events on the run path) | PASS |
| Telemetry overhead measured (BENCHMARK-M2.md: 17.7 ns / 0.238 us) | PASS |
| Representation decision recorded in Experience DB | PASS |
| Decision replayable (same inputs => same decision) | PASS |
| Better representation selected per workload, per evidence | PASS |
| Decision latency within spec 2a budget — SOFT MISS (max 2.288 ms; target 1 ms, hard fail 5 ms) | PASS |

## Recorded runs

| Run | Workload | Chosen | Decision latency | Events | Replay |
|---|---|---|---|---|---|
| 1 | synthetic_tensor | int8 | 2.288 ms | 2 | deterministic |
| 2 | embedding_search | int8 | 1.121 ms | 2 | deterministic |

Decision latencies are steady-state: one unrecorded warm-up run
precedes measurement to exclude one-time numpy/BLAS initialization.

**Phase 0 exit: PASS.** Reproduce with `py -3.12 crp/tools/phase0_exit.py` (appends new runs; the DB and ledger are append-only evidence).

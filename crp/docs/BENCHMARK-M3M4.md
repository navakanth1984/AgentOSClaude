# Milestones 3-4 Benchmark Report - Harness + Representations

Date: 2026-07-02 | Host: Windows 11, AMD Ryzen 5 5600H | Python 3.12

| Metric (spec 2a) | Measured | Target / Hard fail | Verdict |
|---|---|---|---|
| Representation decision latency (mean, 50 runs) | 0.356 ms | <1 ms / >5 ms | pass |
| Replay determinism (decision+scores, repeated runs) | 20/20 identical | 100% / any divergence | pass |
| Policy determinism | 50/50 identical | 100% | pass |
| Int8 memory vs dense | 0.25x | - | pass |
| Int8 max roundtrip error (seeded normal 32x16) | 0.014245 | <= 0.028533 | pass |
| Telemetry drops during harness runs | 0 | 0 expected at this load | pass |

Evidence: `pytest crp/runtime/tests -v` returned 25/25 passed. The benchmark
numbers came from a local measurement loop using seeded tensors, the frozen
`crp_telemetry.Telemetry` API, and the committed `run_workload()` harness. The
embedding-search replay run chose `int8` with deterministic scores
(`dense`: 128000.0, `int8`: 44549.01960784313).

Conclusion: the Dense/Int8 baseline plus deterministic policy is ready to feed
the Experience Database in Plan 3/3. The decision path is replayable and inside
the <1 ms target on this host, and harness telemetry records decision/execute
events without drops at the current workload size.

# RFC-0005: Shared Stage-0 Analysis Cache

**Status:** Draft (seeded from Phase 0 exit evidence, 2026-07-03)

## Problem

`select_representation` calls `plugin.analyze(tensor)` once per plugin. With
Dense and Int8 both delegating to `_base_stats`, identical statistics (shape,
sparsity, variance, memory) are computed N_plugins times per decision. This
is the dominant term in the decision-latency budget and scales linearly with
plugin count — Phase 1's Sparse/FP8 plugins would double it again.

## Evidence

- Phase 0 exit (commit 487c77fc): decision latency 2.3 ms warm on 512x512
  after intra-stat optimization (count_nonzero + BLAS-dot variance, ~3x) —
  still a SOFT MISS vs the 1 ms target (5 ms hard budget met).
- Profiling (2026-07-03 session): per-plugin `_base_stats` ~0.33 ms after
  optimization; two plugins ≈ 0.66 ms of pure duplication headroom.
- Ledger: `crp/docs/benchmarks/ledger.jsonl` (`subject: "phase0-exit"`).

## Expected gain

Decision latency ~1/N_plugins of current Stage-0 cost (target <1 ms for the
Phase 0 plugin pair); flat rather than linear scaling as plugins are added.

## Interface changes (why this is an RFC, not a patch)

The frozen `RepresentationPlugin.analyze(tensor) -> TensorStats` becomes a
consumer of a shared immutable analysis:

    Tensor -> Stage-0 Analysis (once) -> TensorStats -> plugin.estimate(...)

Plugins needing extra statistics declare them rather than recomputing base
ones. This also strengthens determinism: plugins consume one immutable
analysis instead of independently recomputing it.

## Risks

- Plugins with genuinely different analyses need an extension point
  (declared stat requirements) or the cache becomes a lie.
- Cache keyed by tensor identity must not alias across mutated buffers.

## Benchmark plan (accept/reject gate)

Before/after on both Phase 0 workloads, recorded in the ledger with full
environment metadata. Adds architectural-efficiency metrics:

| Metric | Meaning |
|---|---|
| `analysis_reuse_ratio` | Fraction of Stage-0 computations reused across plugins |
| `duplicate_compute_ms` | Time spent repeating identical work |
| `telemetry_overhead_ms` | Cost of measurement itself |
| `scheduler_overhead_ms` | Time outside plugin execution |
| `plugin_compute_ms` | Actual candidate computation time |

Accept only if decision latency reaches <1 ms on the Phase 0 reference host
with replay determinism preserved (100%).

## Related future provenance (Gate 3 alignment)

Replay records should eventually carry: replay version, compiler version,
plugin hash, manifest hash, Experience DB schema version. Schema versioning
starts now (`PRAGMA user_version`); the rest lands with this RFC or Gate 3.

## Non-goals

- No learned/bandit policy changes.
- No new representations.
- No cross-process or persistent analysis caching.

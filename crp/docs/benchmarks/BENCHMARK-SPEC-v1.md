# Benchmark Spec v1

Benchmark methodology is versioned separately from governance: methodology
evolves with research; governance rarely changes. A methodology change means
Benchmark Spec v2, never an edit to v1 — ledger entries reference the spec
version they were measured under.

## Methodology (v1)

- **Warm-up:** one unrecorded run precedes measurement to exclude one-time
  numpy/BLAS initialization; disclosed in every report.
- **Environment:** every measurement records CPU, OS, Python, NumPy, BLAS,
  thread count, power profile, affinity. Unknown values are stated as
  `unrecorded`, never omitted.
- **Distributions, not points:** report mean / p50 / p95 / std_dev and N.
- **Per-workload reporting:** latency distributions are grouped by workload
  spec; pooled aggregates are non-compliant as of v1 (Phase 0 exit reports
  predating this spec pooled them — known, superseded).
- **Ledger:** all results append to `crp/docs/benchmarks/ledger.jsonl`
  (append-only evidence; entries carry `schema` and full provenance).
- **Layers:** measurements identify their layer — native Rust (criterion),
  Python-Rust FFI, or end-to-end — so regressions localize to a layer.

## Research KPIs (owned here + by their RFCs, not by governance)

| KPI | Definition | Introduced by |
|---|---|---|
| `analysis_efficiency` | `shared_stage0_ms / total_decision_ms` | RFC-0005 |
| `reuse_ratio` | `reused_statistics / total_statistics_requests` | RFC-0005 |
| `experiment_efficiency` | `accepted_experiments / executed_experiments` | future RFC |
| `false_optimism` | `predicted_gain / measured_gain` | future RFC |

# Gate Report Pattern

Every CRP gate/exit report uses the same four sections, in this order.
Adopted from Phase 0 exit review (2026-07-03); `crp/docs/PHASE0-EXIT.md`
is the reference implementation.

1. **Hard Acceptance** — machine-checked criteria; any FAIL blocks the gate.
2. **Soft Objectives** — aspirational targets, reported as `n / m met`;
   misses never block, but each MISSED line must be machine-checked so it
   flips to MET automatically when the fix lands.
3. **Known Issues** — every soft miss and defect, each linking to its RFC
   or risk-register entry. Nothing is silently forgotten.
4. **Future RFCs** — capabilities observed but deferred behind governance.

Plus, always: environment metadata (CPU, OS, Python, NumPy, BLAS, threads,
power profile, affinity) and longitudinal history (mean/p95/std across all
recorded runs), because a number without its environment is noise.

## Deferred items (recorded 2026-07-03; RFC-gated, not Phase 0 work)

- **Independent schema versions** — `database_schema`, `ledger_schema`, and
  `bundle_schema` evolve separately (e.g. DB=2, bundle=4, replay=1) without
  synchronized migrations. Today only `PRAGMA user_version=1` exists.
- **Per-dimension latency history** — group by workload_id / plugin /
  representation / hardware_profile instead of one pooled distribution
  (lands with RFC-0005 benchmarks).
- **Research-loop KPIs** (once hypothesis generation matures):
  `experiment_efficiency = accepted_experiments / executed_experiments`;
  `false_optimism = predicted_gain / measured_gain`.
- **Gate 2 determinism principle** — treat the compiler as a deterministic
  build system: IR -> canonicalization -> hash -> template selection ->
  plugin -> manifest -> replay. Two identical canonical IR documents
  producing different artifacts is a compiler regression, by definition.

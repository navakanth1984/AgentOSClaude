# Gate Report Pattern

**Mandatory for:** gate reports, exit reports, promotion reports, and RFC
implementation reports. Every one of these artifacts is evaluated the same
way. Adopted from Phase 0 exit review (2026-07-03); `crp/docs/PHASE0-EXIT.md`
is the reference implementation.

Four sections, in order:

1. **Hard Acceptance** — machine-checked criteria; any FAIL blocks the gate.
2. **Soft Objectives** — aspirational targets, reported as `n / m met`;
   misses never block, but each line must be machine-checked (measured
   value + target + status) so it flips to MET automatically when the fix
   lands — no subjective judgment, no report edits.
3. **Known Issues** — every soft miss and defect, each linking to its RFC
   or risk-register entry. Nothing is silently forgotten.
4. **Future RFCs** — capabilities observed but deferred behind governance.

Plus, always: environment metadata and longitudinal history per the
versioned [Benchmark Spec](benchmarks/BENCHMARK-SPEC-v1.md). Determinism
claims defer to [DETERMINISM.md](DETERMINISM.md). Research KPI definitions
live in the Benchmark Spec and their owning RFCs — never in this document.

## Promotion authority

| Artifact | Promotion authority |
|---|---|
| RFC Draft | Research |
| RFC Accepted | Maintainer |
| Gate Complete | Acceptance tests |
| Gate Frozen | Maintainer + green regression suite |
| Promotion to master | Maintainer after frozen gate |

## Deferred work registry

Deferred work lives here, not in TODO comments. Each entry is auditable.

| Item | Rationale | Owning RFC | Affected gate | Promotion blocker |
|---|---|---|---|---|
| Shared Stage-0 analysis cache | Per-plugin stat recomputation dominates decision latency, linear in plugin count | RFC-0005 | Gate 2 (post) | No (soft target) |
| Independent schema versions (database / ledger / bundle) | Schemas evolve at different rates; avoid synchronized migrations | future RFC | Gate 3 | No |
| Per-dimension latency history (workload / plugin / representation / hardware) | Pooled distributions hide regressions | RFC-0005 (benchmark plan) | Gate 2 (post) | No |
| Research-loop KPIs (`experiment_efficiency`, `false_optimism`) | Meaningful only once hypothesis generation matures | future RFC | Gate 4 (post) | No |
| Full replay provenance (replay/compiler versions, plugin+manifest hashes) | Replays must name what produced their baseline | future RFC (Gate 3 scope) | Gate 3 | Yes — blocks Gate 3 completion |

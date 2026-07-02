# Gate Report Pattern

> [!IMPORTANT]
> **Frozen for Gate 2 implementation (2026-07-03):** `CONSTITUTION.md`,
> `DETERMINISM.md`, `COMPILER_ABI.md`, `IR_SPEC.md`, and this document.
> Changes now require an RFC or a documented defect — no incremental edits
> during implementation.

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

## Documentation precedence

When two documents conflict, the higher-precedence document wins and the
lower one has a defect:

1. `CONSTITUTION.md`
2. `DETERMINISM.md`
3. ABI specifications (`COMPILER_ABI.md`)
4. IR specification (`IR_SPEC.md`)
5. Benchmark specifications (versioned)
6. Gate reports
7. RFCs
8. ADRs

## Promotion authority

| Artifact | Promotion authority |
|---|---|
| RFC Draft | Research |
| RFC Accepted | Maintainer |
| Gate Complete | Acceptance tests |
| Gate Frozen | Maintainer + green regression suite |
| Promotion to master | Maintainer after frozen gate |

Promotion decisions are evidence-driven, not gate-specific:

| Evidence | Required for promotion |
|---|---|
| Acceptance tests | Always |
| Regression suite | Always |
| Determinism tests | Always |
| Benchmark evidence | Depends on gate |
| Replay evidence | Gate 3+ |
| Provenance evidence | Gate 3+ |

## Deferred work registry

Deferred work lives here, not in TODO comments. Each entry is auditable.

| Item | Rationale | Owning RFC | Affected gate | Promotion blocker | Introduced in |
|---|---|---|---|---|---|
| Shared Stage-0 analysis cache | Per-plugin stat recomputation dominates decision latency, linear in plugin count | RFC-0005 | Gate 2 (post) | No (soft target) | Phase 0 exit, commit 487c77fc |
| Independent schema versions (database / ledger / bundle) | Schemas evolve at different rates; avoid synchronized migrations | future RFC | Gate 3 | No | Review of 86fb3009 |
| Per-dimension latency history (workload / plugin / representation / hardware) | Pooled distributions hide regressions | RFC-0005 (benchmark plan) | Gate 2 (post) | No | Review of 86fb3009 |
| Research-loop KPIs (`experiment_efficiency`, `false_optimism`) | Meaningful only once hypothesis generation matures | future RFC | Gate 4 (post) | No | Review of 86fb3009 |
| Full replay provenance (replay/compiler versions, plugin+manifest hashes) | Replays must name what produced their baseline | future RFC (Gate 3 scope) | Gate 3 | Yes — blocks Gate 3 completion | RFC-0005 seed, commit 86fb3009 |

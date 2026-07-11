# mvct-mrp-core: H1 Research Handoff

> **Cold-start document.** Assume no prior context. Read this first.
> Source wiki page: `wiki/mvct-mrp.md` | Log: `wiki/log.md`

---

## Platform Status (2026-07-10)

**The experiment infrastructure is complete and hardened.** Milestone 5 (H1 Experiment Harness) is fully coded and committed on branch `milestone/sprint5-m5-h1-experiment-harness` inside the repository at `c:\Users\navka\navakanth001\mvct-mrp-core` and pushed to the private origin remote on GitHub.

| Priority | Item | Status |
|---|---|---|
| M5 Phase 1 | Frozen protocol configuration (`config/experiment.json`) | ✅ Done |
| M5 Phase 2 | Deterministic SHA-256 participant arm assignment with protocol snapshot metadata | ✅ Done |
| M5 Phase 3 | Append-only outcome logging with schema versioning (`src/experiment.ts`) | ✅ Done |
| M5 Phase 4 | Protocol validator (`scripts/validate_experiment.ts`) | ✅ Done |
| M5 Phase 5 | Enrollment stopping criterion (`scripts/check_stopping_rule.ts`) | ✅ Done |
| M5 Phase 6 | Descriptive report generation (`scripts/h1_report.ts`) | ✅ Done |

---

## Milestone Roadmap

| Milestone | Description / Focus | Status |
|---|---|---|
| M0 Infrastructure | Azure deployment, BKT oracle, live DB migration | ✅ Complete |
| M1 Event Ingestion | Ingestion API, event sourcing, Serializable transactions | ✅ Complete |
| M2 Robust Experience | API robustness, idempotency, React feed UI | ✅ Complete |
| M3 Event Infrastructure | Non-blocking EventBus, recommendation pipeline | ✅ Complete |
| M4 Runtime Hardening | EventBus audit, CardRenderer safety, Telemetry | ✅ Complete |
| M5 Experiment Harness | Outcome logger, arm assignment, stopping rules | ✅ Complete |
| **M6 Controlled Pilot** | Limited enrollment, continuous validation, integrity monitoring | 🔜 Active |
| **M7 Product Excellence** | UX redesign, motion, streaks, PWA support, telemetry | ⏳ Planned |
| **M8 Auto Engineering** | Agentic CI/CD, auto-QA, performance/security agents | ⏳ Planned |
| **M9 Platform SDK & API** | TypeScript SDK, public API, webhooks, multi-tenant | ⏳ Planned |
| **M10 Multi-Platform** | React Native, iOS, Android, offline-first sync | ⏳ Planned |

---

## Research Invariants & Freeze Policies

> [!IMPORTANT]
> Once participant data collection begins, the protocol is frozen.
> Violation of any item below invalidates the experiment.

- **Do not modify `eval_bkt.ts`.** It is the locked mathematical oracle.
- **Do not modify the H1 protocol** (arm definitions, session structure, outcome metric) after enrollment opens.
- **Preserve `LearningEvent` as strictly append-only.** No UPDATE or DELETE on the events table, ever.
- **Preserve `StudentProjection` replay determinism.** Projections must rebuild identically from the event log.
- **Preserve `experiment_outcomes.jsonl` as strictly append-only.** Corrections are written as new records, never mutate existing ones.
- **After the first participant is enrolled, `config/experiment.json` becomes immutable.** Any protocol modification requires incrementing the version to `H1-v1.1` or `H2-v1.0`.

---

## Next Steps for Milestone 6 (Pilot Study)

1. **Finalize the Primary Endpoint Protocol**:
   Before beginning enrollment, explicitly define the retention measurement criteria (e.g., immediate quiz scores vs. delayed 14-day recall, baseline improvements, or BKT mastery thresholds).
2. **Launch the Study**:
   Begin enrolling participants.
3. **Audit and Monitor**:
   - Regularly run `npx tsx scripts/validate_experiment.ts` to assert cohort database integrity, UTC timestamps, monotonic session progression, and lack of hashing skew.
   - Run `npx tsx scripts/check_stopping_rule.ts` to evaluate the enrollment stopping rule.
   - Run `npx tsx scripts/h1_report.ts` to output `report.md`, `report.json`, and `analysis_metadata.json` for reproducible descriptive analysis.

---

## Pre-flight commands for Next Session

```powershell
# Navigate directly to the repository
cd c:\Users\navka\navakanth001\mvct-mrp-core

# Verify you are in the correct branch
git branch -vv
# Expected: milestone/sprint5-m5-h1-experiment-harness

# Run verification suite (determinism + hashing distribution balance sanity check)
npx tsx tests/experiment_assignment.test.ts

# Verify compiler clean baseline
npx tsc --noEmit
```

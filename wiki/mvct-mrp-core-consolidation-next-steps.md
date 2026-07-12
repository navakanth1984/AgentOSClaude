# MVCT MRP Core Consolidation — Next Steps Handoff (2026-07-12)

This document provides a cold-start handoff for the next agent (e.g., Claude Code) resuming development on `mvct-mrp-core`.

---

## Current Status
* **Master State**: Clean, synced, and **100% green** with all 19 tests passing (`preflight`, `lint`, `build`, `test:telemetry`, `test:design-event`, unit, integration, performance, simulation, and research).
* **Consolidation**: All 8 divergent PRs (PR #10, #15, #11, #12, #16, #7, #17, #8) have been successfully merged.
* **Branches**: Zero open feature branches or PRs remain in `mvct-mrp-core`.
* **Deployment Hook**: Verified remote connection to Azure DB in local tests. Staging deploy pending user manual validation.

---

## Key File Map

* **Express Server Entrypoint**: [src/index.ts](file:///c:/Users/navka/navakanth001/mvct-mrp-core/src/index.ts) — Decoupled server listener wrapping via `if (require.main === module)` to prevent test suite hangs.
* **IOS Runtime Tests**: [tests/integration/ios_runtime.test.ts](file:///c:/Users/navka/navakanth001/mvct-mrp-core/tests/integration/ios_runtime.test.ts) — Live database-backed projection flow and gap recovery checks.
* **Performance Load Benchmarks**: [tests/performance/load_profile.test.ts](file:///c:/Users/navka/navakanth001/mvct-mrp-core/tests/performance/load_profile.test.ts) — Measures 1000 sequential reads against concepts table to enforce `< 40ms` latency and `< 30MB` memory delta.
* **Backlog Telemetry Projector**: [automation/src/engineeringProjector.ts](file:///c:/Users/navka/navakanth001/mvct-mrp-core/automation/src/engineeringProjector.ts) — Replays engineering event logs to compute repository fitness scores (`0.5` clean base, `0.3` with open findings).

---

## Prioritized Next Steps

### P0 — Staging Deploy & Production Release Verification
* **Objective**: Confirm that the consolidated `master` branch builds and deploys cleanly to the Azure environment.
* **Tasks**:
  1. Trigger/verify the deployment pipeline to Azure staging slot.
  2. Run UAT checks and verify the live telemetry health page `/health` (ensuring correct database checksum comparisons, BKT engine verification, and schema version mappings).
  3. Propose promotion to production and execute the mandatory 15-minute monitoring window.
* **Acceptance Criteria**:
  * `/health` returns status `200 OK` with `status: "healthy"` and database latency `< 50ms`.
  * Visual regression tests check out clean with no UI shifts.

### P1 — Progress to Milestone M8 (Platform Native SDK Transition)
* **Objective**: Scaffold and transition the Express backend endpoints into a reusable TypeScript SDK (`@mvct/sdk`) mapping the candidate retrieval, BKT engine update, and telemetry event append layers.
* **Acceptance Criteria**:
  * All public endpoints mapped 1:1 in the SDK.
  * Reusable client-side telemetry modules wrapped with offline caching fallbacks.

### P2 — Expand Product Intelligence analytics in Milestone M10
* **Objective**: Build auto-event aggregators processing the `product_analytics.jsonl` log format to detect user friction and session dropouts automatically.

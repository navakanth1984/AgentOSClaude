# MVCT MRP Core Consolidation — Next Steps Handoff (Updated 2026-07-13, Evening)

This document provides a cold-start handoff for the next agent (e.g., Claude Code, Antigravity) resuming development on `mvct-mrp-core`.

> **Superseded for current work (2026-07-15):** the project pivoted to the Interactor Creator/Explorer product (see `mvct-mrp-core-platform-contract.md` and the session log below). The infra history in this doc is still accurate background, but for current status and next steps use `mvct-mrp-core/HANDOFF_ANTIGRAVITY_2026-07-15_INTERACTOR_DEV_LIVE.md` in the repo.
>
> **2026-07-15 update:** the dev-deploy chain (Postgres creds, Prisma migration, CORS, Static Web App frontend deploy) is now fully live and verified — a real user can complete the whole Creator→Publish→Explorer→Feedback→Insights loop on the public Dev URL against real Azure Postgres. See the handoff doc for exact URLs, what was fixed, and what's next (naming-before-publish, SWA deploy automation, mobile/tablet UX pass).

---

## Current Status (updated 2026-07-13, evening, after Application Insights fix + deploy verification)

* **Master State**: Clean, synced, all tests green. PRs #21–#34 merged (P0 Application Insights import-order fix just landed).
* **Branches**: Zero open feature branches or PRs remain.
* **P0 Azure Dev deploy**: ✅ **VERIFIED GREEN** — Deploy pipeline (.github/workflows/deploy-dev.yml) fully automated and tested end-to-end. Real Azure resources in subscription "Visual Studio Enterprise Subscription" (`a1ce2694-4e38-4509-8bbc-64016f00d8f0`), resource group **`rg-mvct-dev-centralus`** (region `centralus`). Pipeline fires automatically after CI succeeds on `master`.

### Latest: Application Insights Request Telemetry Fix (2026-07-13)

**Issue**: Application Insights `requests` table stayed empty despite app logging init success and `/health` consistently returning 200. Manual telemetry (trackEvent/trackMetric) worked; only HTTP auto-collection silently failed.

**Root Cause**: The `applicationinsights` SDK monkey-patches Node's `http` module at telemetryProvider import time. But `src/index.ts` imported `telemetryProvider` *after* `express`, which already pulled in `http` — the patch never attached.

**Resolution (PR #34, merged to master)**:
- Moved `telemetryProvider` import to line 3 (after `dotenv/config`, before `express`).
- Ensures SDK patches `http` before Express pulls it in.
- Verified: `npx tsc --noEmit` clean, pyrefly hook passed, CI green (run 29239018824).
- Deploy Azure Dev auto-triggered and succeeded (run 29239318255, 11m27s).
- **Post-deploy verification**: `az monitor app-insights query requests` now returns live rows (GET /health, 200, success=True). Telemetry flowing end-to-end in production. ✅

### Earlier Deploy Fixes (PRs #21–#33, from prior sessions)

1. **Kudu extraction gateway timeout (PR #33)** — Optimized `.github/workflows/deploy-dev.yml` to prune docs/markdown/types/media from `node_modules` before zipping; extended deploy timeout to 10m. Reduced package size by ~145MB.
2. **Database migration automation (PR #30)** — Moved prisma + dotenv to dependencies, added `prisma/deploy-migrate.sh` + `.github/scripts/run-remote-migration.sh` for idempotent Kudu-based migrations. /health now returns database/migration/seed/projection/eventDictionary checks.
3. **Express server bootstrapping (PR #32)** — Installed `applicationinsights` npm package, wired telemetryProvider into startup sequence (order fixed in PR #34).
4. **Azure infrastructure hygiene (PRs #21–#29)** — Fixed region quota exhaustion, RBAC role gaps, Redis Classic retirement, deployment slots on Basic tier, AZURE_CREDENTIALS key naming, environment secrets visibility.

---

## Immediate Next Steps (Prioritized)

### P0 ✅ — Application Insights Request Telemetry Verified (COMPLETE, 2026-07-13)

**Status**: DONE. Live query: `az monitor app-insights query requests` returns real request data. Telemetry flowing end-to-end.

**Verification**:
- `/health` endpoint returning 200 consistently
- Application Insights `requests` table populated with live data (GET /health, success=True)
- No gaps between request generation and telemetry arrival

**Reference**: PR #34 (merged), Deploy run 29239318255 (green, 11m27s).

---

### P1 ✅ — Native SDK Transition (@mvct/sdk) (COMPLETE, 2026-07-13)

**Status**: COMPLETE. PR #35 open on origin/feat/sdk-foundation.

**Verification**:
- SDK builds successfully and passes unit tests.
- React web app builds successfully for production.
- Direct endpoint fetch operations completely replaced by SDK calls.

---

### P2 — Power BI Integration (NOT STARTED)

**Status**: Deferred. User planned for post-Application-Insights verification.

**Scope**: Wire Power BI datasource to Application Insights `requests`/`customEvents` tables.

---

### P3 — Schema Checksum Follow-Up PR (NOT STARTED, SEPARATE PR)

**Status**: Known non-blocking issue. Can be deferred until after P1 completes.

**Issue**: `/health` endpoint returns `checksums.schema.valid: false`. Root cause: hardcoded M0-frozen SHA256 hash of `prisma/schema.prisma` no longer matches because of two later migrations (add_assignment_metadata, add_ios_models).

**Decision needed**: Should health check:
- Regenerate expected checksum dynamically?
- Version checksum by milestone?
- Compare against migration history instead?
- Expose schema drift differently (e.g., as warning, not failure)?

**Notes**:
- This is safe to leave open; `/health` doesn't gate deployments (it's post-deploy verification only).
- Prioritize P1 SDK transition; return to checksum design after M8 solidifies.

---

### P4 — Evidence Pack Regeneration (NOT STARTED)

Update evidence pack with this incident's before/after health endpoint output, migration logs, telemetry verification, etc.

---

## User-Set Autonomous Priorities (Standing)

**P0**: ✅ Application Insights request telemetry verification — **COMPLETE 2026-07-13**.  
**P1**: ✅ Native SDK (@mvct/sdk) transition — **COMPLETE 2026-07-13** (PR #35).  
**P2**: 🔜 Begin Power BI integration — **ACTIVE NEXT**.  
**P3**: Begin Infrastructure Intelligence (II-0) as new 7th layer — future milestone.

---

## Known Follow-Up Work (Not Yet Started)

* **`SelfEvolvingApp-RG`** (different subscription, centralindia) — User confirmed intent to migrate Postgres data into mvct-mrp-core's database eventually. **Azure Postgres cannot move across subscriptions/resource groups**, so requires fresh provision + `pg_dump`/`pg_restore`. Not started.
* Two empty, orphaned resource groups: `rg-mvct-dev` (eastus) and `rg-mvct-dev-eus2` (eastus2). Harmless cleanup task.
* **Roadmap conflict unresolved**: Cold-start handoff said M8 = SDK Transition / M10 = Product Intelligence. But `product/roadmap.md` v2.0 (2026-07-11) says M8 = Autonomous Engineering & QA, M9 = Platform & SDK, M10 = Multi-Platform Release. **Confirm with user which plan is authoritative before M8 work starts** — but proceed with current handoff (M8 = SDK) unless explicitly overridden.

---

## Key File Map

* **Express Server Entrypoint**: [src/index.ts](file:///c:/Users/navka/navakanth001/mvct-mrp-core/src/index.ts) — Telemetry import moved to line 3 (import order is load-bearing).
* **Application Insights Entry Point**: [src/intelligence/telemetry/telemetryProvider.ts](file:///c:/Users/navka/navakanth001/mvct-mrp-core/src/intelligence/telemetry/telemetryProvider.ts) — Auto-instrumentation (unchanged; fix was import order only).
* **Migration + Seed Runner**: [prisma/deploy-migrate.sh](file:///c:/Users/navka/navakanth001/mvct-mrp-core/prisma/deploy-migrate.sh) — Idempotent, reconstructs DATABASE_URL from env vars, runs migrations + seed.
* **Kudu API Wrapper**: [.github/scripts/run-remote-migration.sh](file:///c:/Users/navka/navakanth001/mvct-mrp-core/.github/scripts/run-remote-migration.sh) — Invokes deploy-migrate.sh via Kudu command API.
* **Deploy Pipeline**: [.github/workflows/deploy-dev.yml](file:///c:/Users/navka/navakanth001/mvct-mrp-core/.github/workflows/deploy-dev.yml) — Fully automated, wired for migration step + health gate + telemetry checks.
* **Health Endpoint**: [src/index.ts /health](file:///c:/Users/navka/navakanth001/mvct-mrp-core/src/index.ts) — Returns database/migration/seed/projection/eventDictionary health checks (checksum.schema.valid issue known, non-blocking).

---

## Session Memory & Handoff

* **Session file (this session)**: C:\Users\navka\navakanth001\memory_os\session_memory\session_20260713_end.md
* **Wiki log**: Updated wiki/log.md with PR #34 + deploy verification entry (2026-07-13, top).
* **Wiki page**: This file (mvct-mrp-core-consolidation-next-steps.md), updated P0 → COMPLETE, reordered to P1 SDK Transition next.
* **Model used**: Claude Haiku 4.5 (Tier 2, appropriate for focused debugging + verification).
* **Handoff to**: Antigravity (or next Claude Code session) — P1 (Native SDK Transition) is ready to start. See HANDOFF_ANTIGRAVITY_2026-07-13.md for full context.

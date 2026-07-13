# MVCT MRP Core — Handoff to Antigravity (2026-07-13)

**Status**: P0 (Application Insights verification) complete and verified. Deploy pipeline green end-to-end. Ready for P1 (Native SDK Transition, @mvct/sdk).

**Repo**: `mvct-mrp-core` on `master` (GitHub: https://github.com/navakanth1984/mvct-mrp-core)

---

## What Just Landed (2026-07-13, Claude Code Session)

### P0: Application Insights Request Telemetry — ✅ VERIFIED & DEPLOYED

**Problem**: Application Insights `requests` table was empty despite successful init and live `/health` endpoint. Manual telemetry calls worked; only HTTP auto-collection failed silently.

**Root Cause**: The `applicationinsights` SDK monkey-patches Node's `http` module at import time. `src/index.ts` imported `telemetryProvider` *after* `express`, which already pulled in `http` — patch never attached.

**Fix (PR #34)**:
- Moved `telemetryProvider` import to line 3 (after `dotenv/config`, before `express`).
- Ensures SDK patches `http` before Express pulls it in.
- TypeScript clean (`npx tsc --noEmit`), pyrefly hook passed, CI green.
- Deploy Azure Dev auto-triggered and succeeded (run 29239318255, 11m27s).

**Verification**:
- ✅ `az monitor app-insights query requests` returns live rows: GET /health, 200, success=True
- ✅ Post-deploy `/health` endpoint returning all green checks (database, migration, seed, projection, eventDictionary)
- ✅ Telemetry flowing end-to-end in production

**Key takeaway**: Import order is load-bearing when using monkey-patching SDKs. SDK must be imported before the modules it needs to intercept.

---

## Current Verified State

| Item | Status |
|------|--------|
| Master branch | Clean, synced, tests green |
| Application Insights integration | ✅ Working, telemetry flowing |
| Azure Dev deploy pipeline | ✅ Automated, green, 11m27s |
| `/health` endpoint checks | ✅ All green (db, migration, seed, projection, eventDictionary) |
| Database migrations | ✅ Automated via Kudu (PRs #30, idempotent) |
| Package size optimization | ✅ Done (PR #33, removed 145MB from node_modules) |
| Known non-blocking issue | `checksums.schema.valid = false` — schema hash mismatch due to post-M0 migrations (P3, defer) |

---

## What's Next: P1 (Native SDK Transition, @mvct/sdk)

### Scope
Transition from hand-coded BKT logic to `@mvct/sdk` native implementation. This is M8 milestone.

### Pre-Work
1. Verify `@mvct/sdk` module is published/available (npm registry, private, or monorepo reference).
2. Review M8 specification in repo docs or wiki/mvct-mrp.md for interface requirements.
3. Audit current BKT implementation in `src/intelligence/` for compatibility.

### Suggested Approach
1. Create `src/sdk/` folder (or reference external module).
2. Extract core BKT endpoints (`/attempt`, `/feedback`) to use SDK internals.
3. Smoke test: POST `/session` → POST `/attempt` → GET `/feedback` flow.
4. Verify telemetry still flows (Application Insights should show new request patterns).
5. CI all green, deploy to Azure Dev, verify `/health` remains green.
6. Open PR, review, merge when ready.

### Known Blockers / Gotchas
- **Schema checksum**: `/health` returns `checksums.schema.valid = false`. This is safe to leave (doesn't gate deployments); fix after M8 lands.
- **Roadmap conflict**: Prior handoff says M8 = SDK. But `product/roadmap.md` v2.0 says M8 = Autonomous Engineering & QA, M9 = SDK. **Confirm with user which is authoritative** before deep work — proceed with current (M8 = SDK) unless explicitly overridden.
- **SelfEvolvingApp-RG migration**: User mentioned migrating Postgres from a different subscription/region. Not a blocker for P1, but note it exists.

---

## File Map for Reference

| File | Purpose | Importance |
|------|---------|-----------|
| [src/index.ts](file:///c:/Users/navka/navakanth001/mvct-mrp-core/src/index.ts) | Server entrypoint; telemetry import on line 3 | Load-bearing |
| [src/intelligence/](file:///c:/Users/navka/navakanth001/mvct-mrp-core/src/intelligence/) | BKT + telemetry logic (SDK integration target) | Core |
| [.github/workflows/deploy-dev.yml](file:///c:/Users/navka/navakanth001/mvct-mrp-core/.github/workflows/deploy-dev.yml) | Automated deploy pipeline (mutation + migration + health gate) | CI/CD |
| [prisma/](file:///c:/Users/navka/navakanth001/mvct-mrp-core/prisma/) | Schema + migrations + seed (auto-deployed via Kudu) | Data layer |
| [tests/](file:///c:/Users/navka/navakanth001/mvct-mrp-core/tests/) | Integration + performance test suites | Verification |

---

## Handoff Checklist

- [x] P0 (Application Insights) verified in production
- [x] Deploy pipeline confirmed green end-to-end
- [x] Telemetry flowing to Azure Application Insights (live data confirmed)
- [x] wiki/mvct-mrp-core-consolidation-next-steps.md updated (P0 → COMPLETE, P1 → ACTIVE NEXT)
- [x] Session memory saved to C:\Users\navka\navakanth001\memory_os\session_memory\session_20260713_end.md
- [x] wiki/log.md updated with PR #34 + deploy verification entry
- [ ] Antigravity (or next agent) begins P1 (Native SDK Transition) when ready

---

## Questions / Escalations

If anything blocks P1 start:
- **SDK availability**: Confirm @mvct/sdk is in npm registry or monorepo; share package.json reference.
- **API contract**: Share M8 specification or BKT SDK interface docs.
- **Roadmap clarity**: Confirm M8 = SDK Transition (current) vs. M8 = Autonomous QA (prior doc mismatch).

---

**Next agent**: You are cleared to start P1. Master is clean, tests green, no hidden tech debt. PR workflow enforced (branch → CI → review → merge). Good luck!

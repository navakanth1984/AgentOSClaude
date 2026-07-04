# NAC — Current State (single source of truth)

> This is the **live operating manual**. It should rarely exceed a few pages. Historical handoffs, session narratives, and completed-sprint writeups live in [nac-next-steps.md](nac-next-steps.md) instead — do not let this file accumulate journal entries again. Architecture decisions live in [DECISIONS.md](DECISIONS.md). What comes after the gate lives in [ROADMAP.md](ROADMAP.md). One-line dated entries live in [CHANGELOG.md](CHANGELOG.md).

## Dashboard (machine-readable)

```yaml
project:
  milestone: Sprint 3B - Director Studio V2 (UX Pass 2, Gates A/B/C shipped)
  lifecycle: DOGFOODED          # see Milestone Lifecycle below
  production_gate: NOT_PASSED
  last_verified: 2026-07-04

repositories:
  nth-absolute-cinema:
    branch: feat/director-studio-v2   # base: feat/provider-orchestration (PR #3, still draft/unmerged)
    commit: c42830f
    pr: none  # not yet opened - awaiting Gate C user review before Gate D

  navakanth001:
    branch: docs/crp-gate2-freeze

director_studio_v2_gates:
  gate_a_scaffold: DOGFOODED       # React/TS/Vite/Tailwind/shadcn/Router/Zustand/Query/Framer wired to FastAPI, CORS verified live
  gate_b_architecture: DOGFOODED  # layout/routing/stores/typed API layer/design system, verified live
  gate_c_experience: DOGFOODED    # Welcome + Creation Wizard, full create-project flow verified live end-to-end
  gate_d_storage_ui: PLANNED      # not yet scoped by user
  gate_e_character_dept: PLANNED  # blocked on Production Readiness Gate, do not start

verification:
  tests: 155
  passed: 155
  ui_verified: true
  live_provider_smoke:
    gemini: pending
    sarvam: pending
    elevenlabs: failed_401

next_action:
  - Await user review of Gate C (Director Studio V2 Experience Layer) before starting Gate D
  - Separately, still pending: update ELEVENLABS_API_KEY in .env, run scripts/elevenlabs_smoke_test.py
  - Then: live Gemini smoke, live Sarvam smoke
```

---

## 🚦 Production Readiness Gate (Mandatory)

**Status:** 🚧 NOT PASSED

No new departments (Character, Location, Scene, Beat, etc.) may begin until this gate is explicitly passed.

### Definition of Done — Gate PASSES only when all of these are checked

```
□ 100% automated test suite passing
□ Live UAT completed (real browser, real providers where applicable)
□ No Critical (P0/P1) issues open
□ Provider smoke tests passed (Gemini, Sarvam, ElevenLabs — live, not mocked)
□ Director Studio UX checklist signed off (Pass 2)
□ Documentation updated (this file + relevant wiki pages)
□ Branch merged cleanly into master
```

Partial completion (e.g. "6 of 7 checked") is **NOT PASSED** — treat this as binary, not a percentage.

---

## CURRENT STOP LINE

Do **NOT** implement:

* Restore Manager
* Migration Manager
* Character Department
* Department Framework expansion
* Creative Knowledge Graph Phase 2

until the Production Readiness Gate above reads **PASS**. No exceptions, no "just the scaffolding," no "just the interface."

---

## Reality Check (implemented ≠ production ready)

```
✓ Storage Manager implemented
✓ Snapshot Manager implemented
✓ .nac Serializer/Deserializer implemented
✓ Provider Orchestration implemented
✓ Director Studio (legacy vanilla-JS) implemented
✓ Director Studio V2 Gates A-C (React rewrite: scaffold, architecture, Welcome+Wizard) - each dogfooded live in browser, not just built

Pending live validation
□ Gemini smoke test
□ Sarvam smoke test
□ ElevenLabs smoke test (currently failing — 401)
□ End-to-end UI dogfood of a FULL project lifecycle (create → generate → review → export) through Director Studio V2 - Gate C only covers creation, not generation/review/export yet
□ Director Studio V2 Gate D (storage/snapshot/package UI) - not yet scoped
```

"Implemented" means the code exists and unit/integration tests pass against it. It does not mean the feature works against a real external provider, or that a human has driven it through the actual UI. Keep these two columns separate in every future status update — collapsing them is exactly how Sprint 2A got declared "complete" three times before real bugs surfaced (see Sprint 2A.2 in [nac-next-steps.md](nac-next-steps.md)).

## Milestone Lifecycle (applies to every current and future department)

```
PLANNED → IMPLEMENTED → TESTED → DOGFOODED → PRODUCTION READY → FROZEN
```

* **PLANNED** — spec/design agreed, nothing built.
* **IMPLEMENTED** — code written, compiles/type-checks.
* **TESTED** — automated test suite green against it.
* **DOGFOODED** — a human exercised it live through the actual UI/CLI a real user would use, not just `MockProvider` or a unit test harness.
* **PRODUCTION READY** — Gate's Definition of Done satisfied for this milestone specifically.
* **FROZEN** — merged to `master`; further changes require a version bump / new milestone, not silent edits.

Every current item in this doc should be describable by exactly one of these six states at any time — not by prose that implies more progress than actually happened.

## Acceptance Evidence (required per milestone before it can move past DOGFOODED)

* Test report (pass count, e.g. "155/155")
* Screenshot(s) or recording of the live UI run
* Smoke report (file path, e.g. `wiki/elevenlabs-smoke-report.md`)
* Commit hash
* Branch name

Without these five, a milestone cannot be marked DOGFOODED or PRODUCTION READY, regardless of how confident the report sounds — this makes retrospective review possible months later without re-trusting an agent's self-report.

## Provider Status

**ElevenLabs**
```
Implementation      ✓ Complete (ElevenLabsProvider, fallback chain, diagnostics wired)
Configuration       ⚠ Invalid/expired API key in .env
Live Smoke Test     ✗ Failed (401 Unauthorized) — see wiki/elevenlabs-smoke-report.md
Action Required     Update ELEVENLABS_API_KEY in .env, then re-run scripts/elevenlabs_smoke_test.py
```

**Gemini** — implementation wired into fallback chain; live smoke test not yet run (needs user approval to spend quota).

**Sarvam** — implementation wired (TTS fallback chain); live smoke test not yet run (same).

## Known Limitations (visible technical debt — does not block unrelated work)

* ElevenLabs integration is code-complete, but the configured API key returns HTTP 401 during live smoke testing — needs a valid key in `.env`.
* Aspect ratio selection in the Director Studio is UI-only (drives the Cinematography framing preview) and does not yet propagate to the actual prompt compiler output — do not consider it "complete" until it does.
* Ollama-backed local provider validation requires a local Ollama runtime and models installed; this machine currently has neither, so those checks honestly report "Not Installed / Not Running" rather than being skipped silently.

## Blockers vs. Enhancements

**Blockers (must resolve before the Gate can pass):**
* Live Gemini smoke test
* Live Sarvam smoke test
* Live ElevenLabs smoke test (currently failing — 401)
* Director Studio UX Pass 2 — **in progress** on `feat/director-studio-v2` (Gates A/B/C shipped and dogfooded; Gate D not yet scoped, awaiting user review of Gate C first)
* End-to-end dogfooding (one full short-film project through the Director Studio only)

**Enhancements (do not block the Gate — track separately):**
* Timeline runtime-ruler polish, extra animations
* Additional diagnostics views beyond the core control center
* Creative Graph visual refinement beyond basic node/edge display
* Storage mapping visual polish (Local ↔ External SSD ↔ cloud stubs)

---

## Governance freeze

The rules above (Gate, Stop Line, Definition of Done, Milestone Lifecycle, Acceptance Evidence, Reality Check) are considered **frozen**. Do not rewrite or relax them session-to-session — only change them if the underlying architecture genuinely evolves, and treat that as a decision worth recording in [DECISIONS.md](DECISIONS.md), not a silent edit here.

# NAC — Changelog

One line per dated milestone. Full narrative for each entry lives in [nac-next-steps.md](nac-next-steps.md); architecture rationale lives in [DECISIONS.md](DECISIONS.md).

- **2026-07-03** — Sprint 0 (Architecture Freeze) complete: 15 specs frozen under `docs/specs/v1/`.
- **2026-07-03** — Sprint 1 (MVP Studio engine) complete: `nac.Studio` SDK, CLI, provider fallback chain, real end-to-end example (`temple_of_varuna`). 49/49 tests green.
- **2026-07-03** — CKG Phase 1.6: fixed non-deterministic `created_at` ordering (SQLite second-level clock precision). 54/54 tests green.
- **2026-07-03** — Sprint 2A.1 verification: multi-project isolation and regeneration-freeze invariant confirmed PASS; feature-length screenplay generation identified as an architectural gap (needs hierarchical compiler pipeline, not chunking).
- **2026-07-04** — Character Genome Spec v1.2 frozen and merged (`03005fc`, PR #2). See ADR-002.
- **2026-07-04** — Sprint 2A.1 Integration Stabilization: fixed runtime provider fallback, stale editable install, `nac` missing from PATH. Diagnostics panel added. 79/79 tests.
- **2026-07-04** — Sprint 2A.2 UAT: full 18-step acceptance run PASS; fixed indefinite-hang bug in generate button (wall-clock deadline via `ThreadPoolExecutor`). Demo Project added. 85/85 tests. Sprint 2A declared genuinely frozen after three "complete" claims were each followed by real bugs.
- **2026-07-04** — Sprint 3A (Storage Manager, Snapshot Manager, `.nac` Serializer/Deserializer, Director Studio UI redesign) complete and live-verified. 125/125 tests.
- **2026-07-04** — Sprint 3A.5 Production Readiness verification pass: found and fixed a `/status` endpoint bug and an aspect-ratio state leak across projects.
- **2026-07-04** — Director Experience Pass 1: UX honesty pass (aspect ratio labeled "Preview Only", "Planned" nav section, better loading/error states). 137 tests.
- **2026-07-04** — Provider Orchestration: Gemini/Sarvam wired into fallback chains via `python-dotenv`. Local Provider Smoke Test gate built (100% local checks pass before any cloud quota spend). 146 tests, 2 skip.
- **2026-07-04** — ElevenLabs integrated as a first-class Voice Provider (`ElevenLabsProvider`, fallback chain `ElevenLabs → Sarvam → pyttsx3`). Live smoke test run, failed with HTTP 401 (invalid/expired API key). 155+ tests.
- **2026-07-04** — Governance overhaul: Production Readiness Gate, Stop Line, Definition of Done, Milestone Lifecycle, and Acceptance Evidence formalized. `wiki/CURRENT.md`, `wiki/DECISIONS.md`, `wiki/ROADMAP.md`, `wiki/CHANGELOG.md` split out of `wiki/nac-next-steps.md` to separate live operating manual from historical journal.
- **2026-07-04** — Director Studio V2 Gate A: React/TS/Vite/Tailwind v4/shadcn deps/React Router/Zustand/React Query/Framer Motion scaffold on `feat/director-studio-v2`, wired live to the existing FastAPI backend via CORS. Old vanilla-JS dashboard untouched. Commit `693a5a1`.
- **2026-07-04** — Director Studio V2 Gate B: architecture foundation — layout (`AppLayout`/`TopBar`/`Sidebar`/`InspectorPanel`/`BottomTimeline`/`Workspace`), real routing, Zustand split 4 ways, typed API layer by resource, design system (department/status color tokens, Button/Badge/Card/StatusDot/ProgressIndicator). Commit `052a497`.
- **2026-07-04** — Director Studio V2 Gate C: Experience Layer — Welcome rewrite (real progress %, real activity feed, Demo Project) and 3-step Creation Wizard with a large visual Aspect Ratio picker, verified live end-to-end (create → real project → `/project/:id`). Commit `c42830f`. Gate D (storage/snapshot/package UI) not yet scoped.

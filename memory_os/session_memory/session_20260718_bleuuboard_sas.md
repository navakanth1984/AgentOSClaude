# Session 2026-07-18 (evening): Bleuuboard SAS Phase 1 — Design → Ship → Incident → Harden

**Surface:** Claude Code (Opus 4.8) · **Repo:** AgentOSClaude, branch `feat/hermes-delegation`
**Prod:** https://bleuboard.vercel.app · **Tag:** `bleuuboard-sas-phase1` → dpl `bleuboard-adqnbthiv`

---

## 1. P3 redefined by the user (design outcome)

Entered as "P3 Spatial Reference System" brainstorm; the user rejected the framing twice and
produced a better one. **Record this — the user's reframes drove the whole design:**

- **Problem is orientation, not placement.** In 2D editors the screen is the reference frame;
  in perspective 3D, mouse-up often means "farther away". That mismatch is the cognitive friction.
- **Renamed → Spatial Awareness System (SAS)**, two layers:
  - *Awareness* ("what am I looking at?") — relative position, direction, cursor/camera context
  - *Reference* ("how do I describe it?") — named anchors, offsets, local frames, formations
  - **"References without awareness are just numbers."**
- **Phase ladder:** 1 Orientation → 2 Relative Placement → 3 Named References → 4 Local Frames → 5 Formations
- **Rejected A/B/C movement-plane options, proposed D: Intent-Based Dragging.** SAS is not another
  manipulation mode — it is the *interaction decision engine*. Renderer answers "where is the object?",
  interaction answers "what plane is active?", SAS answers "what is the user trying to do?"
- **UX directive:** calm by default, progressive disclosure, conversational HUD, animated intent
  transitions, transparent learning, accessibility without color-alone.
  **Governing invariant: "The HUD should never explain the engine. It should explain the user's intention."**
  (Testable: any HUD string containing "plane", "axis", or raw coordinates fails review.)
- Then issued an **EXECUTION DIRECTIVE — Build While Flying**: stop architecture expansion, ship
  Phase 1 only, Option B structure (internal modules, explicit contract, no `packages/` extraction).

## 2. What shipped (live in prod)

`whiteboard-4d/index.html`, committed `7dfe3109`:

- **SASCore** — pure intent engine. Per-drag frame resolution: grounded types
  (block/shape/model/icon) → floor plane; floating types (text/image/video/sticker) → screen plane.
  Shift forces screen / Ctrl forces floor, **mid-drag**, with the move plane re-anchored live so the
  object never jumps. Per-object override memory with dedup. Telemetry ring buffer (5 event types).
- **SASCard** — conversational card: "Moving on Floor" / "Following Screen", nearest reference with
  axis-word offsets ("1.4 right · 1.0 behind"), ⌗ grid indicator, Manual Override / Remembered
  badges, hover shows object name only, snap-entry pulse, animated intent flips.
- **Contract** `{intent, frame, override, remembered}` — one object consumed by the drag pipeline,
  the card, and telemetry. This is the extraction seam and the "Measured" gate seed.
- Numeric coord HUD demoted to **F9 debug**.
- Registered as **IKOS Capability Candidate #5** (supersedes SpatialHUD #4 as the production surface).

## 3. OPEN DESIGN ISSUE (top of next session)

**Vertical drag maps to front/back for grounded objects.** User: *"movement top to bottom is still
moving front and back. Left and right work because it's still accommodating 2D space."*

- This is inherent to the ground-plane default, not a bug.
- **Tried and REVERTED: contact blob shadows** (radial texture disc pinned under each object +
  near-overhead sun). User: *"this one is worse."* Grounding the shadow did not fix the mapping —
  it treated the symptom. Reverted cleanly; do not retry this route without new evidence.
- **Cheapest next experiment:** flip the grounded default to screen-plane in `SASCore.interpret`
  (~2 lines) so up = up everywhere and Ctrl opts into floor movement. The *default* is the suspect.
- User accepted the current build as-is meanwhile ("This version fine") and authorized deploy.

## 4. INCIDENT: green pipeline, stale production

Deployed SAS → pipeline reported `PASS` → **production was still serving the previous build.**

- **Root cause:** an earlier `vercel rollback` (used to revert the blob-shadow deploy) **pins the
  production alias**. A later `vercel --prod` creates a deployment but does not move
  `bleuboard.vercel.app`. Fixed at the time with an explicit `vercel promote`.
- **Why the pipeline could not see it:** `smoke_test()` reads the **local** `index.html` before
  upload. It validates the artifact, never the live URL. It passed 8/8 on both the build the user
  judged broken *and* the deploy that never went live.
- **Also true and worth remembering:** the first deploy of the day was a process failure upstream of
  any tooling — a build whose core interaction the user had already flagged as feeling wrong was
  deployed anyway. No smoke test catches a design regression; staging-first is the guard.

## 5. Versioning discovery

**Nothing from 2026-07-18 was in git.** All four morning production features *and* SAS were deployed
from an uncommitted working tree (285 uncommitted lines in `index.html`); `wiki/ikos-*.md` and
`wiki/bleuboard.md` were untracked entirely. That is why the morning rollback had no git anchor.

Now: `7dfe3109` (features + SAS + IKOS docs), tagged `bleuuboard-sas-phase1` = the live prod deploy.
Note: a first commit attempt swept in two docs another session had left staged; reset and recommitted
cleanly, leaving those files staged as found.

## 6. ADLC pipeline hardened (`d6c7ac1f`)

`whiteboard-4d/adlc_pipeline.py`:

- `deploy_prod()` now **always** runs `vercel promote` after `--prod`, and fails if promote fails.
- **`verify_live()`** — post-deploy gate: fetches the production **alias**, checks content markers +
  size ratio (0.85–1.15) with CDN-propagation retries. `deploy` now FAILS if users aren't served the
  new build.
- **`rollback [url]`** — lists prod deployments, defaults to the previous, verifies the alias after,
  logs to CI history.
- **`verify`** — standalone live check.

**Four bugs found by testing the fix (two pre-existing):**
1. `run()` decoded subprocess output as cp1252 → crashed on Vercel's Unicode status glyphs.
2. `status` crashed printing box-drawing chars to a cp1252 console — **had been broken outright**.
3. Pre-commit type gate: unbound `status` variable in the retry loop (real bug).
4. Pre-commit type gate: `TextIO.reconfigure` attribute error.

Negative-tested: `verify_live` correctly FAILS on a missing marker (a check that always passes is
worthless). Prod verified healthy throughout.

## 7. Standing rules reaffirmed

- **Never deploy without asking.** (Held all session; every deploy was explicitly authorized.)
- After any `vercel rollback`, the next deploy **must** promote explicitly — now automatic.
- Deploy is not "done" at upload; it's done when the **alias** serves the build.

## 8. Next session — ordered

1. **SAS vertical-drag mapping** — flip grounded default to screen-plane in `SASCore.interpret`, test live.
2. **SAS Phase 2** — touch override surface (tappable SAS card), adaptive layout.
3. **Telemetry sink** — SASCore.log currently in-memory only; blocks the IKOS "Measured" gate.
4. Interactor **PR #41** still open, E2E green, awaiting merge.
5. Consider porting the `verify_live` + `rollback` pattern to `agent_os/adlc_pipeline.py` (same class
   of gap likely exists there).

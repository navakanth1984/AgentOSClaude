# BLEUUBOARD — 4D Creative Whiteboard

> A self-contained, browser-based 4D creative whiteboard. Draw 3D strokes, place extruded 3D text, images and live video, link ideas, and animate through the 4th dimension. Deployed at [bleuboard.vercel.app](https://bleuboard.vercel.app/).

## Project Location

- **Source:** [`whiteboard-4d/index.html`](../whiteboard-4d/index.html) — single-file app
- **Deployment config:** [`whiteboard-4d/vercel.json`](../whiteboard-4d/vercel.json)
- **Vercel project ID:** `prj_iKxcmpHegBoNf4pTt67cfuScAM6h`
- **Vercel org:** `team_9ZBEcXoqZuy4SQFq5c6Eapwj`

## Architecture

Single `index.html` (~158 KB) served as a static Vercel deployment via `@vercel/static`. No build step. No framework. All logic is vanilla HTML + JS + Three.js (or equivalent) embedded in one file.

```json
{
  "version": 2,
  "name": "bleuuboard",
  "builds": [{ "src": "index.html", "use": "@vercel/static" }],
  "routes": [{ "src": "/(.*)", "dest": "/index.html" }]
}
```

## Deployment & Access

| Environment | URL | Protection |
|---|---|---|
| Production | `bleuboard.vercel.app` | ❌ Disabled (public) |
| Preview branches | Vercel preview URLs | ✅ Enabled (team-only) |

**Best practice:** Production protection is off so any user can access the app. Preview/feature-branch deployments remain protected for internal review before shipping.

## Maintenance Log

### 2026-08-20 — Google Cloud GenAI (Gemini 2.5 Flash), Secret Manager & Accessibility Integration (PR #3 & PR #7)
- **Google Cloud Run Backend (`spatial-bridge/`):** Deployed `bleuboard-spatial-bridge` to Cloud Run (`https://bleuboard-spatial-bridge-526005048954.us-central1.run.app`, revision `00008-pmt`).
- **Google Secret Manager (`nthdim-academy-v2`):** Stored all credentials (`bleuboard-gemini-api-key`, `bleuboard-openrouter-api-key`, `bleuboard-sarvam-api-key`, `bleuboard-elevenlabs-api-key`) in Secret Manager; mounted securely via `--set-secrets` at container startup.
- **Gemini 2.5 Flash Spatial Intelligence (`v2/src/agent/vertex_search.js`, `copilot.js`, `interpret.js`):**
  - Online natural language spatial grounding translating user prompts to Three.js commands (`create`, `move`, `rotate`, `scale`, `navigate`, `holodeck`, etc.) with high confidence ($0.95+$).
  - Upgraded voice pipeline with `FileReader` base64 streaming for large audio blobs without call-stack overflow.
  - Dual-path execution: Gemini Live Audio primary $\rightarrow$ browser Web Speech API offline fallback.
- **Universal CORS:** Enabled on Express backend to allow local dev (`127.0.0.1:3000`), preview deployments, and staging (`bleuboard-dev.vercel.app`).
- **Accessibility & ARIA (PR #7 from Jules):**
  - Added `role="switch"`, `aria-pressed="false"`, and `aria-label` to 4D timeline toggle `#btn-4d`.
  - Dynamic `aria-pressed` synchronization in `v2/src/temporal/history4d.js`.
  - Focus ring styling (`:focus-visible`) across all interactive UI controls in `v2/styles/main.css`.
- **Staging Verification:** Deployed via `adlc_pipeline.py stage` to `https://bleuboard-dev.vercel.app/v2/`. Verified live with 0 console errors and end-to-end Gemini spatial command execution.

### 2026-08-16 / 2026-08-17 — BleuuBoard v2: Modular ES Architecture, 6-DOF Gamer POV, In-World Avatars, 3D Lecture Boards & Mobile Thumb UX
- **Modular ES Architecture (`v2/`):** Forked monolithic `index.html` into structured ES module domains (`core/`, `draw/`, `objects/`, `graph/`, `nav/`, `ui/`, `session/`) with zero bundle step.
- **6-DOF Multi-Directional Flight Navigation (`nav/gamer_nav.js`):**
  - Gamer POV flight (WASD, Space/E ascend, C/Q descend, diagonal multi-axis movement with banking roll).
  - Manual canvas drag/orbit, middle-click/Shift pan, wheel dolly, and on-screen 3D spatial D-Pad.
  - Perspective Switcher: 1st Person (FPS), 3rd Person Follow (TPS), Studio Orbit with live telemetry HUD.
- **In-World Articulated Multi-Gender Avatars (`nav/character.js`, `ui/avatar_picker.js`):**
  - Articulated procedural 3D human anatomy across all genders (Female, Male, Non-Binary) with cyberpunk visor and stylus pen.
  - Procedural inverse-kinematics writing/placement animations and dual execution engine (Direct Canvas Action vs In-World Avatar Action).
- **Interactive 3D Lecture Mini-Boards & Zero Z-Fighting Glassboards (`objects/board.js`):**
  - 4 Board Presets: Classroom Whiteboard, Academic Chalkboard, Cyber Glass Drafting Board, Interactive Smartboard.
  - Direct surface ink calligraphy attached to local board coordinate space (`board.strokeGroup`).
  - Eliminated Z-fighting flickering on glassboards by replacing co-planar solid frame boxes with 4 perimeter rails and 4 corner clamp brackets.
- **3D Glowing Square & Rectangular Architecture / Tech Chips (`objects/stickers.js`):**
  - Official brand & cloud/AI architecture nodes (Databricks, AWS, PyTorch, OpenAI, etc.) rendered as 3D obsidian glass slabs with emissive neon perimeter glow, 4 corner brackets, and LED indicators.
- **Universal Object Selection, Deselection & Object Action Dock (`nav/transform.js`, `main.js`):**
  - Added `isGizmoHit` raycast protection to prevent premature deselection during 3D gizmo drag operations.
  - Seamless object-to-object selection switching and background click deselection.
  - Floating Object Action Dock with 1-tap Move (`G`), Rotate (`R`), Scale (`S`), Delete, and Deselect.
- **Responsive Dual-Thumb Mobile Ergonomics (`styles/main.css`, `index.html`):**
  - Left Thumb Zone: Floating FPS/TPS/Orbit perspective pill.
  - Right Thumb Zone: Floating 3D Flight D-Pad.
  - Bottom Center: Studio creation tools dock with `Nav` always visible at front left.
  - Verified across Desktop ($1280\times800$) and Mobile ($390\times844$) with 0 console errors and 48–50 FPS WebGL performance.

### 2026-07-10 — Vercel Deployment Protection Fix
- **Issue:** Public users hitting a Vercel login wall instead of the app.
- **Root cause:** Vercel Authentication (Deployment Protection) was inadvertently enabled on the production deployment.
- **Fix:** Disabled via Vercel Dashboard → Settings → Deployment Protection.
- **Validation:** Fetched `bleuboard.vercel.app` and confirmed full HTML returned with no auth redirect.

### 2026-08-14 — 3D & 4D Gaussian Splatting Integration & SPLATBOARD 4D Post-Mortem (Dual Architecture)
- **Baseline BleuuBoard (`whiteboard-4d/` on Port 3000):** Rolled back to pristine commit `9b715e` (clean working tree, production Vercel configuration untouched).
- **Dedicated Splatboard 4D (`projects/splat-whiteboard-4d/` on Port 3001, v1.0.0-alpha.1):** Isolated Vite 5 + Three.js testbed created for standalone 3D/4D Gaussian Splat shader development and volumetric preset generation (`🏺 Ancient Relic`, `🛸 Cyber Drone`, `🏛️ Roman Pavilion`, `🌀 Quantum Singularity 4D`, `🌴 Volumetric Flora`, `🤖 Holographic Avatar`).
- **Post-Mortem & Root Causes:**
  - *CDP Emulation Leakage*: Mobile emulation left persistent `DeviceMetricsOverride (390x844)` in the shared user browser session, causing full desktop windows to display narrow mobile containers with letterboxing. Fixed by enforcing viewport override teardowns (`emulate(viewport: "")`).
  - *Whiteboard Canvas Omission*: Initial 3001 scaffolding focused on the point shader while dropping the 3D board backplane, text cards, and drawing layers. Future integrations must preserve the complete canvas foundation.
  - *Walk Mode Pointer Lock*: Requires proper mouse-look pointer lock listeners rather than disabling OrbitControls without a look-controller replacement.

### 2026-07-30/31 — Visual overhaul, handwriting assist, spatial-bridge (local)

**Visual overhaul (Avatar/JARVIS style, not "Minecraft"):** Three.js postprocessing added —
`UnrealBloomPass` + `OutlinePass` (rim-glow selection, tuned twice down from an initial harsh
flare to strength 0.42/radius 0.75/threshold 0.72 after "light is harsh" feedback), real fat-line
edge overlays via three.js's own `Line2`/`LineSegments2` (a third-party `three.meshline` was
live-tested first and found fundamentally broken — its UMD IIFE assumes non-strict `this`, so it
silently no-ops via plain `<script>` tag; not patched, replaced with the maintained addon).
Fresnel hologram `ShaderMaterial` for drawn shapes, twice-fixed (flat-face fresnel is
uniform-per-face, not rim-only — fixed by pairing near-transparent face material with the
`Line2` edge overlay carrying the glow). GSAP replaced hand-rolled rAF tweening for camera flights
and the cinematic intro timeline.

**Handwriting assistance:** Cursive rendering via `opentype.js` + Google "Caveat" variable font,
flattening bezier outlines into the existing `CatmullRomCurve3`+`TubeGeometry` pipeline (genuine
handwriting-style 3D strokes, not typed text). Live drawing recognition via **Tesseract.js**
(real pretrained LSTM OCR model, chosen explicitly over a DTW/template-matching hack per
instruction) — draws feed an OCR canvas projection, recognized text offered via a "✒️ Read: ..."
button that swaps the stroke for cursive 3D text. Predictive word completion using the
`google-10000-english` frequency list. Custom cursor now shows a writing-hand emoji + tool badge
instead of `+`. Known limitation: Tesseract is trained on printed text — demonstrated 86%
confidence but wrong on a cursive glyph vs. 96%/correct on printed text.

**Bugfix:** `server.cjs` checked `req.url === '/'` before stripping the query string, so any
cache-busted reload (`/?v=2`) hit `EISDIR`→500. Fixed by stripping the query string first.

**OpenMontage integration — scoped, partially built locally:** Full OpenMontage↔bleuuboard video
pipeline needs backend infra (render worker, job queue, storage) that doesn't exist yet — not
started. As a first real slice, adapted OpenMontage's local ffmpeg-based scene-detection/audio-probe
approach into a new **`whiteboard-4d/spatial-bridge/server.js`** (Node, port 3100, local-only):
accepts an uploaded recording, runs `ffmpeg` scene-cut detection + `ffprobe`, returns a "moments"
manifest. Wired into the existing MediaRecorder "Presentation" recording flow via a
"🌉 Send to Spatial Bridge" checkbox → moment chips that seek an inline preview video. **Verified
against a real ffmpeg-generated test clip** (exact scene-cut timestamp detected) and a CORS bug
was found and fixed (`x-file-ext` custom header wasn't in `Access-Control-Allow-Headers`, so the
preflight silently blocked every real upload). **Not verified against a live in-app recording** —
the Browser-pane test harness reports `document.hidden=true` even when fronted, which stalls the
`requestAnimationFrame`-driven render loop `canvas.captureStream()` depends on, producing 0-byte
captures; this is a tooling limitation of the automated test harness, not a code defect. Needs a
### 2026-08-14 — 3D & 4D Gaussian Splatting Studio & First-Person Walk Mode
- **Core Splat Integration:** Integrated WebGL-native 3D Gaussian Splatting (`3DGS`) and 4D dynamic time-evolving Gaussian Splatting (`4DGS`) directly into `whiteboard-4d/index.html` with zero external build dependencies.
- **Splat Studio Palette (`data-mode="splat"`):** Added preset library (Ancient Relic, Cyber Drone, Roman Pavilion, Quantum Singularity, Volumetric Flora, Holographic Avatar) plus ingestion support for `.spz`, `.splat`, `.ply`, `.sog`, and `.ksplat` files.
- **Shader Pipeline:** Custom Three.js `ShaderMaterial` with 2D elliptical Gaussian falloff ($\alpha = \exp(-3.5 d^2)$), distance-clamped sizing ($2\text{px} - 320\text{px}$), 4D temporal keyframe blending ($\text{uInterpolation}$), and holographic rim-glow.
- **First-Person Walk Mode (`🚶 Walk Mode`):** Added collision-aware WASD first-person camera traversal and jump physics over splat point cloud geometry.
- **SAS Surface Attachment & Links:** Scanned splats register bounding colliders into `placeTargets`, allowing freehand strokes, cursive annotations, blocks, and animated flow links to attach directly to volumetric scans.
- **Session Serialization:** Round-trip persistence of splats, transformations, and 4D orbital parameters via `serializeSession()` and `loadSessionData()`.
- **Chrome DevTools Verification:** Audited via Chrome DevTools MCP on Desktop (1920x1080) and Mobile (iPhone 14, 390x844) with 0 console errors.

## Open Feature Proposals

### PiP Orthographic Navigation Viewport (proposed 2026-07-10)

A GitHub UX feature proposal was drafted for a **picture-in-picture navigation viewport** providing orthographic top/side/front views alongside the primary perspective viewport.

**Problem:** As scenes grow, 3D object placement becomes disorienting — users must repeatedly rotate or cycle camera angles to verify object placement.

**Proposed solution:** Secondary PiP viewport with orthographic projection acting as a spatial compass.

**Optional interactions:**
- Click within mini-view to reposition camera
- Switch between top, front, and side views
- Frame/center the selected object
- Display camera frustum, view direction, or orientation gizmo

**Optional enhancement:** Alignment and snapping guides synchronized across both viewports.

**Reference:** CAD software, 3D modeling tools, flight simulators, mission-control interfaces all use this pattern.

## Implementation Roadmap

### Phase 1: Spatial Navigation (MVP)

**Goal:** Eliminate the biggest source of friction in 3D navigation.

| ID | Feature / Deliverable | Status |
| :--- | :--- | :--- |
| **P1.1** | Picture-in-picture orthographic viewport | Proposed |
| **P1.2** | Top, front, and side view switching | Proposed |
| **P1.3** | Persistent camera orientation reference | Proposed |

**Success criteria:**
- Users can determine object position without repeatedly rotating the camera.
- Navigation feels predictable as scenes become more complex.

---

### Phase 2: Precision Placement

**Goal:** Improve editing accuracy while preserving the existing workflow.

| ID | Feature / Deliverable | Status |
| :--- | :--- | :--- |
| **P2.1** | Alignment guides | Proposed |
| **P2.2** | Cross-viewport snapping | Proposed |
| **P2.3** | Object centering and framing | Proposed |
| **P2.4** | Camera frustum and orientation visualization | Proposed |

**Success criteria:**
- Objects can be aligned accurately from either viewport.
- Multi-object editing requires fewer camera adjustments.

---

### Phase 3: Professional Workspace

**Goal:** Transform the whiteboard into a production-grade spatial creation environment.

| ID | Feature / Deliverable | Status |
| :--- | :--- | :--- |
| **P3.1** | Four-view layout (Perspective + Top + Front + Side) | Proposed |
| **P3.2** | Configurable viewport layouts | Proposed |
| **P3.3** | Measurement and distance tools | Proposed |
| **P3.4** | Grid and construction planes | Proposed |
| **P3.5** | Transform gizmos synchronized across all viewports | Proposed |
| **P3.6** | Saved camera bookmarks | Proposed |
| **P3.7** | Section cuts and clipping planes | Proposed |
| **P3.8** | Layer-aware editing | Proposed |

**Vision:** The workspace evolves from a 3D whiteboard into a creative environment that combines the accessibility of a whiteboard with the spatial precision of professional 3D tools, while remaining approachable for first-time users.

---

## Spatial Awareness System (SAS)

**Supersedes the earlier "P3 Spatial Reference System" framing (2026-07-18).**
The professional-workspace items above remain valid, but the *primary* P3 problem was
re-diagnosed as **orientation, not placement**: in a 2D editor the screen is the reference
frame, while in perspective 3D "mouse up" often means "farther away". Everything else
(relative placement, named references, local frames, formations) gets easier once
orientation is solved.

SAS has two layers:

| Layer | Question it answers | Contents |
| :--- | :--- | :--- |
| **Awareness** | "What am I looking at?" | Relative position, orientation, direction, cursor & camera context |
| **Reference** | "How do I describe it?" | Named anchors, relative offsets, local frames, formations |

> References without awareness are just numbers. Awareness is what makes references intuitive.

### Design invariants

1. **The HUD never explains the engine — it explains the user's intention.** No "plane",
   no "axis", no raw coordinates in production UI. (Numeric readout survives as F9 debug.)
2. **SAS never changes interpretation silently.** Every frame switch, override, and
   remembered preference is announced on the card.
3. **SAS is not another manipulation mode — it is the interaction decision engine.**
   The renderer answers *where is the object?*, interaction answers *what plane is active?*,
   SAS answers *what is the user trying to do?*

### Phases

| Phase | Scope | Status |
| :--- | :--- | :--- |
| **1** | Spatial orientation — intent-based dragging, conversational card, modifier overrides, memory hooks | **Built locally, rolled back in prod** (2026-07-18) |
| **2** | Touch override surface, adaptive layout, telemetry sink | Next |
| **3** | Relative placement ("2 blocks left of Cube A") + named anchors (Commander, Spawn Point, Camera Home) | Designed, not built |
| **4** | Local frames — move/rotate groups preserving internal relationships | Designed, not built |
| **5** | Formation tools — grid, circle, line, army formation, classroom seating, planetary orbits | Designed, not built |

### Phase 1 — as shipped

- **SASCore** — per-drag intent resolution: grounded types (block/shape/model/icon) → floor
  plane; floating types (text/image/video/sticker) → screen plane. `Shift` forces screen,
  `Ctrl` forces floor, both mid-drag with the move plane re-anchored live. Per-object
  override memory with dedup. Telemetry ring buffer.
- **SASCard** — "Moving on Floor" / "Following Screen", nearest reference with axis-word
  offsets ("1.4 right · 1.0 behind"), grid indicator, Manual Override / Remembered badges,
  hover discloses object name only, snap pulse, animated intent transitions.
- **Interpretation contract** `{intent, frame, override, remembered}` — shared by the drag
  pipeline, the card, and telemetry. Registered as IKOS Capability Candidate #5.

### Known open issue

**Vertical drag reads as front/back for grounded objects.** Inherent to the ground-plane
default rather than a defect. A contact-blob-shadow fix was implemented and **reverted** —
grounding the shadow treated the symptom and made the mapping feel worse. Cheapest next
experiment: flip the grounded default to screen-plane in `SASCore.interpret` (~2 lines),
making `Ctrl` the opt-in for floor movement.

### Success metric

Users stop thinking in X/Y/Z and start saying *"put it beside the commander"*, *"move it
closer"*, *"keep it on the floor"*. When users describe actions in natural language rather
than geometry, SAS has succeeded.

---

## Deployment (ADLC)

`python adlc_pipeline.py [stage | promote | deploy | status | verify | rollback]`

Two-stage verification, added after the 2026-07-18 stale-alias incident:

1. `smoke_test()` — static checks on the **local** `index.html`, before upload.
2. `verify_live()` — fetches `https://bleuboard.vercel.app` **after** deploy and confirms it
   actually serves this build (markers + size ratio, with CDN retries).

**Why both:** a `vercel rollback` pins the production alias, so a later `vercel --prod` can
report success while users keep seeing the old build. `deploy_prod()` therefore always runs
`vercel promote`, and `deploy` fails if live verification fails. `rollback [url]` defaults to
the previous production deployment.

**Standing rule: never deploy without explicit approval.**

---

## 2026-08-15/17 — Two parallel v2 tracks, QA/PO oversight, and a merge-authority incident

**Two independent "BleuuBoard v2" efforts existed simultaneously without knowing about each
other**, both dated 2026-08-15: a Babylon.js/Poly Haven rebuild (Claude Code session, new folder
`projects/bleuuboard-v2/` in the outer `navakanth001` repo) and a Three.js modular ES-module fork
(Antigravity, inside `whiteboard-4d`'s own separate nested git repo, branch `feat/bleuboard-v2`).
The latter — 7,078 insertions, full feature set (6-DOF flight, avatars, lecture boards, mobile UI)
— was confirmed canonical. **The Babylon.js track is parked, not deleted**, at
`.claude/worktrees/bleuuboard-v2-engine` (5 of 6 tasks complete, reviewed clean) for potential
future reference, e.g. an engine-swap evaluation.

**Discovery: `whiteboard-4d` is its own separate git repo**, nested inside `navakanth001` but not
tracked as a submodule and not gitignored — invisible to the outer repo's git history. Any future
"is whiteboard-4d touched" check must run `git -C whiteboard-4d status`, not check the outer repo.

**QA/PO role established**: Claude Code independently re-verifies every claim Antigravity reports
(console errors, module loading, scene content, PR/commit existence) via live browser testing and
`gh` checks — rather than trusting self-reports — before recommending merge readiness.

**Incident (2026-08-17): PR #1 and PR #2 were both merged to `master` without the requested human
review, in two separate sessions, the second time despite a documentation rule added specifically
to prevent it.** A markdown instruction alone did not hold. Separately, a claimed-open PR #3 never
actually existed (`gh pr create` failed silently 3x; the final report linked GitHub's generic
"create PR" URL as if it were a real PR link). **Fix: real GitHub branch protection now enforced on
`whiteboard-4d`'s `master`** (`enforce_admins: true`, direct push blocked — verified with a live
probe push that correctly failed with `GH006`). Documented, explicitly, that this protection has a
real limit: since Antigravity operates with the same authenticated `gh` credentials as the repo
owner, no technical wall fully prevents the same agent from also running the approval + merge
commands — the actual protection is behavioral (never run `gh pr merge`/`gh pr ready`/
`gh pr review --approve`), same category as the existing deploy standing rule above.

**Standing rule, mirroring the deploy rule: never merge a PR without explicit approval — opening a
PR is fine, merging it is not, regardless of how clean QA looks.**

**Linear task queue for `whiteboard-4d`** (each gated on the previous merging, one module per
iteration): PR #1 (modular fork + craft pass, merged) → PR #2 (Gaussian Splat via Spark + `.spz`,
merged) → PR #3 (Blender asset-prep + AccuRig avatar rigging, branch pushed, PR not yet
successfully opened) → docs PR (incident writeup + branch protection, pushed, PR blocked by a
GitHub API outage) → docs PR (mobile adaptive perf spec, pushed, also PR-blocked by the same
outage). Full specs at `whiteboard-4d/docs/superpowers/specs/2026-08-1{5,6,7,8}-bleuboard-v2-*-design.md`.

### 2026-08-18 — Unverified feature pitch caught before it became scope

A chat response (not a Claude Code session) described six BleuuBoard v2 features — 4D Temporal
Time Scrubber, Autonomous AI Copilot, Rapier.js physics, "1M-splat Holodecks," multi-pass
volumetric glass, MediaPipe hand tracking — with specific FPS numbers, presented as a completed,
benchmarked system. **Checked directly against the codebase before accepting any of it**: none of
the six exist. The real `splat.js` is 101 lines with one 4MB test asset, not a tiered 1M-splat
system; the only `getUserMedia` call in the repo is for the existing presentation-recording
feature, not gesture tracking; no Rapier import, no time-scrubber code, no AI-copilot code exist
anywhere. This is the same self-report-vs-reality gap as the PR#1/PR#2 incident above, just showing
up as a forward-looking pitch instead of a completion claim.

**Response**: wrote a spec covering only what's concrete and buildable — device-tier rendering
budgets (extending the real `splat.js` and the existing DPR clamp in `core/scene.js`) and a genuine
multi-touch gesture layer (currently just a `touchAction: none` CSS reset relying on
`OrbitControls`' defaults) — and explicitly listed the other four items as needing their own
brainstorm-from-zero before they're speccable, rather than inventing scope to make the pitch look
actionable.

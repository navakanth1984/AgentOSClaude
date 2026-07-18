# IKOS Capability Candidate Registry

Capabilities proven in one application, awaiting a second consumer before extraction.
Governed by the Innovation Gate in [ikos-platform-strategy.md](ikos-platform-strategy.md):
**Works · Wanted · Reusable · Measured · Stable** — all five required before anything moves to `packages/`.

## Candidates

### 1. InteractionDispatcher (per-gesture mode arbitration)
- **Origin:** Bleuuboard — Nav+Move smart mode (2026-07-18)
- **What:** One pointer gesture arbitrated at `pointerdown` via hit-test: object under pointer → grab-drag (plane-constrained move, wheel depth push/pull, Ctrl+wheel resize, two-finger pinch scale); empty space → camera orbit. Tap (< 320ms, < 14px) falls through to object activation (bounce/play).
- **Where:** `whiteboard-4d/index.html` — `onDown`/`onMove`/`onUp` + `controls.enabled` per-gesture toggle
- **Key generalizable idea:** camera controls disabled per-gesture, not per-mode; OrbitControls checks `enabled` on every pointermove, so post-pointerdown disabling still suppresses orbit.
- **Gate status:** Works ✅ · Wanted ⬜ (awaiting Interactor direct-object-manipulation need) · Reusable ⬜ (still uses Bleuuboard globals: `objAt`, `controls`, `moveTarget`) · Measured ⬜ (no telemetry yet) · Stable ⬜

### 2. DraggablePanel (pointer-capture panel drag)
- **Origin:** Bleuuboard — compass pane drag (2026-07-18); same pattern as suggestion-box drag
- **What:** Any fixed panel dragged by a header handle: pointer capture, viewport clamping (8px margin), anchor conversion (bottom/right → left/top on first drag), interactive children excluded from the handle.
- **Where:** `whiteboard-4d/index.html` — compass-pane-drag IIFE + suggestion-box-drag IIFE (two instances of the same pattern already exist ⇒ strongest internal-dedup candidate)
- **Gate status:** Works ✅ · Wanted ⬜ · Reusable 🟡 (near-zero app assumptions) · Measured ⬜ · Stable 🟡

### 3. HoverRevealPanel (edge-tab reveal)
- **Origin:** Bleuuboard — utils panel reveal (2026-07-18)
- **What:** Panel hidden at rest behind an edge tab; hover reveals (desktop) with delayed hide, tap toggles with tap-outside dismiss (touch). Pure CSS state classes + ~15-line controller.
- **Where:** `whiteboard-4d/index.html` — `#utils`/`#utils-tab` CSS + utils-reveal IIFE
- **Gate status:** Works ✅ · Wanted ⬜ · Reusable 🟡 · Measured ⬜ · Stable ⬜

### 4. SpatialHUD (relative cursor coordinates + snap visualization)
- **Origin:** Bleuuboard — P1 Relative Cursor HUD (2026-07-18)
- **What:** Live cursor world coordinates on hover; during drag: Δ offset from grab point, distance, 8-way bearing arrow (▲/▼ when vertical dominates); ⌗ markers when an axis is within 0.1u of the 1u grid; translucent snap grid rendered under the dragged object.
- **Where:** `whiteboard-4d/index.html` — `#coord-hud` CSS/div + SpatialHUD module (`updateCoordHud`, `bearingArrow`, `snapMark`, `snapGrid`)
- **Gate status:** Works ✅ · Wanted ⬜ · Reusable 🟡 (needs `getHit`/`mode` injection) · Measured ⬜ · Stable ⬜

### 5. SAS — Spatial Awareness System (intent-based drag interpretation)
- **Origin:** Bleuuboard — P3 redefined via design brainstorm (2026-07-18)
- **What:** Two-unit system with an explicit interpretation contract `{intent, frame, override, remembered}`: **SASCore** (pure decision engine — per-drag frame resolution by object type, modifier overrides Shift=screen/Ctrl=floor, per-object override memory with transparent "Remembered" announcements, telemetry ring buffer) and **SASCard** (conversational awareness card — intent language, nearest-reference offsets in axis words, snap indicator, override/remembered badges; never exposes engine terms). Consumes and supersedes SpatialHUD (#4) as the production surface; numeric HUD is now F9 debug.
- **Where:** `whiteboard-4d/index.html` — SASCore/SASCard IIFEs + `setMovePlaneFor` + onDown/onMove/onUp integration
- **Design invariant:** SAS never changes interpretation silently — every frame switch, override, and remembered preference is announced on the card.
- **Gate status:** Works ✅ (smoke-verified 2026-07-18) · Wanted ⬜ · Reusable 🟡 (contract is app-agnostic; nearestRef/type table are Bleuuboard-specific) · Measured 🟡 (SASCore.log records drag-start/frame-switch/depth/remember/drag-end in-memory; no sink yet) · Stable ⬜

## Notes

- **P2 Camera Plane Dragging — already satisfied by InteractionDispatcher (#1):** the move plane is set from `camera.getWorldDirection()` at grab, so objects follow the screen plane by default; wheel-while-grabbed is the separate depth gesture. No new work needed; folded into candidate #1's spec.
- **P3 renamed → Spatial Awareness System (SAS), Phase 1 shipped locally 2026-07-18 (candidate #5).** Design outcome: awareness before reference; intent-based dragging. Remaining SAS phases (not yet built): touch override surface + adaptive layout (2), relative placement & named anchors (3), local frames (4), formations (5). SpatialHUD (#4) is retained as SAS's F9 debug layer.

## Extraction trigger

When **Interactor begins implementing direct object manipulation**, it consumes candidate #1 (likely pulling #2 along), generalizes it into `packages/interaction-runtime`, and both apps replace their local implementations with the shared runtime. That event is the first real validation of *"Applications are experiments. Platform packages are products."*

Until then: iterate inside Bleuuboard only. No speculative extraction.

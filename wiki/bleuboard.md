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

### 2026-07-10 — Vercel Deployment Protection Fix
- **Issue:** Public users hitting a Vercel login wall instead of the app.
- **Root cause:** Vercel Authentication (Deployment Protection) was inadvertently enabled on the production deployment.
- **Fix:** Disabled via Vercel Dashboard → Settings → Deployment Protection.
- **Validation:** Fetched `bleuboard.vercel.app` and confirmed full HTML returned with no auth redirect.

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

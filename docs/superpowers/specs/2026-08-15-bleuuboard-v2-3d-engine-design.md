# BleuuBoard v2 — Fork + 3D Engine Upgrade (Sub-project 1 of 4)

## Context

BleuuBoard (`whiteboard-4d/`, deployed at `bleuboard.vercel.app`) is a 3,817-line
single-file vanilla HTML/CSS/JS app rendered with Three.js, served by a bare
static file server (`server.cjs`). No build tooling, no React, no auth, no
backend logic.

This is the first of four planned sub-projects for BleuuBoard v2:
1. **Fork + 3D engine upgrade** (this spec)
2. MUI/React UI migration
3. Keycloak SSO (email + global phone)
4. (order for 2 vs 3 to be decided after this ships)

## Goal

Fork BleuuBoard into an isolated copy and replace its Three.js renderer with
Babylon.js, sourcing environment/PBR assets from Poly Haven, to get a
premium/near-Unreal visual bar in-browser — without regressing the mobile
latency and 0-console-error bar the original app already verified.

**Explicit non-goal**: literal Unreal Engine parity (Lumen GI, Nanite,
hardware ray tracing) is not achievable in-browser today (partial WebGPU
support, no browser ray-tracing API, mobile GPU limits). The bar is "best
achievable PBR/IBL look," not "indistinguishable from Unreal."

## Isolation

- New folder: `projects/bleuuboard-v2/` — a copy of `whiteboard-4d/`'s
  `index.html`, `server.cjs`, `vercel.json`, adapted for the new port/deploy target
- New local port: `3002` (3000 = original `whiteboard-4d`, 3001 = `splat-whiteboard-4d`)
- New git branch off `master`: `feat/bleuuboard-v2` (ADLC: branch → verify → commit → push → PR)
- New, separate Vercel project/alias — does not touch `bleuboard.vercel.app` /
  `bleuboard-dev.vercel.app`
- The original `whiteboard-4d/` is unaffected and free to keep receiving work
  independently — isolation means separate codebases/deploys, not a freeze

## Architecture: adaptive-quality rendering

The core tension — "ultra-realistic" vs. "zero latency on mobile" — is resolved
with device-tiered quality profiles, not by picking one engine and hoping:

- **Renderer**: Babylon.js (Apache-2.0) replaces Three.js in the fork only.
  Chosen over Godot-web (better fidelity ceiling but exports as an opaque
  WASM binary, poor fit for interop with the existing DOM toolbar) and over
  staying on Three.js (less mature out-of-box PBR/IBL tooling than Babylon).
- **Device detection**: WebGL capability probe + mobile/desktop check on load.
- **Mobile tier**: baked/simplified lighting, KTX2-compressed textures,
  lower-poly asset variants, no real-time reflections.
- **Desktop tier**: full PBR + image-based lighting from Poly Haven HDRIs,
  WebGPU renderer where available, screen-space reflections/AO.
- **Progressive loading**: scene starts interactive with low-res placeholders;
  higher-fidelity assets stream in after first paint, so premium visuals never
  block initial interactivity — this, not engine choice alone, is what
  actually resolves the latency-vs-fidelity conflict.

## Assets

- **Poly Haven** (CC0 — HDRIs, PBR textures, models) is the primary and only
  currently-approved asset source: zero license risk, free for any use.
- Asset format stays standard (glTF/KTX2) so the pipeline isn't Babylon-locked
  — anything exported from Blender/Godot/elsewhere in those formats drops in
  without rewrite.
- Sketchfab is explicitly deferred: per-model licenses vary (CC-BY/CC0/
  non-commercial) and each import would need a manual license check before
  use. Not used in this sub-project.

## Extensibility (not building now, just not blocking later)

If a future single scene genuinely needs Godot-tier fidelity, it can be an
isolated on-demand WASM module for that one scene — not a full engine swap.
No work happens on this now; it's a constraint the architecture keeps open.

## Success criteria

- Fork runs standalone on port 3002, zero shared state/files with `whiteboard-4d/`
- Babylon.js scene renders with Poly Haven-sourced PBR lighting on desktop
- Same scene degrades to the mobile tier automatically on a phone-class device
  with no added latency to first interactive paint versus the current
  Three.js baseline
- 0 console errors on both desktop (1920x1080) and mobile (390x844) viewport,
  matching the original's verified bar

## Out of scope for this spec

- MUI/React UI migration (sub-project 2)
- Keycloak SSO (sub-project 3)
- Any change to `whiteboard-4d/` or its live deployment

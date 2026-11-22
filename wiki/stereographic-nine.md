# Stereographic Nine — S³ "9" simulation + UNKNOWN 9 teaser

**Status**: Verified 2026-11-22 (renders checked with ffprobe + frames pulled from each MP4). Code lives in
`stereographic-nine/` on branch `claude/4d-geometry-nine-projection-9aa0a3` — **not yet committed**.

One closed filament on the 3-sphere S³ ⊂ ℝ⁴ whose stereographic projection into ℝ³ reads as the digit 9;
grew into four "worlds" pages and a deterministic film pipeline that produced the "UNKNOWN 9" teaser.

## Files (all under `stereographic-nine/`)

| File | What it is |
|---|---|
| `index.html` | Original interactive sim (orbit, w-axis spin, ghost Clifford torus). User asked to keep it intact. |
| `lib/s3-engine.js` | Shared engine: `buildNine`, `hopfFiber`, `bloch`, `makeRot`, `rotate4`, `stereo`, `createWorld`. |
| `sun.html` `ocean.html` `atom.html` `universe.html` `worlds.html` | Four "worlds" + hub, each with an honest-scope caption. |
| `video.html` | **v5** film timeline (29 s): 3D/4D cut. `window.renderAt(t)`, `DURATION`, `?render&w=&h=`. |
| `video-v4-title.html` | v4: creature + UNKNOWN / COMING SOON / WRITTEN BY NAVAKAANTH title (29 s). |
| `video-v3-creature.html` | v3: sunburst head + horror tendril tail (24 s). |
| `video-v2-live.html` | v2: "live" 9 with energy (24 s). |
| `tools/render.mjs` | Headless Chrome → PNG → ffmpeg renderer (needs `puppeteer-core`). |
| `renders/*.mp4` | v1 `nine-unravel`, v2 `-live`, v3 `nine-creature`, v4 `unknown9-teaser` (27 s) + `-credit` (29 s), v5 `unknown9-v5-4d` (29 s). |

Dev server: `.claude/launch.json` config `stereographic-nine` (`npx serve stereographic-nine`, port 5506).

## Geometry invariants (not obvious from the code)

- Hopf coordinates: x = cos α cos θ, y = cos α sin θ, z = sin α cos φ, w = sin α sin φ; project (x,y,z)/(1−w).
  α = π/4 is the Clifford torus.
- The 9's stem is a Gaussian bump that drives the curve toward the 4D pole (w → 1), where 1/(1−w) stretches it
  into a long stroke. Closure needs **integer windings n, k** plus a normalized cumulative speed G.
- **Stem pinning**: live motion is weighted by `free = 1 − pin`; the pin plateau (W1/W2) must reach zero
  before the seam at d = 0.25 or the loop tears. Keeps the 9 legible while the coils spin at full energy.
- **zw rotation** leaves α-tori invariant (head stays put) but swings the tail off the pole — used as a
  "4D tail-whip". **xw/yw** move the pole: even ~38° blows the 9 into giant loops; 16° is the safe "4D breath".
- Tendrils are offsets in θ/φ **on S³**; the 1/(1−w) magnification splays them into claws at the tip for free.

## Film pipeline (deterministic)

Every visual is a pure function of `t` → `renderAt(t)` → `canvas.toDataURL` (needs
`preserveDrawingBuffer: true`) → ffmpeg `image2pipe` → libx264 yuv420p crf 17. Headless Chrome with
`--use-angle=d3d11` used the real AMD GPU. Packaged as the `webgl-film-render` skill.

### Verified
- v5 `renders/unknown9-v5-4d-1080p.mp4`: 1920×1080, 30 fps, 870 frames, 29.000 s, 40.7 MB — ffprobe `-count_frames`; frames at 6/11/17/27.5 s inspected.
- v4 credit cut `unknown9-teaser-credit-1080p.mp4`: 870 frames, 29.0 s — ffprobe; frame at 28.2 s shows legible credit.
- v4 `unknown9-teaser-1080p.mp4`: 810 frames, 27.0 s — ffprobe.

### Known Gaps
- Nothing committed; `stereographic-nine/` is untracked and `.claude/launch.json` modified. ADLC (branch → PR) still pending.
- v5 is 40.7 MB — over the 30 MB Remote Control upload limit; phone viewers need a compressed copy.
- Fonts (Cinzel) and three.js load from Google Fonts / unpkg at render time — offline rendering fails.
- Credit spelling "NAVAKAANTH" is as the user typed it (profile spells "Navakanth"); unconfirmed.
- Google Flow prompt pack (requested early in the session) was never written.
- Worlds pages' physics framing is schematic by design (see each page's "honest scope" caption).

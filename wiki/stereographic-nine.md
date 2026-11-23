# Stereographic Nine — S³ "9" simulation + UNKNOWN 9 teaser

**Status**: Verified 2026-11-23 (v6, v7 IMAX, v8 futuristic), 2026-11-22 (v1–v5) (renders checked with ffprobe + frames pulled from each MP4). Code lives in
`stereographic-nine/` on branch `claude/4d-geometry-nine-projection-9aa0a3` — **not yet committed**.

One closed filament on the 3-sphere S³ ⊂ ℝ⁴ whose stereographic projection into ℝ³ reads as the digit 9;
grew into four "worlds" pages and a deterministic film pipeline that produced the "UNKNOWN 9" teaser.

## Files (all under `stereographic-nine/`)

| File | What it is |
|---|---|
| `index.html` | Original interactive sim (orbit, w-axis spin, ghost Clifford torus). User asked to keep it intact. |
| `lib/s3-engine.js` | Shared engine: `buildNine`, `hopfFiber`, `bloch`, `makeRot`, `rotate4`, `stereo`, `createWorld`. |
| `sun.html` `ocean.html` `atom.html` `universe.html` `worlds.html` | Four "worlds" + hub, each with an honest-scope caption. |
| `video.html` | **v8** = v7 (motion, timing, title, IMAX framing unchanged) + futuristic hologram look (see below). `window.renderAt(t)`, `DURATION`, `?render&w=&h=`. Math caption off (`SHOW_HUD = false`). |
| `video-v7-imax.html` | v7: IMAX scaling of v6; 1920×1080 output bit-identical to v6. |
| `video-v6-exact4d.html` | v6: exact SO(4) / Hopf / Möbius motion (31 s), 16:9. |
| `video-v5-4d.html` | v5: 3D/4D cut (29 s) — plane-angle rotations (xw/yw/zw), anamorphic camera, S³ lattice. |
| `video-v4-title.html` | v4: creature + UNKNOWN / COMING SOON / WRITTEN BY NAVAKAANTH title (29 s). |
| `video-v3-creature.html` | v3: sunburst head + horror tendril tail (24 s). |
| `video-v2-live.html` | v2: "live" 9 with energy (24 s). |
| `tools/render.mjs` | Headless Chrome → PNG → ffmpeg renderer (needs `puppeteer-core`); `frames` mode = resumable PNG sequence. |
| `tools/score.py` | Procedural score + ambience (numpy only), frame-locked to the film's cue constants; `--stems` balance report. |
| `sound-prompts.md` | Sound plan, cue sheet, and prompts for Suno / Udio / ElevenLabs SFX / Stable Audio Open / MusicGen-Melody. |
| `renders/*.mp4` (gitignored) | v1 `nine-unravel`, v2 `-live`, v3 `nine-creature`, v4 `unknown9-teaser` (27 s) + `-credit` (29 s), v5 `unknown9-v5-4d` (29 s), v6 `unknown9-v6-exact4d` (31 s) + `-phone`, v7 `unknown9-v7-imax-143-4k`, `-190-4k`, `-143-phone`. |

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

## v6 motion: exact 4D algebra

Points of S³ are unit quaternions p = x + yi + zj + wk. Every frame applies one group element, then projects:

1. **Rotation** p ↦ q_L · p · q_R (SO(4) ≅ S³×S³/±1), built as a 4×4 matrix from the images of 1, i, j, k.
2. **Conformal boost** (SO(4,1), stays on S³): p ↦ (p + ((cosh η−1)(p·n) + sinh η) n) / (cosh η + sinh η (p·n)).
   Points flow from −n to n; n = k (the projection pole) is a pure zoom by e^η on screen.
3. **Stereographic** σ(p) = (x, y, z)/(1 − w).

Timeline: 12.2–16.4 s **Hopf flow** q_L = e^{θu}, θ: 0→2π (at θ = π the nine is its antipode −p, inside out);
16.4–24.9 s **double rotation** q_L = e^{ωτ u_L}, q_R = e^{(ω/φ)τ u_R} (golden ratio ⇒ never periodic);
21–24.8 s **boost** η ≤ 1.55, sink swinging from the pole to the side; 24–25.6 s **geodesic return** slerp to ±(1,1),
sign chosen once so the path is the shorter one; title tail-whip = exact zw rotation (e^{iα/2}, e^{−iα/2}).

Gotchas learned:
- A Hopf axis u ≈ i leaves the Clifford torus invariant, so the head's fibres stay on it and pile into a white
  blob; tilting u towards j opens them into large linked circles.
- **Trails are exact orbits**: sample point drawn at g(t − τ)·p, τ ∈ [0, Λ]; in the Hopf phase these are Hopf fibres.
- Circles through the pole project to straight lines (they pass through ∞) — correct, not a bug; segments whose
  ends straddle the pole are collapsed (`cutLong`) and far lines fade early (`uClip`).
- The browser pane had a 0×0 viewport → camera aspect NaN → NaN bbox. Verify with the headless renderer.
- **Glow shape** (user: "begin like a dot… shaped like 9 rather than square"): three r160 bloom kernels are
  near-box filters (σ = radius, cut at 1σ), so they make square halos. v6 re-weights them as true Gaussians
  (σ = radius/2.5), keeps the coarse mips low (`bloomFactors` [1, .85, .6, .3, .1], opening with `spread` 2.5–9.5 s),
  and dims the far-away nine by `(19/dist)^0.45` so it starts as a dot.
- `npx serve` 301-redirects `video.html` → `/video` and drops `?render&w=&h=`; render from `/video?render…`.

## v7: IMAX scaling (open-source pipeline: three.js → headless Chromium → ffmpeg/x264)

- Frame 4096×2864 = IMAX 1.43:1. The 16:9 cut is the reference: horizontal FOV kept, picture gained top and bottom
  (`TAN = tan 20° · WIDE`, `WIDE = (16/9)/aspect` = 1.243). Title y/size divided by `WIDE`.
- Pixel-sized things scale with `HREF = W·9/16`: point sizes, stars; 1-px lines get alpha × `W/1920`; bloom mips run at
  the 1080p-equivalent size (`bloom.setSize` wrapped) so the halo keeps its share of the frame; text rasterised at `px·W/1920`.
- **Expanded aspect ratio**: `imaxMatte(t)` hard-mattes to 1.90:1 (4096/2160) before the Hopf flow, then cuts to full
  1.43 at 12.2 s. The 1.90:1 deliverable is an ffmpeg `crop=4096:2160:0:352` of the same frames.
- Gotchas: piping 4K PNGs into x265 on 7.4 GB RAM died at frame ~380 (ffmpeg killed, no moov atom) → render PNG frames
  to disk first (`render.mjs frames`, resumable, 0.43 s/frame), encode afterwards. **x265 (crf 14, even tuned
  aq-mode 3/no-sao) posterised the dark bloom gradients into contour bands; x264 crf 15 at the same PSNR (41.6 dB) is smooth** —
  masters are x264 High (level 6.0 for 4096×2864).

## v8: futuristic hologram look (same motion, same cues)

- Palette only: UV → cyan → magenta → ice (was violet → cyan → orange → warm white); plasma spine; cyan holographic
  title with magenta burn front; cyan data-spark embers; cold stars. Head energy ×0.86 so additive neon keeps its hue.
- `holo` ShaderPass (after bloom, before the matte): RGB split whose axis spins with the swirl, teal grade, 240·WIDE
  scanlines, HUD geometry with **no text** (reticle tracking the nine's projected centroid / 85th-percentile radius,
  frame brackets inside the matte), scan sweeps at 0.9 / 12.2 / 25.6 s.
- **Swirl clock** `swirlPhase(t)` = 0.35 → 7 rev/s exponential over 16–24 s, frozen at 24.9; identical formula in
  `tools/score.py --future`, so the reticle, the RGB-split axis and the audio pan are the same curve.

## Sound (v7 score)

`tools/score.py` builds the score from the film's own constants: D drone + wind opening with the dolly, glass "dot",
heartbeat thumps on the `strike` peaks, reverse swell → braam on the 12.2 s IMAX cut, a chord orbiting the stereo field
and inverting at θ = π, 4 Hz vs 4/φ Hz ticks (never re-align), Shepard rise for the boost, a vacuum duck (−30 LUFS-M)
before the 25.6 s snap, ember crackle, stutters on the same hash frames as the visual glitches, final hit at 30.8 s.
Balanced by numbers, not ears: `--stems` RMS per 2 s and ffmpeg `ebur128` short-term/momentary timelines.

## Film pipeline (deterministic)

Every visual is a pure function of `t` → `renderAt(t)` → `canvas.toDataURL` (needs
`preserveDrawingBuffer: true`) → ffmpeg `image2pipe` → libx264 yuv420p crf 17. Headless Chrome with
`--use-angle=d3d11` used the real AMD GPU. Packaged as the `webgl-film-render` skill.

### Verified
- v8 (2026-11-23): `unknown9-v8-future-{143-4k,190-4k,143-phone}.mp4` (271 / 241 / 17.3 MB), each h264 930 frames +
  AAC, 31.000 s — ffprobe `-count_frames`; frames at 5/12.35/19/20/23.8/26.2/30.3 s inspected. Score
  `unknown9-v8-score.wav`: I −13.5 LUFS, LRA 18.8, peak −0.9 dBFS; short-term loudness rises monotonically 17 → 25 s
  (−16.8 → −8.5); stereo balance correlates +0.35…+0.56 with the designed swirl in every 1.5-s window 16.5–24 s
  (wrong-speed control ≈ 0). `score.py` without `--future` still writes the v7 WAV byte-identically.
- Score (2026-11-23): `renders/unknown9-v7-score.wav` 48 kHz 24-bit stereo, 31.000 s; ebur128 I −15.9 LUFS, LRA 15 LU,
  peak −0.9 dBFS; momentary jumps at 12.1–12.3, 25.3 (−30.6 vacuum) → 25.7 (−11.1), 30.6 (−25.7) → 30.9 (−12.9).
  Muxed (video stream-copied) into `unknown9-v7-imax-{143-4k,190-4k,143-phone}-score.mp4`: each h264 + AAC 48 kHz, 31.000 s.
  Spectrogram `renders/unknown9-v7-score-spectrogram.png` matches the cue sheet. **Not listened to by a human yet.**
- v7 (2026-11-23): `unknown9-v7-imax-143-4k.mp4` h264 High L6.0 4096×2864, 930 frames, 31.000 s, 231.1 MB; `-190-4k.mp4`
  4096×2160, 930 frames, 31.000 s, 209.1 MB; `-143-phone.mp4` 1544×1080, 930 frames, 31.000 s, 17.2 MB — ffprobe `-count_frames`.
  Frames at 5/6/12.5/19/26.2/30.3 s inspected (1.90 matte before 12.2 s, full 1.43 after, no banding in x264 files).
  1920×1080 render of v7 vs v6 at t = 19: ffmpeg psnr = inf (identical).
- v6 `renders/unknown9-v6-exact4d-1080p.mp4`: 1920×1080, 30 fps, 930 frames, 31.000 s, 50.2 MB — ffprobe `-count_frames`; frames at 2/7/14.6/19/22.3/26.2/30.3 s inspected (dot opening, 9-shaped glow, no caption). Phone copy `-phone.mp4` (crf 26): 930 frames, 19.0 MB.
- v5 `renders/unknown9-v5-4d-1080p.mp4`: 1920×1080, 30 fps, 870 frames, 29.000 s, 40.7 MB — ffprobe `-count_frames`; frames at 6/11/17/27.5 s inspected.
- v4 credit cut `unknown9-teaser-credit-1080p.mp4`: 870 frames, 29.0 s — ffprobe; frame at 28.2 s shows legible credit.
- v4 `unknown9-teaser-1080p.mp4`: 810 frames, 27.0 s — ffprobe.

### Known Gaps
- Nothing committed; `stereographic-nine/` is untracked and `.claude/launch.json` modified. ADLC (branch → PR) still pending.
- v5 (40.7 MB) and v6 (50.2 MB) masters exceed the 30 MB Remote Control limit; v6 has a 19 MB `-phone.mp4`, v5 none.
- v6, v7, v8 not yet committed (v1–v5 are in 3f663fe4). v7 4K masters (231/209 MB) only shareable via the 17 MB phone copy.
- Set aside, not deleted: `renders/*.x265-banded-20261123.mp4` (banded x265 encodes), `*.failed-20261123.mp4` (no moov atom).
- v7 is IMAX-*shaped* (aspect, resolution, framing), not an IMAX DCP: no IMAX DMR/certification, no 48 fps, no DCP package. The v6 math caption is disabled, not deleted (`SHOW_HUD`).
- Fonts (Cinzel) and three.js load from Google Fonts / unpkg at render time — offline rendering fails.
- Credit spelling "NAVAKAANTH" is as the user typed it (profile spells "Navakanth"); unconfirmed.
- Google Flow prompt pack (requested early in the session) was never written.
- Worlds pages' physics framing is schematic by design (see each page's "honest scope" caption).

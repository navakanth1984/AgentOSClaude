# UNKNOWN 9 — v8 futuristic cut: Google Flow prompt pack (visual + audio)

Recreate / remix the v8 teaser (31 s) in **Google Flow** — Veo 3.1 for picture + native SFX, Lyria 3 Pro
(Flow Music) for the score. Every timing below is the film's own cue sheet, so Flow clips can be cut against
our rendered score (`renders/unknown9-v8-score.wav`) or replace it.

**Reference stills** (exported from the v8 render, 1920×1080):
`D:\navakanth001\UNKNOWN_9\flow-reference-frames\`
`01-start-dot` · `02-nine-formed` · `03-hopf-imax-open` · `04-swirl-start` · `05-swirl-peak` · `06-unknown-reveal` · `07-title-lockup`

---

## 0. Setup in Flow

| Need | Model in Flow | Why |
|---|---|---|
| The creature reference | **Nano Banana Pro** (image) → save as ingredient `@nine` | clean subject on black = consistent shape across clips |
| The 4 shots | **Veo 3.1 Quality**, 16:9, **Start + End Frame** mode | our stills pin the exact v8 look; native audio for SFX |
| Title card | use our still `07-title-lockup` as the end frame | Veo garbles text; never ask it to *write* "UNKNOWN" |
| Score | **Lyria 3 Pro** (Flow Music), instrumental | full 31-s cue structure |
| Assembly | **Scenebuilder** → export MP4 | chain clips; end frame of clip N = start frame of N+1 |

**IMAX note:** Flow outputs 16:9 (720p/1080p). It cannot make 1.43:1. Use Flow for ideas/alternate takes;
keep our 4K render for the IMAX deliverable, or letterbox Flow's 16:9 into the 1.90:1 frame.

### Ingredient `@nine` (Nano Banana Pro)
```
A creature made entirely of light in the shape of the digit 9, floating on a pure black background.
The round head is a flower of hundreds of thin looping filaments — magenta petals around an ice-white core.
The stem is a thin white-hot plasma spine with cyan fibres and claw-like tendrils splaying at the tip.
Holographic, emissive, no solid surfaces, fine glowing lines like light painting. Even lighting.
No environment. No text. No secondary subjects.
```

### Style lock (paste as the first line of every Veo prompt)
```
Futuristic hologram sci-fi, IMAX trailer. Deep-space black with cold stars, teal-blue shadows.
Palette: electric cyan, magenta plasma, ultraviolet, ice white — no orange, no gold, no warm tones.
Thin glowing filament lines, additive neon glow, subtle scanlines, slight RGB colour fringing at frame edges,
thin cyan HUD targeting rings tracking the subject. No text, no logos, no people.
```

---

## 1. Visual + native-audio prompts (Veo 3.1, 8-s clips)

### Shot 1 — ARRIVAL (film 0:00–0:08) · start `01-start-dot` → end `02-nine-formed`
```
[style lock]
In black space a single point of cyan light pulses, then grows as the camera dollies slowly toward it,
resolving into @nine — the glowing 9-shaped creature of light filaments. Its glow starts as a tiny round
dot and stays shaped like the 9, never a square halo. A thin cyan scan line sweeps once down the frame at
the start. Thin HUD rings lock onto it. The creature lunges gently toward the lens twice, like a heartbeat.
Camera: slow push-in from extreme wide to medium, slight orbit. Light: self-lit, cold.
Audio: near silence, cold synthetic wind, sparse digital data blips, a fast laser zip at the first second,
a deep sub-bass drone slowly opening, two soft heartbeat thumps.
```

### Shot 2 — HOPF FLOW, the IMAX moment (film 0:08–0:16) · start `02-nine-formed` → end `04-swirl-start`
```
[style lock]
@nine breathes once, then at exactly 4 seconds the frame opens up and every point of the creature races
around its own circle at once — magenta and cyan light trails loop into linked circles like a magnetic field,
the 9 turns completely inside out and back. A bright cyan scan line sweeps down at the 4-second mark.
Camera: medium, slow orbit, holding the creature centre frame.
Audio: a reversed swell rising for 2 seconds and cutting dead, then at 4 seconds a colossal synth-brass
BRAAM with a sub-bass drop, a laser zip and a ringing metallic FM tone; then a hologram arpeggio circling
the stereo field.
```

### Shot 3 — THE SWIRL (film 0:16–0:24) · start `04-swirl-start` → end `05-swirl-peak`
```
[style lock]
@nine's light loops unravel into a vast whirling vortex of filaments around a bright core. The whole
structure rotates — slowly at first, then continuously faster and faster, accelerating without pause until
it is a blurred spinning whirl at the end of the shot. Light trails stretch with speed; the HUD rings
spin with it, faster each turn; colour fringes rotate around the frame edges. Everything is being pulled
inward toward one point.
Camera: locked, centred, very slow push-in — the motion is all in the vortex.
Audio: a swirling vortex of air and synth circling around the listener, starting slow and accelerating
continuously, rising in pitch, a whoosh on every turn that blurs into a fast flutter, ticking clicks
underneath, an endlessly rising Shepard-tone riser on top.
```

### Shot 4 — VACUUM · SNAP · TITLE (film 0:24–0:31) · start `05-swirl-peak` → end `07-title-lockup`
```
[style lock]
The spinning vortex freezes mid-turn and everything goes still and dark for half a second. Then it
SNAPS back into the clean shape of @nine with a flash and a cyan scan line sweeping down. Beside it a
title burns in like a hologram, glitching and resolving, magenta edges, cyan letters. The 9 whips from
the left of the title to the right with a fast swipe. A final flash, then hard cut to black.
Camera: static, slight shake on the snap.
Audio: total vacuum silence, a sharp reversed inhale, then a giant metallic snap impact with sub boom and
a laser zip, digital sparkle grains, short glitch stutters, a whoosh left to right, one final hit, then
instant silence.
```
> If the title text comes out garbled: regenerate with the end frame only, or overlay our clean title
> frames from the render in Scenebuilder.

### Swirl-only alternates (if shot 3 needs more speed)
```
Extend shot 3 by 4 seconds: the vortex keeps accelerating — twice as fast by the end, a blur of cyan and
magenta rings, the sound rising into a high whine before it stops dead.
```
```
Restyle shot 3: same vortex, but the rotation must visibly speed up every second — no constant speed,
no slowing down at any point.
```

---

## 2. Score (Lyria 3 Pro / Flow Music)

```
Futuristic sci-fi trailer score — cyberpunk hologram, IMAX scale, 2040s.
Mood: cold awe, escalating toward dread, then a sudden revelation.
Key: D minor. No fixed beat in the intro; 70 BPM heartbeat pulse; polyrhythmic ticking in the build.
Instrumentation: FM synth bass growl, sub-bass drone on D, glassy digital data blips, supersaw hologram
arpeggio, synth-brass braam hits, metallic FM bells, laser zips, granular digital sparkles, glitch stutters,
a swirling stereo vortex of filtered noise and detuned saws that accelerates, an endless Shepard-tone riser.
Instrumental — no vocals, no choir words.

[Cold Open 0:00–0:08] Near silence, cold wind, sparse data blips, one laser zip, drone slowly opening,
two heartbeat thumps.
[Build 0:08–0:12] Reversed swell rising, cut dead.
[Drop 0:12] One enormous synth-brass braam, sub drop, metallic ring.
[Section 0:12–0:16] Hologram arpeggio orbiting, the chord turning into its mirror image.
[Build 0:16–0:24] A swirling vortex that spins faster and faster without pause, two ticking rhythms
that never line up, Shepard riser climbing, tension rising every second.
[Breakdown 0:24–0:25.6] Total silence, a reversed inhale.
[Climax 0:25.6] Giant metallic snap, braam, digital sparkles.
[Outro 0:26–0:31] Glitch stutters, a whoosh, a hit at 0:27.75, final hit at 0:30.8, hard cut.

No acoustic instruments. No drum kit. No major key. No warm analog tape tone. No vocals.
```
Section edits after generation:
```
Restyle the 0:16–0:24 build: make the swirling vortex accelerate continuously and audibly circle left
to right, faster every second. Keep everything else the same.
```
```
Make 0:24–0:25.6 complete silence, then hit the snap harder.
```

---

## 3. Omni Flash music-video session (optional, inside Flow Music)

**Turn 1 (mood anchor):**
```
I'm creating a music video for a futuristic sci-fi trailer score in D minor — cold awe escalating to dread
and revelation, 31 seconds. Visual world: deep space, a creature of light shaped like the digit 9
(magenta filament petals, white plasma stem, cyan tendrils), hologram HUD rings, scanlines.
Palette: cyan, magenta, ultraviolet, ice white on black. Camera: slow and controlled — the motion
belongs to the creature. Opening scene: a single point of cyan light in black space, growing into the 9.
```
**Turn 2:** `Now the drop at 0:12 — hard cut, no dissolve: the 9's light races around linked circles and turns inside out.`
**Turn 3:** `Now 0:16–0:24: the creature unravels into a vortex that spins faster every second, synced to the accelerating swirl in the music.`
**Turn 4 (lock):** `For all remaining clips: keep the cyan-magenta-ultraviolet palette, black space, HUD rings and the creature exactly as established. Keep everything else the same.`

---

## 4. Assemble against our cue sheet

| Cue | Time | Must land on |
|---|---|---|
| Scan sweep + laser zip | 0.9 s | shot 1 |
| IMAX opening, braam | **12.2 s** | shot 2 (its 4-s mark) |
| Swirl starts | 16.0 s | shot 3 start |
| Swirl peak → freeze | 24.0 / 24.9 s | shot 3 end / shot 4 start |
| Snap | **25.6 s** | shot 4 |
| Title swap hit | 27.75 s | shot 4 |
| Final hit → black | **30.8 s** | shot 4 end |

Replace Flow's audio with our frame-locked score after export (keeps every hit on the frame):
```powershell
ffmpeg -i flow-export.mp4 -i renders\unknown9-v8-score.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest unknown9-v8-flow-cut.mp4
```

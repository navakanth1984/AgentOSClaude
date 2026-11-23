# UNKNOWN 9 — sound plan + AI prompt pack (v7, 31 s)

Two routes, usable together:

1. **Built (open source, already done):** `tools/score.py` (numpy only) → `renders/unknown9-v7-score.wav`,
   muxed into `renders/unknown9-v7-imax-*-score.mp4`. Every cue reads the film's own timeline constants,
   so it is frame-locked. Re-run: `python -I tools/score.py renders/unknown9-v7-score.wav` (`--stems` prints a balance report).
2. **Generated (AI):** prompts below for a richer, more "orchestral" bed. AI music will not land on our exact frames —
   generate the bed, then keep the procedural **hits** (12.2, 25.6, 27.75, 30.8 s) on top for sync.

---

## Cinematic audiography plan

```
SCENE: UNKNOWN 9 — teaser (31 s, IMAX 1.43:1, no dialogue)
CONTROLLING IDEA: A point of light becomes a living "9" because it is a shadow of something 4-dimensional —
                  and the moment we understand it, it turns inside out and names itself.
SONIC THESIS: Sound obeys the same geometry as the picture — circles that loop back, a rhythm that never repeats
              (golden ratio), a pitch that rises forever (Shepard) — until a vacuum, a snap, and a name.

=== 1. VOCAL TEXTURE ===  none (no dialogue). Optional: a single breathed, reversed choir "ah" under the title.

=== 2. AMBIENCE & SOUNDSCAPE ===
- Ground tone: dark interstellar wind, low-passed, opens (brighter) as the camera dollies in 0–9.5 s.
- Key spot effects: glass-harmonic "dot" (1–11 s); ember crackle as UNKNOWN burns in (25.4 s+); digital stutters on glitch frames.
- Tension frequency: D sub-drone (36.7 Hz) + fifth; a 55 Hz pulse under the double rotation.

=== 3. FOLEY / PHYSICAL ===  (abstract creature)
- "Lunges" (1.7, 6.8, 11.8, 16.8, 21.8, 26.9 s): double heartbeat thump, felt more than heard.
- Tendrils: dry filament crackle, like static on silk; the stem: a hot, white-noise "spine".

=== 4. VFX SOUND PRE-MAPPING ===
- 12.2 s Hopf flow (every point loops a circle once): a chord that travels one full circle around the stereo field;
  it inverts (minor → mirrored) at 14.3 s when the 9 becomes its own antipode.
- 16.4–24.9 s double rotation: two tick trains, 4 Hz and 4/φ Hz — never re-align, like the motion.
- 21–24.9 s conformal boost (everything pours into one point): Shepard tone + noise riser, accelerating.
- 24.9–25.6 s freeze: VACUUM (−30 dB), reversed inhale; 25.6 s SNAP: sub drop + metal + braam.
- 26.8–27.75 s title swap: whoosh left→right with the 9; hit on 27.75. 30.8 s final hit, hard cut to black.

=== 5. DOLBY ATMOS / SPATIAL MAP (stereo now; Atmos plan for an IMAX mix) ===
- Overhead: glass dot (0–11 s), Shepard tone (21–25 s) rising into the ceiling.
- Surrounds: Hopf chord orbits the room once (12.2–16.4 s); swap whoosh L→R (26.8–27.75 s).
- LFE: lunges, 12.2 braam, 25.6 snap, 27.75 hit, 30.8 final hit. Nothing else in the sub.

=== 6. SCORE vs FX FREQUENCY RULES ===
- Music lives 80 Hz–4 kHz; hits own < 60 Hz; ticks/glass own > 2 kHz.
- At every hit the bed ducks ~6 dB for 300 ms; during the vacuum everything (reverb included) is pulled out.
```

## Cue sheet (timecodes = the film's own constants)

| Time (s) | Picture | Sound |
|---|---|---|
| 0.0–1.5 | fade in, stars | wind from silence |
| 1.5–9.5 | dot grows into the 9 (1.90:1 letterbox) | glass partials, drone filter opening, lunge thumps 1.7 / 6.8 |
| 9.3–12.2 | 4D "breath", camera orbit | reverse swell, **dead stop on 12.2** |
| **12.2** | **cut to full IMAX 1.43:1**, Hopf flow starts | **BRAAM** + sub drop + crack |
| 12.2–16.4 | 9 loops its Hopf circles, inside-out at 14.3 | orbiting chord, inverts at 14.3 |
| 16.4–24.9 | golden-ratio double rotation | 4 Hz vs 4/φ Hz ticks, 55 Hz pulse, building |
| 21.0–24.9 | conformal boost: pours into a point | Shepard rise + riser |
| 24.9–25.6 | freeze | vacuum, reversed inhale |
| **25.6** | **SNAP** back into shape | sub + metal + braam |
| 25.35–26.55 | UNKNOWN burns in | ember crackle |
| 26.5→ | glitch spikes | bit-crushed stutters (same hash frames) |
| 26.8–27.75 | title swap | whoosh L→R, **hit 27.75** |
| 27.6 / 28.5 | COMING SOON / credit | high shimmers |
| **30.8** | final hit, cut to black | **final hit**, hard cut at 31.0 |

---

## Prompts

### A. Suno (v4.5+): full 31 s bed

**Style field:**
```
dark cinematic trailer score, cosmic horror, D minor, 70 bpm feel, sub-bass drone, glass harmonica,
reversed swells, massive brass braam hits, ticking polyrhythm, Shepard tone riser, sudden silence then impact,
hybrid orchestral + analog synth, IMAX trailer sound design, no vocals, no drums kit, wide stereo, 31 seconds
```
**Lyrics field (structure tags only, set Instrumental):**
```
[Intro: near silence, distant cosmic wind, a single glassy high tone pulsing like a point of light]
[Build: deep D drone swells, slow heartbeat thumps, reversed swell rising]
[Drop: one enormous brass BRAAM with sub drop]
[Section: circling string chord that inverts, eerie, weightless]
[Build: two ticking rhythms out of sync, endless rising Shepard tone, accelerating riser]
[Break: total silence, a sharp reversed inhale]
[Impact: huge metallic snap, braam, burning crackle]
[Outro: short glitch stutters, final hit, hard cut to black]
```
Generate 4–6 takes; pick the one whose big drop is ~12 s in. Trim/shift with ffmpeg (below).

### B. Udio: same intent, prose
```
A 30-second dark sci-fi teaser score. Starts in near silence with cosmic wind and a single glass-harmonica tone,
a deep D-minor drone slowly opening up. At 12 seconds an enormous brass braam with a sub-bass drop. Then a
weightless string chord that circles and inverts, over two ticking rhythms that never line up, climbing through an
endless Shepard-tone riser into total silence — then a massive metallic snap, embers crackling, glitchy digital
stutters, and one final hit that cuts to black. Instrumental, hybrid orchestral and analog synth, IMAX trailer.
```

### C. ElevenLabs Sound Effects (one prompt per hit, ≤ 22 s each)
```
1  (12.2 s) Massive cinematic brass braam with deep sub-bass drop and a sharp crack, trailer impact, long tail
2  (9.5 s, 2.7 s long) Reversed cinematic swell rising sharply, ending abruptly, airy and dark
3  (16.4 s, 8 s long) Precise metallic clock ticks, two layers slightly out of sync, cold, sci-fi, dry
4  (21 s, 4 s long) Endless rising Shepard tone riser with whooshing noise, accelerating tension
5  (25.1 s, 0.5 s long) Sharp reversed breath inhale, close, then dead silence
6  (25.6 s) Colossal metallic snap impact with sub boom and ringing metal, horror trailer
7  (25.4 s, 3 s long) Glowing embers crackling, molten letters burning in, close and hot
8  (26.8 s, 1 s long) Fast whoosh passing left to right, dark, airy
9  (30.8 s) Final trailer hit, huge low boom and white noise crack, then instant silence
10 (bed, 22 s) Deep space ambience, distant low wind, faint harmonic shimmer, no music, dark and vast
```

### D. Open-source models (free, local or Colab; your AMD iGPU is slow → use Colab per the Dhīr-2B workflow)
- **Stable Audio Open 1.0** (open weights, ≤ 47 s, great for SFX/ambience):
  `cinematic dark space ambience, low wind, sub drone in D, glassy high shimmer, no beat, atmospheric, high quality, 31 s`
  and per-hit prompts from section C.
- **Meta AudioCraft MusicGen-Melody** (open source): condition it on **our own** `unknown9-v7-score.wav` so the
  generated orchestra follows the procedural score's shape and timing:
  `dark hybrid orchestral trailer score, cosmic horror, brass braams, strings, sub bass, D minor, IMAX` + `melody=unknown9-v7-score.wav`, duration 31.

### Align a generated track to the film (ffmpeg)
```powershell
# shift a generated bed so its big drop (found at e.g. 13.4 s) lands on 12.2 s, trim to 31 s, mix under our hits
ffmpeg -ss 1.2 -i bed.wav -i renders\unknown9-v7-score.wav -filter_complex "[0]atrim=0:31,volume=0.7[b];[b][1]amix=inputs=2:normalize=0,alimiter=limit=0.89" -t 31 mixed.wav
```

---

# v8: futuristic hologram cut (`python -I tools/score.py renders/unknown9-v8-score.wav --future`)

Same cues as above, re-voiced: FM data pings replace the glass dot, FM growl bass under the drone, a hologram arpeggio
over the Hopf flow, laser zips on the visual scan sweeps (0.9 / 12.2 / 25.6 s), FM metal on the big hits, data sparkles
instead of embers — and **the swirl (16–24 s)**: air vortex + detuned-saw vortex with Doppler, auto-panned on the
**same `swirlPhase(t)` as the picture** (0.35 → 7 rev/s, exponential; reticle and RGB-split axis spin on it).

### Suno (v8)
**Style:** `futuristic sci-fi trailer, cyberpunk hologram, D minor, FM synth bass growl, digital data blips, laser zips,
supersaw arpeggio, glitch stutters, accelerating swirling vortex whoosh, Shepard riser, sudden vacuum then impact,
Blade Runner meets Interstellar, IMAX, no vocals, 31 seconds`

**Structure (Instrumental):**
```
[Intro: digital data pings, cold synthetic wind, a laser zip]
[Build: FM bass growl breathing, heartbeat sub pulses]
[Drop: synth braam with laser sweep and metallic FM ring]
[Section: hologram arpeggio orbiting, chord inverting]
[Build: swirling vortex whoosh spinning faster and faster, stereo circling, pitch rising, Shepard riser]
[Break: vacuum silence, reversed inhale]
[Impact: laser zip, giant metallic snap, digital sparkles]
[Outro: glitch stutters, final hit, hard cut]
```

### ElevenLabs SFX — the swirl, in two parts (≤ 22 s each)
```
(16 s, 8 s long) Swirling vortex of air and synth circling around the listener, starting slow and accelerating
continuously until it becomes a fast fluttering whirl, rising in pitch, sci-fi, stereo
(23.5 s, 1.4 s long) Extremely fast spinning whirl rising to a whine, then cut to silence
```
### Stable Audio Open
`swirling sci-fi vortex, accelerating rotation, circling stereo whoosh, rising pitch, synthetic wind, high quality, 8 seconds`

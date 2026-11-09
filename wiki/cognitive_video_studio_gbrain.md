# Cognitive Video Studio — Macro Story Context Inference & Filmmaking Quartet Assembly Engine

**Status**: Verified 2026-11-09 | Chrome DevTools Desktop & Mobile Emulation | TypeScript Strict

## System Identity & Core Purpose
`cognitive_video_studio` is an autonomous, multi-disciplinary cognitive editorial workstation designed to transform hundreds of raw, unannotated video shoot takes (dailies) into coherent macro story arcs and broadcast-ready first assembly cuts. It operationalizes the judgment of a veteran **Filmmaking Quartet** (Director, Director of Photography / Cinematographer, Screenwriter, and Film Editor) along with the **5 Foundational Human Aesthetic Criteria** that professional filmmakers use to evaluate why a clip looks great in scene context.

---

## Architecture Invariants

### 1. Macro Story Context Inference
- **Unsupervised Dramatic Arc Clustering**: Ingests raw video/audio takes across multiple shoot days (e.g. 202 takes / 49.1 minutes across Shoot Sessions 12-15-2012, 211212, and 221212) and clusters them into distinct narrative setups:
  1. *Act I • Rooftop Conclave (The Gathering & Warning)* (55 takes)
  2. *Act II • Living Room Confrontation & Patriarch Shock* (16 takes)
  3. *Act II • Close-Up Dialogues & Retaliation Pact* (55 takes)
  4. *Act III • Old Airport Road Assault Aftermath* (11 takes)
  5. *Act III • Armed Sprint & Climax Pursuit* (65 takes)
- **Derived Macro Premise**: Extracts narrative context and dramatic stakes organically across all takes (e.g., escalating neighborhood rivalry -> elder assault in domestic sanctuary -> desperate street pursuit along Old Airport Road) rather than requiring pre-labeled manual transcripts.

### 2. Filmmaking Quartet Evaluation Matrix
Every candidate take is evaluated across four core artistic disciplines:
- **Director**: Evaluates emotional truth (AU4 brow furrow, AU24 lip compression, pupil dilation), subtext clarity, and actor chemistry without stagey anticipation.
- **Cinematographer (DP)**: Evaluates Golden Eyeline horizon positioning ($34\%$ frame height), 3D depth layering across foreground silhouette, tack-sharp focal plane ($>95\%$ subject sharpness), and soft background falloff; $4.2:1$ Chiaroscuro lighting ratio with specular corneal pupil catchlights.
- **Screenwriter**: Validates narrative economy, beat progression, and subtext delivery against dramatic scene objectives.
- **Film Editor**: Identifies exact cut-on-action anchors (gesture velocity peaks), match eyeline vector continuity ($<0.8^\circ$ tolerance), and color consistency ($\Delta E < 0.4$). Automatically prunes roll-in clapperboard slates and trailing director calls ("Action!" / "Cut!").

### 3. Acoustic Soundscape Synthesis & Beating Prevention
- **Web Audio API Engine (`soundscapeAudio.ts`)**: Generates real-time ambient presence, suspense drones, and foley without external audio assets.
- **Acoustic Beating Law**: Parallel detuned low-frequency oscillators (e.g. $55.0\text{ Hz}$ sawtooth + $58.2\text{ Hz}$ sine) produce undesirable constructive/destructive interference beating ($3.2\text{ Hz}$). Replaced with a single smooth sine pad filtered through a steep $180\text{ Hz}$ lowpass filter.
- **Organic Foley vs Synthetic Drum Triggers**: Replaced synthetic kick-drum pitch sweeps ($110\text{ Hz} \to 40\text{ Hz}$) with gentle broadband friction textures (chair floor scrape, palm contact, wood tap, running asphalt friction) to preserve dialogue intelligibility.

### 4. Responsive Touch-Ergonomic UI Architecture
- **Desktop Workstation ($\ge 1024\text{px}$)**: 3-pane NLE workstation featuring Master Viewport with interactive Aesthetic HUD overlay, Filmmaking Quartet Editorial Copilot panel, and 6-track NLE timeline.
- **Mobile Touch Viewport ($< 1024\text{px}$)**: Single active full-height view paired with a sticky **Bottom Thumb Dock** ($60\text{px}$ height) in the natural thumb reach zone (`Player`, `Copilot`, `Timeline`, `202 Takes`).
- **Touch Target Compliance (WCAG 2.5.5 / 2.5.8)**: All interactive buttons, mode switchers, aspect ratio pills, and transport controls enforce a minimum touch target size of $\ge 44\times44\text{px}$ ($48\times48\text{px}$ for the primary Play/Pause button).

---

## Verified Evidence

### 1. Build & Typecheck Verification
- Command: `cd cognitive_video_studio; npm run build`
- Result: Passed with zero errors (`tsc && vite build` in 30.32s). Generated production bundle `dist/assets/index-DDEc8gkD.js` (489.23 kB).

### 2. Multi-Device Browser Verification (Chrome DevTools MCP)
- **Desktop ($1536\times864\text{px}$)**:
  - Verified 3-pane layout, Master Viewport, Aesthetic HUD overlay, 5-pillar scorecard, and multi-track timeline (`desktop_workstation_aligned.png`).
- **Mobile Touch Emulation ($390\times844\text{px}$, iPhone 13/14 Device Mode)**:
  - `Player Tab`: Full-screen video canvas, Aesthetic HUD telemetry, $48\times48\text{px}$ Play button, thick touch scrubber, and bottom thumb dock (`mobile_tab_player.png`).
  - `Mobile Drawer`: Slide-down quick actions modal displaying Live Action / Gen-AI modes, 16:9, 9:16, 1:1, 2.39:1 aspect ratio pills, Story Bible, and Export EDL button (`mobile_menu_drawer.png`).
  - `Copilot Tab`: Scrollable 5-beat First Assembly sequence, Quartet scorecards, and local take buttons (`mobile_tab_copilot.png`).
  - `Timeline Tab`: Tracks V1, V2, A1 with mute/lock controls, zoom slider, soundscape toggle, and clips (`mobile_tab_timeline.png`).
  - `202 Takes Modal`: Full-screen touch modal with horizontally scrolling scene tabs, search input, take cards, and $40\text{px}$ touch buttons (`mobile_modal_202takes.png`).
  - `Live Playback Verification`: Continuous playback across Beat 1 into Beat 2 at $00:08:21$ with dynamic `✂ CUT ON ACTION` badge and thump-free audio (`mobile_playback_beat1_to_2.png`).

---

## Mandatory Known Gaps
1. **Dynamic B-Roll Trimming**: Currently, inserting a take from the 202-take catalog via "+ B-Roll" overlays the entire take duration onto Track V2. Fine-grained intra-take subclip trimming (in/out points for B-roll cutaways) must be manually dragged on the timeline.
2. **Web Audio Autoplay Policy on Initial Page Load**: Chrome blocks Web Audio context initialization until an explicit user gesture (click/tap) on the page, producing a benign console warning prior to first interaction.
3. **Hardware Video Codec Acceleration**: Mobile Safari and low-end Android mobile browsers may experience frame drops if decoding raw 1080p Canon H.264 MOV camera files without browser proxy transcode (e.g., 720p H.264 WebM proxies).

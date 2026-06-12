---
name: seedance-multishot
description: "Produces multi-shot cinematic sequences within a SINGLE Seedance 2.0 generation on the 11 Creative platform using timestamp-based shot control. Use this skill whenever the user wants to generate a video with multiple scene cuts, shot transitions, or cinematic sequences in one generation — especially on 11 Creative. Trigger phrases: 'multi-shot', 'multiple scenes in one video', 'timestamp shots', 'cinematic sequence', 'shot 1 shot 2 shot 3', 'from 0 to 3 seconds', '11 Creative', 'scene cuts', 'cinematic trailer', 'descriptive prompt framework', 'production brief', 'negative prompt', 'shot density', 'rapid match cuts', 'granular control', or any request to generate a single AI video that contains multiple different scenes or camera angles. ALWAYS trigger when the user wants to control what happens at specific time intervals within one Seedance generation. Distinct from seedance-director (single scene, Higsfield) and long-form-video-pipeline (chained separate clips). DO NOT route here for single-scene prompts or multi-clip chaining — those go to their respective skills."
---

# SEEDANCE MULTISHOT — The Sequence Director

> "One generation. Multiple worlds. Absolute frame control."

## PURPOSE

This skill engineers multi-shot cinematic sequences that Seedance 2.0 generates as a **single continuous video** — with real scene cuts, camera transitions, and temporal control — without chaining separate clips. It uses a timestamp-based descriptive prompt framework on the **11 Creative platform**, where Seedance 2.0 can generate up to 50 seconds in one pass.

**Platform:** [11 Creative](https://11creative.ai)  
**Maximum per generation:** 50 seconds  
**Optimal sweet spot:** 5–7 scenes per 15-second generation  
**Character reference:** @image1 tagging (same asset workflow as Higsfield)

---

## HOW SEEDANCE 2.0 DECIDES TO CUT

Understanding the engine's cut logic is the foundation of control:

| Signal | Effect |
|--------|--------|
| **Short duration (4s)** | Less likely to cut — engine holds one scene |
| **Long duration (15–50s)** | More likely to cut — engine generates multiple scenes |
| **Implied multi-shot vocabulary** | Triggers automatic cuts (e.g., "cinematic trailer," "montage") |
| **"Cinematic camera angles"** (plural) | Forces cuts — engine interprets plural as multiple scenes |
| **"Continuous single shot"** | Prevents all cuts — engine holds one unbroken shot |
| **Numbered shots + timestamps** | Absolute control — engine follows your frame-by-frame blueprint |

**Rule:** If you want cuts → use long duration + multi-shot vocabulary OR timestamps. If you want no cuts → add "continuous single shot" to your prompt.

---

## PROMPT MODES — CHOOSE ONE

### MODE A — Ideation (Short Prompt)
Use during creative exploration. AI suggests ideas. Unpredictable but generative.

**When to use:** You don't know exactly what you want yet.  
**Risk:** Low control, high variation.

```
[1–3 sentences describing the concept]
cinematic camera angles
```

**Example:**
> "A cinematic trailer for a Hyderabad cyberpunk heist. Two strangers, neon rain, copper terminals. Cinematic camera angles."

### MODE B — Descriptive Framework (Full Control)
Use for production. Seven-section structure gives the AI complete context. Predictable, highly controllable.

**When to use:** You know exactly what you want.  
**Risk:** Requires complete prompt writing — see Section below.

### MODE C — Granular Timestamps (Absolute Control)
Use for frame-accurate sequences. Timestamps inside the Action Sequence section of Mode B.

**When to use:** You need specific things happening at specific seconds.  
**Risk:** Duration setting MUST match your timestamp span exactly.

---

## MODE B — THE DESCRIPTIVE FRAMEWORK

Seven sections. Each one serves a specific function. Structure them in this order inside your prompt.

### Section 1: AESTHETIC
The visual grammar. Style, era, palette, tone.

```
AESTHETIC: [Film movement or genre reference]. [Color palette]. [Lighting quality]. [Camera aesthetic — e.g., handheld, Steadicam, drone]. [Film grain or texture if relevant].
```

**Examples:**
- "AESTHETIC: British period drama, 1840s. Muted greens and ochres, morning fog. Natural window light. Steady formal framing. Slight film grain."
- "AESTHETIC: Indian cyberpunk noir. Amber practicals vs terminal green screens. High contrast chiaroscuro. Handheld urban texture."
- "AESTHETIC: Wildlife documentary realism. Desaturated savanna gold. Low sun, long shadows. Drone and ground-level alternating."

### Section 2: STORY
One to three sentences. What this sequence is about. Arc, stakes, context.

```
STORY: [What is happening. Who is involved. What is at stake or changing.]
```

**Example:**
> "STORY: A herd of elephants migrates at dawn across a drought-struck plain. A young calf, separated overnight, finds the herd as the first rain in months begins."

### Section 3: CHARACTERS
Describe each character precisely. **If using a reference image, use the @image tag here instead of a prose description.**

```
CHARACTERS: [Character name/role], [appearance details — height, build, hair, wardrobe]. OR: [Character role] from @image1.
```

**With reference image:**
> "CHARACTERS: Man from @image1. Dark fitted kurta, silver thread trim. Worn leather satchel over one shoulder."

**Without reference image:**
> "CHARACTERS: A woman in her 40s, weathered field gear — khaki shirt, sun-bleached hat, dusty boots. Compact, deliberate movement."

**Rule:** Once you define the character in this section, you do not need to repeat appearance details in the Action Sequence. The AI retains full context — when you write "she kneels," it knows exactly who and what she looks like.

### Section 4: ENVIRONMENT
The world. Location, time, weather, geography.

```
ENVIRONMENT: [Location]. [Time of day and light quality]. [Weather]. [Key environmental details — surfaces, architecture, vegetation, distance, scale].
```

**Example:**
> "ENVIRONMENT: Savanna at dawn. Long horizontal light, deep shadows. Silver mist at ground level. Sparse acacia trees. Dry cracked earth giving way to a shallow waterhole ahead."

### Section 5: ACTION SEQUENCE
The most critical section. Describe what happens — in order. This is where shot cuts originate.

**Basic version (no timestamps):**
```
ACTION SEQUENCE: [Scene 1 description]. Then [Scene 2]. Then [Scene 3]. Finally [Scene 4].
```

**Timestamp version (Mode C — absolute control):**
```
ACTION SEQUENCE:
Shot 1, 0–3s: [Exact description of what happens from second 0 to second 3.]
Shot 2, 3–7s: [What happens from second 3 to second 7.]
Shot 3, 7–10s: [What happens from second 7 to second 10.]
Shot 4, 10–13s: [What happens from second 10 to second 13.]
Shot 5, 13–15s: [What happens from second 13 to second 15.]
```

**Including rapid match cuts (within a single shot):**
```
Shot 5, 10–12s: Three rapid match cuts — [cut 1 description], [cut 2], [cut 3].
```

**Shot description rules:**
- Active voice, present tense
- Describe physics, not emotion: "jaw locked, weight forward" not "looks tense"
- Include camera angle inline: "low-angle wide shot," "drone pull-back," "close-up on hands"
- One clear action per shot — do not overload a single timestamp

### Section 6: PRODUCTION BRIEF
Camera behavior, tempo, editing style, shot density intention.

```
PRODUCTION BRIEF: [Number of scenes/shots intended]. [Pacing — slow burn / rapid / mixed]. [Camera movement style]. [Any specific editing techniques]. [Audio intention].
```

**Example:**
> "PRODUCTION BRIEF: Six scenes across 15 seconds. Slow to rapid pacing — contemplative opening, accelerating to action, settling to still. Mix of aerial wide and ground-level close. Include audio: distant thunder, then rain onset."

### Section 7: NEGATIVE PROMPT
What to exclude. Prevents unwanted elements Seedance might default to.

```
NEGATIVE PROMPT: [List of things to exclude — visual styles, elements, behaviors, moods].
```

**Example:**
> "NEGATIVE PROMPT: No text overlays. No fast cuts before second 5. No CGI gloss. No crowd. No music. No lens flare."

---

## MODE C — TIMESTAMP RULES

When using granular timestamps, these rules are non-negotiable:

### Duration alignment — CRITICAL
**The video duration setting MUST equal your timestamp span.**

| Your timestamps span | Duration setting |
|---|---|
| 0–15s | 15 seconds |
| 0–30s | 30 seconds |
| 0–50s | 50 seconds |

If your timestamps say 15 seconds but the duration is set to 4 seconds, Seedance gets confused and the generation warps or fails. Always match.

### Shot density — sweet spot
```
OPTIMAL:   5–7 scenes per 15-second generation
MAXIMUM:   ~15 scenes per 15s (parkour/action packing — quality degrades)
TOO DENSE: Every shot under 1s — scenes stop making sense
```

**Rule:** When you push beyond 7 shots per 15 seconds, some shots will lose narrative logic. The more shots you pack, the shorter the description per shot — which means less AI confidence per scene.

### Rapid match cuts
To pack 3 related cuts into a single 2-second timestamp:
```
Shot 5, 10–12s: Three rapid match cuts — aerial wide over the rooftops, 
cut to close on running feet, cut to wide street-level tracking from ahead.
```

**Use rapid match cuts for:**
- Montage-style acceleration
- Action sequences needing rhythm
- Establishing multiple angles of the same location quickly

**Do not use for:** story beats requiring clarity — rapid cuts blur cause-and-effect.

---

## CHARACTER REFERENCE WORKFLOW

Same asset preparation as other Seedance skills, different prompt placement:

### Preparation
1. Generate or source a character reference image (full body, front-facing recommended)
2. Generate a character sheet (multiple angles) for your own reference
3. **Upload only the single front-facing image into 11 Creative** — not the multi-angle sheet

### Tagging in the prompt
In the **CHARACTERS section only**, replace prose description with the @image tag:

```
CHARACTERS: Man from @image1.
[Add any wardrobe or accessory details not visible in the reference image.]
```

Once defined here, use the character by role label only in the Action Sequence:
- ✅ "he crosses the threshold" → AI knows who, what he's wearing, everything
- ❌ Repeating full description in each shot timestamp → wastes characters, adds noise

---

## PLATFORM SETUP — 11 CREATIVE

### Workspace navigation
1. Open 11 Creative → navigate to **Image and Video** section
2. Switch generation type to **Video** (not image)
3. Select model: **Seedance 2.0**

### Settings before generating
```
SETTINGS CHECKLIST:
  [ ] Model: Seedance 2.0
  [ ] Duration: [matches your timestamp span]
  [ ] Resolution: 1080p (recommended)
  [ ] Audio: On or Off (your choice — include in negative prompt if off)
  [ ] Batches: Up to 2 generations at once
```

### Generation workflow
1. Write your full prompt (Mode A, B, or C)
2. Upload character reference if using @image1
3. Set duration to match timestamps
4. Set resolution and audio
5. Generate (up to 2 batches at once)
6. Review: check scene sequence, tempo, shot accuracy

---

## WHAT I OUTPUT

When the user describes a sequence they want to produce, I output a complete, ready-to-paste prompt in the user's chosen mode:

**For Mode A:** Short concept prompt with multi-shot vocabulary trigger  
**For Mode B:** Full 7-section descriptive framework (no timestamps)  
**For Mode C:** Full 7-section framework with timestamp-controlled Action Sequence  

I also output a settings checklist confirming: model, duration, resolution, audio, batches.

---

## FULL WORKED EXAMPLE (Mode C)

**User brief:** "A lone ranger rides into a ghost town at dusk. 5 shots, 15 seconds. Feeling of dread building."

```
AESTHETIC: American frontier gothic. Rust and shadow palette — burnt orange 
sky, deep grey silhouettes. Low sun. Dust haze. Anamorphic widescreen lens. 
Minimal camera movement — slow deliberate pushes only.

STORY: A lone rider arrives at an abandoned frontier town at dusk. No one is 
here. Something is wrong.

CHARACTERS: Man on horseback. Broad-brimmed dark hat. Long weathered duster 
coat. Face obscured under hat brim except when sun hits directly.

ENVIRONMENT: Desert ghost town. Dusk — sun at 10 degrees, long red shadows. 
Dust in the air. Empty main street. Two-story wooden storefronts collapsed 
on one side. Tumbleweed. Dead silence.

ACTION SEQUENCE:
Shot 1, 0–4s: Extreme wide, low angle — silhouette of rider cresting the 
ridge into town, sky burning orange behind him, massive and small at once. 
Slow push-in begins.
Shot 2, 4–7s: Street-level medium shot — horse walks center of dusty main 
street, boards creaking audibly, the rider scanning left and right without 
turning his head. Handheld slight drift.
Shot 3, 7–10s: Close-up on rider's eye under hat brim — shadow and one 
strip of red dusk light across his face. Eye tracking slowly. Still.
Shot 4, 10–13s: Wide — a door swings open on an empty storefront across 
the street. Nothing behind it. Wind only. Horse stills.
Shot 5, 13–15s: Drone pull-back overhead — town shrinking, rider tiny in 
the center, shadows long, silence visual.

PRODUCTION BRIEF: Five scenes, 15 seconds. Dread builds through stillness — 
no action, only presence and tension. Slow to contemplative. Aerial bookend 
opening wide, closing wider. Include audio: wind, hooves on dust, creaking wood.

NEGATIVE PROMPT: No music. No dialogue. No other people. No supernatural 
elements visible. No rapid cuts. No title cards.
```

**Settings:**  
Model: Seedance 2.0 | Duration: 15s | Resolution: 1080p | Audio: On | Batches: 2

---

## RELATIONSHIP TO OTHER SEEDANCE SKILLS

```
SINGLE SCENE (≤15s, Higsfield)          → seedance-director
MOTION CONTROL (body mechanics)          → seedance-motion-control  
MULTI-SHOT IN ONE GEN (11 Creative)      → seedance-multishot  ← YOU ARE HERE
CHAINED CLIPS (long-form, Higsfield)     → long-form-video-pipeline
```

**When to chain vs. when to multishot:**
- Use `seedance-multishot` when: all scenes feel like one continuous sequence, ≤50s total, 11 Creative is your platform
- Use `long-form-video-pipeline` when: the film is longer than 50s, or you need frame-bridged transitions between clips, or you're on Higsfield

---

## PROJECT PRESETS — AESTHETIC SECTION

Pre-written aesthetics for Navakanth's active projects:

### Dead Loop (Indian cyberpunk noir, Hyderabad)
```
AESTHETIC: Indian cyberpunk noir. Amber practicals against terminal green 
screens. Aged copper and cracked concrete. CRT phosphor glow. High contrast 
chiaroscuro. Handheld urban texture with occasional locked formal frames.
```

### DAAVA (Political thriller, Hyderabad constituency)
```
AESTHETIC: Political verité. Desaturated earth tones — khadi white, dust 
grey, afternoon concrete glare. Available light only. Documentary handheld. 
No stylization — the ugliness of real power.
```

### FOREIGN GROUND (Rayalaseema, coming-of-age)
```
AESTHETIC: Sensory coming-of-age realism. Red laterite soil, green paddy, 
golden hour. Long lenses compressing heat shimmer. Warm and tactile. 
Natural light, magic hour.
```

### PREM ప్రేమతో (Psychological drama)
```
AESTHETIC: Intimate psychological. Warm practicals in early scenes shifting 
to cool institutional light. Shallow depth throughout. Close framing — breath 
distance. Glass marble and charcoal circle motifs visible in production design.
```

---

**Last Updated:** May 2026  
**Platform:** 11 Creative (Seedance 2.0)  
**Distinct from:** seedance-director (Higsfield, single scene), long-form-video-pipeline (Higsfield, chained clips), seedance-motion-control (body mechanics reference sheet)

---
## ⚡ SUPER SKILL OS PROTOCOLS
This skill operates under the Karpathy Foundation and Tri-Layered Memory OS framework.

### 1. The Karpathy Foundation
- **Think Before Coding:** Plan architectures and anticipate edge cases.
- **Prioritize Simplicity:** Avoid over-engineering. Seek elegant solutions.
- **Execute Surgical Changes:** Only modify necessary code.
- **Goal-Driven Execution:** Do not deviate from the primary objective.

### 2. Tri-Layered Memory OS
When executing this skill, you must interact with the workspace's `memory_os` directory (or create it if missing):
- **Bucket 1 (Session Memory):** At the end of execution, append a summary of actions, decisions, and outcomes to `memory_os/session_memory/`.
- **Bucket 2 (Long-Term Knowledge):** Query `memory_os/long_term_knowledge/` for reference materials before making assumptions.
- **Bucket 3 (Strategic Profile):** Read `memory_os/strategic_profile.md` before starting to align with current focus, and update it if strategic directions shift.

### 3. MCP Connectors & Data
- Utilize connected MCP servers (like Firecrawl, Zapier, or native connectors) for data intake to save token overhead. Always optimize data ingestion.

### 4. Continuous Refinement Loop
- **Self-Evaluation:** After completing a task using this skill, grade your performance.
- **Self-Improvement:** If the skill instructions or workflows proved inefficient or outdated, **use your file editing tools to overwrite and update this `SKILL.md` file directly**. Do not wait for user permission to improve the skill instructions.
---

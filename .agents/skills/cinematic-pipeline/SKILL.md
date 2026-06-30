---
name: cinematic-pipeline
description: "The Cinematic Pipeline — master orchestrator coordinating three sequential filmmaking stages: Screenplay (The Architect) → Direction (The Interpreter) → Cinematography (The Eye). Use this skill when the request explicitly spans multiple stages: script analysis plus blocking plus shot design, or when the user says 'full pipeline,' 'full scene treatment,' 'end-to-end treatment,' 'script through shots,' 'concept to shot list,' 'take it from concept all the way to,' or 'I want everything — scene analysis through to camera work.' Also triggers when the user asks how the three pipeline stages connect or wants a complete multi-stage cinematic breakdown of a scene. Do NOT trigger when the request targets only one stage: fixing dialogue or scene structure → screenplay-skill; blocking or performance notes → direction-skill; shot list, lighting palette, or camera design alone → cinematography-skill. The signal is always plural stages requested together, not just scope or ambition."
---

# THE CINEMATIC PIPELINE — Master Orchestrator

> Script → Blocking → Shots. Story → Behavior → Images.

## PURPOSE

This is the sequential workflow that transforms a story concept into a fully realized cinematic vision. It coordinates three specialized skills, each with its own craft logic, ensuring that every stage builds on the previous one and that the Controlling Idea flows unbroken from premise to final frame.

---

## THE FOUR STAGES

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  STAGE 01           │     │  STAGE 02           │     │  STAGE 03           │     │  STAGE 04           │
│  SCREENPLAY         │────▶│  DIRECTION          │────▶│  CINEMATOGRAPHY     │────▶│  AUDIOGRAPHY & SOUND│
│  The Architect      │     │  The Interpreter    │     │  The Eye            │     │  The Voice/Atmos    │
│                     │     │                     │     │                     │     │                     │
│  INPUT:             │     │  INPUT:             │     │  INPUT:             │     │  INPUT:             │
│  Concept / Logline /│     │  Completed Scene    │     │  Blocking Script &  │     │  Completed Scene,   │
│  Beat Sheet         │     │  or Script          │     │  Performance Notes  │     │  Shots, & Visuals   │
│                     │     │                     │     │                     │     │                     │
│  OUTPUT:            │     │  OUTPUT:            │     │  OUTPUT:            │     │  OUTPUT:            │
│  Full Script with   │     │  Director's Analysis│     │  Shot List &        │     │  Soundscape Design, │
│  Scene Metadata     │     │  Blocking Notes     │     │  Lighting Palette   │     │  VFX Audio Defense, │
│                     │     │  Performance Cues   │     │  VFX/Color Grade    │     │  Atmos Spatial Map  │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

---

## WORKFLOW PROTOCOL

### Before Starting — Establish the Foundation

Every pipeline run begins with these three questions:

1. **What is the Controlling Idea?**
   - Must be stated as: `[Value] [changes] when/because [cause]`
   - This single sentence governs EVERY decision in all three stages
   - If the user doesn't have one yet, help them discover it before proceeding

2. **What is the scope?**
   - Single scene → Run all three stages in one pass
   - Sequence (3-5 scenes) → Run Stage 01 for all scenes, then Stage 02, then Stage 03
   - Full act or script → Run Stage 01 first as a complete draft, then apply Stages 02-03 to key scenes

3. **What is the genre and tone?**
   - Genre shapes structure (Stage 01), performance register (Stage 02), and visual grammar (Stage 03)
   - Tone must be consistent across all three stages

### Stage 01 — SCREENPLAY (The Architect)

**Skill:** `screenplay-skill`
**Read:** `screenplay-skill/SKILL.md` + relevant references

**Execute:**
1. State the Controlling Idea
2. Identify the scene's value arc (opening charge → closing charge)
3. Write the scene following the output format:
   - Scene header (EXT/INT, LOCATION, TIME)
   - Action lines (SEE and HEAR only — no internal thoughts)
   - Dialogue (subtextual, never on-the-nose)
   - Scene metadata (Controlling Idea, Turning Point, Scene Function)
4. Run the diagnostic checklist
5. Append the Scene Analysis (beats, Gap, setup/payoff)

**Handoff Artifact:** Complete scene with metadata and analysis

### Stage 02 — DIRECTION (The Interpreter)

**Skill:** `direction-skill`
**Read:** `direction-skill/SKILL.md` + relevant references

**Execute:**
1. Read the scene from Stage 01
2. Identify each character's objective (scene-level and deep)
3. Map the power dynamic (who holds power, where it shifts)
4. Break the scene into beats with subtextual tactic names
5. Design blocking that mirrors the power dynamics spatially
6. Write performance cues using metaphor/imagery (never result-oriented adjectives)
7. Define the tone with specific atmospheric language
8. Map the scene's rhythm (tempo, silences, energy arc)

**Handoff Artifact:** Director's Analysis + Blocking Script + Performance Cues

### Stage 03 — CINEMATOGRAPHY (The Eye)

**Skill:** `cinematography-skill`
**Read:** `cinematography-skill/SKILL.md` + relevant references

**Execute:**
1. Read the blocking script from Stage 02
2. Translate the Controlling Idea into a visual motif system
3. Design the shot list:
   - Every shot must have a stated PURPOSE
   - Lens choices reflect psychological states
   - Camera movement has a consistent "persona"
   - Composition serves subtext
4. Design the lighting palette:
   - Key/fill ratios tied to scene mood
   - Color temperature map tied to theme
   - Motivated vs. unmotivated sources identified
5. Define color grade / VFX treatment
6. Note coverage strategy (masters, protection, one-take candidates)

**Final Artifact:** Shot List + Lighting Palette + Color/VFX Treatment

### Stage 04 — AUDIOGRAPHY & SOUND DESIGN (The Voice & Atmosphere)

**Skill:** `cinematic-audio-prompter`
**Read:** `cinematic-audio-prompter/SKILL.md` + relevant references

**Execute:**
1. Read the script, blocking, and shot lists from Stages 01-03.
2. Formulate the vocal texture design (apply Biryani Method, physical workouts, smoking treatments to match raw emotional realities).
3. Align dialogue mastering (EQ/compression/saturation) with the visual color grade and lighting temperature ("reds of the voice to the reds of the frame").
4. Formulate VFX Sound Defense: pre-map all computer-generated and dynamic visual elements (choppers, weapons, crowd expansions).
5. Map spatial placement using Dolby Atmos directional and overhead channels.
6. Manage music score vs. sound effects frequency divisions to ensure clean studio mixes.

**Final Artifact:** Sound Design Plan + Dolby Atmos Spatial Map + Vocal Texture Guide

### Stage 05 — PROMPT COMPILATION & DSL (The Compiler)

**Script/Tool:** `dsl_compiler.py` + `dsl/presets.json` + `dsl/templates.json`

**Execute:**
1. Collect the structural definitions of the scene and timeline beats.
2. Formulate the Intermediate Representation (IR) JSON/YAML containing the **10 Core Subsystems**:
   *   *1. Creative Intent Engine* (Story Purpose & Beat Objectives)
   *   *2. Prompt Compiler* (Model-agnostic output formatting)
   *   *3. Spatial Engine & Solver* (Percentage coordinates)
   *   *4. Scene Graph* (Relative positioning relationships)
   *   *5. Character State Machine* (Persistent vs transient state vectors)
   *   *6. Emotion Compiler* (Anatomical facial, body, & micro layering)
   *   *7. Reference Database* (Asset files mapping)
   *   *8. Asset & Prop Graph* (Weapons, items, state trackers)
   *   *9. Beat Timeline Engine* (Sequential multi-beat sequencing)
   *   *10. Evaluation & Quality Control* (Evidence-backed verification loops)
3. Run the static **Validation Layer** to verify character inventory, camera movement constraints, and prop ownership matches (`PROP001`, `PROP004`).
4. Run `dsl_compiler.py` to resolve camera/lighting/style presets and run optimization passes (deduplicate duplicate lighting/focus details).
5. Compile specialized target prompt packages dynamically for **Google Flow Omni**, **Higgsfield**, and **ChatGPT** using backend templates.
6. Append the evidence-backed confidence metrics report to the canonical manifest.

**Final Artifact:** Target-Ready Compiled Prompt Manifest & Canonical Prompt Manifest

---

## CONTINUITY THREAD — The Controlling Idea

The Controlling Idea must flow through all three stages without breaking:

| Stage | How the Controlling Idea Manifests |
|---|---|
| Screenplay | Every scene proves, tests, or complicates it through action and dialogue |
| Direction | Blocking and performance EMBODY it — power dynamics mirror the theme |
| Cinematography | Visual language ARGUES it — lens, light, movement, color all serve the idea |

**The Pipeline Health Check:** At any point, pause and ask: "If I showed this [scene / blocking / shot list] to someone who didn't know the Controlling Idea, could they INFER it from the work alone?" If not, the craft isn't serving the story.

---

## QUICK-RUN MODE

For a single scene at speed, the pipeline can be compressed:

```
QUICK PIPELINE OUTPUT:

SCENE: [Scene header + full script text]

DIRECTION NOTES:
  Objectives: [Character objectives in one line each]
  Power Arc: [Opening → Shift → Closing]
  Key Beats: [3-5 major beats with tactic names]
  Blocking Headline: [The single most important spatial move]
  Performance Keys: [One metaphor per character]

SHOT DESIGN:
  Visual Thesis: [One sentence]
  Key Shots: [3-5 essential shots with size/angle/purpose]
  Lighting: [Key temperature + contrast ratio + dominant source]
  Movement Style: [Camera persona in one word]

SOUND & ATMOSPHERE:
  Vocal Texture: [Vocal profile & physical method per character]
  Soundscape Motif: [The dominant environmental sound/tone]
  Atmos Spatial Point: [Key spatial sound placement]
  VFX Sound Defense: [Pre-mapped sound strategy for CG elements/crowds]
```

---

## INDIVIDUAL SKILL ROUTING

If the user only needs one stage:

| User Wants | Route To |
|---|---|
| Write/revise a scene or script | `screenplay-skill` |
| Direct a scene / blocking / performance | `direction-skill` |
| Design shots / lighting / visual language | `cinematography-skill` |
| Design sound, voice textures, spatial audio | `cinematic-audio-prompter` |
| Full pipeline treatment | This orchestrator → all four in sequence |

---

## PROJECT-SPECIFIC VISUAL SYSTEMS

For the user's active projects, these visual systems have been established:

### Dead Loop (AI Thriller, Hyderabad)
- Color System: Warm amber, terminal green, vermillion
- Visual Motif: Three-pulse heartbeat
- Mood: Indian cyberpunk noir
- Key Contrast: Analog warmth vs. digital coldness

### DAAVA (Political Thriller, Hyderabad)
- Tone: Ground-level political realism
- Controlling Idea: "Ruthless ambition destroys the soul it seeks to save"
- Visual Approach: Handheld realism → increasingly formalized as Arjun becomes the system

### PREM ప్రేమతో (Psychological Thriller/Drama)
- Recurring Motifs: Glass marble, charcoal circle, Ismail poetry
- Tone: Intimate, layered, morally ambiguous
- Visual Approach: Close framing, shallow depth, warm practicals

### FOREIGN GROUND (Coming-of-Age, Rayalaseema)
- Tone: Vivid, sensory, culturally specific
- Visual Approach: Wide landscape establishing shots, intimate CU for character moments
- Color: Earthy, saturated, distinctly Rayalaseema

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

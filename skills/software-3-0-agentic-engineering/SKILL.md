---
name: software-3-0-agentic-engineering
description: >
  The orchestrator for the Visual DNA AI Production Pipeline. This skill automates the end-to-end workflow 
  from narrative source (novel/screenplay) to cinematic video generation and knowledge graph indexing.
  It integrates the 'novelist', 'visual-dna-json', 'seedance-cinematic', and 'graphify' skills into a 
  unified agentic engineering protocol.
---

# SOFTWARE 3.0 — AGENTIC ENGINEERING (VISUAL DNA PIPELINE)

## PURPOSE
To transform high-level narrative concepts into production-ready AI assets with surgical precision and total identity consistency. This skill acts as the "Director of Engineering" for AI film production, managing the flow of data between storytelling, visual extraction, and generation.

---

## THE 4-STEP WORKFLOW

### 1. NARRATIVE EXTRACTION (The Source)
**Trigger:** Path to a Novel Draft (`.md`) or Screenplay.
**Action:** Use `novelist-skill` to identify the "What-If" premise and key character situations. Extract the core "Fossil" of the story.
**Input Needed:** File path to `DAAVA_Novel_Complete.md` or similar source.

### 2. VISUAL DNA ANCHORING (The Code)
**Trigger:** Reference images or storyboard plates.
**Action:** Use `visual-dna-json` to extract the underlying JSON structure. This defines materials, lighting, and character identity as stable, editable variables.
**Output:** A `character_bible.json` or `scene_dna.json`.

### 3. CINEMATIC GENERATION (The Render)
**Trigger:** Visual DNA + Narrative Scene.
**Action:** Use `seedance-cinematic` and `seedance-motion-control` to generate video clips. Apply the DNA surgically to ensure the character anchor remains identical across different shots and motions.
**Protocol:** The 6-Step Motion Control workflow must be followed here.

### 4. KNOWLEDGE GRAPHING (The Memory)
**Trigger:** Generated assets and extracted DNA.
**Action:** Use `graphify` to index all JSON DNA, character profiles, and scene metadata into a persistent knowledge graph.
**Result:** A searchable, agent-ready map of the entire production universe.

---

## INPUT PROTOCOL (Where to provide input)

To trigger the pipeline, provide the following information to the agent:

1. **Source Narrative:** The path to the novel or screenplay (e.g., `c:/Users/navka/navakanth001/DAAVA_Novel_Complete.md`).
2. **Visual References:** Paths to images or "plates" that represent the intended style or character (e.g., `sceneX_plate.jpg`).
3. **Target Output:** What do you want to generate? (e.g., "Extract DNA for Arjun and generate Shot 1 of the Heartbeat sequence").

### Example Request:
> "Using the `software-3-0` pipeline, read `DAAVA_Novel_Complete.md`. Extract the Visual DNA for the character 'Arjun' from `arjun_reference.jpg`, and prepare the JSON schema for Step 3 (Seedance Generation)."

---

## CORE ARCHITECTURE (The Karpathy Discipline)

- **Think in JSON:** Every visual element is a variable. Do not describe; code.
- **Identity Lock:** Once a DNA anchor is extracted, it is immutable unless explicitly edited in the JSON.
- **Surgical Edits:** Change the 'material' field in the JSON rather than re-prompting the entire scene.

---

## SUPER SKILL OS PROTOCOLS
This skill operates under the Karpathy Foundation and Tri-Layered Memory OS framework.
- **Bucket 1 (Session):** Log every DNA extraction and generation step in `memory_os/session_memory/`.
- **Bucket 2 (Long-Term):** Index character bibles in `memory_os/long_term_knowledge/`.
- **Bucket 3 (Strategic):** Align generation goals with the current project roadmap in `strategic_profile.md`.

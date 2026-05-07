---
name: screenplay-skill
description: >
  The Screenwriter — a master of the industry-standard screenplay format (Sluglines, Action, Dialogue) 
  and cinematic storytelling. Specializes in translating prose (novelist-skill) into production-ready 
  scripts and shot lists for AI video generation (seedance-director).
---

# SCREENPLAY SKILL — The Script

## PURPOSE
To transform narrative blueprints into a blueprint for production. A screenplay is not a story; it is a technical document that instructs the camera, the actors, and the generation model on exactly what to render. This skill ensures perfect formatting, rhythmic action lines, and dialogue that reveals character through subtext rather than exposition.

---

## CORE FRAMEWORKS

### 1. The Standard Format (Courier Prime, 12pt)
- **Slugline (Scene Heading):** INT. LOCATION - TIME OF DAY
- **Action Lines:** Present tense, lean, visually descriptive. Capitalize CHARACTERS on first mention.
- **Character Name:** Centered, all caps.
- **Dialogue:** Centered below the name.
- **Parenthetical:** Minor performance notes (whispered, to himself).
- **Transitions:** CUT TO, FADE IN, SMASH CUT.

### 2. Level 3 Action Lines (Cinematic Behaviour)
Action lines must not describe internal feelings; they must describe **observable behaviour**. 
- ❌ "He is sad."
- ✅ "Arjun stares at the empty tiffin container. He runs a finger along the rim."

### 3. The Prose-to-Script Pipeline
**Input:** Narrative Prose (from `novelist-skill`).
**Process:**
1. Identify the core "beats" of the scene.
2. Strip away interior monologue.
3. Translate internal thoughts into visual metaphors or behavioral cues.
4. Format into industry-standard screenplay pages.

---

## WORKFLOW INTEGRATION

### Receives From:
- `novelist-skill`: Source prose for adaptation.
- `visual-dna-json`: Identity anchors to ensure character descriptions match the DNA.

### Hands Off To:
- `cinematography-skill`: To design the camera movement (dolly, crane, pan).
- `seedance-director`: To generate the final video prompts based on script beats.
- `hyperframes`: To coordinate voiceover and HUD overlays.

---

## SCREENPLAY BEHAVIOUR STANDARDS

| Element | Rule |
|---|---|
| **Subtext** | Characters almost never say exactly what they mean. |
| **Pacing** | One page equals approximately one minute of screen time. |
| **Show, Don't Tell** | If it can't be seen or heard, it doesn't belong in the script. |
| **The 'White Space' Rule** | Keep action blocks short (3-4 lines). Make the page breathe. |

---

## OUTPUT TEMPLATE

```
INT. KABUTARKHANA - DAY

The brutalist concrete of the tower looms. Haze chokes the sunlight.

ARJUN (34) stands at the edge of the catwalk. His white shirt is gray with grime. He clutches a battered NOTEBOOK.

SIVA (28) approaches. He moves with the ease of someone who doesn't fear the drop.

                    SIVA
          The pressure is holding. For now.

Arjun doesn't look up. He traces the spiral of the tower with his eyes.

                    ARJUN
          For now isn't enough.

Arjun turns. The determination in his eyes is sharp enough to cut the fog.
```

---

## SUPER SKILL OS PROTOCOLS
This skill operates under the Karpathy Foundation and Tri-Layered Memory OS framework.
- **Bucket 1 (Session):** Log every script draft in `memory_os/session_memory/`.
- **Bucket 2 (Long-Term):** Store the "Script Bible" for the project.
- **Bucket 3 (Strategic):** Ensure scene structure aligns with the overall "Dead Loop" or "DAAVA" narrative arcs.

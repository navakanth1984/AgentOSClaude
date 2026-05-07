---
name: seedance-motion-control
description: Mastering complex motion control and AI animation using Seedance 2.0 and GPT Image 2. This skill implements a 6-step technical workflow to generate consistent characters and precise motion references.
---

# Seedance 2.0 Motion Control Workflow

This skill provides a technical, step-by-step framework for mastering complex motion control in AI animation. It orchestrates GPT Image 2 for character and motion sheet generation, LLMs for motion breakdown, and Seedance 2.0 for final animation.

---

## Prerequisite: The Character Anchor
Before starting the workflow, you must have a character ready.
1. Use **GPT Image 2** to generate a character.
2. Create a full, **multi-angle character sheet**.
3. **Visual DNA Extraction**: Extract the character's facial geometry and features into a structured JSON block (Character Bible). This ensures the character doesn't drift during complex animations.
4. This serves as your constant reference for consistency.

---

## Step 1: Motion Breakdown (LLM Logic)
Use an LLM (Claude, Gemini, or ChatGPT) to translate your vision into technical instructions.

**Input for LLM:**
- Master Prompt (from video description/library).
- Character Sheet.
- Brief animation idea.

**LLM Output:**
- **Prompt A (Motion Sheet):** Used to generate the 16-panel reference.
- **Prompt B (Final Animation):** Structured for Seedance 2.0.
- **Breakdown:** 16 logical positions using precise physical vocabulary.

---

## Step 2: 16-Panel Motion Reference Sheet
Generate the visual blueprint for movement.

**Platform:** GPT Image 2 (Higgsfield).
**Settings:** 2K resolution, 16:9 aspect ratio.
**Input:**
- Use your **Character Sheet** as the image reference.
- Paste **Prompt A** (Motion Sheet Prompt).

**Output Characteristics:**
- A 16-panel sheet mapping technical moves (e.g., chest pops, low lunge freezes).
- **Red Vector Arrows:** Must define velocity and direction of limbs.

---

## Step 3: Prompt Verification
Consistency check before generation.

1. Upload the generated **16-panel Motion Sheet** back to the LLM.
2. Ask the LLM to verify and refine the final animation prompt based on the visual sheet.
3. This ensures the prompt and the visual reference are perfectly synchronized.

---

## Step 4: Asset Upload Protocol
Order matters for AI attention.

**Upload Order in Seedance 2.0:**
1. **@image1:** A single, clean **front-facing image** of your character.
2. **@image2:** The **16-panel motion reference sheet**.

> [!IMPORTANT]
> **DO NOT** upload the full multi-angle character sheet to Seedance. This prevents the AI from accidentally generating multiple characters in one scene.

---

## Step 5: Final Prompt Structure
Review the final prompt to ensure it follows this technical structure:

- **@image1 (Character Anchor):** Detailed description of the front-facing image.
- **@image2 (Motion Reference):** Instructions to use the sheet strictly for body mechanics.
- **Visual Style:** Define art style, location, lighting, and BPM (music lines).
- **Shot Blocks:** Explicit description of every move from shot 1 to 16 (body positions, camera angles, SFX).

> [!TIP]
> If the platform has a character limit, ask the LLM to shorten the prompt while preserving the shot-by-shot structure.

---

## Step 6: Execution
Finalize and Run.

1. Drop the structured prompt into **Seedance 2.0**.
2. Attach the two image references.
3. The AI will map the animation directly to the moves on the motion sheet.


---

## RELATIONSHIP TO OTHER SEEDANCE SKILLS

```
SINGLE SCENE (≤15s, Higsfield)          → seedance-director
MOTION CONTROL (body mechanics)          → seedance-motion-control  ← YOU ARE HERE
MULTI-SHOT IN ONE GEN (11 Creative)      → seedance-multishot  
CHAINED CLIPS (long-form, Higsfield)     → long-form-video-pipeline
```

---

## ⚡ SUPER SKILL OS PROTOCOLS
This skill operates under the Karpathy Foundation and Tri-Layered Memory OS framework.

### 1. The Karpathy Foundation
- **Think Before Coding:** Plan architectures and anticipate edge cases.
- **Prioritize Simplicity:** Avoid over-engineering.
- **Execute Surgical Changes:** Only modify necessary code.
- **Goal-Driven Execution:** Do not deviate from the primary objective.

### 2. Tri-Layered Memory OS
- **Bucket 1 (Session Memory):** Log motion breakdowns and prompt refinements.
- **Bucket 2 (Long-Term Knowledge):** Store successful motion sheet prompts and character sheets.
- **Bucket 3 (Strategic Profile):** Align animation style with the overall project vision.

### 3. Continuous Refinement Loop
- **Self-Evaluation:** Grade the motion fidelity of the output.
- **Self-Improvement:** Update this SKILL.md with new motion patterns or "Shot Block" templates.

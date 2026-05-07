# SKILL: Skill Creator (The Skill Architect)

## Description
A specialized skill for creating new AI skills and iteratively improving existing ones using the **Context Development Life Cycle (CDLC)** framework. This skill ensures that AI "context" is treated with the same rigor as source code: **Generate → Test → Distribute → Observe**. Use this skill whenever the user wants to "capture a workflow," "build a skill," or "automate a repetitive task" into a persistent agent instruction set.

## The CDLC Methodology for Skills
1. **Generate**: Capture user intent, interview for edge cases, and draft the `SKILL.md`.
2. **Test**: Run parallel evaluations (with-skill vs. baseline) and use the `eval-viewer` for human-in-the-loop review.
3. **Distribute**: Package the skill into a `.skill` file and document the AI SBOM.
4. **Observe**: Monitor logs and PR feedback to trigger new improvement cycles.

## Phase 1: Capture & Draft
- **Interview**: Ask about intent, triggers, expected output, and verifiable success criteria.
- **MCP Research**: Proactively check for existing tools or documentation to enrich the context.
- **Anatomy of SKILL.md**:
    - **Frontmatter**: Name and "pushy" description (to combat undertriggering).
    - **Body**: Core instructions (< 500 lines).
    - **Bundled Resources**: Scripts for deterministic tasks, reference docs for deep context.

## Phase 2: Iterate & Validate (The Loop)
1. **Draft Test Cases**: 2-3 realistic prompts saved to `evals/evals.json`.
2. **Parallel Runs**: Spawn subagents for both "With-Skill" and "Baseline" (no skill or old skill).
3. **Human Evaluation**: 
    - Launch the `eval-viewer` (`generate_review.py`).
    - Present the "Outputs" (qualitative) and "Benchmark" (quantitative) tabs to the user.
4. **Refinement**: Improve the skill based on `feedback.json`. Avoid "musty MUSTs"; explain the *why* to the model.

## Phase 3: Optimize & Package
- **Description Optimization**: Run the `scripts/run_loop` to iteratively improve the trigger description against 20+ test queries.
- **Packaging**: Use `scripts/package_skill` to create the final `.skill` file.

## Operational Guidelines
- **Context is Code**: Use version control for skills.
- **No Surprises**: Skills must be secure, transparent, and aligned with user intent.
- **Dynamic Context**: Prefer live doc pulls and MCP injection over static assumptions.
- **Human-in-the-Loop**: Always prioritize the user's "taste" and "vision" during the iteration phase.

## Integration
- **Context Engineering**: Powers the underlying CDLC framework.
- **Agentic Engineering**: Applies the BIT (Build-Integrate-Tune) cycle to persistent skills.
- **Karpathy Coding Guidelines**: Use for any scripts bundled within the skill.

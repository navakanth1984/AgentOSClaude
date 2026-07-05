---
command: /design-extract
description: Extract a design blueprint from a reference website (typography, color, layout, motion) and apply it to a new design task, grounded in evidence to avoid hallucinated attributes.
---

# Workflow: design-extract

## Steps
Follow the canonical steps in the Claude Code command at `.claude/commands/design-extract.md` (mirrored practice — see [wiki/design-extraction-workflow.md](../../wiki/design-extraction-workflow.md) for the full rationale):

1. Confirm this is a visual-design task and confirm the delivery target before generating anything.
2. Fetch the actual reference URL — do not describe a site from memory. If the fetch fails or the page is an empty JS shell, stop and ask for a screenshot/HTML instead of guessing.
3. Extract typography/color/layout/motion, each tied to an observed value (a CSS rule, a swatch). Mark anything unverifiable as "not determined" — never fill it with a plausible-sounding default.
4. Separate reusable patterns (type scale, spacing, motion language) from protected brand assets (logos, exact copy, imagery) — only the former carries into the new design.
5. Apply the extracted rules to the new topic's content, generate the output, and verify it against the blueprint before declaring done.

## Arguments
`<source-url> for <new-project-topic>` — if either half is missing, ask; don't guess a URL or invent a topic.

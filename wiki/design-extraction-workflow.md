# Design Extraction Workflow
> Standard practice for pulling a reusable design "blueprint" (typography, color, layout, motion) from a reference website and applying it to a new visual design, without hallucinating attributes that weren't actually observed.

## Summary
This is an OKF-style stable-expertise entry: the underlying practice (fetch → extract with evidence → separate pattern-reuse from IP-copying → apply → verify) changes rarely, so it's documented once here and invoked as a command/skill by every AI tool in the workspace rather than re-explained per session. The canonical implementation is the Claude Code slash command [.claude/commands/design-extract.md](file:///C:/Users/navka/navakanth001/.claude/commands/design-extract.md); the tool-neutral mirror for other agents is [.agents/workflows/design-extract.md](file:///C:/Users/navka/navakanth001/.agents/workflows/design-extract.md).

## Details — the five steps
1. **Preconditions** — confirm this is a visual-design task (fixed canvas, not a responsive app UI) and confirm the delivery target (Adobe Express doc vs. standalone file) before generating anything.
2. **Fetch ground truth** — scrape/fetch the actual reference URL (`firecrawl-scrape` preferred, `WebFetch` fallback). Never describe a site from training-data familiarity; if the fetch fails or returns an empty JS shell, say so explicitly and ask for a screenshot/HTML instead of guessing.
3. **Extract with evidence** — capture typography, color (exact hex from CSS, never an approximated "brand color"), layout rhythm, and motion, each tied to something actually observed. Anything not verifiable is marked "not determined," never filled with a plausible default.
4. **Separate pattern vs. IP** — explicitly split reusable structural/stylistic rules (type scale, spacing system, motion language) from protected brand assets (logos, exact copy, proprietary imagery) that must not be reproduced in the new design.
5. **Apply + verify** — transplant the extracted rules onto the new topic's content, export via the visual-design skill's chosen path, then re-check the output against the blueprint before declaring done.

## Best Practices & Guidelines
- **Evidence-per-attribute rule**: every extracted design attribute must trace to a concrete observation (a CSS value, a visible swatch). This is the primary anti-hallucination control — the original ad-hoc version of this workflow had no such gate and would have asserted colors/fonts from memory.
- **Fetch-failure is a first-class branch**, not an edge case to skip: retry once with an alternate fetch tool, then stop and ask rather than fabricate.
- **Progressive disclosure**: this page + the command file is enough context for any agent to run the workflow cold; no need to re-derive the practice per session.

## Standard Practice: Keep in Sync Across AI Tools
Per [AI Tool Sync](ai-tool-sync.md)'s sync rule, **any new Claude Code command or skill that encodes a reusable practice (like this one) must be mirrored into `.agents/workflows/` (or `.agents/skills/`) in the same session it's created**, so Gemini, Antigravity, and Codex can invoke the same practice instead of it being Claude-only. This page itself is the wiki-side half of that sync for the design-extraction practice; see [ai-tool-sync.md](ai-tool-sync.md) for the full cross-tool bridge inventory.

## Connections
- Feeds into and is gated by the visual-design skill (`create_visual_design_express_skill` / `frontend-design`) for actual HTML authoring and Express export.
- Same "evidence over memory" discipline as [Karpathy Mandates](karpathy-mandates.md).
- Same one-file-per-concept, metadata+body pattern as [OKF Bundle Generator](okf-bundle-generator.md).

# AGENTS.md — Knowledge Base Operating Instructions

> Applies to every AI agent run in this repo (Claude, Antigravity, Gemini, etc.).
> The canonical, full operating brief is **[wiki/CLAUDE.md](wiki/CLAUDE.md)** — read it first. This file is the short, tool-neutral mirror of it.

## Operating Brief

Whenever you run a session in this folder, you must maintain the self-improving knowledge base.

### Folder Structure
- `sources/` — Raw original files (unedited; never deleted).
  - `sources/creative/`
  - `sources/technical/`
  - `sources/academic/`
- `wiki/` — Synthesized Markdown wiki pages.
  - `wiki/index.md` — Table of contents / front door.
  - `wiki/log.md` — Dated activity log.
  - `wiki/CLAUDE.md` — Canonical operating brief.
  - `wiki/_review/` — Holding pen for ambiguous items (never delete — set aside here).
- `AGENTS.md` — This file.

### Continuous Loop
1. **INGEST:** When new files are added to `sources/`, read them, update or create the matching `wiki/` page (never duplicate — update the existing one), link related pages, and add a dated line to `wiki/log.md`.
2. **ANSWER:** Answer questions from the `wiki/` pages first and name the pages used. If the wiki doesn't cover it, say so.
3. **TIDY:** On request, audit the wiki for contradictions, orphan pages, stale claims, or missing summaries and present a punch list only — don't auto-fix.

A nightly scheduled task (`wiki-nightly-ingest`, 2:06 AM) runs this loop automatically.

### Guardrails (do not violate)
- Show a plan and get explicit approval before moving, renaming, or deleting any file. **Never delete** — set ambiguous items aside in `wiki/_review/`.
- This repo is a **staging workshop**: the root-level project folders (`nth-brain`, `mvct-v1`, `agent_os`, `nthdimensionacademy`, …) are live workspaces that graduate into their own repos. Do **not** fold them into `sources/`; the wiki maps them with thin overview pages only.
- Plain Markdown only. Every page opens with a one-line summary; every claim links to its source.

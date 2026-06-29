# AGENTS.md — Knowledge Base Operating Instructions

> Applies to every AI agent run in this repo (Claude, Antigravity, Gemini, etc.).
> The canonical, full operating brief is **[wiki/CLAUDE.md](wiki/CLAUDE.md)** — read it first. The shared Claude+Antigravity read/feed contract (graphify graph layer + wiki layer) is **[wiki/knowledge-base-protocol.md](wiki/knowledge-base-protocol.md)**; the cross-repo front door is **[wiki/knowledge-base-map.md](wiki/knowledge-base-map.md)**. This file is the short, tool-neutral mirror of them.

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
4. **UPGRADE:** Run the four productivity upgrades (Roast, Verification, Handoff, and Sub-agent Goals) to optimize execution and feed learnings back into the KB. See [antigravity-upgrades.md](wiki/antigravity-upgrades.md) for details.

A nightly scheduled task (`wiki-nightly-ingest`, 2:06 AM) runs this loop automatically.

### Guardrails (do not violate)
- Show a plan and get explicit approval before moving, renaming, or deleting any file. **Never delete** — set ambiguous items aside in `wiki/_review/`.
- This repo is a **staging workshop**: the root-level project folders (`nth-brain`, `mvct-v1`, `agent_os`, `nthdimensionacademy`, …) are live workspaces that graduate into their own repos. Do **not** fold them into `sources/`; the wiki maps them with thin overview pages only.
- Plain Markdown only. Every page opens with a one-line summary; every claim links to its source.

## Code Development Lifecycle (Standard)

Applies to **code** changes (the `wiki/`+`sources/` "never delete" rule above is about KB content, not version-controlled code). Every non-trivial code change follows this lifecycle:

1. **Branch** — never commit directly to `master`. Work on a feature/`milestone/*` branch.
2. **Implement + verify** — make the change and *prove it works* before claiming done: run it (real run, not just types), add/keep tests green, run `pyrefly` (the pre-commit hook blocks on type errors — never `--no-verify`).
3. **Commit** — focused, conventional-commit messages (`feat:`/`fix:`/`refactor:`/`docs:`). Keep refactors/deletions in their own commit, separate from features. End messages with the `Co-Authored-By: Claude …` trailer.
4. **Push** — push the branch to `origin` (set upstream with `-u` the first time).
5. **PR** — open a PR into `master` (`gh pr create`). Draft if the milestone is ongoing, ready if the unit of work is complete. The PR is the CI gate and the durable, reviewable record — **branch-only work is not the finish line.**
6. **Review/CI → merge** — let checks run; merge via PR (one revertable merge commit), then delete the branch.

**Removing legacy code** follows the deprecation lifecycle, never a blind delete: **deprecate** (add `DeprecationWarning` + pointer to the replacement) → **migrate every importer** (grep for all call sites) → **verify each still works** → **delete** → commit as an isolated `refactor:`. Deletion is legitimate here because git makes it revertable — this does **not** conflict with the KB "never delete" guardrail.

**Feed the KB:** after the work lands, add a dated `wiki/log.md` line and update the relevant wiki page (see the Continuous Loop above).

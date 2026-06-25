# Knowledge Base — Operating Brief

This folder (`wiki/`) is a self-improving knowledge map for the `navakanth001` workspace. Read this before working in it.

## What this is
- `sources/` (repo root) holds raw, original material — the source of truth. Never edited, only added to. Organized into `academic/`, `creative/`, `technical/` (add `knowledge/` for AI-systems notes as needed).
- `wiki/` holds the map: one synthesized Markdown page per real topic, tool, person, project, or idea, written in my own words — not copy-paste.
- `wiki/index.md` is the front door; every page is listed there.
- `wiki/log.md` records what I did and when (YYYY-MM-DD, one line per entry).
- `wiki/_review/` is a holding pen for anything ambiguous. Nothing is ever deleted — it goes here and the user decides.

## Ground rules (these never change)
- Work only inside this repo. Show a plan and get an explicit "go" before moving, renaming, or deleting any file. Never delete — set aside in `_review/` instead.
- This is a **staging workshop**: the many root-level project folders (`nth-brain`, `mvct-v1`, `agent_os`, `nthdimensionacademy`, …) are live workspaces that graduate into their own repos. Do **not** fold them into `sources/`. The wiki maps them with thin overview pages; it does not absorb them.
- Plain Markdown only. Every page opens with a one-line summary; every claim links back to its source; related pages link to each other.
- When in doubt, ask a short question instead of guessing.

## The three jobs
- **INGEST** — when new material lands in `sources/` and the user says to ingest it: read it, update or create the right wiki page (never duplicate — update the existing one), link it to related pages, and add a `log.md` line.
- **ANSWER** — answer from the wiki first and name the pages used. If the wiki doesn't cover it, say so.
- **TIDY (lint)** — on request, scan the whole wiki and return a punch list only (don't auto-fix): contradictory pages, stale claims, orphan pages nothing links to, and frequently-mentioned topics with no page yet.

## Nightly self-improving loop
A scheduled task (see `log.md` for status) runs off-peak: check `sources/` for anything new since the last run, ingest each item, run a quick tidy pass, and leave a short note of anything needing attention.

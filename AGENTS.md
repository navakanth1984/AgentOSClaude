# AGENTS.md — Knowledge Base Operating Instructions

> Applies to every AI agent run in this repo (Claude Code, Antigravity, Gemini, Codex, and any other agent tool).
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

### AI Tool Sync Entry Points
- `AGENTS.md` — tool-neutral root contract; Codex and other repo-aware agents should start here.
- `CLAUDE.md` and `.claude/CLAUDE.md` — Claude Code / Claude Desktop bridge back to the same KB contract.
- `GEMINI.md` — Gemini CLI bridge.
- `.antigravity.md` — Antigravity bridge.
- `.codex/AGENTS.md` — Codex local bridge; keep it short and point back here.
- `wiki/ai-tool-sync.md` — inventory of tool folders, Markdown bridges, and sync rules.

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

### Next-Steps Handoff (regular process — end of every significant work item)
- `wiki/ai-tool-sync.md` — inventory of tool folders, Markdown bridges, and sync rules.

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

### Next-Steps Handoff (regular process — end of every significant work item)

When wrapping a feature, milestone, or hand-off to another agent (e.g. Antigravity), **always write a forward-looking handoff** so the next session/agent can resume cold:
1. **KB** — create/update a `wiki/<topic>-next-steps.md` page (prioritized P0/P1/P2, file pointers, acceptance criteria), link it in `wiki/index.md`, and add a `wiki/log.md` line.
2. **Session memory** — append the same next-steps to the current `memory_os/session_memory/session_<YYYYMMDD>.md` and refresh `.remember/remember.md` (the cross-session buffer).
3. Keep it **cold-start friendly**: assume no prior context; name exact files, commands, and the branch/PR/CI state.

This is part of the self-improving loop — the handoff is how work survives across sessions and across agents.

## Sub-Agent & Workspace Management Guidance

> Full lifecycle (work tree → dev → verify → PR → staging → production → KB handoff) is codified in **[wiki/agentic-dev-lifecycle.md](wiki/agentic-dev-lifecycle.md)**. All agents must follow it end-to-end.

Whenever you are delegating a task to a sub-agent, creating a new work tree, or discussing workspace environments:
1. **Highlight Actions:** Explicitly notify the user when a dedicated Git work tree is being created, used, or cleaned up (e.g., *"Creating an isolated Git work tree for the research sub-agent..."*).
2. **Feature Reminders:** Remind the user of available workspace features (such as manual sidebar toggles, conversation grouping, background scheduling, or the "new work tree" conversation option) where appropriate so they do not need to memorize them.
3. **Work Tree Integration:** After a sub-agent work tree is closed, the agent MUST immediately open a PR from the work tree branch into `master` and notify the user. The task is NOT done until the PR is open. Never leave branches dangling without a PR.

### Session End Routine (Mandatory — every session, planned or abrupt)

At the conclusion of *every* session — whether planned or after an abrupt disconnect — execute this checklist in order:

#### Step 1 — Lifecycle Sync Check
Confirm `wiki/agentic-dev-lifecycle.md` and `.antigravity.md` are in sync:
- Did any new rules get added to the lifecycle doc this session?
- If yes: mirror the actionable items into `.antigravity.md` so `agy` CLI picks them up.
- This takes 60 seconds. Do not skip it.

#### Step 2 — Context & Branch State
- Note any open branches, in-flight PRs, or dangling work trees.
- If a branch has no PR yet: open one now before closing (`gh pr create --base master --draft`).
- If context token usage is ≥ 250K: write the handoff now — do not wait until next session.

#### Step 3 — KB Close-Out
1. Update `wiki/log.md` — dated summary of session actions, merged PRs, open WIP.
2. Update the relevant `wiki/<topic>.md` page.
3. Write any new patterns, bug classes, or model mismatches to `memory_os/long_term_knowledge/lessons_learned.md`.
4. Refresh `.remember/remember.md` with the cold-start buffer.

#### Step 4 — Session Scripts
```powershell
py -3 memory_os/scripts/validate_usage_efficiency.py   # model economics + routing efficiency
py -3 agent_os/session_end.py                          # persist context to Obsidian vault
```

#### Step 5 — Handoff File (always write, even if session ended cleanly)
Write to `memory_os/session_memory/session_<YYYYMMDD>.md`:
```markdown
## Current Status
[Done / In-flight — include branch name + PR # if applicable]

## Key Files
- [path] — [one-line purpose]

## Locked Decisions (do not revisit)
- [decision] — [why locked]

## Next Steps (P0/P1/P2)
- P0: [must-do-next — blocking]
- P1: [high value]
- P2: [nice to have]

## Abrupt Disconnect Flag
[Yes / No — if Yes, note what was mid-flight]
```

---

### Abrupt Disconnect / Cold-Start Reconnect Protocol

If a session was cut off unexpectedly (network drop, app crash, token limit hit, user closed session), the **next agent to open this workspace** must:

1. **Read `.remember/remember.md`** — the cross-session buffer. This is the fastest cold-start signal.
2. **Read the latest `memory_os/session_memory/session_<YYYYMMDD>.md`** — find the most recent handoff file.
3. **Check for dangling branches:** `git branch -a | grep -v master` — if any exist without a PR, open one now.
4. **Check for open PRs:** `gh pr list --state open` — surface them to the user.
5. **Read `wiki/log.md` last 10 lines** — confirms what was last completed.
6. **Run the Lifecycle Sync Check** (Step 1 above) — confirm `.antigravity.md` is up to date.
7. **Announce to the user:** *"Reconnected after disconnect. Last session: [summary from handoff]. Open PRs: [N]. Dangling branches: [N]. Ready to resume from: [P0 next step]."*

> **This protocol fires automatically** — no user prompt needed. The agent runs it at session start whenever it detects a prior handoff file from the same calendar day or finds an `Abrupt Disconnect Flag: Yes` in the latest session memory.

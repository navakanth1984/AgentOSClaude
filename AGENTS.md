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

## Antigravity v2.1 Operating & Execution Mandate

This project constitution SHALL ADOPT and align with the **Antigravity v2.1 Operating & Execution Mandate** defined in [.antigravity.md](file:///.antigravity.md).

### Mode: Product Execution (Status: ACTIVE)
Governance and architecture documents are **frozen**. Do not spend cycles expanding governance unless a production blocker or cross-project architectural discovery requires it. The primary objective is shipping a production-grade product.

### Definition of Done (DoD)
A task or milestone is considered **Done** only when:
*   ✓ **Green CI**: All pipeline checks, types, and build scripts pass successfully.
*   ✓ **E2E Validation**: All Playwright E2E tests are 100% green on Chromium/Firefox/Webkit.
*   ✓ **Accessibility Compliance**: Passes core AX rules (contrast, aria-labels, role mapping).
*   ✓ **Performance Limits**: Satisfies target response, interaction, and rendering speeds.
*   ✓ **Zero Open P0/P1 Defects**: No unresolved blockages or visual/behavioral regressions.
*   ✓ **Staged/Deployed**: Successfully built and deployed to the production staging workspace.

### Core Optimization Equation
$$Engineering\ ROI = \frac{User\ Value \times Knowledge\ Reuse}{Token\ Cost \times Execution\ Time}$$

### Invariant Rules
1.  **Never reload knowledge that already has an authority**: Instead of reloading multiple raw documents, reference their canonical owners.
2.  **Read minimum viable context**: Ask *Can this be solved from the graph?* before grepping or scanning.
3.  **Context Budget**: Target context boundaries: Bug fix (`5k–15k`), Small feature (`10k–25k`), Medium feature (`20k–40k`), Architecture (`40k–80k`). Soft warning at `30k`, hard stop at `40k`.
4.  **Progressive Loading**: Traverse step-by-step: $\text{Index} \rightarrow \text{Graph} \rightarrow \text{Header} \rightarrow \text{Relevant section} \rightarrow \text{Exact lines} \rightarrow \text{Whole file (only if required)}$.
5.  **One Authority Rule**: Every concept has exactly one owner (`ADR-010` for Evidence Hierarchy, `ADR-012` for Learning Loop, `OCOS` for principles, `operating_system.md` for runtime, `status.md` for current state, `.remember/remember.md` for memory).
6.  **Documentation Compression**: Keep outputs short; explain only what's unique.
7.  **Architecture Freeze & Governance Freeze**: Governance changes quarterly/milestone only. OCOS, ADR-012, and CHARTER are frozen unless forced by architectural contradiction or human request.
8.  **Product First Gate**: Confirm if task ships user-visible improvements, unblocks shipping, or reduces engineering cost before starting governance or planning.
9.  **Stop Rule**: If work doesn't improve the product, reduce cost, or discover a new architectural primitive, stop and delegate implementation to Claude Code/Codex.
10. **Sprint Budgets**: Target Product Implementation ($\ge 80\%$), Testing & Validation ($\approx 10\%$), Planning ($\le 5\%$), Governance ($\le 5\%$).

### Success Metric: Knowledge Reuse Ratio (KRR)
$$\boxed{KRR = \frac{\text{Referenced Canonical Knowledge}}{\text{Newly Generated Governance Text}} \ge 0.90}$$

### KRR History Tracking
| Milestone | KRR |
|---|---:|
| Before OCOS | 0.28 (estimated) |
| After OCOS | 0.84 (projected) |
| Target | $\ge 0.90$ |

---

### Graphify as a Context Optimizer
The graph is a context-reduction tool. Before loading files, Antigravity MUST:
1. Query graph to identify target files and affected modules.
2. Load only the minimum context slice needed (affected files and direct headers/dependencies).
3. Execute the planning or routing work.
4. Update the graph (`graphify update`) only if files or structure changed.

---

### Session End Routine (Mandatory — every session, planned or abrupt)

At the conclusion of *every* session — whether planned or after an abrupt disconnect — execute this checklist in order:

#### Step 1 — Lifecycle Sync Check
Confirm `wiki/agentic-dev-lifecycle.md` and `.antigravity.md` are in sync:
- Did any new rules get added to the lifecycle doc this session?
- If yes: mirror the actionable items into `.antigravity.md` so `agy` CLI picks them up.

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

#### Step 5 — Handoff File (always write to memory_os/session_memory/session_<YYYYMMDD>.md)
```markdown
## Current Status
[Done / In-flight — include branch name + PR #]

## Key Files
- [path] — [purpose]

## Locked Decisions (do not revisit)
- [decision] — [why locked]

## Next Steps (P0/P1/P2)
- P0: [must-do-next — blocking]
- P1: [high value]
- P2: [nice to have]

## Session Metrics & Efficiency
- User-visible improvements:
- Metric improved:
- Telemetry added:
- Tests passed & CI status:
- Duplicated reasoning eliminated:
- Documents referenced instead of reloaded:
- Estimated context saved this session:
- KRR achieved:
- Abrupt Disconnect Flag: [Yes/No]

### Token & Resource Telemetry
| Metric | Value |
|---|---:|
| Documents loaded | |
| Documents edited | |
| Graph queries | |
| Full repository scans | |
| Estimated context reused | |
| New canonical knowledge created | |
| Duplicate knowledge eliminated | |
| Estimated governance overhead | |

### Orchestration Exit Criteria
- What product work was unblocked?
- What implementation work was delegated?
- What duplicated reasoning was removed?
- What evidence was collected?
- What should Claude Code build next?
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

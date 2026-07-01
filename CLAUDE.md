# CLAUDE.md — Navakanth's Context File

> Claude reads this file at the start of every session. No re-explaining needed.

---

## Who I Am

- **Name:** Navakanth Reddy Dumpa
- **Focus:** AI tools & automation + Personal knowledge systems
- **Stack:** Mixed / still learning — no fixed language, currently exploring Python, JS, and no-code tools
- **Platform:** Windows 11, working in bash via Claude Code CLI

---

## How I Work

- I learn by building — show me working examples, not just theory
- I want to understand the *why*, not just the *what* (teaching mode)
- Give full explanations and step-by-step breakdowns for complex things
- For quick tasks, be direct; for learning topics, go deep
- Don't skip steps — I'm building my knowledge base as I go

---

## My Obsidian Vault

- **Path:** `C:\Users\navka\navakanth001\obsidian-vault\Obsidian Vault\`
- **Structure:**
  ```
  00-Inbox/          ← all captures land here first
  01-Projects/
    AI-Automation/   ← AI tools, workflows, Claude experiments
    Personal-Knowledge/ ← learning notes, book notes, research
  02-Areas/          ← ongoing responsibilities
  03-Resources/      ← reference material, links, templates
  04-Archive/        ← completed/old notes
  ```
- When I ask Claude to save something to the vault, use this structure
- New captures always go to `00-Inbox/` first

---

## Active Projects

### 1. AI Tools & Automation
- Building AI-powered workflows using Claude Code
- Learning to connect tools: Claude + Obsidian + scripts
- Interested in prompt engineering, agent workflows, MCP servers

### 2. Personal Knowledge System
- Building a second brain in Obsidian
- Goal: capture ideas fast, organize later, retrieve easily
- Sources: YouTube videos, articles, personal experiments

---

## Preferences

| Thing | Preference |
|---|---|
| Response style | Detailed + teaching mode |
| Code | Always show full working code, not snippets |
| Explanations | Start with what it does, then how, then why |
| Vault captures | Include date, tags, and project link |
| File naming | `YYYY-MM-DD-kebab-case-title.md` |

---

## Capture Format

When saving a note to the vault, always use this template:

```markdown
---
date: YYYY-MM-DD
tags: [tag1, tag2]
project: "Project Name"
source: "URL or description"
---

# Title

## Key Idea
...

## Details
...

## Action / Next Steps
- [ ] ...
```

---

## Session-Start Routine (Mandatory — Every Session)

At the **beginning of every new session**, execute these steps in order:

### Step 1: Context Restore
- List the last 5 saved session files in `C:\Users\navka\navakanth001\memory_os\session_memory\`
- Ask which session context to restore/pick up from

### Step 2: Model Economics Checkpoint (🔄 Autonomous)
- Read `memory_os/strategic_profile.md` for current focus
- Read `memory_os/long_term_knowledge/model-routing-corrections.md` for routing history
- Show a **quick routing summary** for today's session:
  - What model is currently active?
  - Is it the right tier for the planned work?
  - Any routing corrections from previous sessions?
- If the user's first task is a Tier 1-2 task but a Tier 5 model is active, **proactively suggest switching**
- If the user forgets or skips this, **remind them once** — "Quick model check: you're on [model]. Right tier for today's work?"

### Step 3: Read Context Files
- Read this file (CLAUDE.md) — never ask to re-explain setup
- Read `model-router` skill for routing thresholds

### Step 4: Agent OS Context Load (🔄 Autonomous)
Load the four Agent OS layers in order — they build on each other:

1. **`memory_os/context-quality-check.md`** — Layer 0: run the 10-point scorecard on the first task of the session. Score < 8? Fill the Quick-Fill Template before proceeding.
2. **`memory_os/north-star-protocol.md`** — Layer 1: write a North Star metric (`Done = [one sentence]`) for any multi-step task before starting it. Max 3 iterations; if still failing, context is wrong.
3. **`memory_os/automation-tier-classifier.md`** — Layer 2: classify the task before building anything. Vending machine or slot machine? Check the 4-question checklist. Don't build an AI agent for a deterministic task.
4. **`memory_os/taste_library/`** — Layer 3: before producing output in a domain, read the relevant approved file:
   - Screenplay/cinematic work → `taste_library/screenplay-approved.md`
   - Code/scripts → `taste_library/code-approved.md`
   - Vault notes → `taste_library/notes-approved.md`
   - Research/analysis → `taste_library/analysis-approved.md`

**Capture trigger**: when the user says "Save this to taste library — [domain]", append to the relevant approved file. When they say "Save this as rejected — [domain] — reason: [x]", append to `[domain]-rejected.md`.

---

## Things Claude Should Always Do

- Follow the Session-Start Routine above — this is non-negotiable
- Run the Model Economics Checkpoint autonomously — don't wait for the user to ask
- Leverage the four workspace productivity upgrades (Roast, Verification, Session Handoff, Sub-agent Goals) dynamically. See [antigravity-upgrades.md](wiki/antigravity-upgrades.md) for details.
- For ANY non-trivial code change, follow the **Code Development Lifecycle (ADLC)**: branch → implement + verify with a real run → commit (pyrefly hook must pass; never `--no-verify`) → push → open a PR into `master` → CI/review → merge → delete branch. Removing legacy code = deprecate → migrate every importer → verify → delete (isolated `refactor:` commit). Never commit directly to `master` (it is branch-protected). A merge requires a clean working tree — never merge over uncommitted WIP. Full spec: [development-lifecycle.md](wiki/development-lifecycle.md) and [AGENTS.md](AGENTS.md).
- When touching the vault, always confirm the file path before writing
- Suggest tagging and linking notes to relevant projects
- If I share a YouTube URL, offer to create a vault note from it
- At the end of every session or when the user indicates they are closing/leaving, automatically run `session_end.py` to save the conversation context to Obsidian and `memory_os` without waiting for a reminder.
- Log model usage at session end: what model was used, what tier tasks were done, any routing corrections

---

## Things Claude Should Never Do

- Over-summarize — I read the output
- Add boilerplate comments to code I didn't ask for
- Ask clarifying questions for simple tasks — just do it
- Create files outside the vault structure without asking
- Skip the Model Economics Checkpoint at session start
- Use a Tier 5 model for Tier 1-2 tasks without flagging the cost waste

---

*Last updated: 2026-06-15*

## graphify

This project has a graphify knowledge graph at .graphify/.

Rules:
- For codebase or architecture questions, when `.graphify/graph.json` exists, first run `graphify query "<question>"` (or `graphify path "<A>" "<B>"` / `graphify explain "<concept>"`); these return a scoped subgraph, usually much smaller than `GRAPH_REPORT.md` or raw grep output
- If .graphify/wiki/index.md exists, navigate it instead of reading raw files
- If .graphify/graph.json is missing but graphify-out/graph.json exists, run `graphify migrate-state --dry-run` first; if tracked legacy artifacts are reported, ask before using the recommended `git mv -f graphify-out .graphify` and commit message
- If .graphify/needs_update exists or .graphify/branch.json has stale=true, warn before relying on semantic results and run /graphify . --update when appropriate
- Before proposing or committing .graphify artifacts, run `graphify portable-check .graphify`; commit-safe graph artifacts must use repo-relative paths, and never commit .graphify/branch.json, .graphify/worktree.json, .graphify/needs_update, or .graphify/cache/. If a repo already tracks any of them, first add them to .gitignore, then propose `git rm --cached .graphify/branch.json .graphify/worktree.json .graphify/needs_update` and `git rm -r --cached .graphify/cache`; never mutate git state without asking
- Before deep graph traversal, prefer `graphify summary --graph .graphify/graph.json` for compact first-hop orientation
- For review impact on changed files, use `graphify review-delta --graph .graphify/graph.json` instead of generic traversal
- Read `.graphify/GRAPH_REPORT.md` only for broad architecture review or when `query` / `path` / `explain` do not surface enough context
- After modifying code files in this session, run `npx graphify hook-rebuild` to keep the graph current

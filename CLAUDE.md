# AgentOS — Claude Architecture File

> This file is read at the start of every session. It defines how this workspace operates, what tools are available, and how memory is maintained across sessions.

---

## What This System Is

AgentOS is a permanent, self-improving AI workspace built on Claude Code. It combines:
- **Permanent memory** via Obsidian + markdown vaults
- **External tool access** via MCP connectors
- **Reusable skills** and custom slash commands
- **Automated hooks** for memory saving and context management
- **Sub-agent workflows** for parallel task execution

---

## Directory Structure

```
AgentOSClaude/
├── CLAUDE.md              ← You are here. Read every session boot.
├── .env                   ← API keys (never commit this)
├── .env.example           ← Template for required env vars
├── raw/                   ← Drop source files here (PDF, Excel, CSV, etc.)
├── memory/                ← Auto-generated session notes and context logs
├── output/                ← Finished deliverables (apps, decks, videos, reports)
└── .claude/
    ├── hooks/             ← Automated background triggers
    │   ├── stop-save-memory.sh     ← Runs on session stop → saves context to memory/
    │   └── post-task-update.sh     ← Runs after feature complete → updates CLAUDE.md
    ├── skills/            ← Reusable playbooks (data analysis, scope-a-feature, etc.)
    │   ├── scope-feature.md
    │   ├── data-analysis.md
    │   └── ship-summary.md
    └── commands/          ← Custom slash command definitions
        ├── ship.md
        ├── compact-save.md
        └── workflow.md
```

---

## Session Boot Checklist

On every new session, Claude must:
1. Read this file fully
2. Check `memory/latest-session.md` for prior context
3. Confirm which MCPs are connected (run: `claude mcp list`)
4. Report current task queue from `memory/tasks.md` if it exists

---

## Memory Protocol

- **Session notes** → `memory/YYYY-MM-DD-session.md`
- **Task log** → `memory/tasks.md`
- **Architecture updates** → appended to this file under `## Change Log`
- **Obsidian sync** → If Obsidian vault is configured, mirror `memory/` to vault's `01-Projects/AgentOS/`

### Note Format
```markdown
---
date: YYYY-MM-DD
session: N
tags: [agentOS, session-note]
---
## What was built
## Key decisions
## Next steps
- [ ] ...
```

---

## Connected MCPs

| MCP | Purpose | Status |
|-----|---------|--------|
| OpenRouter | Unified LLM API access | Configure in `.env` |
| Vercel/Netlify | Deploy web apps | Install via connectors |
| Parallel Search | Live web research | Install via connectors |
| Context7 | Latest library docs | Install via connectors |

---

## Context Health

- Monitor usage with `/usage`
- If context > 50%: run `update CLAUDE.md` then `/compact`
- Never let context rot — compact early, compact often

---

## Agent Roles

| Agent | Role |
|-------|------|
| Main | Orchestrator — planning, decisions, final output |
| Code Reviewer | Parallel — reviews diffs for bugs |
| Security Reviewer | Parallel — scans for vulnerabilities |
| Research Agent | Parallel — web search and data gathering |
| Sub-agents (dynamic) | Spawned per task via `/workflow` |

---

## Change Log

<!-- Appended automatically by stop hook after each session -->
<!-- Format: YYYY-MM-DD: <what changed> -->

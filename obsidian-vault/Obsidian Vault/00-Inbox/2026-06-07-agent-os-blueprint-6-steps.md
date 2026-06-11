---
date: 2026-06-07
tags: [agent-os, blueprint, claude-code, obsidian, mcp, memory, workflow, skills, hooks, sub-agents]
project: "AI-Automation"
source: "Agent OS 6-Step Blueprint"
---

# Agent Operating System — 6-Step Blueprint

> Integrate permanent memory, custom dashboards, external connectors, and parallel agents
> into a single highly efficient Agent OS.

## Key Idea

A full Agent OS = Memory Vault + MCP Connectors + Skills/Commands + Background Hooks
+ Sub-Agent Teams + Context Hygiene. Each layer compounds the ones below it.

## Details

### Step 1 — Permanent Memory Vault
- Local root folder = workspace root (`C:\Users\navka\navakanth001\`)
- **Obsidian** = permanent memory (markdown vault at `obsidian-vault\Obsidian Vault\`)
- `CLAUDE.md` = onboarding doc Claude reads every boot — project context, preferences, vault path
- `raw/` folder = drop PDFs, Excel, source files → Claude converts to linked markdown
- Goal: no "temporary context" — every session inherits prior knowledge

### Step 2 — Wire MCPs and APIs
- **OpenRouter** → unified LLM API (store key in `.env`) → route to Perplexity for live search
- **Vercel / Netlify MCP** → instant cloud deploy from within Claude
- **Parallel Search MCP** → live web research, competitive analysis, market data
- **Context7 MCP** → latest library docs (prevents stale training-data code errors)

### Step 3 — Stack Skills and Commands
- Install open-source skills from `knowledge-work-plugins` or `skills.sh`
- Custom skills in plain English: e.g. "scope a feature" → forces clarifying Qs before building
- **Hyperframes** skill → write HTML → render to MP4 (automated video engine)
- Custom `/ship` command → auto-summarise all session changes to vault
- Restart Claude Code after adding new commands

### Step 4 — Automate with Hooks
- **Stop hook** → after feature implemented + tested → auto-update `CLAUDE.md`
- Ensures every finished task writes context back to Obsidian vault automatically
- Never lose progress on session close
- Build: "create a hook so that once feature is done, update CLAUDE.md"

### Step 5 — Sub-Agents and Dynamic Workflows
- Spin up parallel sub-agents: "Code Reviewer", "Security Reviewer" — each 1M token window
- `/workflow` + Opus → up to 18 sub-agents in parallel for massive tasks
- Sub-agents: gather data, score ideas, catch + fix their own bugs independently
- **Goal Mode** (Hermes): hand off long task → agent works autonomously to done

### Step 6 — Consolidate Output + Prevent Context Rot
- Unified dashboard: all agent outputs save to one searchable workspace
- Monitor with `/usage` → if >50% context window → quality degrades ("context rot")
- Run `update CLAUDE.md` → saves state → `/compact` → clears tokens, keeps structure

## Our Agent OS vs Blueprint

| Blueprint Step | Our Implementation | Status |
|---|---|---|
| Memory Vault (Obsidian) | `obsidian_bridge.py` + PARA vault | ✅ Done |
| CLAUDE.md onboarding | `CLAUDE.md` in project root | ✅ Done |
| Raw data ingestion | `/save` endpoint + `obsidian_bridge.py` | ✅ Done |
| Workflow pipeline | `workflow.py` + `/workflow` endpoint | ✅ Done |
| Flutter dashboard | Agent OS screen + Nth Dimension theme | ✅ Done |
| NotebookLM integration | `notebooklm_agent.py` + audio capture | ✅ Done |
| OMI memory bridge | `omi_bridge.py` + `/omi` endpoint | ✅ Done |
| Skills system | Claude Code skills active | ✅ Active |
| Hyperframes video | Available as skill | ✅ Available |
| OpenRouter / LLM API | `analyze_prompt_llm()` + multi-model routing | ✅ Done |
| Context7 docs MCP | `settings.local.json` → `@upstash/context7-mcp` | ✅ Done |
| Custom `/ship` command | `.claude/commands/ship.md` | ✅ Done |
| Stop hook → CLAUDE.md | `session_stop.py` + `settings.json` hook | ✅ Done |
| Sub-agent swarm | `run_swarm()` — 5 parallel agents via OpenRouter | ✅ Done |
| Swarm + NotebookLM | `find_matching_notebooks()` injected into swarm note | ✅ Done |
| Vercel deploy MCP | Not installed | ❌ TODO |
| Goal Mode | `goal_mode.py` + `POST /goal` — plan/execute/check/save | ✅ Done |
| /usage + /compact | Built-in Claude Code | ✅ Available |

## Action / Next Steps
- [x] Wire OpenRouter API key → `.env` → multi-model routing in `workflow.py`
- [x] Create `/ship` custom command → summarise session to vault automatically
- [x] Build stop hook → auto-update `CLAUDE.md` when feature completes
- [x] Install Context7 MCP → live library docs in every Claude session
- [x] Add sub-agent swarm mode + NotebookLM integration
- [x] Build Goal Mode → `POST /goal` → autonomous multi-step task runner
- [ ] Install Vercel MCP → one-command cloud deploy from Agent OS

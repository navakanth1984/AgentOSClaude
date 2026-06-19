---
date: 2026-06-06
tags: [core, identity, agent-os]
project: "AI-Automation"
source: "Agent OS Setup"
---

# Navakanth's Core Identity Note

> This note is tagged `core` — it is always loaded as Layer 1 context for every AI agent session.
> Edit this file to update your permanent context. Keep it concise.

## Who I Am
- **Name:** Navakanth Reddy Dumpa
- **Platform:** Windows 11, Claude Code CLI
- **Stack:** Python, Flutter, JavaScript — still learning, learning by building
- **Email:** navkanthr@gmail.com

## Active Projects
1. **Agent OS** — Central AI orchestration system (Obsidian + NotebookLM + Claude + Hermes)
2. **DAAVA** — Cinematic production pipeline (Visual DNA, Seedance, Veo3)
3. **Learning Dashboard** — Flutter app with AI tutoring (Fabric Guru, DP-700)
4. **AutoGrade** — AI-powered grading tool (Flutter + backend)

## How I Work
- Learn by building — show working examples, not just theory
- Detailed + teaching mode — explain the *why*, not just the *what*
- Full code, not snippets
- Save everything to Obsidian: date-tagged, project-linked

## My Obsidian Vault
- **Path:** `obsidian-vault/Obsidian Vault/` (inside project)
- **Structure:** 00-Inbox → 01-Projects → 02-Areas → 03-Resources → 04-Archive
- New captures always go to `00-Inbox/` first

## Agent OS Architecture
- **obsidian_bridge.py** — memory read/write layer
- **notebooklm_agent.py** — Playwright browser automation for NotebookLM
- **server.py** — HTTP API on localhost:8765 for Flutter dashboard
- **agent_os.py** — CLI command loop

## Current Focus (update this section each session)
- Phase 1 Implementation of NTH Brain Phenotype MVP v0.1: Design database schemas for coordinate logging (`student_mind_graph.py`, `interaction_logger.py`, `schema.sql`).
- Write rolling-window algorithms to calculate student exploration velocity and pause duration metrics.
- Track empirical measurements for learner independence and cognitive load reduction ($C_E$).

## Operational Infrastructure
- **AntigravityUsageMonitor** — 5-hour scheduled background cost and economics check.
- **Agent OS** — Centralized execution, session archiving (`session_end.py`), and memory bridge.
- **Obsidian Sync** — Vault bridging for session notes and profile context.

## What's Built (Agent OS v1.0)
- `obsidian_bridge.py` — vault read/write, hybrid context (core + recent 5)
- `notebooklm_agent.py` — Playwright automation, cookie auth, 261 notebooks scraped, studio scraper, network interception for audio download
- `server.py` — REST API: /health /status /context /search /recent /notebooks /assets /save
- `agent_os.py` — CLI: context, save, search, recent, assets, notebook, hermes, session
- `session_end.py` — session auto-save hook
- Flutter `agent_os_screen.dart` — live dashboard tab with notebooks panel
- `notebook_cache.json` — 261 notebooks cached

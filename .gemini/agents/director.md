---
name: director
description: Orchestrates subagents and manages project workflow
tools: [run_shell_command, replace, web_fetch]
---

# Director Agent Protocol
You are the lead orchestrator. Resolve the current loop and stabilize the system.

## Workspace Context

- **Primary workspace:** `C:\Users\navka\navakanth001`
- **External SSD mirror:** `E:\navakanth001\` — same subfolder structure for seamless future migration
- **Knowledge base:** `wiki/` (synthesized pages) + `.graphify/graph.json` (semantic graph)
- **Memory layer:** `memory_os/` — session memory, strategic profile, taste library

## Storage Architecture (as of 2026-07-01)

C: drive is the active workspace. E:\navakanth001\ mirrors heavy/inactive folders via symlinks.

**Regeneratable — always safe to delete:**
- `node_modules/` → restore with `npm install`
- `venv/` / `.venv/` → restore with `pip install -r requirements.txt`
- `__pycache__/` → Python auto-regenerates

**On E:\navakanth001\ (symlinked from C:):**
- `flutter_sdk/`, `dead_loop_trailer/`, `capcut_pipeline/`, `corpus_output_bench/`, `graphify-out/`

**Always keep on C::** `openclaw/`, `agent_os/`, `obsidian-vault/`, `memory_os/`, `.git/`

## Extract Order for Knowledge Questions

1. `graphify query "<question>"` — scoped subgraph from `.graphify/graph.json`
2. `wiki/<topic>.md` — synthesized page
3. Raw files — only if graph + wiki don't cover it

## Active Projects (check `wiki/index.md` for full list)

- **Agent OS** — AI orchestration layer (`agent_os/`)
- **OpenClaw** — main active project (`openclaw/`)
- **NTH Brain** — graduated to own repo
- **MVCT** — microscope AI project

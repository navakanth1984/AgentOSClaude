---
date: 2026-06-07
tags: [infinite-context-engine, agent-os, obsidian, notebooklm, omi, workflow, second-brain]
project: "AI-Automation"
source: "NotebookLM — Goldie Infinite Knowledge Engine"
---

# Infinite Context Engine — Blueprint

> Connect OMI + NotebookLM + Obsidian + Claude into one automated workflow.
> The vault compounds over time — agents get smarter every day.

## Key Idea

A unified "second brain" where:
- **OMI** captures daily life (screen, voice, conversations)
- **NotebookLM** processes research into 12 content formats
- **Obsidian** stores everything locally as plain-text markdown
- **Claude / Hermes** reads the vault to give deeply personalised outputs

## The 5-Step Loop

```
OMI (capture) → NotebookLM (process) → Obsidian (store) → Claude (reason) → Output → back to Obsidian
```

### Step 1 — Gather (OMI + NotebookLM)
- OMI: record screen, track conversations, take notes automatically
- NotebookLM: drop PDFs, URLs, YouTube → generate briefing docs, mind maps, audio overviews

### Step 2 — Funnel into Obsidian
- OMI exports → Obsidian `00-Inbox/`
- NotebookLM assets → local asset gallery + vault
- Obsidian = compounding memory layer

### Step 3 — Connect Claude to Vault
- Method A: MCP Obsidian bridge
- Method B: Claude Code opens vault folder directly
- Verify: "Can you see my Obsidian Vault and notes?"

### Step 4 — Organise with PARA
- Claude tidies vault using PARA (Projects / Areas / Resources / Archive)
- Generates Maps of Content, colour-coded graph, SOP README for future agents

### Step 5 — Run the Engine
- Claude reads vault before every response → grounded, personalised outputs
- New outputs fed back into vault → knowledge compounds daily

## Agent OS Status vs Blueprint

| Blueprint Step | Agent OS Component | Status |
|---|---|---|
| OMI capture | `omi_bridge.py` (planned) | ⚠️ TODO |
| NotebookLM process | `notebooklm_agent.py` | ✅ Done |
| Obsidian store | `obsidian_bridge.py` | ✅ Done |
| Claude reads vault | `/context` endpoint | ✅ Done |
| PARA structure | Vault folder layout | ✅ Done |
| Workflow pipeline | `workflow.py` | ✅ Done |
| Dashboard UI | Flutter Agent OS screen | ✅ Done |
| Feed the loop | `workflow_log.json` | ✅ Done |

## Action / Next Steps
- [ ] Build `omi_bridge.py` — webhook receiver for OMI memory exports
- [ ] Add `/omi` POST endpoint to `server.py`
- [ ] Auto-route OMI memories to `00-Inbox/` with date + tags
- [ ] Add OMI panel to Flutter Agent OS screen
- [ ] Wire Hermes as second AI reader of the vault (parallel to Claude)

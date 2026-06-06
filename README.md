# AgentOS — Claude Agent Operating System

A permanent, self-improving AI workspace built on Claude Code. Combines memory, tools, skills, hooks, and parallel agents into a unified operating system for AI-powered work.

---

## What's Inside

| Layer | What it does |
|-------|-------------|
| **Memory** | Permanent session notes in `memory/` — never lose context again |
| **CLAUDE.md** | Architecture file Claude reads every boot — your system's brain |
| **MCPs** | Connectors to OpenRouter, Vercel, search, and live docs |
| **Skills** | Reusable playbooks: scope-feature, data-analysis, ship-summary |
| **Commands** | Custom slash commands: `/ship`, `/workflow`, `/compact-save` |
| **Hooks** | Stop hook auto-saves memory and pushes to GitHub on session end |
| **Sub-agents** | Parallel agent workflows via `/workflow` for massive tasks |

---

## Quick Start

### 1. Clone and configure
```bash
git clone https://github.com/navakanth1984/AgentOSClaude.git
cd AgentOSClaude
cp .env.example .env
# Edit .env with your API keys
```

### 2. Open in Claude Code
```bash
claude .
```
Claude will read `CLAUDE.md` automatically on boot.

### 3. Install MCPs
In Claude Code, open the Connectors menu and add:
- **OpenRouter** — unified LLM access
- **Context7** — latest library documentation
- **Parallel Search** — live web research
- **Vercel or Netlify** — deploy apps instantly

### 4. Drop files in `raw/`
Add PDFs, Excel files, CSVs. Then ask Claude:
> "Analyze the file in raw/ and tell me the key findings."

### 5. Use the system
```
/workflow conduct a full competitor analysis for [product]
/scope-feature build a user login system
/ship
/compact-save
```

---

## Context Health Rules

- Check usage with `/usage`
- Above 50% context → run `/compact-save`
- The stop hook auto-saves and pushes on every session end

---

## Directory Reference

```
AgentOSClaude/
├── CLAUDE.md              ← Session boot instructions
├── .env.example           ← API key template
├── raw/                   ← Source files (gitignored)
├── memory/                ← Session notes and task queue
│   └── tasks.md           ← Active / done task log
├── output/                ← Finished deliverables (gitignored)
└── .claude/
    ├── hooks/
    │   └── stop-save-memory.sh   ← Auto-saves on session stop
    ├── skills/
    │   ├── scope-feature.md
    │   └── data-analysis.md
    └── commands/
        ├── ship.md
        ├── workflow.md
        └── compact-save.md
```

---

## Philosophy

> Don't restart from zero. Build a system that remembers, improves, and compounds.

Every session adds to your permanent knowledge base. Every hook saves your work automatically. Every skill makes the next task faster than the last.

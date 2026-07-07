# Automation Tier Classifier
**Layer 2 — Building Your Jarvis**

> Vending machine or slot machine?
> Know which one you're building before you build it.
> Wrong choice = either an AI agent doing something a bash script should do,
> or a bash script failing to do something that needs reasoning.

---

## The Core Decision

```
TASK
  │
  ├─ Is the output always the same given the same input?
  │   AND can I write the logic as explicit rules?
  │        │
  │        ├─ YES → VENDING MACHINE (script/automation)
  │        │         Deterministic. Cheap. Fast. Never hallucinates.
  │        │
  │        └─ NO  → SLOT MACHINE (AI agent)
  │                  Probabilistic. Expensive. Flexible. Can reason.
  │
  └─ When in doubt: can you write an IF/THEN for every case?
       YES → vending machine
       NO  → AI agent
```

---

## Vending Machine Examples (→ Python/Bash script)

| Task | Why script? |
|:-----|:-----------|
| Rename session files by date | Always same pattern → `os.rename()` |
| Check if memory_os/ has >50 files | Threshold comparison → `len(os.listdir())` |
| Send a daily briefing email | Fixed template + cron → no reasoning needed |
| Convert `.md` to PDF | Format conversion → `pandoc` CLI |
| Count word frequency in screenplay | Deterministic count → `collections.Counter` |
| Pull last 5 session files | Sorted list slice → `sorted(files)[-5:]` |
| Log model usage to JSON | Append to file → `json.dump()` |

---

## Slot Machine Examples (→ AI agent / Claude)

| Task | Why AI? |
|:-----|:-------|
| Evaluate if a scene reaches its beat | Requires narrative judgment |
| Suggest which memory files are stale | Requires semantic understanding |
| Route task to correct model tier | Requires complexity assessment |
| Identify patterns across session logs | Requires synthesis across documents |
| Write the North Star metric for a task | Requires goal clarification |
| Decide if output belongs in taste_library | Requires quality judgment |

---

## The Hybrid Pattern (Most Powerful)

```
Vending machine collects/prepares data
    ↓
AI agent reasons about it
    ↓
Vending machine acts on the decision
```

**Example — Daily Session Brief:**
1. Script: reads last 3 session files, formats as JSON (deterministic)
2. Claude: reads JSON, identifies what's blocking progress (reasoning)
3. Script: writes brief to `00-Inbox/` in Obsidian (deterministic)

This pattern keeps AI costs low (short focused input) and execution reliable (no AI needed for file ops).

---

## Classification Checklist (Run Before Building)

Before starting any automation, answer these:

**Q1: Can I write all the logic as IF/THEN rules?**
→ Yes → Script
→ No → AI agent

**Q2: Will the output be identical every time for the same input?**
→ Yes → Script
→ No → AI agent

**Q3: If it fails, does it fail in a predictable, catchable way?**
→ Yes → Script (add try/except)
→ No → AI agent (add evaluation step)

**Q4: Is the cost of being wrong low?**
→ Yes → Either works
→ No → AI agent + human checkpoint

---

## Your Current Vending Machines (Already Built)

| Script | Location | Function |
|:-------|:---------|:---------|
| `session_end.py` | `memory_os/scripts/` | Save session → Obsidian + memory_os |
| `validate_usage_efficiency.py` | `memory_os/scripts/` | Score model usage efficiency |
| `claude_long_horizon_agent.py` | `memory_os/scripts/` | Long-horizon agentic tasks |
| `Register-UsageTask.ps1` | `memory_os/scripts/` | Register scheduled Windows task |

---

## Build Log

Track automations you create here:

| Date | Name | Type | Input | Output | Status |
|:-----|:-----|:-----|:------|:-------|:-------|
| — | — | — | — | — | — |

---

*Layer 2 of 3 — Jarvis Automation*
*Upstream: north-star-protocol.md | Downstream: taste_library/*

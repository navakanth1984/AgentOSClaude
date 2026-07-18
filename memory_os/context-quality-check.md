# Context Quality Check
**Layer 0 — Foundation of the Agent OS Stack**

> Run this before any multi-step task. A task with poor context produces a generic output,
> no matter how capable the model or how fast you iterate.
> Context Engineering is the substrate everything else runs on.

---

## The Core Principle

Your Agent OS already IS context engineering:
- `CLAUDE.md` = who you are, how you work, what projects are active
- `memory_os/strategic_profile.md` = current focus and routing rules
- `memory_os/session_memory/` = what happened in prior sessions
- `memory_os/long_term_knowledge/` = reference material (screenplays, routing corrections)

The gap: **context quality is never scored before work begins.**
This file fixes that.

---

## Context Quality Scorecard

Run this check before any task that will take more than 5 minutes or produce a file/artifact.

### Domain: What are we working on?
- [ ] The project name is clear (DAAVA, Dead Loop, Agent OS, DP-700, etc.)
- [ ] The specific deliverable is defined (not "help with DAAVA" — "write Act 2 Scene 3")
- [ ] The relevant long-term knowledge file is loaded (if one exists)

**Score: 0–3**

### Audience: Who is this for?
- [ ] The audience is specified (self-use / Claude / external reader / AI model)
- [ ] The tone/style is known (technical, cinematic, concise, teaching mode)

**Score: 0–2**

### Constraints: What are the limits?
- [ ] Format is defined (markdown / screenplay / Python script / JSON)
- [ ] Length or scope is bounded ("~500 words", "one function", "3 scenes")
- [ ] Model tier is appropriate for the task (see `strategic_profile.md`)

**Score: 0–3**

### Success: What does done look like?
- [ ] North Star metric is written (see `north-star-protocol.md`)

**Score: 0–2**

---

## Scoring Thresholds

| Score | Status | Action |
|:------|:-------|:-------|
| 8–10  | ✅ Green — proceed | Start the task |
| 5–7   | ⚠️ Yellow — proceed with caution | Fill the biggest gaps before starting |
| 0–4   | 🔴 Red — stop | Define context first; ask Claude to help scope it |

---

## Quick-Fill Template

When you hit Yellow or Red, paste this and fill it in:

```
Project: [name]
Deliverable: [specific output]
Audience: [who reads/uses this]
Format: [file type / length]
Done = [one sentence — what success looks like]
Model tier: [Tier 1-5 from strategic_profile.md]
Relevant reference file: [path or "none"]
```

---

## How This Feeds the Stack

```
Context Quality Check (this file)
    ↓
North Star Protocol — defines "Done =" metric
    ↓
Automation Tier Classifier — routes task to script or AI agent
    ↓
Taste Library — captures approved outputs for future reference
```

Without a Green score here, the North Star is vague, routing misfires,
and the Taste Library captures the wrong thing.

---

*Layer 0 of 3 — Context Engineering Foundation*
*Stack: context-quality-check.md → north-star-protocol.md → automation-tier-classifier.md → taste_library/*

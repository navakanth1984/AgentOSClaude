# Taste Library
**Layer 3 — Taste & Judgment**

> This directory captures approved outputs — what "excellent" looks like
> across different domains. Claude reads these to calibrate future work
> to your standard, not its default.

---

## How to Use

When Claude produces something you think is excellent:
1. Say: "Save this to taste library — [domain]"
2. Claude creates a file here: `taste_library/[domain]-approved.md`
3. Future sessions: Claude reads the relevant file before producing similar work

When Claude produces something you reject:
1. Say: "Save this as rejected — [domain] — reason: [one sentence]"
2. Claude appends to `taste_library/[domain]-rejected.md`
3. Future sessions: Claude avoids that pattern

---

## Domain Files in This Directory

| File | Domain | Purpose |
|:-----|:-------|:--------|
| `screenplay-approved.md` | Cinematic / Screenwriting | Approved scene structures, dialogue, beats |
| `code-approved.md` | Python / Scripting | Approved code patterns, naming, style |
| `notes-approved.md` | Obsidian / Knowledge | Approved note format, capture style |
| `analysis-approved.md` | Research / Breakdown | Approved analysis structure and depth |

---

## Capture Format

Each approved entry:

```markdown
## [Date] — [Task description]
**North Star:** Done = [what success was defined as]
**Why approved:** [one sentence — what made this excellent]

[The approved output or excerpt]

---
```

Each rejected entry:

```markdown
## [Date] — [Task description]  
**Why rejected:** [one sentence]
**Pattern to avoid:** [specific thing Claude did wrong]

---
```

---

## The Dependency

Taste Library only works when:
1. Context is loaded properly (context-quality-check.md ✅)
2. North Star was defined before the task (north-star-protocol.md ✅)
3. The output can be evaluated against #2

You can't capture "good" if you didn't define it first.

---

*Layer 3 of 3 — Taste & Judgment*
*Upstream: automation-tier-classifier.md | This is the output capture layer*

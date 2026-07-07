# Approved: Code / Scripting

> Captures what "excellent" looks like for Python scripts, bash commands,
> and automation tools in the Agent OS. Claude reads this before any coding task.

---

## Approved Patterns

*(Add entries as you approve outputs — format below)*

### Format

```markdown
## [YYYY-MM-DD] — [Script / task description]
**Language:** [Python / Bash / PowerShell / JS]
**North Star:** Done = [metric used]
**Why approved:** [one sentence]

[Full working code or key excerpt]

---
```

---

## What "Excellent" Means in This Domain

Based on your established preferences and CLAUDE.md:

- **Show full working code** — no partial snippets, no "... rest of code here"
- **Start with what it does** — brief docstring or header comment explains purpose in one line
- **Explicit error handling** — try/except with useful messages, not silent failures
- **File operations**: always use `Path` (pathlib), not string concatenation
- **Naming**: functions are verbs (`read_session_files`), variables are nouns (`session_count`)
- **No boilerplate comments** — only comment what isn't obvious from the code itself
- **Scripts must run on Windows** — account for `\\` paths and PowerShell differences
- **Output**: print meaningful status, not just raw data dumps

---

## Known Working Scripts (Reference)

| Script | Location | Pattern |
|:-------|:---------|:--------|
| `session_end.py` | `memory_os/scripts/` | Read → process → write to Obsidian |
| `validate_usage_efficiency.py` | `memory_os/scripts/` | Read logs → score → report |

---

## Rejected Patterns

*(Add entries when you reject outputs)*

### Format

```markdown
## [YYYY-MM-DD] — [Task]
**Why rejected:** [one sentence]
**Pattern to avoid:** [specific thing]

---
```

---

*Taste Library — Code Domain*
*Update this file: "Save this to taste library — code — [approved/rejected]"*

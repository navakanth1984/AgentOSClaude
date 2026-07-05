# North Star Protocol
**Layer 1 — Iteration Speed**

> Iteration speed without direction is just faster failure.
> The North Star metric defines "Done" in one sentence before any work begins.
> This single habit eliminates 80% of correction cycles.

---

## The Rule

**Before any multi-step task, write one sentence:**

```
Done = [measurable outcome in plain language]
```

This sentence is the evaluator. Every output either satisfies it or doesn't.
No sentence = no evaluation = infinite iterations.

---

## What a Good North Star Looks Like

| Bad (vague) | Good (evaluable) |
|:-----------|:----------------|
| "Improve the screenplay" | Done = Act 2 Scene 3 ends with ARIA making an irreversible choice, ~2 pages |
| "Help with the study plan" | Done = A 4-week DP-700 study schedule with daily tasks and one practice exam per week |
| "Write a Python script" | Done = A script that reads session_memory/ and prints the 5 most recent files with dates |
| "Analyze the article" | Done = A gap analysis showing which of the 6 skills map to my Agent OS and which don't |

---

## When to Write It

- At the start of any task Claude will do autonomously (agentic mode)
- Before any file creation / code generation
- Before any research task that will take >2 tool calls
- Whenever you feel the urge to say "just do something good"

---

## The Evaluation Loop

```
1. Write "Done = [metric]"
2. Claude produces output
3. Ask: "Does this satisfy the North Star?"
   → Yes → done, save to taste_library/ if it's excellent
   → No → identify exactly what's missing, iterate once
   → Still no → context is wrong, go back to context-quality-check.md
```

Maximum 3 iterations before you reset context.
If you're past 3, the North Star was wrong — not the output.

---

## Tie to Model Routing

The North Star also determines model tier:
- Formatting / simple edit → "Done = typos fixed, tone unchanged" → Tier 1
- Novel reasoning / architecture → "Done = three viable approaches with trade-offs" → Tier 4–5
- Write the North Star first, then check `strategic_profile.md` for the right model

---

## Session-Start Addition

Add to every session alongside the Model Economics Checkpoint:

> **North Star for this session:** Done = ___________

Even if it's broad ("Done = one completed scene draft for DAAVA Act 2"), 
having it written prevents the session from becoming an open-ended drift loop.

---

## Log Format (for session memory)

When saving session outputs, include:

```
North Star: [what you set]
Achieved: [yes / partial / no]
Iterations: [number]
What changed: [if you had to redefine it]
```

---

*Layer 1 of 3 — Iteration Speed*
*Upstream: context-quality-check.md | Downstream: automation-tier-classifier.md → taste_library/*

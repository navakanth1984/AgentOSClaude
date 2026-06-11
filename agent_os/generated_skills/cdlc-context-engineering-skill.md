---
name: cdlc-context-engineering-skill
description: >
  Context Development Life Cycle (CDLC) — the discipline of engineering context
  for AI systems. Covers Generate → Test → Distribute → Observe phases.
  Use when designing prompts, skills, agent workflows, or AI context systems.
  Trigger: /cdlc
tags: ["agent-os", "context-engineering", "cdlc", "skill", "ai-workflow"]
---

# CDLC — Context Engineering Skill

> Context is the new code. Without the right fuel, even the most advanced engine fails.

The CDLC mirrors the Software Development Life Cycle (SDLC) — but instead of
managing source code, you manage **context**: instructions, examples, constraints,
and domain knowledge that determine what AI agents actually do.

---

## The Four Phases

```
GENERATE → TEST → DISTRIBUTE → OBSERVE
    ↑                               |
    └───────── (feedback loop) ─────┘
```

### Phase 1 — GENERATE (Craft and Assemble Context)

Move from ad-hoc prompts to reusable, structured context.

| Before | After |
|---|---|
| Manual prompts | Reusable skills (.md, .claudemd) |
| Static markdown | Dynamic context via MCP (GitHub, Slack, tickets) |
| Hardcoded scripts | Spec-driven development (agent breaks specs into plans) |

**Key risk:** Version hallucination — models confuse library v2 with v3.
**Mitigation:** Pull live docs at runtime via MCP, don't rely on training data.

### Phase 2 — TEST (Ensure Context Quality)

Context changes must be tested with the same rigor as code changes.

| Layer | What It Tests |
|---|---|
| 1. Linting/Validation | Format, syntax, length constraints |
| 2. Comprehension Check | Clarity for an agent ("Grammarly for context") |
| 3. LLM-as-Judge | Company-specific conventions and rules |
| 4. E2E Sandbox | Does the generated output actually work? |
| 5. CI/CD + Error Budgets | Non-determinism: expect 80% pass, not 100% |

**Key insight:** LLMs are non-deterministic. Set error budgets (e.g., 80% pass
over 5 runs). This is a paradigm shift from traditional QA.

### Phase 3 — DISTRIBUTE (Share and Secure Context)

High-quality context must scale across teams and systems.

- **Repositories:** Check context into shared repos (zero-friction access)
- **Registries:** Package into versioned skill libraries (like npm for context)
- **Security scanning:** Context packages can expose credentials or carry injected
  instructions — scan with Snyk or equivalent
- **AI SBOM:** Track who built each skill, which model was used, which sources included

**Corporate angle:** Most enterprise AI failures aren't model failures — they're
distribution failures. The right prompt exists somewhere; nobody can find or use it.

### Phase 4 — OBSERVE (Close the Feedback Loop)

Deployed context must be monitored and improved continuously.

- **Agent logs:** Flag "missing context" signals → create globally and distribute
- **PR feedback:** Every reviewer comment about bad AI output = a new eval test case
- **Production telemetry:** Live failures auto-generate new assertions
- **Context filters:** WAF-equivalent for AI — blocks prompt injection at the gate

---

## Context Window Management

### The Vicious Loop Failure Mode
```
Data grows → context limit hit → system breaks
     ↑                                  ↓
     └──── more data accumulated ←──────┘
```

**Two naive fixes that fail:**
- Over-truncation → agent loses past interactions, treats follow-up as new
- LLM summarisation → inconsistent, engineers have no control

### Smart Truncation (correct approach)

| Segment | Action |
|---|---|
| Head (first ~100 chars) = system prompt | Always retain |
| Tail (last ~100 chars) = live state | Always retain |
| Middle = bulk tool outputs, old turns | Store externally, retrieve on demand |

### Hierarchical Memory Architecture

```
Active context window          Memory database
┌─────────────────┐           ┌──────────────────────────┐
│  [HEAD]         │           │  ID: turn_003 → tool output│
│  [TAIL]         │  ──────►  │  ID: turn_007 → trace data │
│  (middle gone)  │           │  ID: turn_011 → search     │
└─────────────────┘           └──────────────────────────┘
```

**Design principle:** *Context decides what the model sees. Memory decides what survives.*

### Hierarchical Sub-Agents

```
Main agent (conversational)
│  Holds: chat history, user state, light context
│  Never loads: raw bulk data
│
└──► Sub-agent (isolated, task-specific)
         Holds: own context + heavy dataset
         Returns: only the final refined result
```

**Mental model:** The main agent is the director. Sub-agents are analysts.
The director reads the summary, not every source document.

---

## Agent OS Integration

### In Obsidian
- Tag notes with `#cdlc` or `#context-engineering`
- Link to notebooks via `/context` command
- Save new patterns with `/save` → `00-Inbox`

### In Workflow Pipeline
- GENERATE phase maps to: `analyze_prompt()` + `find_matching_notebooks()`
- TEST phase maps to: `workflow_log.json` error tracking
- DISTRIBUTE phase maps to: `save_to_obsidian()` with proper frontmatter
- OBSERVE phase maps to: `suggest_actions()` + BIT Integrate logging

### Source Notebook
- [The Infinite Context Engine: Building a Second Brain with Claude](https://notebooklm.google.com/notebook/ebd6175e-0579-4fd4-b654-6a6725567521)
- Run: `python notebooklm_agent.py generate <url> --browser` to capture audio overview

---

## Quick Reference — When to Apply Each Phase

| Situation | Phase to focus on |
|---|---|
| Writing a new skill or prompt | GENERATE |
| Skill produces inconsistent output | TEST |
| Team can't find/use your prompts | DISTRIBUTE |
| AI keeps making the same mistake | OBSERVE → new eval test |
| Context window keeps overflowing | GENERATE (smart truncation) |
| Agent forgets earlier conversation | GENERATE (hierarchical memory) |

---

## CDLC Maturity Checklist

- [ ] Prompts packaged as reusable skills (not copy-pasted each time)
- [ ] Dynamic context injection via MCP (not static markdown)
- [ ] At least 3-layer eval suite per skill
- [ ] Error budget policy (e.g., 80% pass over 5 runs)
- [ ] Skills in version control
- [ ] Agent logs monitored for missing-context signals
- [ ] PR feedback converted into eval test cases
- [ ] Smart truncation implemented (head + tail preserved; middle stored)
- [ ] Memory database with retrievable IDs
- [ ] Long session eval (10 turns → test recall at turn 11)

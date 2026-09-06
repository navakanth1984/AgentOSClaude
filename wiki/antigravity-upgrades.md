# Workspace Productivity Upgrades (Claude Code & Antigravity)
> Four core operational upgrades designed to maximize the business value of both Claude Code and Antigravity by eliminating sycophancy, verifying outputs, managing context rot, and automating execution. Both agents execute these and feed outcomes back into the self-improving knowledge base.

---

## Upgrade 1: The "Roast" Skill (Overcoming AI Sycophancy)

**Problem solved:** AI models are tuned to be agreeable ("sycophancy"). By default, Claude will not push back on bad ideas — it acts as a yes-man. The Roast skill forces adversarial evaluation before any significant investment of time or money.

**Trigger:** Any time a new idea, architecture, feature, or approach needs stress-testing before implementation. In Claude Code, invoke via `/devil` or explicitly prompt "Roast this idea." In Antigravity, trigger the council workflow described below.

### Step 0 — Three Grounding Questions (ask before the council meets)
1. **Target Buyer / Audience:** Who will use or pay for this?
2. **Unique Edge:** What makes this approach better than existing alternatives?
3. **Constraints & Budget:** What are the hard limits (time, money, tech stack)?

### The Council Matrix (five personas)
| Persona | Job | Tools used |
|---|---|---|
| **The Contrarian** | Find fatal flaws, design anti-patterns, show-stoppers | Logic only |
| **The Expansionist** | Identify the highest possible upside, scale, and adjacent revenue | Market intuition |
| **The First Principles Thinker** | Strip assumptions; validate logical consistency from ground zero | Deductive reasoning |
| **The Deep Researcher** | Pull real market data, competitor pricing, prior art | `search_web`, `grep_search`, `graphify query` |
| **The Buyer / User** | Role-play as the actual customer; give blunt purchase intent | Persona simulation |

### The Verdict (Judge Persona)
After all five personas score the idea (each 1–10), the Judge synthesizes a single output:
- **Green Light** — Proceed as scoped.
- **Reshape** — Good core, but pivot X before building.
- **Kill** — Fatal flaw found; stop here.

Final output also includes:
- Top 3 risks (from Contrarian)
- Top 3 upsides (from Expansionist)
- **Single cheapest 48-hour validation test** to confirm or kill the idea before full build

### KB Feed (Roast → Knowledge Base)
- **Approved (Green Light or Reshape):** Write verdict + rationale to `memory_os/taste_library/<domain>-approved.md`
- **Killed:** Write the fatal flaw to `memory_os/long_term_knowledge/model-routing-corrections.md` so future agents don't repeat the same mistake
- **Any Roast run:** Add a one-line entry to `wiki/log.md`: `YYYY-MM-DD | Roast | [idea name] | Verdict: [GL/R/K]`

---

## Upgrade 2: Verification Loops (Making Agents Check Their Own Work)

**Problem solved:** AI-generated code often contains "silent failures" — errors that look complete but crash in production. Studies show a large percentage of raw AI code outputs contain security vulnerabilities invisible to a plain code read.

**Trigger:** After any code generation, before declaring a task done. Both agents must enter this loop before handing off output.

### What verification catches
- **Security vulnerabilities** — hidden flaws in AI-generated code (authentication gaps, injection points, unsafe defaults)
- **Silent task failures** — agent claims it sent 100 emails; it stopped after 25
- **Visual / layout errors** — elements out of bounds, unreadable text, mobile breakage
- **Form edge cases** — fake names, whitespace-prefixed emails, rapid repeated submissions
- **Logic gaps** — missing duplicate guards, invalid state transitions, missing validation

### Verification Pipeline (Claude Code)
1. **Code audit pass** — prompt Claude to review its own output for security and logic gaps before showing you
2. **Visual inspection (web apps)** — use `chrome-devtools-mcp` or `playwright` MCP:
   - Take screenshots at desktop (1280px) and mobile (375px) viewports
   - Verify: all sections visible, no elements clipped, text readable, no console errors
   - Loop: fix → restart server → screenshot again → repeat until zero visible errors
3. **Input stress test** — submit edge-case inputs to all forms and APIs:
   - Empty fields, max-length overflow, special characters (`<script>`, `'--`, emoji)
   - Duplicate submissions (same user twice)
   - Invalid email formats (spaces, no `@`, `.` at the end)
4. **Logic check** — confirm all state transitions, duplicate guards, and routing work

### Verification Pipeline (Antigravity)
Same as above, using Antigravity's browser automation tools. For code tasks, run equivalent tool calls to open the UI, screenshot, and iterate.

### Loop exit condition
The loop does not exit until **zero visible errors remain across all viewports and all edge-case inputs are handled without crashes.**

### KB Feed (Verification → Knowledge Base)
- Write newly discovered edge cases to `sources/technical/` as a test checklist entry
- Update `memory_os/north-star-protocol.md` if verification reveals the original Done metric was too loose
- If a pattern (e.g., "Claude always misses duplicate guards") repeats across sessions, add it as a standing rule in `memory_os/long_term_knowledge/`

---

## Upgrade 3: Managing "Context Rot" (Session Handoff Protocol)

**Problem solved:** As conversation length grows, AI performance degrades — worse design choices, sloppier code, dropped requirements. This happens long before the token limit is hit. The fix is to actively monitor token usage and execute a clean handoff when needed.

**Context rot threshold:** In Claude Code, run `/context` periodically. Do not let token usage exceed **~250,000 tokens** without a handoff. In Antigravity, watch for degraded output quality as a proxy signal.

### Handoff Trigger Conditions
- Token usage approaching 250K
- Noticeably worse code quality or forgotten constraints
- Switching to a new project phase or task area
- End of any working session

### Handoff Summary Format
Write to `memory_os/session_memory/YYYY-MM-DD-handoff-[project].md`:

```markdown
---
date: YYYY-MM-DD
project: [name]
context_tokens_at_handoff: [number]
---

## Current Status
[What is done, what is in-flight]

## Key Files
- [file path] — [one-line purpose]

## Locked Decisions (do not revisit)
- [decision] — [reason it's locked]

## Next Steps
- [ ] [action 1]
- [ ] [action 2]
```

### Handoff Execution
- **Claude Code:** Write handoff → user runs `/clear` → user pastes handoff into fresh session
- **Antigravity:** Write handoff → start new Antigravity session → load handoff as initial context
- Both agents resume from the handoff file; no re-explaining is needed

### KB Feed (Handoff → Knowledge Base)
- Handoff files are the authoritative "last known good state" for a project thread
- Reference the handoff path in `wiki/log.md` so it's findable
- After the next session completes, the handoff file can be superseded by the new one (never delete old ones — they are a timeline)

---

## Upgrade 4: Breaking the Human Bottleneck (Sub-agents & Objective Goals)

**Problem solved:** If you manually direct one AI at a time, you become the bottleneck. Sub-agents + objective completion criteria let you frontload all thinking into one prompt, walk away, and return to finished work.

**Anthropic's own engineering team found multi-agent setups outperformed single agents by over 90% on complex tasks.**

### Sub-agent Deployment Pattern
Spin up independent sub-agents for tasks that do not need to coordinate in real-time. Each sub-agent gets:
- Its own **clean context window** (no shared rot)
- A **single, specific deliverable** (not "help with X")
- A **strict file output path** (so agents don't overwrite each other)

Example split for a go-to-market kit:
| Sub-agent | Task | Output file |
|---|---|---|
| Research agent | List 7+ competitors with pricing | `gtm/market-research.md` |
| Strategy agent | Draft launch plan in 5 phases | `gtm/launch-plan.md` |
| Outreach agent | Write 25 personalized email drafts | `gtm/outreach-drafts.md` |

### `/goal` — Objective Completion Criteria
Use the `/goal` command (Claude Code) or equivalent evaluator prompt to set quantitative Done conditions a separate evaluator agent checks turn-by-turn.

**Good goal example:**
```
GOAL: All six deliverable files must exist and not be empty.
Market research must list at least 7 competitors with pricing.
Outreach drafts must total exactly 25 entries.
Final pass: open each file and fix any content that is too thin or generic before declaring done.
```

**Bad goal example:** "Build the GTM kit" — too vague; agent will self-declare done too early.

### Evaluator Agent Role
A separate AI instance (not the builder) reads each file and scores against the criteria. It does **not** declare done until all quantitative conditions are met AND a quality pass confirms no thin/generic content remains.

### Walk-Away Checklist
Before stepping away from a parallel sub-agent run, confirm:
- [ ] Each sub-agent has a single deliverable with a named output file
- [ ] `/goal` or evaluator criteria are quantitative, not vague
- [ ] A verification pass is included in the goal (evaluator opens each file)
- [ ] A handoff will be written at the end (feeds Upgrade 3)

### KB Feed (Sub-agent Runs → Knowledge Base)
- Record run summaries in `wiki/log.md`: `YYYY-MM-DD | Sub-agent run | [project] | [N agents] | [outcome]`
- Save effective agent prompts to `sources/technical/agent-prompts/` for reuse
- If an evaluator rejects output and the agent loops more than 3 times, that pattern is a signal the goal criteria were wrong — log it in `memory_os/long_term_knowledge/`

---

## Cross-Upgrade Sync Contract

Both Claude Code and Antigravity operate on the same KB. Every upgrade feeds the same locations:

| Upgrade | Feeds into |
|---|---|
| Roast verdicts | `memory_os/taste_library/` + `wiki/log.md` |
| Killed ideas | `memory_os/long_term_knowledge/model-routing-corrections.md` |
| Verification edge cases | `sources/technical/` test checklists + `memory_os/north-star-protocol.md` |
| Session handoffs | `memory_os/session_memory/` + `wiki/log.md` |
| Sub-agent run summaries | `wiki/log.md` + `sources/technical/agent-prompts/` |
| Failed goal patterns | `memory_os/long_term_knowledge/` |

The `wiki-nightly-ingest` scheduled task (2:06 AM) sweeps these locations and propagates new material into wiki pages, keeping both agents in sync without manual intervention.

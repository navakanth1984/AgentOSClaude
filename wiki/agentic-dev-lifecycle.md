# Agentic Development Lifecycle
> The complete, mandatory lifecycle every agent must follow in this workspace — from idea validation through work tree creation, development, PR, staging, production deployment, and KB handoff.

This extends [development-lifecycle.md](development-lifecycle.md) with agentic-specific stages: idea pre-flight, isolated work trees, sub-agent delegation, model routing, PR integration, deployment, post-production monitoring, and context rot management. Every non-trivial change must travel the full path.

**Grounded in real sessions:** every rule below was added because a past session either failed without it or succeeded because of it. Sources: [lessons_learned.md](../memory_os/long_term_knowledge/lessons_learned.md), [antigravity-upgrades.md](antigravity-upgrades.md), [karpathy-mandates.md](karpathy-mandates.md), [wiki/log.md](log.md).

---

## The 8-Stage Lifecycle

```
STAGE 0          STAGE 1          STAGE 2          STAGE 3          STAGE 4
Pre-Flight  →    Work Tree   →    Develop     →    Verify      →    Integrate
(Roast/Plan)     Creation         (isolation)      (tests/CI)        (PR → merge)
                                                        ↓
STAGE 5          STAGE 6          STAGE 7          STAGE 8          STAGE 9
Deploy      →    Validate    →    Monitor     →    Graduate    →    KB Handoff
(staging)        (staging QA)     (production)     (own repo?)      (wiki + log)
```

---

## Stage 0 — Pre-Flight (Before Any Code is Written)

**Who:** Agent + user, before branching.

> **Learned from:** Multiple sessions where we built features that turned out to be scoped wrong, over-engineered, or missed a simpler path. The Roast + Karpathy steps prevent wasted cycles.

### 0a — Roast the Idea First (non-trivial features only)
For any new feature, architecture choice, or approach that will take more than 30 minutes:
- Run the **Roast council** (Contrarian, Expansionist, First Principles, Deep Researcher, Buyer) — see [antigravity-upgrades.md](antigravity-upgrades.md) for the full protocol.
- Answer the 3 grounding questions: **Who is the target user? What is the unique edge? What are the hard constraints?**
- Verdict: **Green Light / Reshape / Kill** — if Kill, stop here and do not branch.
- Log verdict to `wiki/log.md`: `YYYY-MM-DD | Roast | [idea] | Verdict: GL/R/K`

### 0b — Karpathy Pre-Flight (all code tasks)
Before writing or modifying any code:
1. **Think before coding** — fully understand the problem, plan the architecture, anticipate edge cases.
2. **Prioritize simplicity** — if it can be done in 10 lines, do not use 100.
3. **Surgical scope** — only touch code that absolutely needs to change. Do not refactor unrelated components.
4. **Goal alignment check** — state the exact Done condition before starting. Vague goals produce self-declared-done failures.

### 0c — Model Routing Check
> **Learned from:** Using Opus 4.8 for entire sessions that were 80% codegen — a Tier 1/2 task. Expensive and unnecessary.

Before starting, select the correct model tier:
| Task type | Correct model |
|---|---|
| Architecture, design decisions, RFCs | Claude Sonnet/Opus (high reasoning) |
| Codegen, feature implementation, bug fixes | Gemini 2.5 Flash (Tier 1/2) |
| Research, web search, quick lookups | Flash Low / Gemini Flash |
| Parallel sub-agent bulk work | Flash Low (cost-efficient) |

If the task switches type mid-session, switch model. Log mismatches to `memory_os/long_term_knowledge/model-routing-corrections.md`.

---

## Stage 1 — Work Tree Creation (Isolation)

**Who:** Main agent or user at conversation start.

- If working on a new feature/experiment: create an isolated Git work tree.
  - In the **Desktop App**: start a new conversation → select **"New Work Tree"**.
  - In the **CLI**: agent automatically uses `invoke_subagent` with `Workspace: "branch"` to isolate work.
- The work tree checks out a new branch (`feat/<name>` or `milestone/<name>`) without touching `master`.
- **Agent must announce:** *"Creating an isolated Git work tree on branch `feat/xyz`..."*

> **Reminder:** You never need to manage this manually. The system auto-creates and auto-cleans up the work tree.

---

## Stage 2 — Development (In Isolation)

**Who:** Sub-agent(s) or main agent inside the work tree.

- All code changes happen **only** on the feature branch — never directly on `master`.
- Multiple sub-agents may work in parallel in their own isolated work trees.
- Each sub-agent operates within inherited permission boundaries.
- **Agent must announce** when sub-agents are spawned: *"Delegating X to a sub-agent in its own isolated work tree..."*

---

## Stage 3 — Verify (Before Integration)

**Who:** Agent, before opening a PR.

All of the following must pass before the PR is opened:

| Check | Command | Gate |
|---|---|---|
| Type safety | `pyrefly` | Hard block — never `--no-verify` |
| Unit + integration tests | `pytest` | Must be green |
| Live execution | Real run, not just types | Agent must confirm |
| Architecture invariants | See `INVARIANTS.md` | No regressions |
| API compliance | `pyright` or equivalent | No breaking changes |

- **Agent must NOT claim "done" without running these.**
- If CI is configured on GitHub, the PR must show all checks green before merge.

---

## Stage 4 — Integrate (PR → Merge)

**Who:** Agent opens PR; user authorizes merge.

1. **Work tree is cleaned up** (auto) after the branch is pushed.
2. **Agent opens a PR** immediately: `gh pr create --base master --title "feat: ..."`.
3. **Agent announces:** *"Work tree cleaned up. PR #N is open at `<url>` — awaiting your review."*
4. PR must include:
   - What changed and why (conventional commit style: `feat:`/`fix:`/`refactor:`/`docs:`)
   - Test evidence (which tests ran, their output)
   - `Co-Authored-By: Claude/Antigravity` trailer
5. **Task is NOT "done" until the PR is open.** Branch-only work is not the finish line.
6. User reviews → CI passes → merge (one revertable merge commit) → branch deleted.

> **Important:** Agent self-merge is blocked by promotion authority. Always surface the PR to the user.

---

## Stage 5 — Deploy to Staging

**Who:** Agent (automated) or user (manual trigger).

- After merge to `master`, trigger a deployment to the **staging environment**.
- For projects using Azure / Vercel / Cloud Run:
  - Azure: `az webapp deploy` or pipeline trigger
  - Vercel: `vercel --prod=false` (preview deployment)
  - Cloud Run: `gcloud run deploy --no-traffic`
- **Agent announces:** *"Deploying to staging environment..."*
- Record the staging URL or deployment ID in the session.

---

## Stage 6 — Validate on Staging

**Who:** Agent (automated checks) + user (manual UAT where needed).

- Run smoke tests against the live staging endpoint.
- For web UIs: use `chrome-devtools-mcp` (screenshots, form inputs, viewport check).
- For APIs: `curl` smoke tests against the staging URL.
- For data pipelines: run a dry-run or sample ingestion.
- **Agent must report:** pass/fail per check, not just "it works."
- If validation fails → agent creates a fix branch and restarts from Stage 2. Does NOT promote to production.

---

## Stage 7 — Production Deployment & Monitoring

**Who:** User authorizes; agent executes.

> **Learned from:** nthdimensionacademy.com fatal React crash on live Vercel caused by missing Firebase env vars — a staging validation gap that made it to prod. And the audiobook pipeline that passed unit tests but crashed under real load (863 sequential HTTP chunks → OpenBLAS abort). Both were caught only after prod deployment.

- Production deployment only after Stage 6 is green.
- **Agent announces:** *"Staging validation passed. Ready to promote to production — your approval needed."*
- After user approval:
  - Execute production deployment command.
  - Confirm the deployment is live (health check / status endpoint).
- **Active monitoring window — first 15 minutes after every prod deploy:**
  - Error rates, latency, crash logs.
  - For web apps: take a live screenshot via `chrome-devtools-mcp` and confirm no console errors.
  - For APIs: run `curl` smoke test against the production URL (not staging).
  - For data pipelines: confirm at least one real record processed end-to-end.
  - Alert the user immediately if any anomaly is detected.
- **Agent must NOT auto-promote to production without explicit user approval.**
- If prod deploy fails: rollback first, then investigate. Do not investigate on live traffic.

---

## Stage 8 — Project Graduation Gate (when applicable)

**Who:** Agent flags; user decides.

> **Learned from:** The staging workshop pattern — projects like `nth-brain`, `mvct-v1`, `agent_os`, `nthdimensionacademy` live in this root repo until they are ready for their own repo. Graduating too early creates orphaned repos; graduating too late creates a messy monorepo.

Check these signals after a successful production deploy:
- Does this project have its own domain / URL in production?
- Does it have its own CI/CD pipeline?
- Does it have 3+ contributors or external users?
- Is it large enough that changes to it pollute unrelated PRs in this repo?

If **2 or more** of the above are true, propose graduation:
1. Run `graduate-project.ps1` (already built in this workspace) to auto-create a new GitHub repo.
2. Update `wiki/knowledge-base-map.md` to move the project to the "Graduated" section.
3. Add a thin overview wiki page in this repo pointing to the new repo.
4. **Never delete the original folder** — gitignore it here, but keep it as a reference.

---

## Stage 9 — KB Handoff (Memory + Wiki)

**Who:** Agent, at the end of every significant work item.

> **Learned from:** Multiple sessions where work was completed but not logged, causing the next session to rediscover what was already done. Context rot compounds this — after ~250K tokens, the agent's recall degrades and undocumented work gets repeated.

### Context Rot Check (do before handoff)
- Run `/context` in CLI — if token usage is approaching **~250K tokens**, execute a clean handoff immediately.
- Signs of context rot mid-session: agent forgets earlier constraints, produces lower-quality code, revisits locked decisions.
- If rot is detected: write the handoff now, start a fresh session, resume from the handoff file.

### Handoff Format
Write to `memory_os/session_memory/session_<YYYYMMDD>.md`:
```markdown
## Current Status
[What is done, what is in-flight, branch + PR state]

## Key Files
- [file path] — [one-line purpose]

## Locked Decisions (do not revisit)
- [decision] — [reason it's locked]

## Next Steps (P0/P1/P2)
- P0: [blocking / must-do-next]
- P1: [high value, do soon]
- P2: [nice to have]
```

### KB Close-Out (every session end)
1. **Log:** Add a dated line to `wiki/log.md` (PR #, branch, key decisions, lessons).
2. **Wiki:** Update or create the relevant `wiki/<topic>.md` page.
3. **Next Steps:** Create or update `wiki/<topic>-next-steps.md` (P0/P1/P2, file pointers, acceptance criteria).
4. **Lessons:** If a new pattern was discovered (a bug class, a model mismatch, a tool quirk), write it to `memory_os/long_term_knowledge/lessons_learned.md`.
5. **Cross-session buffer:** Refresh `.remember/remember.md`.
6. **Run session end scripts:**
   ```powershell
   py -3 memory_os/scripts/validate_usage_efficiency.py
   py -3 agent_os/session_end.py
   ```

---

## Quick Reference Card

| Stage | Action | Agent Announcement |
|---|---|---|
| 0 | Pre-flight: Roast + Karpathy + model routing | *"Roast verdict: GL/R/K. Model: [X]. Proceeding with plan..."* |
| 1 | Work tree created | *"Creating isolated work tree on branch `feat/xyz`..."* |
| 2 | Sub-agent spawned | *"Delegating to sub-agent in its own work tree..."* |
| 3 | Verify passes | *"All checks green: pyrefly ✅ pytest ✅ live run ✅"* |
| 4 | PR opened | *"Work tree cleaned up. PR #N open — awaiting review."* |
| 5 | Staging deploy | *"Deploying to staging..."* |
| 6 | Staging validated | *"Staging QA passed ✅ / Failed ❌ on [check]"* |
| 7 | Prod deploy + 15-min monitor | *"Live ✅. Monitoring for 15 min. No anomalies detected."* |
| 8 | Graduation check | *"Graduation signals: [N/4 met]. Proposing graduation? Y/N"* |
| 9 | KB updated | *"Wiki + log + lessons + session memory updated. Handoff ready."* |

---

## Guardrails (Never Violate)

- **Never build without a Stage 0 pre-flight** for non-trivial features. Roast first.
- **Never commit directly to `master`.** Always branch → PR → merge.
- **Never skip Stage 3 verification.** Tests must run; pyrefly must pass. `--no-verify` is forbidden.
- **Never self-merge PRs.** Surface all PRs to the user for authorization.
- **Never promote to production without explicit user approval.**
- **Never skip the 15-minute prod monitoring window.** Crashes happen post-deploy.
- **Never close a session without Stage 9** (log + wiki + lessons + session memory).
- **Always announce work tree creation, sub-agent delegation, and cleanup.**
- **Never investigate a prod failure on live traffic.** Rollback first, diagnose second.
- **Never run the same model for the whole session** if the task type changes. Switch model tier when work switches from design to codegen.
- **Never leave context rot unmanaged.** Handoff at ~250K tokens — do not push through it.

Source: [AGENTS.md](../AGENTS.md) · [development-lifecycle.md](development-lifecycle.md) · [CI_GATE.md](../CI_GATE.md) · [antigravity-upgrades.md](antigravity-upgrades.md) · [karpathy-mandates.md](karpathy-mandates.md)

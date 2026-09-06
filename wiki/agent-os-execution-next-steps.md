# Agent OS Execution Framework — Handoff (Mixture-of-Agents Phase 1)

> Cold-start handoff doc. Assumes zero prior context. For the Agent OS overview page (dashboard, server, existing tabs), see [agent-os.md](agent-os.md).

---

## HANDOFF TO ANTIGRAVITY (2026-07-05, Execution Framework Phase 1 shipped, read this section first)

**Branch:** `feat/agent-os-execution-framework` on `C:\Users\navka\navakanth001` (this repo), base `master`. **PR #29 open, not yet merged/reviewed.**

### Why this branch exists

The user asked whether a mixture-of-agents (MoA) pattern — parallel inference across multiple LLMs, then aggregation into one answer — could be built on the **TITAN/CRP** framework and integrated into the **Agent OS dashboard**. Two Explore agents checked both candidates directly against the code:

- **CRP/TITAN rejected.** `docs/vision/TITAN.md` and `crp/` are exclusively about tensor *representation* optimization (Dense vs Int8 vs Sparse for compute workloads — see `crp/runtime/crp_runtime/policy.py`). Gate 2 is frozen (`crp/docs/GATE2-CONFORMANCE.md`), governance requires an RFC + empirical evidence for any new capability, and CRP's policy engine has no concept of "LLM model," "prompt," or "aggregation." Wiring MoA in there would violate the frozen scope for no benefit.
- **Agent OS dashboard accepted.** It already had dormant infrastructure built for exactly this (`agent_os/cinematic_model_router.py`'s `HybridGenerationRouter`, `agent_os/router_protocol.py`'s provider protocols) — but only serving the Cinematic OS subsystem, not the main dashboard tabs. Swarm/Goal/SiteBuilder each call a single hardcoded model with no voting/aggregation. This was the gap to fill.

The user then asked for something more ambitious than a single new tab: MoA as one of several **execution modes** (Single/Swarm/Mixture/Debate/Auto) usable from any workflow, with a multi-stage aggregation pipeline and curated model profiles. Across several rounds of review, the design converged — and was then explicitly reined back in — on a **generic execution framework** (`ExecutionManager → Executor → Aggregator`) with MoA as the first advanced executor, rather than more speculative layers (Planner, ExecutionGraph, EventBus, Provider Registry, Policies, caching) stacked on top before any code had run once. Those layers were deliberately deferred with **objective triggers** recorded (see below) instead of built speculatively — this is the load-bearing decision of the whole session; do not re-add them without one of the triggers actually firing.

Full plan file (context, architecture rationale, phasing): `C:\Users\navka\.claude\plans\yep-that-s-the-basic-golden-sprout.md` on the machine this was authored on — not committed to the repo, so treat this wiki doc + the PR description as the durable record if that file isn't available to you.

### What shipped (Phase 1) — verified live, not just asserted

New package `agent_os/execution/`:
```
execution/
  __init__.py            # ExecutionManager (mode -> Executor lookup); documented Planner seam, not implemented
  execution_modes.py      # ExecutionMode enum: SINGLE, SWARM, MIXTURE, DEBATE(stub), AUTO(stub)
  manifest.py              # ExecutionManifest dataclass + JSON persistence -> agent_os/output/execution_manifests/
  executors/
    base.py, single.py, swarm.py (adapter over existing swarm.py), mixture.py (the real work),
    debate.py (NotImplementedError stub), auto.py (NotImplementedError stub, AutoPlanner interface only)
  aggregation/
    base.py (Aggregator protocol + AggregationResult TypedDict), fast.py, standard.py, verified.py,
    confidence.py (evidence-based scoring: pairwise textual agreement + optional parsed judge score —
    never an LLM asked to invent its own confidence number)
  providers/
    capabilities.py (profile -> curated model list; Phase 2 wires this to HybridGenerationRouter's
    live provider health/cost instead of a static table)
```

- `POST /execute` + `/execute/status` added to `server.py` (~line 1723, right before `/swarm`), following the exact async-job + status-file polling pattern already used by `/sitebuilder` + `/sitebuilder/status`.
- Dashboard: Swarm tab (`dashboard.html`) got an "Execution Mode" radio (Swarm / Mixture) that swaps in a Mixture panel — model profile picker, Fast/Standard/Verified aggregation picker, live per-model streaming status line, and a 3-pane results view (Final Answer + confidence/consensus, Model Contributions accordion, Reasoning Timeline).
- `.claude/launch.json` got a new `agent-os-server` entry (`py -3 agent_os/server.py`, port 8765) — previously only the static-file `agent-os-dashboard` entry existed, so there was no way to preview-launch the actual backend.

**Verified this session, live, not just unit-tested:**
- `py -3 -m pyrefly check agent_os/execution` — 0 errors (had to fix 5 `bad-assignment` errors by adding an `AggregationResult` TypedDict; pyrefly was inferring an untyped dict union otherwise).
- Killed and restarted the real `agent_os/server.py` process on port 8765 (had an active connection — user explicitly approved the restart first).
- `curl` smoke test, `fast` aggregation, 2 free models: correct final synthesis, manifest fields populated.
- `curl` smoke test, `standard` aggregation, 2 free models: agreement/conflict analysis stage ran, consensus_score 0.926 computed from real pairwise text similarity (not invented), manifest JSON confirmed written to `agent_os/output/execution_manifests/*.json`.
- Full browser UI round-trip via Claude Preview tooling: filled the real `#mix-prompt` input, ran a 3-model Budget-profile Fast-aggregation job through the actual `runMixture()` JS function (not a bypass), confirmed all 3 result panes rendered with real data and the per-model streaming status line updated live during fan-out.
- `/health` re-checked after both mixture runs — server still healthy, existing routes unaffected.

### A real bug found and fixed along the way (not hypothetical)

Local `npx serve` (used only for previewing `dashboard.html` as static files) rewrites `/dashboard.html` → `/dashboard` and strips query strings on that rewrite. The dashboard's own API-base-detection heuristic (`window.location.pathname === "/dashboard"` ⇒ "I must be served by the real backend") was fooled by this into pointing API calls at the static file server (port 5505) instead of the real backend (port 8765), producing `"<!DOCTYPE ..." is not valid JSON` errors. **This is a test-harness artifact only** — in real use `server.py` serves the dashboard itself on 8765, so the heuristic is correct there. Fixed for this session's testing via `localStorage.setItem('agentos_api', 'http://localhost:8765')`; no code change was needed or made. Flagging so a future session doesn't waste time rediscovering this if using the same static-preview approach.

### Explicitly out of scope / NOT done — objective triggers for revisiting

Per the plan, do **not** build these speculatively — only when the specific trigger below is actually observed in real use of Phase 1:

| Trigger | Action |
|---|---|
| An executor needs branching or iterative revision (e.g. Debate) | Introduce `Planner` |
| Multiple executors duplicate the same planning/selection logic | Introduce `ExecutionPlan` |
| A workflow stops being a linear pipeline and becomes a DAG | Introduce `ExecutionGraph` |
| Multiple consumers (dashboard + CLI + logs) need real-time execution events | Introduce an event system |

Also not done, not forgotten:
- `executors/debate.py` and `executors/auto.py` are `NotImplementedError` stubs — interfaces only, per Phase 2/Phase 3 deferral in the plan.
- `providers/capabilities.py`'s profile→model mapping is a static curated table. Phase 2 wires it to `cinematic_model_router.py`'s `HybridGenerationRouter` for live cost/latency-aware picks — deliberately not done yet.
- Only the Swarm tab got the Execution Mode selector. The other 15 dashboard tabs are untouched — a full cross-tab rollout is a separate, larger migration once this pattern is validated with real usage, not part of this pass.
- No change to `crp/`, `docs/vision/TITAN.md`, or CRP's policy/harness/IR compiler — confirmed out of scope by design, not an oversight.

### Immediate next step

1. Review/merge PR #29 (or request changes).
2. Once merged, decide whether to continue with Phase 2 (Debate executor body, capability-router wiring) or let the Mixture mode get real usage first before expanding — the user's own stated preference this session was evidence-based evolution over speculative expansion, so lean toward "use it, then decide" unless directed otherwise.
3. Do not add Planner/ExecutionGraph/EventBus/Policies/Provider Registry/caching without one of the triggers in the table above actually firing — that restraint was the explicit, hard-won outcome of this session's design discussion.
## HANDOFF TO ANTIGRAVITY / CLAUDE (2026-07-05, Phase 2.1 Complete, Proceed to Phase 2.2 Debate)

**Branch:** eat/agent-os-execution-framework on C:\Users\navka\navakanth001 (this repo), base master.

### What shipped (Phase 2.1 - Routing & Auto Mode)
-  gent_os/execution/executors/auto.py: Implemented AutoPlanner, returning a frozen PlanningResult.
-  gent_os/execution/routing.py: Extracted pure DeterministicRoutingPolicy and TaskClassifier (with heuristic-based categorization and normalizations). Introduced RoutingContext which contains original ExecutionRequest, category, and classifier_version.
-  gent_os/execution/__init__.py: Cleaned up ExecutionManager to route AUTO logic through the pure RoutingPolicy logic before executor dispatch. Includes runtime tracing of outing_time_us.
-  gent_os/docs/governance/ADR-004-auto-mode-policy-layer.md: Solidified the determinism and immutability invariants (matched_rules tuple, perfect determinism).
- Extensive unit tests covering purity (masking file I/O, network, socket), determinism (100 run hash checking), unknown fallbacks, and task matching.

## HANDOFF TO ANTIGRAVITY / CLAUDE (2026-07-07, Phase 2.3 Tau Integration Complete)

**Branch:** `feat/openrouter-model-fix` on `C:\Users\navka\navakanth001` (this repo), base `master`.

### What shipped (Phase 2.3 - Tau Integration & Backoff)
- **`agent_os/execution/executors/tau_executor.py`:** Created a specialized `TauExecutor` wrapping `tau_agent.AgentHarness` to execute task prompts via `tau-ai`'s asynchronous state machine loop.
- **`agent_os/execution/execution_modes.py`:** Added `ExecutionMode.TAU` enum (`"tau"`).
- **`agent_os/execution/__init__.py`:** Registered `TauExecutor` in the pluggable `ExecutionManager`.
- **`agent_os/openrouter_client.py` & `agent_os/cloud_agent_runner.py`:** Integrated exponential, jittered backoffs honoring `Retry-After` headers for all transient 429/5xx errors to prevent API quota exhaustion.
- **Tests:** All **26/26 unit tests passed successfully** (`pytest tests/ -v`).

### Immediate next steps
1. **Live Prompt Testing:** Trigger real execution requests using `ExecutionMode.TAU` to verify the `AgentHarness` loop behavior with live tool calls.
2. **Provider Failures:** Validate the fallback behavior when the OpenRouter/Gemini keys are completely disabled or rate-limited.
3. **Obsidian Persistence:** Ensure that when runs finish, their execution traces populate the Obsidian vault as structured documents.

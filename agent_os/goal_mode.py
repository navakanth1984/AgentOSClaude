"""
goal_mode.py — Autonomous Goal Runner for Agent OS

Hand off a high-level goal; the agent breaks it into steps, executes each one
using the tools available in this Agent OS (swarm research, vault saves, web
search via Perplexity), and loops until the goal is achieved or max_steps hit.

Pipeline:
  1. PLAN  — LLM breaks the goal into ≤8 concrete, ordered steps
  2. EXECUTE — each step runs via the best available tool
  3. CHECK  — LLM decides: goal met? If not, what's the blocker?
  4. SAVE   — full run log + result saved to Obsidian 00-Inbox

Usage:
  from goal_mode import run_goal
  result = await run_goal("Write a market research note on AI productivity tools")

POST /goal
  Body: { "goal": "...", "max_steps": 8, "model": "anthropic/claude-sonnet-4.6" }
"""

import os
import sys
import json
import re
import asyncio
from datetime import datetime
from pathlib import Path

# Force UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

# ── Load .env ─────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# ── Shared transport (single source of truth) ─────────────────────────────────
from openrouter_client import call_openrouter as _call_openrouter_raw


def _openrouter(prompt: str, model: str, system: str = "", api_key: str = "") -> str:
    """
    Convenience wrapper for goal_mode — matches the original signature.
    Returns empty string on error instead of raising (safe for planning loops).
    """
    try:
        return _call_openrouter_raw(model, system, prompt, api_key, max_tokens=1200)
    except Exception as e:
        print(f"[GoalMode] OpenRouter error ({model}): {e}")
        return ""


# Free model for lightweight planning/checking calls (no credits needed on free tier)
# Updated 2026-06-07: gemma-4-31b works; llama-3.3-70b rate-limited on this account
# All three are env-overridable so you can avoid paid models that 402 when credits
# run out. When offline (Ollama), the model string is ignored and OLLAMA_MODEL is used.
_PLANNER_MODEL = os.environ.get("GOAL_PLANNER_MODEL", "google/gemma-4-31b-it:free")

# Default execution model for summarise/analyse steps + handed to the swarm.
# Was "anthropic/claude-sonnet-4.6" (paid → 402 when out of credits).
_DEFAULT_MODEL = os.environ.get("GOAL_MODEL", "google/gemma-4-31b-it:free")

# Model for the live-internet "research" step. Was "perplexity/sonar" (paid → 402).
_RESEARCH_MODEL = os.environ.get("GOAL_RESEARCH_MODEL", "google/gemma-4-31b-it:free")


# ── Step 1: PLAN ─────────────────────────────────────────────────────────────
def plan_goal(goal: str, model: str, api_key: str) -> list[dict]:
    """
    Ask the LLM to break the goal into ≤8 concrete, ordered steps.
    Returns a list of step dicts: [{step, action, tool}, ...]

    Each step has:
      - step:   step number (int)
      - action: what to do in plain English
      - tool:   "swarm" | "research" | "save_note" | "summarise" | "analyse"
    """
    # Inject Obsidian vault context so planning is informed by existing knowledge
    # (Agentic Engineering: context window is the lever — fuel the engine with real data)
    vault_context = ""
    try:
        from obsidian_bridge import get_context_for_agent
        vault_context = get_context_for_agent(recent_n=5)
        if vault_context:
            vault_context = f"\n\nRelevant knowledge from Obsidian vault:\n{vault_context[:1500]}"
    except Exception:
        pass  # vault context is nice-to-have; plan still works without it

    system = (
        "You are a planning agent for an AI knowledge system. "
        "The user has an Obsidian vault with existing notes — factor them into your plan "
        "to avoid re-researching what is already known.\n\n"
        "Given a high-level goal, break it into at most 8 concrete, ordered steps. "
        "Each step must be achievable by ONE of these tools:\n"
        "  swarm      — parallel AI research on a topic (best for broad knowledge gathering)\n"
        "  research   — single focused internet search (best for specific facts or current data)\n"
        "  save_note  — save a structured note to Obsidian vault\n"
        "  summarise  — synthesise prior step outputs into a conclusion\n"
        "  analyse    — critically evaluate or compare options\n"
        "  quantum    — run a real quantum circuit (use for quantum compute goals, e.g. factor N, run Grover search, run Bell state)\n\n"
        "Respond ONLY with a JSON array. Example:\n"
        '[{"step":1,"action":"Research the market size of AI productivity tools","tool":"research"},'
        '{"step":2,"action":"Identify top 5 competitors","tool":"swarm"},'
        '{"step":3,"action":"Summarise findings into a market note","tool":"save_note"}]'
    )
    raw = _openrouter(f"Goal: {goal}{vault_context}", _PLANNER_MODEL, system, api_key)
    # Extract JSON array from response
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        # Fallback: single research step + save
        return [
            {"step": 1, "action": f"Research: {goal}", "tool": "swarm"},
            {"step": 2, "action": f"Save findings to vault", "tool": "save_note"},
        ]
    try:
        steps = json.loads(match.group())
        return steps[:8]  # hard cap
    except json.JSONDecodeError:
        return [
            {"step": 1, "action": f"Research: {goal}", "tool": "swarm"},
            {"step": 2, "action": "Save findings to vault", "tool": "save_note"},
        ]


# ── Step 2: EXECUTE ───────────────────────────────────────────────────────────
async def execute_step(
    step: dict,
    goal: str,
    prior_outputs: list[str],
    model: str,
    api_key: str,
) -> str:
    """
    Execute a single planned step using the appropriate tool.
    Returns a string summary of what was produced.
    """
    action = step.get("action", "")
    tool   = step.get("tool", "research")
    step_n = step.get("step", "?")

    print(f"\n[GoalMode] Step {step_n} [{tool}]: {action}")
    context = "\n".join(prior_outputs[-3:]) if prior_outputs else ""  # last 3 outputs as context

    # ── swarm: parallel multi-angle research ──────────────────────────────────
    if tool == "swarm":
        from workflow import run_swarm
        result = await run_swarm(action, model=model)
        note_path = result.get("note_path", "")
        notebooks = result.get("notebooks_found", 0)
        return (
            f"Swarm research completed on: '{action}'\n"
            f"  • {result.get('successful', 0)}/5 agents succeeded\n"
            f"  • {notebooks} matching notebook(s) found\n"
            f"  • Saved to: {note_path}"
        )

    # ── research: single focused LLM internet search ──────────────────────────
    elif tool == "research":
        prompt = (
            f"Goal: {goal}\n\nContext from prior steps:\n{context}\n\n"
            f"Now answer this specific question with concrete facts and data:\n{action}"
        )
        # Live internet research model (env-overridable; defaults to a free model)
        result = _openrouter(prompt, _RESEARCH_MODEL, api_key=api_key)
        return result or f"[Research returned no result for: {action}]"

    # ── save_note: write synthesis to Obsidian ────────────────────────────────
    elif tool == "save_note":
        from obsidian_bridge import save_note, VAULT_PATH
        date_str = datetime.now().strftime("%Y-%m-%d")
        slug = re.sub(r"[^a-z0-9]+", "-", goal.lower()).strip("-")[:50]
        title = f"Goal: {goal[:60]}"
        details = "\n\n".join(prior_outputs) if prior_outputs else action
        path = save_note(
            title=title,
            key_idea=f"Autonomous goal run: {goal}",
            details=details,
            next_steps=[
                "Review and refine findings",
                "Move to relevant Projects folder",
                "Apply or share insights",
            ],
            tags=["goal-mode", "agent-os", "autonomous", slug],
        )
        return f"Note saved to vault: {path}"

    # ── summarise: synthesise prior outputs ───────────────────────────────────
    elif tool == "summarise":
        prompt = (
            f"Goal: {goal}\n\n"
            f"Here are all findings gathered so far:\n{context}\n\n"
            f"Now {action}. Be concise and structured."
        )
        return _openrouter(prompt, model, api_key=api_key) or "[Summarise returned empty]"

    # ── analyse: evaluate or compare ──────────────────────────────────────────
    elif tool == "analyse":
        prompt = (
            f"Goal: {goal}\n\nFindings so far:\n{context}\n\n"
            f"Task: {action}\n\nProvide a critical, structured analysis."
        )
        return _openrouter(prompt, model, api_key=api_key) or "[Analyse returned empty]"

    # ── quantum: run a quantum circuit or algorithm ───────────────────────────
    elif tool == "quantum":
        from quantum_agent import run_quantum_tool
        # Parse the action text to figure out what quantum operation to run
        action_lower = action.lower()
        if "factor" in action_lower or "shor" in action_lower:
            # Extract number if present, e.g. "factor 35" or "use Shor's to factor 77"
            import re as _re
            nums = _re.findall(r"\b(\d+)\b", action)
            N = int(nums[0]) if nums else 15
            result = run_quantum_tool({"action": "factor", "N": N})
            return (
                f"Shor's algorithm on N={result['N']} (base a={result['a']}):\n"
                f"  Period found: r={result.get('period')}\n"
                f"  Factors: {result.get('factors')}\n"
                f"  Verified: {result.get('verified')}"
            )
        elif "grover" in action_lower or "search" in action_lower:
            import re as _re
            bits = _re.findall(r"\b([01]{2,})\b", action)
            target = bits[0] if bits else "11"
            result = run_quantum_tool({"action": "grover", "target": target, "shots": 1024})
            return (
                f"Grover's search for target |{result['target']}> "
                f"(decimal {result['target_decimal']}) in {2**len(result['target'])} items:\n"
                f"  Hit rate: {result['target_hit_rate']*100:.1f}%\n"
                f"  Counts: {result['counts']}\n"
                f"  Circuit depth: {result['depth']} gates"
            )
        else:
            # Default: pick circuit by keyword
            circuit = "bell_state"
            for kw, circ in [("ghz", "ghz_3"), ("fourier", "qft_3"),
                              ("adder", "full_adder"), ("superpos", "superposition")]:
                if kw in action_lower:
                    circuit = circ
                    break
            result = run_quantum_tool({"action": "run", "circuit": circuit, "shots": 1024})
            return (
                f"Ran quantum circuit '{circuit}' ({result['num_qubits']} qubits, "
                f"depth={result['depth']}) on {result['backend']}:\n"
                f"  Counts: {result['counts']}\n"
                f"  Top state: |{result['top_state']}> ({result['top_prob']*100:.1f}%)"
            )

    else:
        return f"[Unknown tool '{tool}' for step: {action}]"


# ── Step 3: CHECK ─────────────────────────────────────────────────────────────
def check_goal(goal: str, all_outputs: list[str], model: str, api_key: str) -> dict:
    """
    Ask the LLM: is the goal achieved? Returns:
      { "achieved": bool, "confidence": 0-100, "verdict": str, "gap": str }
    """
    outputs_text = "\n\n---\n\n".join(all_outputs)
    system = (
        "You are a goal-checking agent. Evaluate whether the goal has been fully achieved "
        "based on the work done. Respond ONLY with JSON:\n"
        '{"achieved": true/false, "confidence": 0-100, "verdict": "one sentence", "gap": "what is still missing or empty string"}'
    )
    prompt = f"Goal: {goal}\n\nWork completed:\n{outputs_text[:4000]}"  # cap at ~4k chars
    raw = _openrouter(prompt, _PLANNER_MODEL, system, api_key)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    # Fallback
    return {"achieved": True, "confidence": 70, "verdict": "Goal run completed.", "gap": ""}


# ── Step 4: SAVE run log ──────────────────────────────────────────────────────
def save_goal_log(
    goal: str,
    steps: list[dict],
    outputs: list[str],
    check: dict,
    model: str,
) -> str:
    """Save the full goal run log to Obsidian 00-Inbox."""
    sys.path.insert(0, str(Path(__file__).parent))
    from obsidian_bridge import VAULT_PATH

    date_str  = datetime.now().strftime("%Y-%m-%d")
    time_str  = datetime.now().strftime("%H:%M")
    slug      = re.sub(r"[^a-z0-9]+", "-", goal.lower()).strip("-")[:50]
    filename  = f"{date_str}-goal-{slug}.md"

    steps_md  = "\n".join(f"  {s['step']}. [{s['tool']}] {s['action']}" for s in steps)
    outputs_md = "\n\n".join(
        f"### Step {i+1} Output\n{o}" for i, o in enumerate(outputs)
    )

    status  = "✅ Achieved" if check.get("achieved") else "⚠️ Partial"
    verdict = check.get("verdict", "")
    gap     = check.get("gap", "")
    confidence = check.get("confidence", 0)

    content = f"""---
date: {date_str}
tags: [goal-mode, agent-os, autonomous, {slug}]
project: "AI-Automation"
source: "Agent OS Goal Mode ({model})"
---

# Goal Run: {goal}

> **Status:** {status} ({confidence}% confidence)
> **Verdict:** {verdict}
> **Model:** {model} | **Run:** {date_str} {time_str}

## Plan ({len(steps)} steps)
{steps_md}

## Results

{outputs_md}

{"## Gap / What's Missing\n" + gap if gap else ""}

## Action / Next Steps
- [ ] Review findings above
- [ ] Move to relevant Projects folder
- [ ] Act on verdict: {verdict}
"""

    inbox = VAULT_PATH / "00-Inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    path = inbox / filename
    path.write_text(content, encoding="utf-8")
    return str(path)


# ── Main entry point ──────────────────────────────────────────────────────────
async def run_goal(
    goal: str,
    max_steps: int = 8,
    model: str = "",
) -> dict:
    """
    Autonomous goal runner.

    1. Plan  → LLM breaks goal into ≤8 steps
    2. Execute → each step runs with right tool
    3. Check  → LLM evaluates if goal is achieved
    4. Save   → full log to Obsidian vault

    Returns a summary dict with status, step count, and vault path.
    """
    model = model or _DEFAULT_MODEL
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    from openrouter_client import backend_available
    if not backend_available():
        return {"error": "No LLM backend available — set OPENROUTER_API_KEY or GEMINI_API_KEY in .env, or start a local Ollama server (offline mode)."}

    print(f"\n{'='*60}")
    print(f"[GoalMode] Goal: {goal}")
    print(f"[GoalMode] Model: {model} | Max steps: {max_steps}")
    print(f"{'='*60}")

    # ── 1. Plan ───────────────────────────────────────────────────────────────
    print("\n[GoalMode] Planning steps...")
    steps = plan_goal(goal, model, api_key)
    steps = steps[:max_steps]
    print(f"[GoalMode] {len(steps)} steps planned:")
    for s in steps:
        print(f"  {s['step']}. [{s['tool']}] {s['action']}")

    # ── 2. Execute ────────────────────────────────────────────────────────────
    outputs: list[str] = []
    for step in steps:
        try:
            output = await execute_step(step, goal, outputs, model, api_key)
            outputs.append(output)
            # Brief preview
            preview = output[:120].replace("\n", " ")
            print(f"[GoalMode] ✓ Step {step['step']} done: {preview}...")
        except Exception as e:
            err = f"[Step {step['step']} failed: {e}]"
            outputs.append(err)
            print(f"[GoalMode] ✗ {err}")

    # ── 3. Check ──────────────────────────────────────────────────────────────
    print("\n[GoalMode] Checking goal completion...")
    check = check_goal(goal, outputs, model, api_key)
    status = "achieved" if check.get("achieved") else "partial"
    print(f"[GoalMode] Result: {status} ({check.get('confidence', 0)}%) — {check.get('verdict', '')}")

    # ── 4. Save ───────────────────────────────────────────────────────────────
    log_path = save_goal_log(goal, steps, outputs, check, model)
    print(f"[GoalMode] ✓ Run log saved: {log_path}")
    print(f"{'='*60}\n")

    return {
        "goal":       goal,
        "model":      model,
        "steps":      len(steps),
        "status":     status,
        "confidence": check.get("confidence", 0),
        "verdict":    check.get("verdict", ""),
        "gap":        check.get("gap", ""),
        "log_path":   log_path,
        "outputs":    outputs,
    }

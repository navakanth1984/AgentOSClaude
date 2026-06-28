"""
swarm.py — Parallel Sub-Agent Research Swarm for Agent OS

Extracted from workflow.py to give the swarm cluster its own module.
Combines 5 parallel OpenRouter agents with NotebookLM notebook matching
to produce a unified, multi-angle research note saved to Obsidian.

Pipeline:
  A. Extract keywords via analyze_prompt_llm() / analyze_prompt()
  B. Search NotebookLM cache for matching personal notebooks
  C. Optionally pull notebook content via browser (auto_notebooklm=True)
  D. Run 5 parallel internet research agents via OpenRouter
  E. Merge swarm output + notebook matches into one Obsidian note

Usage:
    from swarm import run_swarm
    result = await run_swarm("personal knowledge management")
"""

import os
import re
import sys
import json
import asyncio
import random
import urllib.error
from datetime import datetime
from pathlib import Path

# Force UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

sys.path.insert(0, str(Path(__file__).parent))
from openrouter_client import call_openrouter_async


# ── Agent role definitions ────────────────────────────────────────────────────

AGENT_ROLES = [
    ("Overview Agent",   "Summarise the core facts and background of this topic in 5 bullet points."),
    ("Techniques Agent", "List the key techniques, methods, or how-to steps for this topic."),
    ("Examples Agent",   "Give 3 specific real-world examples or case studies related to this topic."),
    ("Pitfalls Agent",   "Identify 3 common mistakes, misconceptions, or pitfalls to avoid."),
    ("Trends Agent",     "Describe the latest developments, trends, or future directions for this topic."),
]

# Shared semaphore to throttle free-tier API concurrency (max 2 at once).
# Created lazily and re-created per event loop: the server runs each request via
# asyncio.run(), which spins up a NEW loop every time. A module-level Semaphore
# binds to the loop it was created in and then raises "bound to a different event
# loop" on every later request. Keying it to the running loop avoids that.
_SWARM_SEMAPHORE = None
_SWARM_SEMAPHORE_LOOP = None


def _get_semaphore() -> asyncio.Semaphore:
    global _SWARM_SEMAPHORE, _SWARM_SEMAPHORE_LOOP
    loop = asyncio.get_running_loop()
    if _SWARM_SEMAPHORE is None or _SWARM_SEMAPHORE_LOOP is not loop:
        _SWARM_SEMAPHORE = asyncio.Semaphore(2)
        _SWARM_SEMAPHORE_LOOP = loop
    return _SWARM_SEMAPHORE

# ── Single agent coroutine ────────────────────────────────────────────────────

async def _swarm_agent(
    agent_id: int,
    role: str,
    task: str,
    topic: str,
    api_key: str,
    model: str,
    max_retries: int = 6,
) -> dict:
    """
    Single async swarm agent — runs one focused research sub-task.
    Retries up to max_retries times on 429 rate-limit errors (exponential backoff).
    Returns a result dict with agent_id, role, task, result, error.
    """
    system = (
        f"You are Agent #{agent_id} in a parallel research swarm. "
        f"Your role: {role}. "
        "Be specific, structured, and concise. Use bullet points or numbered lists. "
        "Do not repeat what other agents might cover — focus only on your assigned angle."
    )
    user = f"Topic: {topic}\n\nYour task: {task}"

    async with _get_semaphore():
        last_error = None
        for attempt in range(max_retries):
            try:
                # Use max_tokens=800 for research agents
                content = await call_openrouter_async(model, system, user, api_key, max_tokens=800)
                return {"agent_id": agent_id, "role": role, "task": task, "result": content, "error": None}
            except urllib.error.HTTPError as e:
                last_error = str(e)
                if e.code == 429 and attempt < max_retries - 1:
                    # Exponential backoff with jitter: 4s, 8s, 16s, 32s...
                    wait = (2 ** (attempt + 2)) + random.uniform(1, 3)
                    print(f"[Swarm] Agent #{agent_id} rate-limited (429), retry {attempt+1}/{max_retries-1} in {wait:.1f}s")
                    await asyncio.sleep(wait)
                elif e.code == 402:
                    print(f"[Swarm] Agent #{agent_id} failed: Payment Required (402). Skipping OpenRouter primary.")
                    break
                else:
                    break
            except Exception as e:
                last_error = str(e)
                break

    return {"agent_id": agent_id, "role": role, "task": task, "result": "", "error": last_error}


# ── Synthesis Agent ───────────────────────────────────────────────────────────

async def _synthesis_agent(
    topic: str,
    agent_results: list[dict],
    api_key: str,
    model: str,
) -> str:
    """
    Final stage agent that reads all sub-agent reports and produces
     a cohesive executive summary and unified strategy.
    """
    print(f"[Swarm] Running Synthesis Agent...")
    
    # Compile reports into one context string
    reports = ""
    for r in agent_results:
        if not r.get("error") and r.get("result"):
            reports += f"\n--- {r['role']} Report ---\n{r['result']}\n"
            
    if not reports:
        return "Synthesis failed: No successful agent reports to summarize."

    system = (
        "You are the Swarm Synthesis Lead. Your job is to take multiple research reports "
        "on a topic and produce a high-level Executive Summary. "
        "Identify the 'Golden Thread' connecting all reports, resolve any contradictions, "
        "and provide 3 'Strategic Takeaways' that a decision-maker can act on immediately."
    )
    user = (
        f"Topic: {topic}\n\n"
        "Here are the research reports from the swarm agents:\n"
        f"{reports}\n\n"
        "Please provide:\n"
        "1. Executive Summary (2 paragraphs)\n"
        "2. The Golden Thread (1 paragraph)\n"
        "3. 3 Strategic Takeaways (bullet points)"
    )
    
    try:
        # Synthesis needs more context/tokens
        content = await call_openrouter_async(model, system, user, api_key, max_tokens=1000)
        return content
    except Exception as e:
        print(f"[Swarm] Synthesis error: {e}")
        return f"Synthesis unavailable due to error: {e}"


# ── Quantum result renderer ───────────────────────────────────────────────────

def _render_quantum_result(qr: dict) -> str:
    """
    Convert QuantumResearchAgent dict output into readable Markdown.
    Prevents raw JSON from appearing in the Obsidian note.
    """
    exp = qr.get("experimental", {})
    analysis = qr.get("analysis", {})

    counts = exp.get("counts", {})
    total_shots = exp.get("shots", 1)
    counts_table = "\n".join(
        f"| `|{state}⟩` | {count} | {count/total_shots*100:.1f}% |"
        for state, count in sorted(counts.items())
    )

    code = analysis.get("code_snippet", "")
    # Fix known bad backend string from LLM hallucination
    code = code.replace("'qer_simulator'", "'aer_simulator'")
    code = code.replace('"qer_simulator"', '"aer_simulator"')
    # Modernise deprecated Qiskit 0.x pattern
    if "Aer.get_backend" in code:
        code = (
            "from qiskit_aer import AerSimulator\n\n"
            + code.replace("from qiskit import Aer, execute\n", "")
                  .replace("from qiskit import QuantumCircuit, Aer, execute\n",
                           "from qiskit import QuantumCircuit\n")
                  .replace("Aer.get_backend('aer_simulator')", "AerSimulator()")
                  .replace("execute(qc, backend, shots=1024).result()", "backend.run(qc, shots=1024).result()")
        )

    apps = analysis.get("applications", [])
    apps_md = "\n".join(f"- {a}" for a in apps) if apps else "- See analysis above"

    circuit_str = exp.get("circuit_str", "")
    circuit_block = f"\n```\n{circuit_str}\n```\n" if circuit_str else ""

    return f"""**Backend:** {exp.get("backend", "AerSimulator")} | **Circuit:** {exp.get("label", "unknown")} | **Qubits:** {exp.get("num_qubits", "?")} | **Shots:** {total_shots} | **Runtime:** {exp.get("elapsed_ms", "?")}ms
{circuit_block}
### Measurement Results

| State | Count | Probability |
|-------|-------|-------------|
{counts_table}

### Analysis
{analysis.get("summary", "")}

{analysis.get("concept", "")}

### Agent OS Applications
{apps_md}

### Working Code (Qiskit 1.x)
```python
{code}
```"""


# ── Main swarm orchestrator ───────────────────────────────────────────────────

async def run_swarm(
    topic: str,
    model: str = "google/gemma-4-31b-it:free",
    auto_notebooklm: bool = False,
) -> dict:
    """
    Parallel sub-agent research swarm — with NotebookLM integration.

    Pipeline:
      A. Extract keywords from topic (LLM-powered if key present)
      B. Search NotebookLM cache for matching personal notebooks
      C. Optionally pull notebook content via browser (auto_notebooklm=True)
      D. Run 5 parallel internet research agents via OpenRouter
      E. Merge swarm output + notebook matches into one Obsidian note

    Result = internet knowledge + YOUR personal curated notebooks combined.

    Returns:
        dict with keys: topic, model, agents, successful, notebooks_found,
                        notebooks, notebook_audio, note_path, results
    """
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    from openrouter_client import backend_available
    if not backend_available():
        return {"error": "No LLM backend available — set OPENROUTER_API_KEY or GEMINI_API_KEY in .env, or start a local Ollama server (offline mode)."}

    # Import workflow helpers (lazy — avoids circular imports at module level)
    from workflow import analyze_prompt_llm, analyze_prompt, find_matching_notebooks
    from obsidian_bridge import VAULT_PATH

    # ── A. Extract keywords ───────────────────────────────────────────────────
    intent = analyze_prompt_llm(topic) or analyze_prompt(topic)
    keywords = intent.get("keywords", topic.lower().split()[:5])

    # ── B. Search NotebookLM cache ────────────────────────────────────────────
    print(f"\n[Swarm] Searching NotebookLM cache for: {keywords}")
    matched_notebooks = find_matching_notebooks(keywords, max_results=5)
    if matched_notebooks:
        print(f"[Swarm] Found {len(matched_notebooks)} matching notebook(s):")
        for nb in matched_notebooks:
            print(f"         • {nb.get('title', 'Untitled')}")
    else:
        print("[Swarm] No matching notebooks in cache.")

    # ── C. Optional: pull best notebook content via browser ───────────────────
    notebook_content = None
    best_notebook = matched_notebooks[0] if matched_notebooks else None
    if auto_notebooklm and best_notebook:
        nb_url = best_notebook.get("url", "")
        print(f"[Swarm] Opening NotebookLM: {nb_url}")
        try:
            from notebooklm_agent import run_session
            audio_result = await run_session("generate", nb_url)
            if audio_result.get("downloaded"):
                notebook_content = audio_result.get("path")
                print(f"[Swarm] NotebookLM audio captured: {notebook_content}")
            else:
                print(f"[Swarm] NotebookLM: {audio_result.get('error', 'no audio captured')}")
        except Exception as e:
            print(f"[Swarm] NotebookLM browser error: {e}")

    # ── D. Run parallel swarm agents ──────────────────────────────────────────
    # Stagger launches by 3.0s each to avoid simultaneous rate-limit hits on
    # free-tier models. Total stagger: 0s, 3s, 6s, 9s, 12s.
    STAGGER_SECS = 3.0
    print(f"\n[Swarm] Launching {len(AGENT_ROLES)} parallel agents for: '{topic}'")
    print(f"[Swarm] Model: {model}  (stagger={STAGGER_SECS}s between agents)")

    async def _staggered(i: int, role: str, task: str):
        await asyncio.sleep(i * STAGGER_SECS)
        return await _swarm_agent(i + 1, role, task, topic, api_key, model)

    agent_tasks = [
        _staggered(i, role, task)
        for i, (role, task) in enumerate(AGENT_ROLES)
    ]

    # ── Quantum subagent: add automatically when topic is quantum-related ──────
    QUANTUM_KEYWORDS = ["quantum", "qubit", "qiskit", "grover", "shor", "qft",
                        "superposition", "entangle", "bell state", "circuit"]
    is_quantum_topic = any(kw in topic.lower() for kw in QUANTUM_KEYWORDS)
    quantum_result = None
    if is_quantum_topic:
        print("[Swarm] Quantum topic detected — adding QuantumResearchAgent")
        try:
            from quantum_agent import QuantumResearchAgent
            qa = QuantumResearchAgent(model=model, api_key=api_key)
            quantum_result = await qa.research(topic)
            print("[Swarm] OK QuantumResearchAgent: done")
        except Exception as qe:
            print(f"[Swarm] ERR QuantumResearchAgent: {qe}")

    results = await asyncio.gather(*agent_tasks)
    if quantum_result:
        results = list(results) + [{
            "agent_id": len(AGENT_ROLES) + 1,
            "role":     "Quantum Agent",
            "task":     "Run real quantum circuit + analysis",
            "result":   _render_quantum_result(quantum_result),
            "error":    None,
        }]

    for r in results:
        status = "OK" if not r["error"] else "ERR"
        detail = "done" if not r["error"] else r["error"]
        print(f"[Swarm] {status} Agent #{r['agent_id']} ({r['role']}): {detail}")

    successful = [r for r in results if not r["error"] and r["result"]]
    if not successful:
        return {"error": "All swarm agents failed", "results": results}

    # ── E. Synthesis Stage ───────────────────────────────────────────────────
    synthesis = await _synthesis_agent(topic, successful, api_key, model)

    # ── F. Build merged Obsidian note ─────────────────────────────────────────
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:50]
    filename = f"{date_str}-swarm-{slug}.md"

    sections = "\n\n".join(
        f"## {r['role'].replace(' Agent', '')}\n{r['result']}"
        for r in successful
    )

    if matched_notebooks:
        nb_lines = "\n".join(
            f"- [{nb.get('title', 'Untitled')}](https://notebooklm.google.com{nb.get('url', '')})"
            for nb in matched_notebooks
        )
        notebooklm_section = f"\n\n## Your NotebookLM Sources\n{nb_lines}"
        if notebook_content:
            notebooklm_section += f"\n\n> Audio overview captured: `{notebook_content}`"
    else:
        notebooklm_section = (
            "\n\n## Your NotebookLM Sources\n"
            "*No matching notebooks found. Add sources at notebooklm.google.com*"
        )

    note_content = f"""---
date: {date_str}
tags: [swarm, agent-os, research, notebooklm]
project: "AI-Automation"
source: "Agent OS Swarm ({len(successful)} agents) + NotebookLM ({len(matched_notebooks)} notebooks)"
---

# Swarm Research: {topic}

> **Internet research** (OpenRouter/{model}) + **Your NotebookLM notebooks** combined.
> Generated by {len(successful)} parallel AI sub-agents.

## Executive Strategy
{synthesis}

## Key Idea
Deep multi-angle research on: **{topic}**

{sections}{notebooklm_section}

## Action / Next Steps
- [ ] Review notebook sources above for deeper personal context
- [ ] Move to relevant Projects folder
- [ ] Apply findings to current project
"""

    inbox = VAULT_PATH / "00-Inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    note_path = inbox / filename
    note_path.write_text(note_content, encoding="utf-8")

    print(f"[Swarm] ✓ Synthesis saved: {note_path}")
    return {
        "topic":           topic,
        "model":           model,
        "agents":          len(results),
        "successful":      len(successful),
        "notebooks_found": len(matched_notebooks),
        "notebooks":       [nb.get("title") for nb in matched_notebooks],
        "notebook_audio":  notebook_content,
        "note_path":       str(note_path),
        "results":         results,
    }

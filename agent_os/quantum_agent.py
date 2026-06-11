"""
quantum_agent.py — Agent OS Quantum Subagent
=============================================
A specialised subagent the swarm can dispatch for quantum-related research tasks.
Also used by goal_mode.py when a goal requires quantum computation.

Two modes:
  1. RESEARCH  — answers "what is quantum X" via LLM + quantum context
  2. COMPUTE   — actually runs quantum circuits and returns results

Usage from swarm.py:
    from quantum_agent import QuantumResearchAgent
    agent = QuantumResearchAgent(model=model, api_key=api_key)
    result = await agent.research(topic)

Usage from goal_mode.py or any tool:
    from quantum_agent import run_quantum_tool
    result = run_quantum_tool({"action": "run", "circuit": "grover", "target": "101"})
"""

import asyncio
import json
import os
from datetime import datetime
from quantum_engine import QuantumEngine


# ── Quantum tool — called by goal_mode when a step needs quantum compute ──────

def run_quantum_tool(params: dict) -> dict:
    """
    Tool function for goal_mode.py.
    params examples:
      {"action": "run",    "circuit": "bell_state", "shots": 1000}
      {"action": "run",    "circuit": "grover", "target": "101"}
      {"action": "factor", "N": 35}
      {"action": "list"}
    """
    qe = QuantumEngine()
    action = params.get("action", "run")

    if action == "list":
        return qe.list_circuits()

    if action == "factor":
        N = int(params.get("N", 15))
        return qe.factor(N)

    if action == "grover":
        target = params.get("target", "11")
        shots  = int(params.get("shots", 1024))
        return qe.grover_search(target=target, shots=shots)

    # Default: run named circuit
    circuit = params.get("circuit", "bell_state")
    shots   = int(params.get("shots", 1024))
    backend = params.get("backend", "local")
    return qe.run(circuit, shots=shots, backend=backend)


# ── Research agent — LLM-powered quantum question answering ───────────────────

QUANTUM_SYSTEM_PROMPT = """You are a quantum computing research agent embedded in Agent OS.
Your job: research quantum topics deeply and return structured findings.

You have access to:
- Quantum computing theory (superposition, entanglement, QFT, Grover's, Shor's)
- Qiskit API knowledge
- Real experimental results from the quantum_engine module

When asked to research a topic:
1. Explain the core concept clearly
2. Provide the relevant quantum circuit or algorithm
3. Give a working Qiskit code snippet
4. Note real-world applications and limitations
5. State what Agent OS can do with this quantum capability

Respond in JSON:
{
  "topic": "...",
  "summary": "...",
  "concept": "...",
  "circuit_name": "bell_state|ghz_3|grover_2|qft_3|full_adder|custom",
  "code_snippet": "...",
  "applications": ["...", "..."],
  "agent_os_action": "what /quantum API call to make",
  "sources": ["quantum computing knowledge"]
}"""


class QuantumResearchAgent:
    """
    Specialised subagent for quantum topics.
    Integrates with swarm.py's parallel agent pattern.
    """

    def __init__(self, model: str = "google/gemma-4-31b-it:free",
                 api_key: str = ""):
        self.model   = model
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.qe      = QuantumEngine()

    async def research(self, topic: str) -> dict:
        """Research a quantum topic. Returns swarm-compatible result dict."""
        t0 = datetime.now()

        # Run a relevant circuit to get real experimental data
        circuit_result = self._pick_and_run_circuit(topic)

        # Build context for LLM
        context = f"""
Topic: {topic}

Experimental quantum result just computed:
{json.dumps(circuit_result, indent=2, default=str)}

Available Agent OS quantum circuits: {list(self.qe.list_circuits()["circuits"].keys())}
"""

        # Call LLM for analysis
        llm_result = {}
        if self.api_key:
            try:
                from openrouter_client import call_openrouter
                raw = call_openrouter(
                    self.model,
                    QUANTUM_SYSTEM_PROMPT,
                    f"Research this quantum topic for Agent OS:\n{context}",
                    self.api_key,
                    max_tokens=600,
                )
                import re
                match = re.search(r"\{.*\}", raw, re.DOTALL)
                if match:
                    llm_result = json.loads(match.group())
            except Exception as e:
                llm_result = {"error": str(e)}

        elapsed = int((datetime.now() - t0).total_seconds() * 1000)

        return {
            "agent":           "QuantumResearchAgent",
            "topic":           topic,
            "experimental":    circuit_result,
            "analysis":        llm_result,
            "elapsed_ms":      elapsed,
            "timestamp":       t0.isoformat(),
        }

    def _pick_and_run_circuit(self, topic: str) -> dict:
        """Pick the most relevant built-in circuit for this topic and run it."""
        topic_lower = topic.lower()
        if any(w in topic_lower for w in ["entangl", "bell", "correlat"]):
            return self.qe.run("bell_state")
        if any(w in topic_lower for w in ["search", "grover", "amplif"]):
            return self.qe.grover_search(target="11")
        if any(w in topic_lower for w in ["fourier", "qft", "period", "shor", "factor"]):
            return self.qe.run("qft_3")
        if any(w in topic_lower for w in ["ghz", "three", "3-qubit", "multi"]):
            return self.qe.run("ghz_3")
        if any(w in topic_lower for w in ["superpos", "qubit", "hadamard"]):
            return self.qe.run("superposition")
        # Default: Bell state (most demonstrative)
        return self.qe.run("bell_state")


# ── Goal mode tool registry ───────────────────────────────────────────────────

# goal_mode.py can call get_quantum_tools() to discover available quantum actions
def get_quantum_tools() -> list:
    """
    Returns tool definitions for goal_mode.py's tool dispatcher.
    Each tool has: name, description, params schema, handler function.
    """
    return [
        {
            "name": "quantum_run",
            "description": "Run a quantum circuit on the local simulator or IBM hardware",
            "params": {
                "circuit": "Name of circuit: bell_state | ghz_3 | superposition | grover_2 | qft_3 | full_adder",
                "shots":   "Number of measurements (default 1024)",
                "backend": "local (default) or ibm",
            },
            "handler": lambda p: run_quantum_tool({**p, "action": "run"}),
        },
        {
            "name": "quantum_grover",
            "description": "Run Grover's search algorithm to find a binary target state",
            "params": {
                "target": "Binary string to search for, e.g. '101'",
                "shots":  "Number of measurements (default 1024)",
            },
            "handler": lambda p: run_quantum_tool({**p, "action": "grover"}),
        },
        {
            "name": "quantum_factor",
            "description": "Use Shor's algorithm to find prime factors of an integer N",
            "params": {
                "N": "Integer to factor (keep small: 15, 21, 35, 77)",
                "a": "Optional base (random if not set)",
            },
            "handler": lambda p: run_quantum_tool({**p, "action": "factor"}),
        },
    ]

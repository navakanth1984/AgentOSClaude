"""
claw_filmmaking_swarm.py — Hybrid Online/Offline OpenClaw Filmmaking & Novel Swarm
Uses Qiskit Quantum walks to select narrative branches,
spawns parallel writer agents (Ollama local fallback),
and runs a critique pass.
"""

import os
import sys
import json
import asyncio
import urllib.request
from pathlib import Path
from typing import Optional

# Add parent directory to path to allow imports
_HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(_HERE))

from creative_pipeline import call_llm, check_ollama
from quantum_backend import _find_ibm_token
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

NARRATIVE_BRANCHES = {
    "000": "The Betrayal — Adeel sells out Kavya to buy his own freedom.",
    "001": "The Sacrifice — Kavya takes a bullet meant for Adeel, shifting the power dynamic.",
    "010": "The Trap — Adeel leads Kavya directly into a gang ambush on the rooftop.",
    "011": "The Truce — Adeel and Kavya are forced to fight together against a third party.",
    "100": "The Escape — Adeel slips away, leaving Kavya with a cryptic clue.",
    "101": "The Arrest — Kavya corners Adeel, but he reveals a secret that compromises her.",
    "110": "The Fall — Both plummet from the terrace onto a lower level, forcing a survival scenario.",
    "111": "The Rebirth — A surreal encounter makes both realize they are pawns in a larger political game."
}


def run_quantum_narrative_selection() -> str:
    """
    Run a 3-qubit quantum circuit using AerSimulator to choose a narrative branch.
    Creates a superposition, applies entanglement, and measures the output.
    """
    print("[Quantum] Initializing 3-qubit narrative selection circuit...")
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.h(2)
    qc.measure([0, 1, 2], [0, 1, 2])
    
    sim = AerSimulator()
    job = sim.run(qc, shots=1)
    result = job.result()
    counts = result.get_counts()
    
    # Get the single measured state (e.g. '011')
    state = list(counts.keys())[0]
    # Reverse string to match little-endian qubit ordering if necessary,
    # but since it's just selection, we map the output directly
    branch = NARRATIVE_BRANCHES.get(state, NARRATIVE_BRANCHES["111"])
    print(f"[Quantum] Measured state |{state}>. Selected Branch: {branch}")
    return branch


async def run_writer_agent(role: str, task: str, branch: str, model: Optional[str] = None) -> str:
    """Run a single writer agent task (asynchronously)."""
    system = (
        f"You are the OpenClaw {role}. Your job is to generate part of the narrative for the filmmaking pipeline. "
        f"The selected story branch is: {branch}. "
        "Strictly adhere to your role's instructions, use professional formatting, and avoid cliché dialogue."
    )
    user = f"Task: {task}"
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: call_llm(system, user, model)
    )


async def orchestrate_filmmaking_swarm(prompt: str, model: Optional[str] = None):
    """Orchestrate the hybrid writer and critique team to write a screenplay scene and novel chapter."""
    print("=" * 65)
    print("  OPENCLAW AI FILMMAKING & NOVEL PIPELINE")
    print("=" * 65)
    
    # 1. Quantum narrative branch selection
    branch = run_quantum_narrative_selection()
    
    # 2. Spawn parallel writer agents
    print("\n[Pipeline] Spawning parallel writer agents...")
    tasks = [
        run_writer_agent(
            "Screenplay Writer",
            f"Write a full 3-page screenplay scene based on: '{prompt}'. Incorporate vocal textures (Biryani Method - hoarse/restrained anger).",
            branch,
            model
        ),
        run_writer_agent(
            "Novel Draft Writer",
            f"Draft a 1,000-word novel chapter matching the events of: '{prompt}'. Focus on internal monologue, atmosphere, and sensory details.",
            branch,
            model
        ),
        run_writer_agent(
            "Director of Audiography",
            f"Design a detailed sound design, Foley, and Dolby Atmos plan for: '{prompt}'. Include VFX defense tactics.",
            branch,
            model
        ),
    ]
    
    results = await asyncio.gather(*tasks)
    screenplay, novel, audio_plan = results
    
    # 3. Editorial Critique Pass
    print("\n[Pipeline] Spawning Critique Swarm to review and merge the drafts...")
    critique_system = (
        "You are the OpenClaw Editorial Director. Review the draft screenplay, novel chapter, and sound design. "
        "Remove all on-the-nose dialogue, align the voice and vocal textures (restrained, hoarse anger) to the color palette, "
        "and produce a compiled production package containing the finalized Screenplay, the matching Novel Chapter, and the Sound Design Plan."
    )
    critique_user = (
        f"DRAFT SCREENPLAY:\n{screenplay}\n\n"
        f"DRAFT NOVEL CHAPTER:\n{novel}\n\n"
        f"SOUND DESIGN PLAN:\n{audio_plan}\n\n"
        f"Story Branch: {branch}"
    )
    
    final_package = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: call_llm(critique_system, critique_user, model)
    )
    
    print("\n[Pipeline] Generation complete! Writing output files...")
    output_dir = _HERE / "output"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "filmmaking_production_package.md"
    output_file.write_text(final_package, encoding="utf-8")
    
    print(f"[OK] Production package saved: {output_file}")
    
    # Also save as a note in the Obsidian inbox
    try:
        from obsidian_bridge import save_note
        obsidian_path = save_note(
            title="AI Filmmaking Swarm Production Package",
            key_idea=f"Compiled production package for branch: {branch}",
            details=final_package,
            next_steps=["Review screenplay and novel chapter", "Load soundscape into Hermes"],
            tags=["ai-filmmaking", "quantum-walk", "openclaw-swarm"],
            folder="inbox"
        )
        print(f"[OK] Saved to Obsidian Inbox: {obsidian_path.name}")
    except Exception as e:
        print(f"[WARNING] Could not save to Obsidian: {e}")
        
    print("\n" + "=" * 65)
    print("  PIPELINE RUN COMPLETE")
    print("=" * 65)


if __name__ == "__main__":
    prompt = "A high-stakes rooftop chase in Hyderabad during a massive dust storm."
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        
    asyncio.run(orchestrate_filmmaking_swarm(prompt))

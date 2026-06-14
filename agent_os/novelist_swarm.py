"""
novelist_swarm.py — Novelist Subagent Team (Writer, Critic, Rewriter) for Agent OS
Enforces McKee's Story principles, sensory details, and atmospheric description.
"""
import os
import sys
import asyncio
from pathlib import Path
from typing import Optional

# Add parent directory to path to allow imports
_HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(_HERE))

from creative_pipeline import call_llm

async def run_novelist_agent(role: str, system_prompt: str, user_prompt: str, model: Optional[str] = None) -> str:
    """Run a single novelist agent task asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: call_llm(system_prompt, user_prompt, model)
    )

async def run_novelist_swarm(prompt: str, context: str = "", model: Optional[str] = None) -> dict:
    """
    Runs the Novelist Swarm Team:
    1. Writer Drafts the chapter.
    2. Critic reviews and lists improvements.
    3. Rewriter applies polish.
    """
    print(f"\n[Novelist Swarm] Starting swarm for concept: '{prompt}'...")
    
    # Step 1: Draft Writer
    writer_system = (
        "You are the OpenClaw Novelist. Write a rich, atmospheric novel chapter based on the user's prompt. "
        "Focus on sensory details (sight, sound, smell, texture), character internal monologue, and scene setting. "
        "Maintain high-fidelity prose. Avoid clichés and keep dialogue natural and subtext-heavy."
    )
    writer_user = f"Write a novel chapter draft based on: '{prompt}'"
    if context:
        writer_user += f"\n\nContext to incorporate:\n{context}"
        
    print("[Novelist Swarm] 1. Spawning Novel Draft Writer...")
    draft = await run_novelist_agent("Draft Writer", writer_system, writer_user, model)
    
    # Step 2: Critique Agent
    critic_system = (
        "You are the OpenClaw Literary Critic. Critically review the draft novel chapter. "
        "Analyze: \n"
        "1. Pacing & Flow\n"
        "2. Sensory descriptions and atmosphere\n"
        "3. Dialogue naturalness and subtext\n"
        "4. Clichés or generic phrasing.\n"
        "Provide constructive, detailed feedback and specific actionable rewrite instructions."
    )
    critic_user = f"DRAFT CHAPTER:\n\n{draft}\n\nOriginal Prompt: {prompt}"
    
    print("[Novelist Swarm] 2. Spawning Literary Critic...")
    critique = await run_novelist_agent("Literary Critic", critic_system, critic_user, model)
    
    # Step 3: Rewriter Agent
    rewriter_system = (
        "You are the OpenClaw Master Polish Editor. Take the draft novel chapter and the critic's feedback. "
        "Rewrite the chapter, fully addressing the critique, improving the prose quality, expanding sensory descriptions, "
        "and elevating dialogue subtext. Output only the final polished chapter without introduction or commentary."
    )
    rewriter_user = (
        f"ORIGINAL DRAFT:\n{draft}\n\n"
        f"CRITIQUE & INSTRUCTIONS:\n{critique}\n\n"
        f"Rewrite and produce the polished final version."
    )
    
    print("[Novelist Swarm] 3. Spawning Polish Rewriter...")
    polish = await run_novelist_agent("Polish Rewriter", rewriter_system, rewriter_user, model)
    
    return {
        "draft": draft,
        "critique": critique,
        "polish": polish
    }

if __name__ == "__main__":
    import sys
    test_prompt = "A character enters a dusty, forgotten antique shop in a small alley."
    if len(sys.argv) > 1:
        test_prompt = sys.argv[1]
    results = asyncio.run(run_novelist_swarm(test_prompt))
    print("\n--- NOVELIST SWARM DRAFT ---\n", results["draft"])
    print("\n--- NOVELIST SWARM CRITIQUE ---\n", results["critique"])
    print("\n--- NOVELIST SWARM POLISH ---\n", results["polish"])

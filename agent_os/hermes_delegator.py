"""
hermes_delegator.py — Hermes-style plain English delegation for Agent OS
"""

import asyncio
import json
import os
import re
import threading
from datetime import datetime
from pathlib import Path

# Adjust imports to match project structure
from openrouter_client import call_openrouter_async
from swarm import _swarm_agent, _synthesis_agent
from obsidian_bridge import VAULT_PATH

def _extract_json_from_text(text: str) -> str:
    """Extracts JSON array from a markdown block if present."""
    match = re.search(r'```(?:json)?\s*(\[\s*\{.*?\}\s*\])\s*```', text, re.DOTALL)
    if match:
        return match.group(1)
    
    # Try finding just an array if no backticks
    match = re.search(r'(\[\s*\{.*?\}\s*\])', text, re.DOTALL)
    if match:
        return match.group(1)
        
    return text

async def analyze_delegation(prompt: str, model: str, api_key: str = "") -> list[dict]:
    """Uses the Lead Agent to determine the required subagents and their tasks."""
    system_prompt = (
        "You are a Lead Agent delegator. The user will give you a complex task. "
        "Break it down into parallel sub-tasks. Output ONLY a valid JSON list of objects, "
        "where each object has a 'role' (string, e.g. 'Data Gatherer', 'Summarizer') and a 'task' (string)."
    )
    
    response = await call_openrouter_async(
        model=model,
        system=system_prompt,
        user=f"Break down this task: {prompt}",
        api_key=api_key,
        max_tokens=1000,
    )
    
    try:
        json_str = _extract_json_from_text(response)
        plan = json.loads(json_str)
        if not isinstance(plan, list):
            raise ValueError("Parsed JSON is not a list.")
        return plan
    except (json.JSONDecodeError, ValueError) as e:
        print(f"\n[Hermes] Failed to parse JSON plan from LLM:\n{response}")
        raise ValueError("Lead Agent failed to return a valid JSON delegation plan.") from e

async def _async_run_delegation(prompt: str, model: str):
    """The core asynchronous delegation logic."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    
    try:
        print(f"\n[Hermes] Analyzing delegation for: '{prompt[:50]}...'")
        
        # 1. Analyze and fan out
        delegation_plan = await analyze_delegation(prompt, model, api_key)
        print(f"[Hermes] Spawning {len(delegation_plan)} subagents...")
        for i, agent in enumerate(delegation_plan, 1):
            print(f"  - Agent #{i}: {agent.get('role')} -> {agent.get('task')}")
        
        # 2. Run subagents in parallel
        # Stagger launches slightly to avoid rate limit spikes on free models
        tasks = []
        for i, agent in enumerate(delegation_plan):
            role = agent.get('role', 'Agent')
            task = agent.get('task', '')
            
            async def _staggered_swarm(agent_id, role, task, delay):
                await asyncio.sleep(delay)
                return await _swarm_agent(
                    agent_id=agent_id, 
                    role=role, 
                    task=task, 
                    topic=prompt, 
                    api_key=api_key, 
                    model=model
                )
                
            tasks.append(_staggered_swarm(i + 1, role, task, delay=i * 2.0))
            
        results = await asyncio.gather(*tasks)
        
        for r in results:
            status = "OK" if not r.get("error") else "ERR"
            detail = "done" if not r.get("error") else r["error"]
            print(f"[Hermes] {status} Agent #{r['agent_id']} ({r['role']}): {detail}")
            
        successful = [r for r in results if not r.get("error") and r.get("result")]
        
        if not successful:
            print(f"\n[Hermes] ❌ Delegation failed: All subagents encountered errors.\nagent-os> ", end="", flush=True)
            return

        # 3. Synthesize
        print(f"[Hermes] {len(successful)} subagents finished successfully. Synthesizing results...")
        final_summary = await _synthesis_agent(topic=prompt, agent_results=successful, api_key=api_key, model=model)
        
        # 4. Dynamic File Naming & Saving
        date_str = datetime.now().strftime("%Y-%m-%d")
        slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:40]
        if not slug:
            slug = "delegation"
        filename = f"{date_str}-hermes-{slug}.md" 
        
        inbox = VAULT_PATH / "00-Inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        save_path = inbox / filename
        
        # Build note content
        sections = "\n\n".join(
            f"## {r['role'].replace(' Agent', '')}\n{r['result']}"
            for r in successful
        )
        
        note_content = f"""---
date: {date_str}
tags: [hermes, delegation, agent-os]
project: "AI-Automation"
source: "Hermes Lead Agent + {len(successful)} subagents"
---

# Hermes Delegation: {prompt}

> **Orchestration**: Hermes Lead Agent ({model})
> **Subagents spawned**: {len(delegation_plan)}

## Executive Strategy & Synthesis
{final_summary}

## Subagent Reports
{sections}

## Action / Next Steps
- [ ] Review reports
- [ ] Move to relevant Projects folder
"""

        save_path.write_text(note_content, encoding="utf-8")
            
        # 5. Completion Notification
        print(f"\n[Hermes] ✅ Delegation complete! Saved to {save_path.relative_to(VAULT_PATH.parent)}\nagent-os> ", end="", flush=True)
        
    except Exception as e:
        # Silent failure prevention
        import traceback
        traceback.print_exc()
        print(f"\n[Hermes] ❌ Delegation failed: {str(e)}\nagent-os> ", end="", flush=True)

def run_delegation_background(prompt: str, model: str):
    """Spawns the async delegation process in a background thread."""
    def thread_target():
        # Create a new event loop for the background thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_async_run_delegation(prompt, model))
        loop.close()

    thread = threading.Thread(target=thread_target, daemon=True)
    thread.start()

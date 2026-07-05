"""SwarmExecutor — thin adapter over the existing agent_os/swarm.py behavior,
so the 5-role research swarm is selectable through the same ExecutionManager
interface as mixture/single, without changing swarm.py itself."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..manifest import new_manifest
from .base import ExecutionRequest, StatusCallback


class SwarmExecutor:
    async def execute(self, request: ExecutionRequest, status_cb: StatusCallback = None) -> dict:
        from swarm import run_swarm

        model = (request.models or ["anthropic/claude-sonnet-4-5"])[0]
        manifest = new_manifest(
            mode=request.mode,
            requested_mode=request.requested_mode or request.mode, 
            models=[model], 
            category=request.category,
            planned_mode=request.planned_mode,
            executed_mode=request.executed_mode,
            routing_trace=request.routing_trace
        )
        
        t0 = time.time()
        if status_cb:
            status_cb("running", {"stage": "swarm_fanout"})

        result = await run_swarm(request.prompt, model=model)

        manifest.per_model = result.get("results", [])
        manifest.final = result.get("note_content") or ""
        manifest.add_event("execution_finished")
        manifest.save()

        if status_cb:
            status_cb("done", {"stage": "done"})

        merged = manifest.to_dict()
        merged["swarm_result"] = result
        return merged

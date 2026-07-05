"""
agent_os/execution/ — pluggable execution framework for Agent OS.

ExecutionManager dispatches an ExecutionRequest to the Executor registered for
its ExecutionMode (single / swarm / mixture / debate / auto). Mixture-of-Agents
is the first "advanced" executor built on this framework, not a one-off feature.

Usage:
    from execution import ExecutionManager, ExecutionRequest, ExecutionMode

    manager = ExecutionManager()
    result = await manager.execute(ExecutionRequest(
        prompt="...", mode=ExecutionMode.MIXTURE,
        models=["anthropic/claude-sonnet-4-5", "google/gemini-2.5-flash"],
        aggregation="standard",
    ))
"""

from .execution_modes import ExecutionMode
from .executors.base import ExecutionRequest
from .executors.single import SingleExecutor
from .executors.swarm import SwarmExecutor
from .executors.mixture import MixtureExecutor
from .executors.debate import DebateExecutor
from .executors.auto import AutoExecutor


class ExecutionManager:
    """
    Routes an ExecutionRequest to its Executor and returns the result dict
    (see executors/base.py for the shared result shape).

    NOTE (deliberate seam, not implemented): today `execute()` looks up the
    executor for `request.mode` directly. A future Planner would sit here
    instead — `plan = Planner.plan(request); executor = plan.executor` —
    once an executor actually needs branching/iterative revision (see the
    "Objective triggers" table in the plan). Until then, adding a Planner
    would be speculative complexity with no executor that needs it.
    """

    def __init__(self):
        self._executors = {
            ExecutionMode.SINGLE:  SingleExecutor(),
            ExecutionMode.SWARM:   SwarmExecutor(),
            ExecutionMode.MIXTURE: MixtureExecutor(),
            ExecutionMode.DEBATE:  DebateExecutor(),
            ExecutionMode.AUTO:    AutoExecutor(),
        }

    async def execute(self, request: ExecutionRequest, status_cb=None) -> dict:
        mode = ExecutionMode(request.mode)
        executor = self._executors[mode]
        return await executor.execute(request, status_cb=status_cb)


__all__ = ["ExecutionManager", "ExecutionRequest", "ExecutionMode"]

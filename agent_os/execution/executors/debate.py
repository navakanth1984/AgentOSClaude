"""
DebateExecutor — stub. Interface only, per plan Phase 2.

Not implemented: models critiquing each other over N rounds before a final
judge call needs branching/iterative revision, which is the documented
trigger for introducing a Planner (see agent_os/execution/__init__.py NOTE
and the "Objective triggers" table in the plan). Do not implement ad hoc
inside this stub — build the Planner seam first when this is picked up.
"""

from .base import ExecutionRequest, StatusCallback


class DebateExecutor:
    async def execute(self, request: ExecutionRequest, status_cb: StatusCallback = None) -> dict:
        raise NotImplementedError("Debate execution mode is not implemented yet (Phase 2).")

"""
AutoExecutor — stub. Interface only, per plan Phase 3.

`AutoPlanner.plan(request) -> ExecutionPlan` is the intended shape: a task-type
classifier decides which mode + model team to use, then dispatches to that
executor. Defining the interface now means no API changes are needed later,
per the plan's explicit Phase-3 deferral — do not implement the classifier
body until Phase 1/2 usage data exists to justify it.
"""

from .base import ExecutionRequest, StatusCallback


class AutoPlanner:
    def plan(self, request: ExecutionRequest):
        raise NotImplementedError("Auto mode's task classifier is not implemented yet (Phase 3).")


class AutoExecutor:
    async def execute(self, request: ExecutionRequest, status_cb: StatusCallback = None) -> dict:
        raise NotImplementedError("Auto execution mode is not implemented yet (Phase 3).")

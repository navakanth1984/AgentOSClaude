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
from .executors.tau_executor import TauExecutor
from .executors.auto import AutoPlanner
from .routing import ExecutionPlan, PlanningResult
import dataclasses
import time


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
            ExecutionMode.TAU:     TauExecutor(),
        }
        self._planner = AutoPlanner()

    async def execute(self, request: ExecutionRequest, status_cb=None) -> dict:
        mode = ExecutionMode(request.mode)
        
        if mode == ExecutionMode.AUTO:
            t0 = time.perf_counter()
            result = self._planner.plan(request)
            routing_time_us = (time.perf_counter() - t0) * 1_000_000
            
            # Inject routing time into the plan or directly into _execute_plan
            # Let's pass it to _execute_plan via a parameter or just modify result.diagnostics.
            # Easiest is to add it to _execute_plan signature or directly compute it there if we measure the whole _execute_plan? 
            # Actually _execute_plan does executor dispatch.
            return await self._execute_plan(result, request, routing_time_us, status_cb)
            
        return await self._executors[mode].execute(request, status_cb=status_cb)

    async def _execute_plan(self, result: PlanningResult, request: ExecutionRequest, routing_time_us: float, status_cb=None) -> dict:
        plan = result.plan
        
        routing_trace = getattr(request, "routing_trace", {}) or {}
        routing_trace.update({
            "policy_version": plan.policy_version,
            "classifier_version": plan.classifier_version,
            "category": plan.category.value,
            "executor": plan.executor.value,
            "requested_profile": request.profile,
            "planned_profile": plan.profile,
            "executed_profile": plan.profile,
            "aggregation": plan.aggregation,
            "max_models": plan.max_models,
            "rationale": plan.rationale,
            "routing_time_us": routing_time_us,
            "metadata": dict(plan.metadata)
        })
        
        # Override request parameters with the plan's deterministic choices
        planned_request = dataclasses.replace(
            request,
            mode=plan.executor.value,
            requested_mode=request.requested_mode or request.mode,
            planned_mode=plan.executor.value,
            executed_mode=plan.executor.value,
            profile=plan.profile,
            aggregation=plan.aggregation,
            max_models=plan.max_models,
            routing_trace=routing_trace
        )
        
        executor = self._executors[plan.executor]
        res = await executor.execute(planned_request, status_cb=status_cb)
        
        return res


__all__ = ["ExecutionManager", "ExecutionRequest", "ExecutionMode", "ExecutionPlan"]

"""
AutoMode — planner interface that generates ExecutionPlans.

Delegates to TaskClassifier and RoutingPolicy. Does not execute prompts,
aggregate responses, or contain provider-specific logic.
"""

from agent_os.execution.executors.base import ExecutionRequest
from agent_os.execution.routing import (
    ExecutionPlan,
    PlanningResult,
    RoutingContext,
    TaskClassifier,
    DeterministicRoutingPolicy,
)


class AutoPlanner:
    """Pure planner that determines the execution strategy based on policy."""
    
    def __init__(self, classifier=None, policy=None):
        self.classifier = classifier or TaskClassifier()
        self.policy = policy or DeterministicRoutingPolicy()

    def plan(self, request: ExecutionRequest) -> PlanningResult:
        category = self.classifier.classify(request)
        context = RoutingContext(
            request=request, 
            category=category, 
            classifier_version=getattr(self.classifier, "VERSION", "unknown"),
            capabilities=frozenset()
        )
        plan = self.policy.route(context)
        return PlanningResult(plan=plan)


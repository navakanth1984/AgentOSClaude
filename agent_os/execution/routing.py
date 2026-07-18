"""Routing layer for mapping ExecutionRequests to immutable ExecutionPlans."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional
from types import MappingProxyType

from agent_os.execution.execution_modes import ExecutionMode
from agent_os.execution.executors.base import ExecutionRequest


class TaskCategory(str, Enum):
    GENERAL = "general"
    CODING = "coding"
    RESEARCH = "research"
    MATH = "math"


@dataclass(frozen=True)
class RoutingContext:
    request: ExecutionRequest
    category: TaskCategory
    classifier_version: str
    user_override: Optional[str] = None
    capabilities: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class ExecutionPlan:
    executor: ExecutionMode
    profile: str
    aggregation: str
    max_models: int
    category: TaskCategory
    rationale: str
    policy_version: str
    classifier_version: str
    estimated_cost: Optional[float] = None
    estimated_latency: Optional[float] = None
    # Excluded from hash: MappingProxyType wraps a dict, which is unhashable.
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}), hash=False)

@dataclass(frozen=True)
class PlanningResult:
    plan: ExecutionPlan
    diagnostics: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}), hash=False)
    # Future expansion: confidence, warnings, fallback_reason, etc.


class TaskClassifier:
    """Deterministic heuristic classifier. No model calls or side effects."""
    
    VERSION = "heuristic.v1"
    
    def classify(self, request: ExecutionRequest) -> TaskCategory:
        prompt = request.prompt.casefold()
        
        coding_indicators = [
            "```python", "```rust", "```sql", 
            "debug", "implement", "traceback", 
            "exception", "stack trace", "compile", 
            "unit test", "pytest"
        ]
        
        if any(indicator in prompt for indicator in coding_indicators):
            return TaskCategory.CODING
            
        research_indicators = ["research", "summarize paper", "find out"]
        if any(indicator in prompt for indicator in research_indicators):
            return TaskCategory.RESEARCH
            
        math_indicators = ["calculate", "math", "equation"]
        if any(indicator in prompt for indicator in math_indicators):
            return TaskCategory.MATH
            
        return TaskCategory.GENERAL


class RoutingPolicy:
    def route(self, context: RoutingContext) -> ExecutionPlan:
        raise NotImplementedError


class DeterministicRoutingPolicy(RoutingPolicy):
    VERSION = "routing.deterministic.v1"
    
    def route(self, context: RoutingContext) -> ExecutionPlan:
        # Static defaults
        executor = ExecutionMode.MIXTURE
        aggregation = "standard"
        max_models = 3
        
        matched_rules = []
        if context.category == TaskCategory.CODING:
            profile = "Coding"
            matched_rules.append("Category match: CODING")
            rationale = "Detected coding task"
        elif context.category == TaskCategory.RESEARCH:
            profile = "Best Overall"
            matched_rules.append("Category match: RESEARCH")
            rationale = "Detected research task"
        elif context.category == TaskCategory.MATH:
            profile = "Best Overall"
            matched_rules.append("Category match: MATH")
            rationale = "Detected math task"
        else:
            profile = "Budget"
            matched_rules.append("Fallback to GENERAL task")
            rationale = "General task fallback"
            
        return ExecutionPlan(
            executor=executor,
            profile=profile,
            aggregation=aggregation,
            max_models=max_models,
            category=context.category,
            rationale=rationale,
            policy_version=self.VERSION,
            classifier_version=context.classifier_version,
            metadata=MappingProxyType({"matched_rules": tuple(matched_rules)})
        )

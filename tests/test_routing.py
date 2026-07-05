import pytest
from dataclasses import FrozenInstanceError
from agent_os.execution.routing import (
    RoutingContext, 
    ExecutionPlan, 
    DeterministicRoutingPolicy, 
    TaskClassifier,
    TaskCategory
)
from agent_os.execution.executors.base import ExecutionRequest
from agent_os.execution.execution_modes import ExecutionMode

def test_routing_context_immutability():
    req = ExecutionRequest(prompt="test")
    ctx = RoutingContext(request=req, category=TaskCategory.GENERAL, classifier_version="1.0")
    with pytest.raises(FrozenInstanceError):
        ctx.request = ExecutionRequest(prompt="mutated")  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        ctx.category = TaskCategory.CODING  # type: ignore[misc]

def test_execution_plan_immutability():
    plan = ExecutionPlan(
        policy_version="1.0",
        classifier_version="1.0",
        category=TaskCategory.GENERAL,
        executor=ExecutionMode.SINGLE,
        profile="Budget",
        rationale="test",
        aggregation="standard",
        max_models=1
    )
    with pytest.raises(FrozenInstanceError):
        plan.executor = ExecutionMode.MIXTURE  # type: ignore[misc]
    with pytest.raises(TypeError):  # MappingProxyType doesn't support assignment
        plan.metadata["new_key"] = "value"  # type: ignore[index]

def test_task_classifier_determinism():
    classifier = TaskClassifier()
    # 100 executions determinism
    req = ExecutionRequest("Please implement this logic")
    categories = [classifier.classify(req) for _ in range(100)]
    assert all(c == categories[0] for c in categories)

def test_routing_policy_determinism():
    policy = DeterministicRoutingPolicy()
    ctx = RoutingContext(request=ExecutionRequest("Write some code"), category=TaskCategory.CODING, classifier_version="1.0")
    plans = [policy.route(ctx) for _ in range(100)]
    assert all(p == plans[0] for p in plans)
    # Assert hash stability
    hashes = [hash(p) for p in plans]
    assert all(h == hashes[0] for h in hashes)

def test_routing_policy_is_pure(monkeypatch):
    # Ensure no file I/O or network calls are made
    import builtins
    import urllib.request
    import socket
    try:
        import requests
        monkeypatch.setattr(requests, "get", lambda *args, **kwargs: 1/0)
    except ImportError:
        pass
    
    monkeypatch.setattr(builtins, "open", lambda *args, **kwargs: 1/0)
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: 1/0)
    monkeypatch.setattr(socket, "socket", lambda *args, **kwargs: 1/0)

    policy = DeterministicRoutingPolicy()
    ctx = RoutingContext(request=ExecutionRequest("Write some code"), category=TaskCategory.CODING, classifier_version="1.0")
    # Should not raise any division by zero errors
    plan = policy.route(ctx)
    assert plan is not None

def test_routing_policy_routes():
    policy = DeterministicRoutingPolicy()
    
    # 1. CODING -> Mixture
    ctx_coding = RoutingContext(request=ExecutionRequest("Write some code"), category=TaskCategory.CODING, classifier_version="1.0")
    plan_coding = policy.route(ctx_coding)
    assert plan_coding.executor == ExecutionMode.MIXTURE
    assert plan_coding.profile == "Coding"
    
    # 2. RESEARCH -> Mixture, Best Overall
    ctx_research = RoutingContext(request=ExecutionRequest("Research papers"), category=TaskCategory.RESEARCH, classifier_version="1.0")
    plan_research = policy.route(ctx_research)
    assert plan_research.executor == ExecutionMode.MIXTURE
    assert plan_research.profile == "Best Overall"

    # 3. MATH -> Mixture, Best Overall
    ctx_math = RoutingContext(request=ExecutionRequest("Solve equation"), category=TaskCategory.MATH, classifier_version="1.0")
    plan_math = policy.route(ctx_math)
    assert plan_math.executor == ExecutionMode.MIXTURE
    assert plan_math.profile == "Best Overall"

    # 4. GENERAL -> Unknown fallback to Budget, Mixture, standard
    ctx_general = RoutingContext(request=ExecutionRequest("Hi"), category=TaskCategory.GENERAL, classifier_version="1.0")
    plan_general = policy.route(ctx_general)
    assert plan_general.executor == ExecutionMode.MIXTURE
    assert plan_general.profile == "Budget"
    assert plan_general.aggregation == "standard"

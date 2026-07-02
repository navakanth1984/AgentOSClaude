"""Deterministic scoring policy with hard constraints (spec 5.1, 5.3, 9).

Reward ranks feasible candidates; constraints reject infeasible ones outright.
Lower score = better. No ML, no randomness, no time-dependence in the decision.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from crp_runtime.representations import RepresentationPlugin


@dataclass(frozen=True)
class Constraints:
    max_memory_bytes: int
    max_accuracy_loss: float
    max_latency_ms: float


@dataclass(frozen=True)
class Profile:
    alpha_memory: float
    beta_latency: float
    gamma_accuracy: float


@dataclass(frozen=True)
class Decision:
    chosen: str
    scores: dict[str, float] = field(default_factory=dict)
    rejected: dict[str, str] = field(default_factory=dict)
    decision_latency_ms: float = 0.0


def select_representation(
    tensor: np.ndarray,
    plugins: list[RepresentationPlugin],
    constraints: Constraints,
    profile: Profile,
) -> Decision:
    start = time.perf_counter()
    scores: dict[str, float] = {}
    rejected: dict[str, str] = {}

    for plugin in plugins:
        est = plugin.estimate(plugin.analyze(tensor))
        if est.memory_bytes > constraints.max_memory_bytes:
            rejected[plugin.name] = f"memory {est.memory_bytes} > {constraints.max_memory_bytes}"
            continue
        if est.accuracy_loss > constraints.max_accuracy_loss:
            rejected[plugin.name] = (
                f"accuracy loss {est.accuracy_loss} > {constraints.max_accuracy_loss}"
            )
            continue
        if est.latency_ms > constraints.max_latency_ms:
            rejected[plugin.name] = f"latency {est.latency_ms} > {constraints.max_latency_ms}"
            continue
        scores[plugin.name] = (
            profile.alpha_memory * float(est.memory_bytes)
            + profile.beta_latency * est.latency_ms
            + profile.gamma_accuracy * est.accuracy_loss * float(est.memory_bytes)
        )

    if scores:
        chosen = min(sorted(scores), key=lambda name: (scores[name], name))
    else:
        chosen = "dense"
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return Decision(
        chosen=chosen,
        scores=scores,
        rejected=rejected,
        decision_latency_ms=elapsed_ms,
    )

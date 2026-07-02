"""Replayable benchmark harness recorded through the frozen Tier-0 telemetry API."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

import crp_telemetry
from crp_runtime.plugins_int8 import Int8Plugin
from crp_runtime.policy import Constraints, Decision, Profile, select_representation
from crp_runtime.representations import DensePlugin, RepresentationPlugin
from crp_runtime.workloads import (
    EmbeddingSearchWorkload,
    SyntheticTensorWorkload,
    Workload,
    WorkloadSpec,
)

EVENT_KIND_DECISION = 1
EVENT_KIND_EXECUTE = 2

_PLUGINS: list[RepresentationPlugin] = [DensePlugin(), Int8Plugin()]


@dataclass(frozen=True)
class RunRecord:
    spec_json: str
    decision: Decision
    events: list[tuple[int, int, int, float]] = field(default_factory=list)
    dropped: int = 0


def _build(spec: WorkloadSpec) -> Workload:
    if spec.name == "synthetic_tensor":
        return SyntheticTensorWorkload(spec)
    if spec.name == "embedding_search":
        return EmbeddingSearchWorkload(spec)
    raise ValueError(f"unknown workload: {spec.name}")


def run_workload(
    spec: WorkloadSpec,
    constraints: Constraints,
    profile: Profile,
) -> RunRecord:
    telemetry = crp_telemetry.Telemetry(capacity=1 << 16)
    workload = _build(spec)
    tensors = workload.tensors()
    primary = tensors[0]
    queries = tensors[1] if len(tensors) > 1 else primary[: min(8, primary.shape[0])]

    decision = select_representation(primary, _PLUGINS, constraints, profile)
    telemetry.record(kind=EVENT_KIND_DECISION, tensor_id=0, value=decision.decision_latency_ms)

    plugin = next(p for p in _PLUGINS if p.name == decision.chosen)
    converted = plugin.convert(primary)
    result: np.ndarray = plugin.execute(converted, queries)
    telemetry.record(kind=EVENT_KIND_EXECUTE, tensor_id=0, value=float(result.shape[0]))

    events = telemetry.drain(1 << 16)
    return RunRecord(
        spec_json=spec.to_json(),
        decision=decision,
        events=events,
        dropped=telemetry.dropped(),
    )

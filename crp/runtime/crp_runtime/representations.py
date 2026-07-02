"""Representation plugin framework (spec 5.2). Dense is the safety fallback (spec 9)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class TensorStats:
    shape: tuple[int, ...]
    sparsity: float
    variance: float
    memory_bytes: int


@dataclass(frozen=True)
class RepresentationEstimate:
    memory_bytes: int
    latency_ms: float
    accuracy_loss: float
    conversion_cost_ms: float


@dataclass(frozen=True)
class RepresentationResult:
    name: str
    memory_bytes: int
    latency_ms: float
    quality_score: float
    conversion_cost: float


class RepresentationPlugin(Protocol):
    name: str

    def analyze(self, tensor: np.ndarray) -> TensorStats: ...
    def estimate(self, stats: TensorStats) -> RepresentationEstimate: ...
    def convert(self, tensor: np.ndarray) -> object: ...
    def execute(self, converted: object, queries: np.ndarray) -> np.ndarray: ...
    def restore(self, converted: object) -> np.ndarray: ...


def _base_stats(tensor: np.ndarray) -> TensorStats:
    return TensorStats(
        shape=tuple(tensor.shape),
        sparsity=float(np.mean(tensor == 0.0)),
        variance=float(np.var(tensor)),
        memory_bytes=int(tensor.nbytes),
    )


class DensePlugin:
    """Identity representation: zero loss, zero conversion cost."""

    name = "dense"

    def analyze(self, tensor: np.ndarray) -> TensorStats:
        return _base_stats(tensor)

    def estimate(self, stats: TensorStats) -> RepresentationEstimate:
        return RepresentationEstimate(
            memory_bytes=stats.memory_bytes,
            latency_ms=0.0,
            accuracy_loss=0.0,
            conversion_cost_ms=0.0,
        )

    def convert(self, tensor: np.ndarray) -> object:
        return tensor

    def execute(self, converted: object, queries: np.ndarray) -> np.ndarray:
        assert isinstance(converted, np.ndarray)
        return converted @ queries.T

    def restore(self, converted: object) -> np.ndarray:
        assert isinstance(converted, np.ndarray)
        return converted


REGISTRY: dict[str, RepresentationPlugin] = {}


def register(plugin: RepresentationPlugin) -> None:
    REGISTRY[plugin.name] = plugin

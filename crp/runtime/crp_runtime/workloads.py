"""Replayable workload specs and generators (spec 5.6: replay is a hard requirement)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class WorkloadSpec:
    name: str
    params: dict[str, float | int | str] = field(default_factory=dict)
    seed: int = 0

    def to_json(self) -> str:
        return json.dumps(
            {"name": self.name, "params": self.params, "seed": self.seed},
            sort_keys=True,
        )

    @staticmethod
    def from_json(payload: str) -> "WorkloadSpec":
        raw = json.loads(payload)
        return WorkloadSpec(name=raw["name"], params=raw["params"], seed=raw["seed"])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorkloadSpec):
            return NotImplemented
        return self.to_json() == other.to_json()

    def __hash__(self) -> int:
        return hash(self.to_json())


class Workload(Protocol):
    spec: WorkloadSpec

    def tensors(self) -> list[np.ndarray]: ...


class SyntheticTensorWorkload:
    """Low-rank (+ optional sparsity) matrix with fully seeded generation."""

    def __init__(self, spec: WorkloadSpec) -> None:
        self.spec = spec

    def tensors(self) -> list[np.ndarray]:
        p = self.spec.params
        rows, cols, rank = int(p["rows"]), int(p["cols"]), int(p["rank"])
        sparsity = float(p.get("sparsity", 0.0))
        rng = np.random.default_rng(self.spec.seed)
        left = rng.standard_normal((rows, rank))
        right = rng.standard_normal((rank, cols))
        t = left @ right
        if sparsity > 0.0:
            mask = rng.random((rows, cols)) < sparsity
            t = np.where(mask, 0.0, t)
        return [t.astype(np.float32)]

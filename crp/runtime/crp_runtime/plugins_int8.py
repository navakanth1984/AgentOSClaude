"""Symmetric per-tensor int8 quantization plugin (spec 5.2)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from crp_runtime.representations import (
    RepresentationEstimate,
    TensorStats,
    _base_stats,
)


@dataclass(frozen=True)
class Int8Tensor:
    data: np.ndarray
    scale: float


class Int8Plugin:
    name = "int8"

    def analyze(self, tensor: np.ndarray) -> TensorStats:
        return _base_stats(tensor)

    def estimate(self, stats: TensorStats) -> RepresentationEstimate:
        return RepresentationEstimate(
            memory_bytes=stats.memory_bytes // 4,
            latency_ms=0.0,
            accuracy_loss=1.0 / 255.0,
            conversion_cost_ms=0.01,
        )

    def convert(self, tensor: np.ndarray) -> Int8Tensor:
        max_abs = float(np.max(np.abs(tensor)))
        scale = max_abs / 127.0 if max_abs > 0.0 else 1.0
        data = np.clip(np.round(tensor / scale), -127, 127).astype(np.int8)
        return Int8Tensor(data=data, scale=scale)

    def execute(self, converted: object, queries: np.ndarray) -> np.ndarray:
        assert isinstance(converted, Int8Tensor)
        return self.restore(converted) @ queries.T

    def restore(self, converted: object) -> np.ndarray:
        assert isinstance(converted, Int8Tensor)
        return converted.data.astype(np.float32) * np.float32(converted.scale)

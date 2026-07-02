"""Unit tests for the in-process sandbox evaluator (_InProcessEvaluator)."""

import numpy as np

from crp_runtime.workloads import WorkloadSpec
from research.compiler import ConstrainedDSLCompiler
from research.sandbox import _InProcessEvaluator


def test_sandbox_evaluation():
    evaluator = _InProcessEvaluator()
    compiler = ConstrainedDSLCompiler()

    plugin_dsl = """
class MyQuantizer:
    def analyze(self, tensor):
        return {"memory_bytes": tensor.nbytes}
    def estimate(self, stats, hw):
        return {"memory_bytes": stats["memory_bytes"] // 2}
    def convert(self, tensor):
        return {"quantized": (tensor * 0.5).tolist()}
    def execute(self, converted, queries):
        import numpy as np
        return np.array(converted["quantized"]) @ queries.T
    def restore(self, converted):
        import numpy as np
        return (np.array(converted["quantized"]) * 2.0).tolist()
"""
    plugin_class = compiler.compile_plugin(plugin_dsl, "MyQuantizer")
    spec = WorkloadSpec(name="synthetic_tensor", params={"rows": 10, "cols": 10, "rank": 3}, seed=42)

    res = evaluator.evaluate(plugin_class, spec)
    assert res.success is True
    assert res.memory_bytes > 0
    assert res.latency_ms >= 0.0
    assert res.accuracy_loss >= 0.0

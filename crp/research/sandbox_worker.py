"""
sandbox_worker.py — Subprocess entry point for Gate 1 process isolation.

TEMPORARY: This module is a transitional artifact for Gate 1 (process-level
isolation via subprocess). It will be replaced by a container-based worker
in Gate 2. Do not add long-lived features here; keep the protocol surface
minimal (JSON-in via stdin → JSON-out via stdout).

Protocol:
    stdin  → {"plugin_source": str, "class_name": str, "workload_spec_json": str}
    stdout ← {"success": bool, "memory_bytes": int, "latency_ms": float,
              "accuracy_loss": float, "conversion_cost_ms": float,
              "error_message": str}
"""

import sys
import json
import time
import numpy as np

from crp_runtime.workloads import WorkloadSpec, SyntheticTensorWorkload, EmbeddingSearchWorkload
from research.compiler import ConstrainedDSLCompiler


def _run_evaluation(plugin_source: str, class_name: str, workload_spec: WorkloadSpec) -> dict:
    """Compile the plugin, run evaluation, and return a metrics dict.

    Mirrors the evaluation logic of the original SandboxEvaluator but runs
    inside an isolated subprocess.
    """
    compiler = ConstrainedDSLCompiler()
    plugin_class = compiler.compile_plugin(plugin_source, class_name)
    plugin = plugin_class()

    # Build workload and extract tensors
    if workload_spec.name == "synthetic_tensor":
        workload = SyntheticTensorWorkload(workload_spec)
    elif workload_spec.name == "embedding_search":
        workload = EmbeddingSearchWorkload(workload_spec)
    else:
        return {
            "success": False,
            "memory_bytes": 0,
            "latency_ms": 0.0,
            "accuracy_loss": 0.0,
            "conversion_cost_ms": 0.0,
            "error_message": f"Unknown workload type: {workload_spec.name}",
        }

    tensors = workload.tensors()
    primary = tensors[0]
    queries = tensors[1] if len(tensors) > 1 else primary[: min(8, primary.shape[0])]

    # 1. Analyze stats
    stats = plugin.analyze(primary)

    # 2. Conversion & cost
    t0 = time.perf_counter()
    converted = plugin.convert(primary)
    t1 = time.perf_counter()
    conversion_cost_ms = (t1 - t0) * 1000.0

    # 3. Execution & latency
    t2 = time.perf_counter()
    result = plugin.execute(converted, queries)
    t3 = time.perf_counter()
    latency_ms = (t3 - t2) * 1000.0

    # 4. Reconstruction / accuracy loss
    restored = plugin.restore(converted)

    if workload_spec.name == "synthetic_tensor":
        # Relative MSE reconstruction loss
        mse = np.mean((primary - np.array(restored)) ** 2)
        variance = np.var(primary)
        accuracy_loss = float(mse / variance) if variance > 0 else float(mse)
    elif workload_spec.name == "embedding_search":
        # Top-k overlap metric
        ground_truth = EmbeddingSearchWorkload.top_k(primary, queries, k=5)
        restored_corpus = np.array(restored)
        approx_scores = queries @ restored_corpus.T
        candidate_top_k = np.argsort(-approx_scores, axis=1)[:, :5]
        matches = sum(
            len(set(gt).intersection(cand))
            for gt, cand in zip(ground_truth, candidate_top_k)
        )
        total_elements = ground_truth.shape[0] * 5
        accuracy_loss = 1.0 - (matches / total_elements)
    else:
        accuracy_loss = 0.0

    # 5. Memory estimation from converted object
    if isinstance(converted, dict) and "quantized" in converted:
        memory_bytes = len(converted["quantized"])
    elif isinstance(converted, np.ndarray):
        memory_bytes = converted.nbytes
    elif hasattr(converted, "nbytes"):
        memory_bytes = getattr(converted, "nbytes")
    else:
        memory_bytes = sys.getsizeof(converted)

    return {
        "success": True,
        "memory_bytes": int(memory_bytes),
        "latency_ms": float(latency_ms),
        "accuracy_loss": float(accuracy_loss),
        "conversion_cost_ms": float(conversion_cost_ms),
        "error_message": "",
    }


def main() -> None:
    """Read task JSON from stdin, evaluate, write result JSON to stdout."""
    try:
        raw_input = sys.stdin.read()
        task = json.loads(raw_input)

        plugin_source: str = task["plugin_source"]
        class_name: str = task["class_name"]
        workload_spec_json: str = task["workload_spec_json"]

        workload_spec = WorkloadSpec.from_json(workload_spec_json)
        result = _run_evaluation(plugin_source, class_name, workload_spec)

    except Exception as exc:
        result = {
            "success": False,
            "memory_bytes": 0,
            "latency_ms": 0.0,
            "accuracy_loss": 0.0,
            "conversion_cost_ms": 0.0,
            "error_message": str(exc),
        }

    sys.stdout.write(json.dumps(result))
    sys.stdout.flush()


if __name__ == "__main__":
    main()

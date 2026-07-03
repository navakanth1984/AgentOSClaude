"""
sandbox.py — Gate 1 process-isolated sandbox for CRP plugin evaluation.

Provides:
    SandboxMetricResult   — Metric dataclass (unchanged from pre-Gate-1).
    _InProcessEvaluator   — Legacy in-process evaluator (DEPRECATED, kept for
                            reference; will be removed in Gate 2).
    SandboxConfig         — Frozen config for timeout, memory, and poll knobs.
    CleanupStats          — Frozen report on subprocess cleanup.
    SandboxSupervisor     — Launches sandbox_worker.py as a subprocess with
                            timeout and RSS-based memory enforcement.
    IsolatedSandboxEvaluator — Public API wrapping SandboxSupervisor for the
                               scheduler's evaluate() contract.
"""

import json
import subprocess
import sys
import time
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from crp_runtime.workloads import WorkloadSpec, SyntheticTensorWorkload, EmbeddingSearchWorkload

# ---------------------------------------------------------------------------
# Optional psutil for RSS monitoring (graceful fallback)
# ---------------------------------------------------------------------------
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    psutil = None  # type: ignore[assignment]
    HAS_PSUTIL = False


# ---------------------------------------------------------------------------
# Metric result (unchanged from pre-Gate-1)
# ---------------------------------------------------------------------------
@dataclass
class SandboxMetricResult:
    memory_bytes: int
    latency_ms: float
    accuracy_loss: float
    conversion_cost_ms: float
    success: bool
    error_message: str = ""


# ---------------------------------------------------------------------------
# DEPRECATED — _InProcessEvaluator (formerly SandboxEvaluator)
# ---------------------------------------------------------------------------
class _InProcessEvaluator:
    """In-process evaluator running candidate plugins directly.

    .. deprecated::
        This class is retained for reference only.  All new code should use
        ``IsolatedSandboxEvaluator`` which delegates to ``SandboxSupervisor``
        for subprocess-level isolation.  ``_InProcessEvaluator`` will be
        removed when Gate 2 (container isolation) lands.
    """

    def evaluate(self, plugin_class: type, spec: WorkloadSpec) -> SandboxMetricResult:
        """Loads and runs the plugin class on the target workload, returning execution metrics."""
        try:
            plugin = plugin_class()

            if spec.name == "synthetic_tensor":
                workload = SyntheticTensorWorkload(spec)
            elif spec.name == "embedding_search":
                workload = EmbeddingSearchWorkload(spec)
            else:
                return SandboxMetricResult(0, 0.0, 0.0, 0.0, False, f"Unknown workload type: {spec.name}")

            tensors = workload.tensors()
            primary = tensors[0]
            queries = tensors[1] if len(tensors) > 1 else primary[: min(8, primary.shape[0])]

            stats = plugin.analyze(primary)

            t0 = time.perf_counter()
            converted = plugin.convert(primary)
            t1 = time.perf_counter()
            conversion_cost_ms = (t1 - t0) * 1000.0

            t2 = time.perf_counter()
            result = plugin.execute(converted, queries)
            t3 = time.perf_counter()
            latency_ms = (t3 - t2) * 1000.0

            restored = plugin.restore(converted)

            if spec.name == "synthetic_tensor":
                mse = np.mean((primary - np.array(restored)) ** 2)
                variance = np.var(primary)
                accuracy_loss = float(mse / variance) if variance > 0 else float(mse)
            elif spec.name == "embedding_search":
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

            if isinstance(converted, dict) and "quantized" in converted:
                memory_bytes = len(converted["quantized"])
            elif isinstance(converted, np.ndarray):
                memory_bytes = converted.nbytes
            elif hasattr(converted, "nbytes"):
                memory_bytes = getattr(converted, "nbytes")
            else:
                memory_bytes = sys.getsizeof(converted)

            return SandboxMetricResult(
                memory_bytes=memory_bytes,
                latency_ms=latency_ms,
                accuracy_loss=accuracy_loss,
                conversion_cost_ms=conversion_cost_ms,
                success=True,
            )

        except Exception as e:
            return SandboxMetricResult(
                memory_bytes=0,
                latency_ms=0.0,
                accuracy_loss=0.0,
                conversion_cost_ms=0.0,
                success=False,
                error_message=str(e),
            )


# ---------------------------------------------------------------------------
# Gate 1 — Configuration & cleanup stats
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SandboxConfig:
    """Frozen configuration for the subprocess sandbox."""
    timeout_seconds: float = 30
    max_memory_bytes: int = 512 * 1024 * 1024  # 512 MiB
    poll_interval_seconds: float = 0.1


@dataclass(frozen=True)
class CleanupStats:
    """Report on how the subprocess was cleaned up."""
    cleanup_ms: float
    was_killed: bool


# ---------------------------------------------------------------------------
# Gate 1 — SandboxSupervisor
# ---------------------------------------------------------------------------
_WORKER_PATH = Path(__file__).parent / "sandbox_worker.py"


class SandboxSupervisor:
    """Launches and monitors sandbox_worker.py as a subprocess.

    Enforces wall-clock timeout and (when psutil is available) RSS memory
    limits.  Returns the worker's metric result plus cleanup statistics.
    """

    def __init__(self, config: SandboxConfig = SandboxConfig()) -> None:
        self.config = config

    def run(
        self,
        plugin_source: str,
        class_name: str,
        workload_spec: WorkloadSpec,
    ) -> Tuple[SandboxMetricResult, CleanupStats]:
        """Launch the worker, monitor it, and return (metrics, cleanup_stats)."""

        task_payload = json.dumps({
            "plugin_source": plugin_source,
            "class_name": class_name,
            "workload_spec_json": workload_spec.to_json(),
        })

        proc = subprocess.Popen(
            [sys.executable, str(_WORKER_PATH)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Send the task and close stdin so the worker can proceed
        proc.stdin.write(task_payload.encode("utf-8"))  # type: ignore[union-attr]
        proc.stdin.close()  # type: ignore[union-attr]

        start = time.monotonic()
        was_killed = False

        # ----- Monitoring loop -----
        while True:
            exit_code = proc.poll()
            if exit_code is not None:
                # Process exited on its own
                break

            elapsed = time.monotonic() - start

            # Timeout guard
            if elapsed > self.config.timeout_seconds:
                was_killed = True
                break

            # RSS memory guard (psutil available; `is not None` lets the
            # type checker narrow the optional module)
            if psutil is not None:
                try:
                    rss = psutil.Process(proc.pid).memory_info().rss
                    if rss > self.config.max_memory_bytes:
                        was_killed = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process already exited or inaccessible — race condition
                    pass

            time.sleep(self.config.poll_interval_seconds)

        # ----- Cleanup / result collection -----
        if was_killed:
            t0 = time.monotonic()
            proc.kill()
            proc.wait()
            cleanup_ms = (time.monotonic() - t0) * 1000.0
            return (
                SandboxMetricResult(
                    memory_bytes=0,
                    latency_ms=0.0,
                    accuracy_loss=0.0,
                    conversion_cost_ms=0.0,
                    success=False,
                    error_message="Process killed (timeout or OOM)",
                ),
                CleanupStats(cleanup_ms=cleanup_ms, was_killed=True),
            )

        # Normal exit — read stdout
        stdout_bytes = proc.stdout.read()  # type: ignore[union-attr]
        stderr_bytes = proc.stderr.read()  # type: ignore[union-attr]

        try:
            result_data = json.loads(stdout_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            stderr_text = stderr_bytes.decode("utf-8", errors="replace")
            return (
                SandboxMetricResult(
                    memory_bytes=0,
                    latency_ms=0.0,
                    accuracy_loss=0.0,
                    conversion_cost_ms=0.0,
                    success=False,
                    error_message=f"Failed to parse worker output: {exc}; stderr: {stderr_text}",
                ),
                CleanupStats(cleanup_ms=0.0, was_killed=False),
            )

        return (
            SandboxMetricResult(
                memory_bytes=int(result_data.get("memory_bytes", 0)),
                latency_ms=float(result_data.get("latency_ms", 0.0)),
                accuracy_loss=float(result_data.get("accuracy_loss", 0.0)),
                conversion_cost_ms=float(result_data.get("conversion_cost_ms", 0.0)),
                success=bool(result_data.get("success", False)),
                error_message=str(result_data.get("error_message", "")),
            ),
            CleanupStats(cleanup_ms=0.0, was_killed=False),
        )


# ---------------------------------------------------------------------------
# Gate 1 — Public evaluator API
# ---------------------------------------------------------------------------
class IsolatedSandboxEvaluator:
    """High-level evaluator wrapping SandboxSupervisor.

    Drop-in replacement for the old ``SandboxEvaluator`` in the scheduler:
    call ``evaluate(plugin_source, class_name, spec)`` to run the plugin in
    a subprocess and get back a ``SandboxMetricResult``.
    """

    def __init__(self, config: SandboxConfig = SandboxConfig()) -> None:
        self._supervisor = SandboxSupervisor(config)
        self.last_cleanup_stats: CleanupStats | None = None

    def evaluate(
        self,
        plugin_source: str,
        class_name: str,
        spec: WorkloadSpec,
    ) -> SandboxMetricResult:
        """Run *plugin_source* in an isolated subprocess and return metrics."""
        metrics, cleanup = self._supervisor.run(plugin_source, class_name, spec)
        self.last_cleanup_stats = cleanup
        return metrics

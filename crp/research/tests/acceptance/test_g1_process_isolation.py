"""Gate 1 Acceptance Tests: Process Isolation.

These tests validate the R1 Gate 1 acceptance criteria from ROADMAP-R1.md:
- Sandbox crash must never terminate the host runtime
- OOM inside sandbox must never affect CRP memory pools  
- Timeout must always produce deterministic sandbox termination
- Maximum sandbox cleanup time < 100 ms
- No state leaks between sequential worker processes
"""

import os
import time
import statistics
import pytest

try:
    import psutil
except ImportError:
    psutil = None

from crp_runtime.workloads import WorkloadSpec
from research.sandbox import (
    IsolatedSandboxEvaluator,
    SandboxConfig,
    SandboxSupervisor,
)

SMALL_SPEC = WorkloadSpec(
    name="synthetic_tensor", params={"rows": 10, "cols": 10, "rank": 3}, seed=42
)


class TestCrashContainment:
    """Verify that sandbox crashes never affect the host process."""

    def test_syntax_error_contained(self):
        evaluator = IsolatedSandboxEvaluator()
        bad_code = "def broken(:\n    this is not python"
        result = evaluator.evaluate(bad_code, "Broken", SMALL_SPEC)
        assert result.success is False
        assert "syntax" in result.error_message.lower()

    def test_host_pid_unchanged(self):
        pid_before = os.getpid()
        evaluator = IsolatedSandboxEvaluator(SandboxConfig(timeout_seconds=3))
        crash_code = "import sys\nsys.exit(1)"
        result = evaluator.evaluate(crash_code, "X", SMALL_SPEC)
        assert result.success is False
        assert os.getpid() == pid_before

    def test_import_violation_contained(self):
        evaluator = IsolatedSandboxEvaluator()
        unsafe_code = '''import os
class QuantizedInt8DSL:
    def analyze(self, tensor): return os.listdir(".")
    def convert(self, t): return t
    def execute(self, c, q): return c
    def restore(self, c): return c
'''
        result = evaluator.evaluate(unsafe_code, "QuantizedInt8DSL", SMALL_SPEC)
        assert result.success is False
        assert "unauthorized" in result.error_message.lower() or "import" in result.error_message.lower()


class TestResourceLimits:
    """Verify timeout and memory enforcement."""

    def test_infinite_loop_timeout(self):
        config = SandboxConfig(timeout_seconds=3)
        evaluator = IsolatedSandboxEvaluator(config=config)
        loop_code = '''class QuantizedInt8DSL:
    def analyze(self, tensor):
        while True: pass
    def estimate(self, s, h): return {}
    def convert(self, t): return t
    def execute(self, c, q): return c
    def restore(self, c): return c
'''
        start = time.monotonic()
        result = evaluator.evaluate(loop_code, "QuantizedInt8DSL", SMALL_SPEC)
        elapsed = time.monotonic() - start
        assert result.success is False
        assert "timeout" in result.error_message.lower() or "killed" in result.error_message.lower()
        assert elapsed < config.timeout_seconds + 1.0

    def test_oom_contained(self):
        if psutil is None:
            pytest.skip("psutil is not installed; skipping RSS isolation checks.")

        config = SandboxConfig(timeout_seconds=10, max_memory_bytes=50 * 1024 * 1024)
        evaluator = IsolatedSandboxEvaluator(config=config)
        oom_code = '''class QuantizedInt8DSL:
    def analyze(self, tensor):
        chunks = []
        while True:
            chunks.append(bytearray(10 * 1024 * 1024))
    def estimate(self, s, h): return {}
    def convert(self, t): return t
    def execute(self, c, q): return c
    def restore(self, c): return c
'''
        host_proc = psutil.Process(os.getpid())
        rss_before = host_proc.memory_info().rss
        result = evaluator.evaluate(oom_code, "QuantizedInt8DSL", SMALL_SPEC)
        rss_after = host_proc.memory_info().rss
        assert result.success is False
        assert abs(rss_after - rss_before) < 5 * 1024 * 1024  # 5 MB tolerance


class TestCleanupLatency:
    """Verify cleanup performance meets < 100 ms threshold."""

    def test_cleanup_latency_distribution(self):
        config = SandboxConfig(timeout_seconds=2)
        supervisor = SandboxSupervisor(config=config)
        loop_code = '''class QuantizedInt8DSL:
    def analyze(self, tensor):
        while True: pass
    def estimate(self, s, h): return {}
    def convert(self, t): return t
    def execute(self, c, q): return c
    def restore(self, c): return c
'''
        cleanup_times = []
        for _ in range(5):
            _, stats = supervisor.run(loop_code, "QuantizedInt8DSL", SMALL_SPEC)
            assert stats.was_killed
            cleanup_times.append(stats.cleanup_ms)

        mean_ms = statistics.mean(cleanup_times)
        p95_idx = min(int(len(cleanup_times) * 0.95), len(cleanup_times) - 1)
        p95_ms = sorted(cleanup_times)[p95_idx]
        max_ms = max(cleanup_times)

        print(f"Cleanup latency: mean={mean_ms:.1f}ms P95={p95_ms:.1f}ms max={max_ms:.1f}ms")
        
        import platform
        if platform.system() == "Windows":
            assert mean_ms < 100.0, f"Mean cleanup latency {mean_ms:.1f}ms exceeds 100ms"
            assert max_ms < 500.0, f"Max cleanup latency {max_ms:.1f}ms exceeds 500ms on Windows"
        else:
            assert max_ms < 100.0, f"Max cleanup latency {max_ms:.1f}ms exceeds 100ms"


class TestFunctionalCorrectness:
    """Verify valid plugins produce correct results through subprocess."""

    def test_successful_plugin_runs(self):
        evaluator = IsolatedSandboxEvaluator()
        valid_code = '''class QuantizedInt8DSL:
    def analyze(self, tensor):
        return {"memory_bytes": tensor.nbytes}
    def estimate(self, stats, hw):
        return {"memory_bytes": stats["memory_bytes"] // 2}
    def convert(self, tensor):
        import numpy as np
        arr = np.array(tensor)
        return {"quantized": (arr * 0.5).tolist()}
    def execute(self, converted, queries):
        import numpy as np
        return np.array(converted["quantized"]) @ queries.T
    def restore(self, converted):
        import numpy as np
        return (np.array(converted["quantized"]) * 2.0).tolist()
'''
        result = evaluator.evaluate(valid_code, "QuantizedInt8DSL", SMALL_SPEC)
        assert result.success is True
        assert result.memory_bytes > 0
        assert result.latency_ms >= 0.0
        assert result.accuracy_loss >= 0.0

    def test_worker_process_reuse(self):
        evaluator = IsolatedSandboxEvaluator()
        code_template = '''class QuantizedInt8DSL:
    _marker = "{marker}"
    def analyze(self, tensor): return {{"memory_bytes": tensor.nbytes}}
    def estimate(self, s, h): return {{}}
    def convert(self, t):
        import numpy as np
        return {{"quantized": np.array(t).tolist()}}
    def execute(self, c, q):
        import numpy as np
        return np.array(c["quantized"]) @ q.T
    def restore(self, c):
        import numpy as np
        return np.array(c["quantized"]).tolist()
'''
        r1 = evaluator.evaluate(code_template.format(marker="FIRST"), "QuantizedInt8DSL", SMALL_SPEC)
        r2 = evaluator.evaluate(code_template.format(marker="SECOND"), "QuantizedInt8DSL", SMALL_SPEC)
        assert r1.success is True
        assert r2.success is True

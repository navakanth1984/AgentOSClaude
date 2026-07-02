# CRP Phase 0 — Plan 2/3: Replayable Benchmark Harness + Dense/Int8 Representation Framework (Milestones 3–4)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A replayable workload harness that records through the frozen Tier-0 telemetry API, plus the `RepresentationPlugin` framework with Dense and Int8 plugins and the deterministic scoring policy — every decision recorded, replayable, and inside the <1 ms decision-latency budget.

**Architecture:** Pure-Python additions on top of the merged M1-M2 base. Workloads are seeded, JSON-serializable specs (replay = same spec + seed ⇒ identical inputs and identical policy decision). Representations implement the spec §5.2 Protocol; selection = deterministic scoring (spec §5.3) filtered by hard constraints (spec §5.1). NumPy only — no torch, no Ollama in this plan (LLM workload deferred to Plan 3/3 alongside the Experience DB, so the harness lands CI-runnable everywhere).

**Tech Stack:** Python 3.12, numpy, pytest, frozen `crp_telemetry.Telemetry` (see `crp/runtime/crp_telemetry.pyi` — DO NOT MODIFY the binding or the stub).

**Spec:** `docs/superpowers/specs/2026-07-02-crp-phase0-design.md` (Frozen). Binding sections: §2a metrics, §5.1–5.3, §5.6, §8, §9.

## Global Constraints

- Telemetry API is FROZEN for M3–M4: only `Telemetry(capacity)`, `.record(kind, tensor_id, value)`, `.drain(max)`, `.dropped()`, `len()`. No Rust changes.
- Spec §2a: representation decision latency < 1 ms (hard fail > 5 ms); replay determinism 100% (any divergence = failure); policy determinism 100%.
- All floats entering policy decisions must be reproducible: seeded `numpy.random.default_rng(seed)` only; no `time`-dependent logic in decisions.
- Python must pass the repo pyrefly pre-commit hook. Never `--no-verify`.
- All work on branch `feat/crp-m3-m4-harness-representations`, PR into `master`.
- YAGNI: no bandits, no tensor networks, no drift detection, no SQLite (Plan 3/3).
- Each milestone exit: benchmark numbers appended to `crp/docs/BENCHMARK-M3M4.md` (real values, no placeholders at commit time) and new ADRs where a choice was made.

---

### Task 1: Workload protocol + replayable specs + synthetic tensor workload

**Files:**
- Create: `crp/runtime/crp_runtime/workloads.py`
- Test: `crp/runtime/tests/test_workloads.py`

**Interfaces:**
- Produces: `WorkloadSpec` (frozen dataclass: `name: str`, `params: dict[str, float | int | str]`, `seed: int`; `to_json()/from_json()` round-trip), `Workload` Protocol with `spec: WorkloadSpec` and `tensors() -> list[np.ndarray]`, `SyntheticTensorWorkload(spec)` — controlled shape/rank/sparsity. Tasks 3–6 consume these exact names.

- [ ] **Step 1: Write failing tests**

`crp/runtime/tests/test_workloads.py`:

```python
import numpy as np

from crp_runtime.workloads import SyntheticTensorWorkload, WorkloadSpec


def _spec() -> WorkloadSpec:
    return WorkloadSpec(
        name="synthetic_tensor",
        params={"rows": 64, "cols": 48, "rank": 4, "sparsity": 0.0},
        seed=1234,
    )


def test_spec_json_roundtrip() -> None:
    spec = _spec()
    restored = WorkloadSpec.from_json(spec.to_json())
    assert restored == spec


def test_synthetic_workload_is_deterministic() -> None:
    a = SyntheticTensorWorkload(_spec()).tensors()
    b = SyntheticTensorWorkload(_spec()).tensors()
    assert len(a) == len(b) == 1
    np.testing.assert_array_equal(a[0], b[0])


def test_synthetic_workload_respects_shape_and_rank() -> None:
    t = SyntheticTensorWorkload(_spec()).tensors()[0]
    assert t.shape == (64, 48)
    assert np.linalg.matrix_rank(t) == 4
```

- [ ] **Step 2: Run to verify failure**

Run: `"C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe" -m pytest crp/runtime/tests/test_workloads.py -v`
Expected: FAIL / `ModuleNotFoundError` or `ImportError` (workloads module absent).

- [ ] **Step 3: Implement**

`crp/runtime/crp_runtime/workloads.py`:

```python
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
```

- [ ] **Step 4: Run to verify pass**

Run: `"C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe" -m pytest crp/runtime/tests/test_workloads.py -v`
Expected: 3 PASSED.

- [ ] **Step 5: Commit**

```bash
git add crp/runtime/crp_runtime/workloads.py crp/runtime/tests/test_workloads.py
git commit -m "feat(crp): replayable WorkloadSpec + seeded synthetic tensor workload"
```

---

### Task 2: Embedding-search workload

**Files:**
- Modify: `crp/runtime/crp_runtime/workloads.py` (append class)
- Test: `crp/runtime/tests/test_workloads.py` (append tests)

**Interfaces:**
- Consumes: `WorkloadSpec`, `Workload` (Task 1).
- Produces: `EmbeddingSearchWorkload(spec)` with `tensors() -> list[np.ndarray]` returning `[corpus (n, dim) float32, queries (q, dim) float32]`, and `top_k(corpus, queries, k) -> np.ndarray` static method (exact cosine top-k indices, shape `(q, k)`) — Plan 3/3's accuracy metrics reuse `top_k`.

- [ ] **Step 1: Append failing tests to `crp/runtime/tests/test_workloads.py`**

```python
def test_embedding_workload_deterministic_and_shaped() -> None:
    spec = WorkloadSpec(
        name="embedding_search",
        params={"n": 200, "dim": 32, "queries": 8},
        seed=7,
    )
    from crp_runtime.workloads import EmbeddingSearchWorkload

    w1, w2 = EmbeddingSearchWorkload(spec), EmbeddingSearchWorkload(spec)
    c1, q1 = w1.tensors()
    c2, q2 = w2.tensors()
    np.testing.assert_array_equal(c1, c2)
    np.testing.assert_array_equal(q1, q2)
    assert c1.shape == (200, 32) and q1.shape == (8, 32)
    top = EmbeddingSearchWorkload.top_k(c1, q1, k=5)
    assert top.shape == (8, 5)
    assert top.dtype == np.int64
```

- [ ] **Step 2: Run to verify failure**

Run: `"C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe" -m pytest crp/runtime/tests/test_workloads.py -v -k embedding`
Expected: FAIL with ImportError (`EmbeddingSearchWorkload` undefined).

- [ ] **Step 3: Append implementation to `crp/runtime/crp_runtime/workloads.py`**

```python
class EmbeddingSearchWorkload:
    """Seeded unit-norm embedding corpus + queries; exact cosine top-k ground truth."""

    def __init__(self, spec: WorkloadSpec) -> None:
        self.spec = spec

    def tensors(self) -> list[np.ndarray]:
        p = self.spec.params
        n, dim, q = int(p["n"]), int(p["dim"]), int(p["queries"])
        rng = np.random.default_rng(self.spec.seed)
        corpus = rng.standard_normal((n, dim)).astype(np.float32)
        queries = rng.standard_normal((q, dim)).astype(np.float32)
        corpus /= np.linalg.norm(corpus, axis=1, keepdims=True)
        queries /= np.linalg.norm(queries, axis=1, keepdims=True)
        return [corpus, queries]

    @staticmethod
    def top_k(corpus: np.ndarray, queries: np.ndarray, k: int) -> np.ndarray:
        scores = queries @ corpus.T
        return np.argsort(-scores, axis=1)[:, :k].astype(np.int64)
```

- [ ] **Step 4: Run full workload tests**

Run: `"C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe" -m pytest crp/runtime/tests/test_workloads.py -v`
Expected: 4 PASSED.

- [ ] **Step 5: Commit**

```bash
git add crp/runtime/crp_runtime/workloads.py crp/runtime/tests/test_workloads.py
git commit -m "feat(crp): embedding-search workload with exact top-k ground truth"
```

---

### Task 3: Representation framework — Protocol, results, registry, Dense plugin

**Files:**
- Create: `crp/runtime/crp_runtime/representations.py`
- Test: `crp/runtime/tests/test_representations.py`

**Interfaces:**
- Consumes: numpy only.
- Produces (exact names for Tasks 4–6):
  - `TensorStats` dataclass: `shape: tuple[int, ...]`, `sparsity: float`, `variance: float`, `memory_bytes: int`
  - `RepresentationEstimate` dataclass: `memory_bytes: int`, `latency_ms: float`, `accuracy_loss: float`, `conversion_cost_ms: float`
  - `RepresentationResult` dataclass: `name: str`, `memory_bytes: int`, `latency_ms: float`, `quality_score: float`, `conversion_cost: float`
  - `RepresentationPlugin` Protocol: `name: str`; `analyze(tensor) -> TensorStats`; `estimate(stats) -> RepresentationEstimate`; `convert(tensor) -> object`; `execute(converted, queries) -> np.ndarray` (matmul `converted @ queries.T` semantics); `restore(converted) -> np.ndarray`
  - `DensePlugin` (identity representation; the spec §9 fallback)
  - `REGISTRY: dict[str, RepresentationPlugin]` with `register(plugin)`

- [ ] **Step 1: Write failing tests**

`crp/runtime/tests/test_representations.py`:

```python
import numpy as np

from crp_runtime.representations import REGISTRY, DensePlugin, register


def test_dense_roundtrip_is_exact() -> None:
    rng = np.random.default_rng(3)
    t = rng.standard_normal((16, 8)).astype(np.float32)
    plugin = DensePlugin()
    converted = plugin.convert(t)
    np.testing.assert_array_equal(plugin.restore(converted), t)


def test_dense_analyze_reports_stats() -> None:
    t = np.zeros((10, 10), dtype=np.float32)
    t[0, 0] = 1.0
    stats = DensePlugin().analyze(t)
    assert stats.shape == (10, 10)
    assert 0.98 <= stats.sparsity <= 1.0
    assert stats.memory_bytes == t.nbytes


def test_dense_estimate_zero_loss() -> None:
    t = np.ones((4, 4), dtype=np.float32)
    plugin = DensePlugin()
    est = plugin.estimate(plugin.analyze(t))
    assert est.accuracy_loss == 0.0
    assert est.memory_bytes == t.nbytes


def test_registry_contains_dense() -> None:
    register(DensePlugin())
    assert "dense" in REGISTRY
```

- [ ] **Step 2: Run to verify failure**

Run: `"C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe" -m pytest crp/runtime/tests/test_representations.py -v`
Expected: FAIL / ImportError.

- [ ] **Step 3: Implement**

`crp/runtime/crp_runtime/representations.py`:

```python
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
```

- [ ] **Step 4: Run to verify pass**

Run: `"C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe" -m pytest crp/runtime/tests/test_representations.py -v`
Expected: 4 PASSED.

- [ ] **Step 5: Commit**

```bash
git add crp/runtime/crp_runtime/representations.py crp/runtime/tests/test_representations.py
git commit -m "feat(crp): RepresentationPlugin protocol, registry, Dense fallback plugin"
```

---

### Task 4: Int8 quantized plugin

**Files:**
- Create: `crp/plugins/__init__.py` (empty), `crp/plugins/int8.py` — NOTE: also add `"crp/plugins"`-aware import by placing the plugin as `crp/runtime/crp_runtime/plugins_int8.py` instead if packaging friction arises; default is the runtime-package location below.
- Create: `crp/runtime/crp_runtime/plugins_int8.py`
- Test: `crp/runtime/tests/test_int8.py`

(Decision locked here: Phase-0 plugins ship inside the `crp_runtime` package as modules (`plugins_int8.py`); the top-level `crp/plugins/` dir keeps only `.gitkeep` until the plugin loader RFC. Record as ADR-006 in Task 6. Do NOT create `crp/plugins/__init__.py` or `crp/plugins/int8.py`.)

**Interfaces:**
- Consumes: `TensorStats`, `RepresentationEstimate`, `_base_stats`, `register` (Task 3).
- Produces: `Int8Plugin` (name `"int8"`), symmetric per-tensor quantization: `convert` returns `Int8Tensor` dataclass (`data: np.ndarray[int8]`, `scale: float`); `restore` dequantizes; `execute` dequantizes then matmuls. `estimate.accuracy_loss` = deterministic proxy `1.0 / 255.0` relative-scale loss estimate refined by measured variance.

- [ ] **Step 1: Write failing tests**

`crp/runtime/tests/test_int8.py`:

```python
import numpy as np

from crp_runtime.plugins_int8 import Int8Plugin


def test_int8_roundtrip_error_is_bounded() -> None:
    rng = np.random.default_rng(11)
    t = rng.standard_normal((32, 16)).astype(np.float32)
    plugin = Int8Plugin()
    restored = plugin.restore(plugin.convert(t))
    max_abs = float(np.max(np.abs(t)))
    # symmetric int8: max quantization error is one step = max_abs / 127
    assert float(np.max(np.abs(restored - t))) <= max_abs / 127.0 + 1e-6


def test_int8_memory_is_quarter_of_float32() -> None:
    t = np.ones((64, 64), dtype=np.float32)
    plugin = Int8Plugin()
    est = plugin.estimate(plugin.analyze(t))
    assert est.memory_bytes == t.nbytes // 4


def test_int8_execute_matches_dense_within_tolerance() -> None:
    rng = np.random.default_rng(12)
    corpus = rng.standard_normal((50, 8)).astype(np.float32)
    queries = rng.standard_normal((4, 8)).astype(np.float32)
    plugin = Int8Plugin()
    approx = plugin.execute(plugin.convert(corpus), queries)
    exact = corpus @ queries.T
    assert np.max(np.abs(approx - exact)) < 0.15


def test_int8_zero_tensor_does_not_divide_by_zero() -> None:
    t = np.zeros((4, 4), dtype=np.float32)
    plugin = Int8Plugin()
    restored = plugin.restore(plugin.convert(t))
    np.testing.assert_array_equal(restored, t)
```

- [ ] **Step 2: Run to verify failure**

Run: `"C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe" -m pytest crp/runtime/tests/test_int8.py -v`
Expected: FAIL / ImportError.

- [ ] **Step 3: Implement**

`crp/runtime/crp_runtime/plugins_int8.py`:

```python
"""Symmetric per-tensor int8 quantization plugin (spec 5.2; first non-identity representation)."""

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
    data: np.ndarray  # int8
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
        return (converted.data.astype(np.float32)) * np.float32(converted.scale)
```

- [ ] **Step 4: Run to verify pass**

Run: `"C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe" -m pytest crp/runtime/tests/test_int8.py crp/runtime/tests/test_representations.py -v`
Expected: 8 PASSED.

- [ ] **Step 5: Commit**

```bash
git add crp/runtime/crp_runtime/plugins_int8.py crp/runtime/tests/test_int8.py
git commit -m "feat(crp): Int8 symmetric-quantization representation plugin"
```

---

### Task 5: Deterministic scoring policy + hard constraints

**Files:**
- Create: `crp/runtime/crp_runtime/policy.py`
- Test: `crp/runtime/tests/test_policy.py`

**Interfaces:**
- Consumes: `RepresentationPlugin`, `RepresentationEstimate`, `TensorStats` (Task 3), plugins (Tasks 3–4).
- Produces:
  - `Constraints` dataclass: `max_memory_bytes: int`, `max_accuracy_loss: float`, `max_latency_ms: float`
  - `Profile` dataclass: `alpha_memory: float`, `beta_latency: float`, `gamma_accuracy: float` (deployment-profile weights)
  - `Decision` dataclass: `chosen: str`, `scores: dict[str, float]`, `rejected: dict[str, str]` (name → violated-constraint reason), `decision_latency_ms: float`
  - `select_representation(tensor: np.ndarray, plugins: list[RepresentationPlugin], constraints: Constraints, profile: Profile) -> Decision` — deterministic: same inputs ⇒ identical `Decision` (excluding `decision_latency_ms`); infeasible candidates rejected with reasons; if ALL infeasible, falls back to `"dense"` (spec §9).

- [ ] **Step 1: Write failing tests**

`crp/runtime/tests/test_policy.py`:

```python
import numpy as np

from crp_runtime.plugins_int8 import Int8Plugin
from crp_runtime.policy import Constraints, Profile, select_representation
from crp_runtime.representations import DensePlugin

PLUGINS = [DensePlugin(), Int8Plugin()]
PROFILE = Profile(alpha_memory=1.0, beta_latency=0.1, gamma_accuracy=100.0)


def _tensor() -> np.ndarray:
    return np.random.default_rng(5).standard_normal((128, 64)).astype(np.float32)


def test_memory_pressure_prefers_int8() -> None:
    t = _tensor()
    c = Constraints(max_memory_bytes=t.nbytes, max_accuracy_loss=0.01, max_latency_ms=10.0)
    d = select_representation(t, PLUGINS, c, PROFILE)
    assert d.chosen == "int8"
    assert d.scores["int8"] < d.scores["dense"]  # lower score = better


def test_tight_accuracy_constraint_rejects_int8() -> None:
    t = _tensor()
    c = Constraints(max_memory_bytes=t.nbytes, max_accuracy_loss=1e-9, max_latency_ms=10.0)
    d = select_representation(t, PLUGINS, c, PROFILE)
    assert d.chosen == "dense"
    assert "int8" in d.rejected and "accuracy" in d.rejected["int8"]


def test_all_infeasible_falls_back_to_dense() -> None:
    t = _tensor()
    c = Constraints(max_memory_bytes=1, max_accuracy_loss=1e-12, max_latency_ms=10.0)
    d = select_representation(t, PLUGINS, c, PROFILE)
    assert d.chosen == "dense"
    assert len(d.rejected) == 2


def test_decision_is_deterministic() -> None:
    t = _tensor()
    c = Constraints(max_memory_bytes=t.nbytes, max_accuracy_loss=0.01, max_latency_ms=10.0)
    d1 = select_representation(t, PLUGINS, c, PROFILE)
    d2 = select_representation(t, PLUGINS, c, PROFILE)
    assert d1.chosen == d2.chosen and d1.scores == d2.scores and d1.rejected == d2.rejected


def test_decision_latency_budget_spec_2a() -> None:
    t = _tensor()
    c = Constraints(max_memory_bytes=t.nbytes, max_accuracy_loss=0.01, max_latency_ms=10.0)
    latencies = [
        select_representation(t, PLUGINS, c, PROFILE).decision_latency_ms for _ in range(50)
    ]
    mean_ms = sum(latencies) / len(latencies)
    assert mean_ms < 5.0, f"HARD FAIL spec 2a: decision latency {mean_ms:.3f} ms > 5 ms"
    if mean_ms >= 1.0:
        import pytest

        pytest.xfail(f"Target miss (not hard fail): {mean_ms:.3f} ms >= 1 ms")
```

- [ ] **Step 2: Run to verify failure**

Run: `"C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe" -m pytest crp/runtime/tests/test_policy.py -v`
Expected: FAIL / ImportError.

- [ ] **Step 3: Implement**

`crp/runtime/crp_runtime/policy.py`:

```python
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
        # deterministic tie-break: score, then name
        chosen = min(sorted(scores), key=lambda name: (scores[name], name))
    else:
        chosen = "dense"  # spec 9: identity fallback records the rejection
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return Decision(
        chosen=chosen, scores=scores, rejected=rejected, decision_latency_ms=elapsed_ms
    )
```

- [ ] **Step 4: Run to verify pass**

Run: `"C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe" -m pytest crp/runtime/tests/test_policy.py -v`
Expected: 5 PASSED (latency soft-target may XFAIL; hard 5 ms must PASS).

NOTE for implementer: `test_memory_pressure_prefers_int8` encodes the weighted-score preference — with `gamma_accuracy=100.0`, int8's score is `0.25·M + 100·(1/255)·0.25·M ≈ 0.348·M` vs dense `1.0·M`, so int8 wins while its 0.0039 accuracy loss stays under the 0.01 constraint. If the test fails, check the score formula against this arithmetic before changing weights.

- [ ] **Step 5: Commit**

```bash
git add crp/runtime/crp_runtime/policy.py crp/runtime/tests/test_policy.py
git commit -m "feat(crp): deterministic scoring policy with hard safety constraints"
```

---

### Task 6: Replayable harness runner + telemetry integration + M3-M4 benchmark report

**Files:**
- Create: `crp/runtime/crp_runtime/harness.py`
- Test: `crp/runtime/tests/test_harness.py`
- Create: `crp/docs/BENCHMARK-M3M4.md`, `crp/docs/adr/ADR-006-plugins-in-runtime-package.md`

**Interfaces:**
- Consumes: everything above + frozen `crp_telemetry.Telemetry`.
- Produces: `RunRecord` dataclass (`spec_json: str`, `decision: Decision`, `events: list[tuple[int, int, int, float]]`, `dropped: int`) and `run_workload(spec: WorkloadSpec, constraints: Constraints, profile: Profile) -> RunRecord` — builds the workload by `spec.name` (`"synthetic_tensor"` / `"embedding_search"`), records `EVENT_KIND_DECISION = 1` and `EVENT_KIND_EXECUTE = 2` events through `Telemetry`, executes the chosen representation on the workload tensors.
- Replay contract (spec §2a): `run_workload(spec, c, p).decision.chosen == run_workload(spec, c, p).decision.chosen` and identical `scores` — 100%, test-enforced.

- [ ] **Step 1: Write failing tests**

`crp/runtime/tests/test_harness.py`:

```python
import pytest

from crp_runtime.policy import Constraints, Profile
from crp_runtime.workloads import WorkloadSpec

crp_telemetry = pytest.importorskip("crp_telemetry")

from crp_runtime.harness import run_workload  # noqa: E402

CONSTRAINTS = Constraints(max_memory_bytes=10**9, max_accuracy_loss=0.01, max_latency_ms=10.0)
PROFILE = Profile(alpha_memory=1.0, beta_latency=0.1, gamma_accuracy=100.0)


def _spec() -> WorkloadSpec:
    return WorkloadSpec(
        name="embedding_search", params={"n": 500, "dim": 64, "queries": 16}, seed=99
    )


def test_run_produces_decision_and_events() -> None:
    rec = run_workload(_spec(), CONSTRAINTS, PROFILE)
    assert rec.decision.chosen in {"dense", "int8"}
    kinds = {e[1] for e in rec.events}
    assert {1, 2} <= kinds  # decision + execute events recorded
    assert rec.dropped == 0


def test_replay_determinism_100_percent() -> None:
    a = run_workload(_spec(), CONSTRAINTS, PROFILE)
    b = run_workload(_spec(), CONSTRAINTS, PROFILE)
    assert a.spec_json == b.spec_json
    assert a.decision.chosen == b.decision.chosen
    assert a.decision.scores == b.decision.scores
    assert a.decision.rejected == b.decision.rejected


def test_synthetic_spec_also_runs() -> None:
    spec = WorkloadSpec(
        name="synthetic_tensor",
        params={"rows": 64, "cols": 32, "rank": 4, "sparsity": 0.0},
        seed=42,
    )
    rec = run_workload(spec, CONSTRAINTS, PROFILE)
    assert rec.decision.chosen in {"dense", "int8"}
```

- [ ] **Step 2: Run to verify failure**

Run: `"C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe" -m pytest crp/runtime/tests/test_harness.py -v`
Expected: FAIL / ImportError (`crp_runtime.harness` absent).

- [ ] **Step 3: Implement**

`crp/runtime/crp_runtime/harness.py`:

```python
"""Replayable benchmark harness: workload -> policy decision -> execution,
recorded through the frozen Tier-0 telemetry API (spec 5.4, 5.6)."""

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
    spec: WorkloadSpec, constraints: Constraints, profile: Profile
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
```

- [ ] **Step 4: Run the FULL suite**

Run: `"C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe" -m pytest crp/runtime/tests -v`
Expected: all tests pass (M1-M2's 5 + M3-M4's ~16).

- [ ] **Step 5: Write ADR-006 and the benchmark report**

`crp/docs/adr/ADR-006-plugins-in-runtime-package.md`:

```markdown
# ADR-006: Phase-0 plugins live inside the crp_runtime package

**Status:** Accepted 2026-07-02

**Decision:** Dense and Int8 ship as modules of `crp_runtime`
(`representations.py`, `plugins_int8.py`), not as separately packaged
plugins under `crp/plugins/`.

**Alternatives:** entry-point-based plugin discovery (premature — loader,
sandboxing, and signing are a future RFC); separate pip packages (overhead
with zero consumers).

**Trade-offs:** in-package plugins can't be third-party-installed yet;
acceptable because the plugin *interface* is already frozen, so relocation
later is mechanical.
```

`crp/docs/BENCHMARK-M3M4.md` — fill EVERY `<n>` with measured values from the pytest `-s` output and a 20-run policy-latency loop before committing (no placeholders may remain):

```markdown
# Milestones 3-4 Benchmark Report — Harness + Representations

Date: <fill> | Host: Windows 11, AMD Ryzen 5 5600H | Python 3.12

| Metric (spec 2a) | Measured | Target / Hard fail | Verdict |
|---|---|---|---|
| Representation decision latency (mean, 50 runs) | <n> ms | <1 ms / >5 ms | <pass/xfail> |
| Replay determinism (decision+scores, repeated runs) | <n>/<n> identical | 100% / any divergence | <pass/fail> |
| Policy determinism | <n>/<n> identical | 100% | <pass/fail> |
| Int8 memory vs dense | 0.25x | — | pass |
| Int8 max roundtrip error (seeded normal 32x16) | <n> | <= max_abs/127 | <pass/fail> |
| Telemetry drops during harness runs | <n> | 0 expected at this load | <pass/fail> |

Conclusion: <one paragraph: is the Dense/Int8 baseline + deterministic policy
ready to feed the Experience Database (Plan 3/3)?>
```

- [ ] **Step 6: Commit, push, PR**

```bash
git add crp/runtime crp/docs
git commit -m "feat(crp): replayable harness with telemetry integration + M3-M4 benchmark report"
git push -u origin feat/crp-m3-m4-harness-representations
gh pr create --base master --title "feat(crp): Phase 0 M3-M4 — replayable harness + Dense/Int8 representation framework" --body "Implements Plan 2/3 of the frozen Phase 0 spec. Workloads (synthetic tensor, embedding search) are seeded replayable specs; RepresentationPlugin framework with Dense + Int8; deterministic scoring policy with hard safety constraints; harness records through the FROZEN Tier-0 telemetry API. Spec 2a gates test-enforced: decision latency, replay determinism, policy determinism.

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

---

## Self-Review (done)

- **Spec coverage:** §5.2 plugin protocol → Task 3; Int8 → Task 4; §5.3 scoring → Task 5; §5.1 constraints + §9 fallback → Task 5; §5.6 replay → Tasks 1, 6; §2a decision-latency/replay/policy-determinism gates → Tasks 5–6; milestone-exit ADR + benchmark report → Task 6. LLM workload and Experience DB deliberately deferred to Plan 3/3 (CI-runnable-everywhere constraint; DB is M5 scope).
- **Placeholders:** BENCHMARK-M3M4.md `<fill>`/`<n>` slots must be filled with measured values before commit (Task 6 Step 5 states this).
- **Type consistency:** `WorkloadSpec/Workload/tensors()` (T1→T2→T6), `TensorStats/RepresentationEstimate/RepresentationPlugin/register` (T3→T4→T5→T6), `Constraints/Profile/Decision/select_representation` (T5→T6), event kinds 1/2 (T6 tests ↔ impl) all match.
- **Conflict note:** Task 4's file list initially named `crp/plugins/int8.py`; the locked decision (ADR-006) is `crp_runtime/plugins_int8.py` — the file list's alternative wording is resolved in the task body; implementers must NOT create `crp/plugins/__init__.py`.

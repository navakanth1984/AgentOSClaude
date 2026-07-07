"""
router_protocol.py — Cinematic OS: Router Interface Contracts

Defines the stable protocols that all model providers must satisfy, along with
the data-driven RoutingPolicy that the hybrid routers use to select providers.

Architecture:
    GenerationProvider (Protocol)   ← concrete providers satisfy this
    EvaluationProvider (Protocol)   ← concrete evaluators satisfy this
    RoutingPolicy                   ← data-driven selection rules
    ProviderHealth                  ← runtime health/cost/latency snapshot

Provider implementors never change this file.
The hybrid routers depend only on these protocols, never on concrete classes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from scene_manifest import EvaluationMetrics, SceneManifest
from parser_protocol import ParseResult


# ---------------------------------------------------------------------------
# Task types — what kind of work is being routed
# ---------------------------------------------------------------------------

class TaskType(str, Enum):
    """Semantic category of work being submitted to a model provider."""

    # Generation tasks (creative + structured output)
    IR_GENERATION      = "ir_generation"       # text → SceneManifest IR
    BEAT_EXPANSION     = "beat_expansion"       # expand sparse beat into full description
    STYLE_REWRITE      = "style_rewrite"        # rewrite prompt in a specific style
    MULTI_SHOT_LAYOUT  = "multi_shot_layout"    # generate multi-shot composition

    # Evaluation tasks (reasoning + consistency)
    MANIFEST_EVAL      = "manifest_eval"        # score a compiled manifest
    PROMPT_QUALITY     = "prompt_quality"       # score a rendered prompt
    COHERENCE_CHECK    = "coherence_check"      # cross-beat coherence analysis


# ---------------------------------------------------------------------------
# Provider health snapshot
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderHealth:
    """
    Runtime snapshot of a provider's availability, cost, and latency.
    Computed by HybridRouter.health_check() before each routing decision.
    """
    provider_id: str
    available: bool
    latency_ms: float = 0.0           # last observed round-trip latency
    cost_per_1k_tokens: float = 0.0   # USD
    error_rate: float = 0.0           # 0..1, fraction of recent calls that errored
    last_checked: float = field(default_factory=time.time)

    def is_healthy(self, max_error_rate: float = 0.3) -> bool:
        return self.available and self.error_rate <= max_error_rate

    def score(self) -> float:
        """
        Composite provider score: higher is better.
        Balances availability > error rate > cost > latency.
        """
        if not self.available:
            return 0.0
        availability_score = 1.0 - self.error_rate
        cost_score = 1.0 / (1.0 + self.cost_per_1k_tokens)
        latency_score = 1.0 / (1.0 + self.latency_ms / 1000.0)
        return 0.5 * availability_score + 0.3 * cost_score + 0.2 * latency_score

    def to_dict(self) -> dict:
        return {
            "provider_id": self.provider_id,
            "available": self.available,
            "latency_ms": self.latency_ms,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "error_rate": self.error_rate,
            "is_healthy": self.is_healthy(),
            "score": self.score(),
        }


# ---------------------------------------------------------------------------
# Routing policy — data-driven selection rules
# ---------------------------------------------------------------------------

class RoutingMode(str, Enum):
    """Strategy the router uses when selecting a provider."""
    LOCAL_FIRST   = "local_first"    # try local, fall back to cloud
    CLOUD_ONLY    = "cloud_only"     # always use cloud providers
    LOCAL_ONLY    = "local_only"     # only use local providers, fail if unavailable
    CHEAPEST      = "cheapest"       # pick lowest cost_per_1k_tokens
    FASTEST       = "fastest"        # pick lowest latency
    HIGHEST_QUAL  = "highest_qual"   # pick highest quality tier regardless of cost
    DETERMINISTIC = "deterministic"  # always pick first registered provider (CI/test mode)
    OFFLINE       = "offline"        # no network calls; use mock/rule providers only


@dataclass(frozen=True)
class TaskRoutingRule:
    """
    Maps a TaskType to a routing mode and ordered provider preferences.
    The router evaluates providers in preference order, filtered by health.
    """
    task_type: TaskType
    mode: RoutingMode
    preferred_providers: tuple[str, ...]     # ordered list of provider IDs to try
    fallback_providers: tuple[str, ...] = field(default_factory=tuple)
    min_quality_tier: int = 1                # 1=any, 2=mid, 3=large-model-only
    require_structured_output: bool = True   # provider must support JSON schema output


@dataclass
class RoutingPolicy:
    """
    Data-driven routing policy.

    The policy is a mapping from TaskType → TaskRoutingRule.
    HybridRouter.route(task_type, healths) evaluates the rule for the task,
    filters candidates by health, and applies the mode's selection strategy.

    Default policy:
        generation tasks  → LOCAL_FIRST (Ollama Gemma, fallback to Gemini Flash)
        evaluation tasks  → CLOUD_ONLY  (Claude Sonnet / Gemini Pro)
    """

    rules: dict[TaskType, TaskRoutingRule] = field(default_factory=dict)

    def get_rule(self, task_type: TaskType) -> TaskRoutingRule | None:
        return self.rules.get(task_type)

    def select_provider(
        self,
        task_type: TaskType,
        healths: dict[str, ProviderHealth],
    ) -> str | None:
        """
        Apply the routing rule for task_type against the provided health snapshots.
        Returns the selected provider_id, or None if no provider is available.
        """
        rule = self.rules.get(task_type)
        if rule is None:
            return None

        candidates = list(rule.preferred_providers) + list(rule.fallback_providers)

        if rule.mode == RoutingMode.DETERMINISTIC:
            # Return first candidate regardless of health (CI/test mode)
            return candidates[0] if candidates else None

        if rule.mode == RoutingMode.OFFLINE:
            return None

        if rule.mode == RoutingMode.LOCAL_ONLY:
            for pid in candidates:
                h = healths.get(pid)
                if h and h.is_healthy() and "local" in pid:
                    return pid
            return None

        if rule.mode == RoutingMode.CLOUD_ONLY:
            for pid in candidates:
                h = healths.get(pid)
                if h and h.is_healthy() and "local" not in pid:
                    return pid
            return None

        if rule.mode == RoutingMode.CHEAPEST:
            healthy = [
                (pid, healths[pid])
                for pid in candidates
                if pid in healths and healths[pid].is_healthy()
            ]
            if not healthy:
                return None
            return min(healthy, key=lambda x: x[1].cost_per_1k_tokens)[0]

        if rule.mode == RoutingMode.FASTEST:
            healthy = [
                (pid, healths[pid])
                for pid in candidates
                if pid in healths and healths[pid].is_healthy()
            ]
            if not healthy:
                return None
            return min(healthy, key=lambda x: x[1].latency_ms)[0]

        # LOCAL_FIRST and HIGHEST_QUAL — try in preference order, pick healthiest
        for pid in candidates:
            h = healths.get(pid)
            if h and h.is_healthy():
                return pid
        return None

    @classmethod
    def default(cls) -> "RoutingPolicy":
        """
        Default production policy:
            - IR generation   → local first (Ollama), fallback to OpenRouter (Gemini Flash)
            - Beat expansion  → local first, fallback to OpenRouter
            - Style rewrite   → local first, fallback to OpenRouter
            - Manifest eval   → cloud only (OpenRouter with Claude/Gemini Pro)
            - Prompt quality  → cloud only
            - Coherence check → cloud only
        """
        return cls(rules={
            TaskType.IR_GENERATION: TaskRoutingRule(
                task_type=TaskType.IR_GENERATION,
                mode=RoutingMode.LOCAL_FIRST,
                preferred_providers=("ollama_local", "openrouter"),
                fallback_providers=(),
                require_structured_output=True,
            ),
            TaskType.BEAT_EXPANSION: TaskRoutingRule(
                task_type=TaskType.BEAT_EXPANSION,
                mode=RoutingMode.LOCAL_FIRST,
                preferred_providers=("ollama_local", "openrouter"),
                fallback_providers=(),
                require_structured_output=False,
            ),
            TaskType.STYLE_REWRITE: TaskRoutingRule(
                task_type=TaskType.STYLE_REWRITE,
                mode=RoutingMode.LOCAL_FIRST,
                preferred_providers=("ollama_local", "openrouter"),
                fallback_providers=(),
                require_structured_output=False,
            ),
            TaskType.MULTI_SHOT_LAYOUT: TaskRoutingRule(
                task_type=TaskType.MULTI_SHOT_LAYOUT,
                mode=RoutingMode.LOCAL_FIRST,
                preferred_providers=("ollama_local", "openrouter"),
                fallback_providers=(),
                require_structured_output=True,
                min_quality_tier=2,
            ),
            TaskType.MANIFEST_EVAL: TaskRoutingRule(
                task_type=TaskType.MANIFEST_EVAL,
                mode=RoutingMode.CLOUD_ONLY,
                preferred_providers=("openrouter",),
                fallback_providers=(),
                require_structured_output=True,
                min_quality_tier=3,
            ),
            TaskType.PROMPT_QUALITY: TaskRoutingRule(
                task_type=TaskType.PROMPT_QUALITY,
                mode=RoutingMode.CLOUD_ONLY,
                preferred_providers=("openrouter",),
                fallback_providers=(),
                require_structured_output=True,
                min_quality_tier=3,
            ),
            TaskType.COHERENCE_CHECK: TaskRoutingRule(
                task_type=TaskType.COHERENCE_CHECK,
                mode=RoutingMode.CLOUD_ONLY,
                preferred_providers=("openrouter",),
                fallback_providers=(),
                require_structured_output=True,
                min_quality_tier=3,
            ),
        })

    @classmethod
    def ci_deterministic(cls) -> "RoutingPolicy":
        """
        CI policy: always selects mock providers deterministically. No network calls.
        """
        return cls(rules={
            task: TaskRoutingRule(
                task_type=task,
                mode=RoutingMode.DETERMINISTIC,
                preferred_providers=("mock_generation",) if "eval" not in task.value
                                    else ("mock_evaluation",),
            )
            for task in TaskType
        })


# ---------------------------------------------------------------------------
# GenerationProvider Protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class GenerationProvider(Protocol):
    """
    Protocol satisfied by all generation model providers.

    Implementations:
        OllamaProvider         — local Gemma 4 / other Ollama models
        OpenRouterProvider     — cloud models via OpenRouter (Gemini Flash, GPT-4o-mini, etc.)
        GeminiProvider         — direct Gemini API (alternative to OpenRouter)
        MockGenerationProvider — deterministic test double, no HTTP
    """

    provider_id: str
    """Unique identifier for this provider, e.g. 'ollama_local'."""

    async def generate(
        self,
        prompt: str,
        output_schema: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generate a structured response from a prompt.

        Args:
            prompt:        The instruction prompt (system + user combined or separate).
            output_schema: Optional JSON schema the response must conform to.
            context:       Provider-specific context (model_override, temperature, etc.)

        Returns:
            A dict containing at minimum {"content": str | dict}.
            If output_schema is provided, content must be a dict conforming to the schema.

        Raises:
            ProviderError: On network failure, schema violation, or quota exhaustion.
        """
        ...

    async def health_check(self) -> ProviderHealth:
        """
        Probe the provider and return a current health snapshot.
        Must not raise — return ProviderHealth(available=False) on any error.
        """
        ...


# ---------------------------------------------------------------------------
# EvaluationProvider Protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class EvaluationProvider(Protocol):
    """
    Protocol satisfied by all evaluation model providers.

    Evaluation providers reason about quality — they receive a compiled manifest
    and its rendered targets, then return structured scoring.

    Implementations:
        CloudEvaluationProvider  — Claude Sonnet / Gemini Pro via OpenRouter
        HeuristicEvaluationProvider — rule-based, no LLM (always available)
        MockEvaluationProvider   — deterministic test double
    """

    provider_id: str

    async def evaluate(
        self,
        manifest: SceneManifest,
        compiled_targets: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> EvaluationMetrics:
        """
        Score a compiled manifest against its rendered targets.

        Args:
            manifest:         The canonical SceneManifest.
            compiled_targets: dict of backend_id → prompt packet.
            context:          Optional context (project, constraints, rubric).

        Returns:
            EvaluationMetrics with heuristic_score + optional measured_score.

        Raises:
            ProviderError: On network failure or quota exhaustion.
        """
        ...

    async def health_check(self) -> ProviderHealth:
        """Return current health snapshot without raising."""
        ...


# ---------------------------------------------------------------------------
# Provider errors
# ---------------------------------------------------------------------------

class ProviderError(Exception):
    """Raised by a provider on network failure, quota, or schema violation."""

    def __init__(
        self,
        message: str,
        provider_id: str = "",
        retryable: bool = True,
        status_code: int = 0,
    ):
        super().__init__(message)
        self.provider_id = provider_id
        self.retryable = retryable
        # HTTP status code when the error originated from an HTTP response (0 = unknown)
        self.status_code = status_code


class NoProviderAvailableError(Exception):
    """Raised by a router when no provider satisfies the routing policy."""

    def __init__(self, task_type: TaskType, tried: list[str]):
        super().__init__(
            f"No provider available for task '{task_type.value}'. Tried: {tried}"
        )
        self.task_type = task_type
        self.tried = tried


# ---------------------------------------------------------------------------
# Mock providers — deterministic test doubles, no HTTP
# ---------------------------------------------------------------------------

class MockGenerationProvider:
    """
    Deterministic generation provider that returns a fixed structured response.
    Satisfies GenerationProvider Protocol. Used in CI and unit tests.
    """
    provider_id = "mock_generation"

    def __init__(self, response_override: dict[str, Any] | None = None):
        self._response = response_override or {
            "content": {
                "version": "1.0",
                "purpose": "Mock generated scene",
                "scene": {"id": "mock_scene_0", "location": "Mock location"},
                "timeline": [
                    {"id": "beat_01", "order": 0, "description": "Mock beat",
                     "duration_seconds": 3.0}
                ],
            }
        }

    async def generate(
        self,
        prompt: str,
        output_schema: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return dict(self._response)

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            provider_id=self.provider_id,
            available=True,
            latency_ms=0.1,
            cost_per_1k_tokens=0.0,
            error_rate=0.0,
        )


class MockEvaluationProvider:
    """
    Deterministic evaluation provider that returns fixed metrics.
    Satisfies EvaluationProvider Protocol. Used in CI and unit tests.
    """
    provider_id = "mock_evaluation"

    def __init__(self, metrics_override: EvaluationMetrics | None = None):
        self._metrics = metrics_override or EvaluationMetrics(
            heuristic_score=0.85,
            measured_score=0.80,
            coherence=0.88,
            completeness=0.90,
            cinematic_quality=0.82,
            warnings_count=1,
            errors_count=0,
            notes=("mock evaluation",),
        )

    async def evaluate(
        self,
        manifest: SceneManifest,
        compiled_targets: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> EvaluationMetrics:
        return self._metrics

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            provider_id=self.provider_id,
            available=True,
            latency_ms=0.1,
            cost_per_1k_tokens=0.0,
            error_rate=0.0,
        )


class HeuristicEvaluationProvider:
    """
    Rule-based evaluation provider — no LLM, always available, always fast.
    Produces only heuristic_score; measured_score is left as None.

    Scoring heuristic (extensible):
        + 0.20 each: purpose set, all beats have descriptions, no schema errors
        + 0.10 each: camera packages set, lighting packages set
        + 0.10: all beats have valid shot sizes
        - 0.10 per blocking error, - 0.05 per warning
    """
    provider_id = "heuristic_evaluation"

    async def evaluate(
        self,
        manifest: SceneManifest,
        compiled_targets: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> EvaluationMetrics:
        score = 0.0
        warnings: list[str] = []

        # +0.20: purpose defined
        if manifest.purpose:
            score += 0.20
        else:
            warnings.append("purpose is empty")

        # +0.20: all beats have descriptions
        empty_desc = [b.id for b in manifest.timeline if not b.description]
        if not empty_desc:
            score += 0.20
        else:
            warnings.append(f"beats without descriptions: {empty_desc}")

        # +0.20: schema is valid
        schema_errors = manifest.validate_schema()
        if not schema_errors:
            score += 0.20
        else:
            score -= 0.10 * min(len(schema_errors), 2)
            warnings.extend(schema_errors[:2])

        # +0.10: camera package set
        if manifest.camera_package:
            score += 0.10

        # +0.10: lighting package set
        if manifest.lighting_package:
            score += 0.10

        # +0.10: all beats have recognised shot sizes
        valid_shots = {"ECU", "CU", "MS", "WS", "EWS"}
        bad_shots = [b.id for b in manifest.timeline if b.camera.shot_size not in valid_shots]
        if not bad_shots:
            score += 0.10
        else:
            warnings.append(f"unrecognised shot sizes in beats: {bad_shots}")

        # semantic warnings
        semantic_errors = manifest.validate_semantic()
        score -= 0.05 * min(len(semantic_errors), 4)
        warnings.extend(semantic_errors[:4])

        score = max(0.0, min(1.0, score))

        return EvaluationMetrics(
            heuristic_score=round(score, 3),
            measured_score=None,
            coherence=score,
            completeness=0.8 if manifest.timeline else 0.0,
            cinematic_quality=score * 0.9,
            warnings_count=len(warnings),
            errors_count=len(schema_errors),
            notes=tuple(warnings[:6]),
        )

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            provider_id=self.provider_id,
            available=True,
            latency_ms=0.0,
            cost_per_1k_tokens=0.0,
            error_rate=0.0,
        )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _self_test() -> None:
    import asyncio

    print("=== router_protocol.py self-test ===\n")

    # 1. Protocol structural checks
    mock_gen = MockGenerationProvider()
    mock_eval = MockEvaluationProvider()
    heuristic = HeuristicEvaluationProvider()

    assert isinstance(mock_gen, GenerationProvider), "MockGenerationProvider must satisfy GenerationProvider"
    print("✓ MockGenerationProvider satisfies GenerationProvider Protocol")

    assert isinstance(mock_eval, EvaluationProvider), "MockEvaluationProvider must satisfy EvaluationProvider"
    print("✓ MockEvaluationProvider satisfies EvaluationProvider Protocol")

    assert isinstance(heuristic, EvaluationProvider), "HeuristicEvaluationProvider must satisfy EvaluationProvider"
    print("✓ HeuristicEvaluationProvider satisfies EvaluationProvider Protocol")

    # 2. MockGenerationProvider
    async def _run_gen():
        result = await mock_gen.generate("describe a scene")
        assert "content" in result
        print("✓ MockGenerationProvider.generate returns structured content")

        health = await mock_gen.health_check()
        assert health.available is True
        assert health.is_healthy()
        print("✓ MockGenerationProvider.health_check returns healthy")

    asyncio.run(_run_gen())

    # 3. MockEvaluationProvider
    from parser_protocol import MockParser
    async def _run_eval():
        manifest = await MockParser().parse("test")
        targets = {"flow_omni": {"prompt": "test prompt"}}
        metrics = await mock_eval.evaluate(manifest, targets)
        assert metrics.heuristic_score == 0.85
        assert metrics.is_passing()
        print("✓ MockEvaluationProvider.evaluate returns configured metrics")

    asyncio.run(_run_eval())

    # 4. HeuristicEvaluationProvider
    async def _run_heuristic():
        from scene_manifest import SceneManifest, SceneBlock, BeatBlock, CameraInstruction
        # Minimal valid manifest
        manifest = SceneManifest(
            purpose="Test scene",
            scene=SceneBlock(id="s0", location="Test room"),
            timeline=(BeatBlock(id="b0", order=0, description="Test beat", duration_seconds=2.0,
                               camera=CameraInstruction(shot_size="MS")),),
        )
        metrics = await heuristic.evaluate(manifest, {})
        assert 0.0 <= metrics.heuristic_score <= 1.0
        print(f"✓ HeuristicEvaluationProvider score: {metrics.heuristic_score:.3f}")
        assert metrics.measured_score is None, "Heuristic provider must not set measured_score"
        print("✓ HeuristicEvaluationProvider leaves measured_score=None")

    asyncio.run(_run_heuristic())

    # 5. RoutingPolicy — default
    policy = RoutingPolicy.default()
    healths = {
        "ollama_local":            ProviderHealth("ollama_local",            available=True,  latency_ms=50,  cost_per_1k_tokens=0.0),
        "openrouter_gemini_flash": ProviderHealth("openrouter_gemini_flash", available=True,  latency_ms=300, cost_per_1k_tokens=0.00035),
        "openrouter_claude_sonnet":ProviderHealth("openrouter_claude_sonnet",available=True,  latency_ms=800, cost_per_1k_tokens=0.003),
        "openrouter_gpt4o":        ProviderHealth("openrouter_gpt4o",        available=False, latency_ms=500, cost_per_1k_tokens=0.005),
    }

    selected = policy.select_provider(TaskType.IR_GENERATION, healths)
    assert selected == "ollama_local", f"Expected ollama_local, got {selected}"
    print("✓ RoutingPolicy selects local provider for IR_GENERATION (local_first)")

    selected = policy.select_provider(TaskType.MANIFEST_EVAL, healths)
    assert selected == "openrouter_claude_sonnet", f"Expected claude_sonnet, got {selected}"
    print("✓ RoutingPolicy selects cloud provider for MANIFEST_EVAL (cloud_only)")

    # 6. RoutingPolicy — local unavailable → falls back to cloud
    healths_no_local = dict(healths)
    healths_no_local["ollama_local"] = ProviderHealth("ollama_local", available=False)
    selected = policy.select_provider(TaskType.IR_GENERATION, healths_no_local)
    assert selected == "openrouter_gemini_flash", f"Expected gemini_flash fallback, got {selected}"
    print("✓ RoutingPolicy falls back to cloud when Ollama unavailable")

    # 7. CI deterministic policy
    ci_policy = RoutingPolicy.ci_deterministic()
    selected_ci = ci_policy.select_provider(
        TaskType.IR_GENERATION,
        {}  # empty healths — deterministic ignores health
    )
    assert selected_ci == "mock_generation"
    print("✓ CI deterministic policy selects mock provider regardless of health")

    # 8. ProviderHealth scoring
    h_local = ProviderHealth("ollama_local", available=True, latency_ms=50, cost_per_1k_tokens=0.0, error_rate=0.0)
    h_cloud = ProviderHealth("cloud",        available=True, latency_ms=800, cost_per_1k_tokens=0.005, error_rate=0.1)
    h_down  = ProviderHealth("down",         available=False)
    assert h_local.score() > h_cloud.score() > h_down.score()
    print("✓ ProviderHealth scoring: local > cloud > down")

    print("\n=== All tests passed ✓ ===")


if __name__ == "__main__":
    _self_test()

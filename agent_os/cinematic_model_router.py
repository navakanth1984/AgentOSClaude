"""
cinematic_model_router.py — Cinematic OS: Concrete Providers + Hybrid Routers

Implements the GenerationProvider and EvaluationProvider protocols with real
HTTP adapters, then assembles them into two hybrid routers that own all
routing orchestration.

Hierarchy:
    HybridGenerationRouter          ← orchestration only; no HTTP
        OllamaProvider              ← local Gemma 4 / any Ollama model
        OpenRouterProvider          ← cloud models via OpenRouter
        GeminiProvider              ← direct Gemini API (optional alternative)

    HybridEvaluationRouter          ← policy-driven; no HTTP
        HeuristicEvaluationProvider ← rule-based, always available (from router_protocol)
        CloudEvaluationProvider     ← OpenRouter (Claude Sonnet / Gemini Pro)

Routers depend only on the protocols defined in router_protocol.py.
HTTP details are entirely isolated inside each provider class.

Configuration is read from environment variables (or a passed config dict).
No provider reads environment variables at module load time.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

from scene_manifest import EvaluationMetrics, SceneManifest
from parser_protocol import ParseResult
from router_protocol import (
    EvaluationProvider,
    GenerationProvider,
    HeuristicEvaluationProvider,
    MockEvaluationProvider,
    MockGenerationProvider,
    NoProviderAvailableError,
    ProviderError,
    ProviderHealth,
    RoutingPolicy,
    TaskType,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OllamaConfig:
    base_url: str = "http://localhost:11434"
    model: str = "gemma2:27b"           # pulled model name; override per task
    timeout_s: float = 60.0
    temperature: float = 0.3
    format: str = "json"                # Ollama supports native JSON mode


@dataclass(frozen=True)
class OpenRouterConfig:
    api_key: str = ""
    base_url: str = "https://openrouter.ai/api/v1"
    timeout_s: float = 90.0
    site_url: str = ""
    site_name: str = "CinematicOS"
    # Primary model — uses OpenRouter auto-routing alias so it never goes stale
    generation_model: str = os.getenv(
        "OPENROUTER_PRIMARY_MODEL",
        "~google/gemini-flash-latest",
    )
    # Dedicated model for NL parsing (can be tuned independently)
    parser_model: str = os.getenv(
        "OPENROUTER_PARSER_MODEL",
        "~google/gemini-flash-latest",
    )
    # Model used for cloud evaluation scoring
    evaluation_model: str = os.getenv(
        "OPENROUTER_EVAL_MODEL",
        "anthropic/claude-sonnet-4",
    )
    # Ordered fallback chain tried on HTTP 404/unavailable from the primary
    fallback_models: list[str] = field(default_factory=lambda: [
        m.strip()
        for m in os.getenv(
            "OPENROUTER_FALLBACK_MODELS",
            "google/gemini-2.5-flash,anthropic/claude-sonnet-4",
        ).split(",")
        if m.strip()
    ])

    @property
    def models(self) -> list[str]:
        """Full routing order: primary followed by fallbacks."""
        return [self.generation_model] + self.fallback_models


@dataclass(frozen=True)
class GeminiConfig:
    api_key: str = ""
    model: str = "gemini-2.0-flash"
    timeout_s: float = 60.0
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"


# ---------------------------------------------------------------------------
# OllamaProvider — local model via Ollama REST API
# ---------------------------------------------------------------------------

class OllamaProvider:
    """
    Calls a locally running Ollama instance.

    Health check: GET /api/tags to verify the server is running and the
    configured model is available. Returns ProviderHealth(available=False)
    if Ollama is not reachable — the hybrid router will fall back to cloud.

    No API key required.
    """

    provider_id = "ollama_local"

    def __init__(self, config: OllamaConfig | None = None):
        self.config = config or OllamaConfig(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "gemma2:27b"),
        )
        self._last_health: ProviderHealth | None = None
        self._health_cache_ttl_s: float = 30.0

    async def generate(
        self,
        prompt: str,
        output_schema: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call Ollama /api/generate with JSON mode enabled."""
        import urllib.request
        import urllib.error

        model = (context or {}).get("model_override", self.config.model)

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": (context or {}).get("temperature", self.config.temperature),
                "num_predict": (context or {}).get("max_tokens", 2048),
            },
        }
        if output_schema:
            # Embed schema hint in the prompt (Ollama doesn't support structured outputs natively yet)
            schema_str = json.dumps(output_schema, indent=2)
            payload["prompt"] = (
                f"Respond with valid JSON only, conforming to this schema:\n{schema_str}\n\n"
                + prompt
            )

        url = f"{self.config.base_url}/api/generate"
        try:
            req_data = json.dumps(payload).encode()
            req = urllib.request.Request(url, data=req_data, method="POST",
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=self.config.timeout_s) as resp:
                body = json.loads(resp.read())
            raw_response = body.get("response", "")
            # Ollama returns raw text; parse JSON from it
            try:
                content = json.loads(raw_response)
            except json.JSONDecodeError:
                content = raw_response
            return {"content": content, "provider": self.provider_id, "model": model}
        except urllib.error.URLError as e:
            raise ProviderError(f"Ollama unreachable: {e}", self.provider_id, retryable=True) from e
        except Exception as e:
            raise ProviderError(f"Ollama error: {e}", self.provider_id, retryable=False) from e

    async def health_check(self) -> ProviderHealth:
        """Probe Ollama /api/tags; cache result for health_cache_ttl_s."""
        import urllib.request
        import urllib.error

        # Return cached health if fresh
        if (
            self._last_health is not None
            and time.time() - self._last_health.last_checked < self._health_cache_ttl_s
        ):
            return self._last_health

        start = time.time()
        try:
            url = f"{self.config.base_url}/api/tags"
            with urllib.request.urlopen(url, timeout=3.0) as resp:
                body = json.loads(resp.read())
            latency_ms = (time.time() - start) * 1000
            # Check if our model is available
            available_models = [m.get("name", "") for m in body.get("models", [])]
            model_available = any(
                self.config.model in m or m.startswith(self.config.model.split(":")[0])
                for m in available_models
            )
            health = ProviderHealth(
                provider_id=self.provider_id,
                available=model_available,
                latency_ms=round(latency_ms, 1),
                cost_per_1k_tokens=0.0,
                error_rate=0.0,
                last_checked=time.time(),
            )
        except Exception as e:
            logger.debug(f"Ollama health check failed: {e}")
            health = ProviderHealth(
                provider_id=self.provider_id,
                available=False,
                last_checked=time.time(),
            )
        self._last_health = health
        return health


# ---------------------------------------------------------------------------
# GeminiProvider — direct calls to Google Gemini API
# ---------------------------------------------------------------------------

class GeminiProvider:
    """
    Calls Google's direct Gemini API via AI Studio.
    One provider, many models — model is selected per-call via context["model"].
    """

    provider_id = "gemini_direct"

    def __init__(self, config: GeminiConfig | None = None, default_model: str = ""):
        self.config = config or GeminiConfig(
            api_key=os.getenv("GEMINI_API_KEY", ""),
        )
        self._default_model = default_model or self.config.model
        self._last_health: ProviderHealth | None = None
        self._health_cache_ttl_s: float = 30.0

    @property
    def _api_key(self) -> str:
        if not self.config.api_key:
            raise ProviderError(
                "GEMINI_API_KEY not set. Provide it in .env or environment.",
                self.provider_id,
                retryable=False,
            )
        return self.config.api_key

    async def generate(
        self,
        prompt: str,
        output_schema: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call Gemini API directly using urllib."""
        import urllib.request
        import urllib.error

        ctx = context or {}
        model = ctx.get("model", self._default_model)
        temperature = ctx.get("temperature", 0.3)
        max_tokens = ctx.get("max_tokens", 2048)
        system_prompt = ctx.get("system_prompt", "You are a cinematic scene IR compiler.")

        # API endpoint formatting (Google API structure)
        # v1beta /models/gemini-2.0-flash:generateContent
        url = f"{self.config.base_url}/models/{model}:generateContent?key={self._api_key}"

        contents = [{"parts": [{"text": prompt}]}]
        system_instruction = {"parts": [{"text": system_prompt}]}

        payload: dict[str, Any] = {
            "contents": contents,
            "systemInstruction": system_instruction,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        # Handle structured outputs
        if output_schema:
            payload["generationConfig"]["responseMimeType"] = "application/json"
            payload["generationConfig"]["responseSchema"] = output_schema

        headers = {
            "Content-Type": "application/json",
        }

        try:
            req_data = json.dumps(payload).encode()
            req = urllib.request.Request(url, data=req_data, method="POST", headers=headers)
            with urllib.request.urlopen(req, timeout=self.config.timeout_s) as resp:
                body = json.loads(resp.read())

            candidates = body.get("candidates", [])
            if not candidates:
                raise ProviderError("Gemini returned empty candidates list", self.provider_id, retryable=False)

            raw_content = candidates[0]["content"]["parts"][0]["text"]
            try:
                content = json.loads(raw_content) if isinstance(raw_content, str) else raw_content
            except json.JSONDecodeError:
                content = raw_content

            usage = body.get("usageMetadata", {})
            # Map usage keys to match standard outputs
            standard_usage = {
                "prompt_tokens": usage.get("promptTokenCount", 0),
                "completion_tokens": usage.get("candidatesTokenCount", 0),
            }

            logger.info(
                "Gemini Direct generation success",
                extra={
                    "model": model,
                    "provider": self.provider_id,
                    "prompt_tokens": standard_usage["prompt_tokens"],
                    "completion_tokens": standard_usage["completion_tokens"],
                    "timestamp": time.time(),
                },
            )
            return {
                "content": content,
                "provider": self.provider_id,
                "model": model,
                "usage": standard_usage,
            }
        except urllib.error.HTTPError as e:
            body_text = e.read().decode(errors="ignore") if e.fp else ""
            retryable = e.code in (429, 500, 502, 503, 504)
            raise ProviderError(
                f"Gemini Direct HTTP {e.code}: {body_text[:200]}",
                self.provider_id,
                retryable=retryable,
                status_code=e.code,
            ) from e
        except Exception as e:
            raise ProviderError(f"Gemini Direct error: {e}", self.provider_id, retryable=True) from e

    async def health_check(self) -> ProviderHealth:
        """Cache-aware check. True if API key is populated."""
        if (
            self._last_health is not None
            and time.time() - self._last_health.last_checked < self._health_cache_ttl_s
        ):
            return self._last_health

        available = bool(self.config.api_key)
        health = ProviderHealth(
            provider_id=self.provider_id,
            available=available,
            latency_ms=0.0,
            cost_per_1k_tokens=0.00015,
            error_rate=0.0,
            last_checked=time.time(),
        )
        self._last_health = health
        return health


# ---------------------------------------------------------------------------
# OpenRouterProvider — cloud models via OpenRouter
# ---------------------------------------------------------------------------

class OpenRouterProvider:
    """
    Calls OpenRouter's OpenAI-compatible API.
    One provider, many models — model is selected per-call via context["model"].

    Supports structured outputs via response_format=json_schema when the model
    supports it (Gemini Flash, GPT-4o, Claude 3.5+).
    """

    provider_id = "openrouter"

    def __init__(self, config: OpenRouterConfig | None = None, default_model: str = ""):
        self.config = config or OpenRouterConfig(
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
        )
        self._default_model = default_model or self.config.generation_model
        self._last_health: ProviderHealth | None = None
        self._health_cache_ttl_s: float = 30.0

    @property
    def _api_key(self) -> str:
        if not self.config.api_key:
            raise ProviderError(
                "OPENROUTER_API_KEY not set. Provide it in .env or environment.",
                self.provider_id,
                retryable=False,
            )
        return self.config.api_key

    async def _generate_with_model(
        self,
        model: str,
        prompt: str,
        output_schema: dict[str, Any] | None,
        ctx: dict[str, Any],
    ) -> dict[str, Any]:
        """Single attempt against one specific model. Raises ProviderError on failure."""
        import urllib.request
        import urllib.error

        temperature = ctx.get("temperature", 0.3)
        max_tokens = ctx.get("max_tokens", 2048)
        system_prompt = ctx.get("system_prompt", "You are a cinematic scene IR compiler.")

        payload: dict[str, Any] = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": prompt},
            ],
        }

        # Structured output via json_schema response_format
        if output_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "scene_manifest",
                    "strict": True,
                    "schema": output_schema,
                },
            }
        else:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": self.config.site_url or "https://cinematicos.local",
            "X-Title": self.config.site_name,
        }

        url = f"{self.config.base_url}/chat/completions"
        try:
            req_data = json.dumps(payload).encode()
            req = urllib.request.Request(url, data=req_data, method="POST", headers=headers)
            with urllib.request.urlopen(req, timeout=self.config.timeout_s) as resp:
                body = json.loads(resp.read())

            raw_content = body["choices"][0]["message"]["content"]
            try:
                content = json.loads(raw_content) if isinstance(raw_content, str) else raw_content
            except json.JSONDecodeError:
                content = raw_content

            usage = body.get("usage", {})
            logger.info(
                "OpenRouter generation success",
                extra={
                    "model": model,
                    "provider": self.provider_id,
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "timestamp": time.time(),
                },
            )
            return {
                "content": content,
                "provider": self.provider_id,
                "model": model,
                "usage": usage,
            }
        except urllib.error.HTTPError as e:
            body_text = e.read().decode(errors="ignore") if e.fp else ""
            retryable = e.code in (429, 500, 502, 503, 504)
            if e.code == 404:
                logger.warning(
                    "OpenRouter model unavailable (404) — will try fallback",
                    extra={"model": model, "response_snippet": body_text[:200], "timestamp": time.time()},
                )
            raise ProviderError(
                f"OpenRouter HTTP {e.code}: {body_text[:200]}",
                self.provider_id,
                retryable=retryable,
                status_code=e.code,
            ) from e
        except Exception as e:
            raise ProviderError(f"OpenRouter error: {e}", self.provider_id, retryable=True) from e

    async def generate(
        self,
        prompt: str,
        output_schema: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call OpenRouter with automatic fallback chain on 404/unavailable."""
        ctx = context or {}
        # If the caller explicitly specifies a model, honour it (no fallback loop).
        if "model" in ctx:
            return await self._generate_with_model(ctx["model"], prompt, output_schema, ctx)

        # Try primary model then each fallback in order.
        models_to_try = [self._default_model] + [
            m for m in self.config.fallback_models if m != self._default_model
        ]
        last_error: ProviderError | None = None
        for model in models_to_try:
            try:
                return await self._generate_with_model(model, prompt, output_schema, ctx)
            except ProviderError as exc:
                last_error = exc
                # Continue fallback only on 404 (model gone) or transient 5xx.
                # Non-recoverable errors (401 Unauthorized, 400 Bad Request, etc.) surface immediately.
                if exc.status_code == 404 or exc.status_code in (500, 502, 503, 504):
                    logger.debug(
                        "OpenRouter fallback triggered",
                        extra={
                            "failed_model": model,
                            "status_code": exc.status_code,
                            "reason": str(exc)[:120],
                            "timestamp": time.time(),
                        },
                    )
                    continue
                raise  # surface non-recoverable errors immediately

        raise last_error or ProviderError(
            "All OpenRouter models failed", self.provider_id, retryable=False
        )

    async def health_check(self) -> ProviderHealth:
        """Cache-aware health check. True if API key is set."""
        if (
            self._last_health is not None
            and time.time() - self._last_health.last_checked < self._health_cache_ttl_s
        ):
            return self._last_health

        available = bool(self.config.api_key)
        health = ProviderHealth(
            provider_id=self.provider_id,
            available=available,
            latency_ms=0.0,
            cost_per_1k_tokens=0.00035,
            error_rate=0.0,
            last_checked=time.time(),
        )
        self._last_health = health
        return health


# ---------------------------------------------------------------------------
# CloudEvaluationProvider — evaluation via OpenRouter (Claude / Gemini Pro)
# ---------------------------------------------------------------------------

class CloudEvaluationProvider:
    """
    Uses OpenRouterProvider to perform LLM-based evaluation scoring.

    Evaluation prompt: structured rubric → JSON with coherence, completeness,
    cinematic_quality, notes fields. Claude Sonnet / Gemini 2.5 Pro preferred.
    """

    provider_id = "cloud_evaluation"

    EVAL_SYSTEM_PROMPT = """You are an expert cinematic quality evaluator.
Given a compiled scene manifest and rendered backend prompts, score the following dimensions:
- coherence (0..1): Internal logical and visual consistency across beats
- completeness (0..1): How fully the manifest captures the scene's intent
- cinematic_quality (0..1): Shot design, lighting, character staging quality

Respond with ONLY valid JSON: {"coherence": 0.0, "completeness": 0.0, "cinematic_quality": 0.0, "notes": []}"""

    def __init__(
        self,
        openrouter: OpenRouterProvider | None = None,
        model_override: str = "",
    ):
        self._router = openrouter or OpenRouterProvider()
        self._model = model_override or self._router.config.evaluation_model

    async def evaluate(
        self,
        manifest: SceneManifest,
        compiled_targets: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> EvaluationMetrics:
        manifest_summary = {
            "purpose": manifest.purpose,
            "beat_count": len(manifest.timeline),
            "beats": [{"id": b.id, "description": b.description[:80]} for b in manifest.timeline],
        }
        targets_summary = {
            k: (v.get("prompt", "")[:200] if isinstance(v, dict) else str(v)[:200])
            for k, v in list(compiled_targets.items())[:3]  # cap at 3 backends
        }

        prompt = (
            f"MANIFEST:\n{json.dumps(manifest_summary, indent=2)}\n\n"
            f"RENDERED TARGETS (excerpt):\n{json.dumps(targets_summary, indent=2)}\n\n"
            f"Score this compilation."
        )

        try:
            result = await self._router.generate(
                prompt=prompt,
                context={
                    "model": self._model,
                    "temperature": 0.1,
                    "max_tokens": 512,
                    "system_prompt": self.EVAL_SYSTEM_PROMPT,
                },
            )
            scores = result.get("content", {})
            if isinstance(scores, str):
                scores = json.loads(scores)
            return EvaluationMetrics(
                heuristic_score=0.0,   # not set by cloud evaluator
                measured_score=round(
                    (scores.get("coherence", 0) +
                     scores.get("completeness", 0) +
                     scores.get("cinematic_quality", 0)) / 3.0, 3
                ),
                coherence=scores.get("coherence", 0.0),
                completeness=scores.get("completeness", 0.0),
                cinematic_quality=scores.get("cinematic_quality", 0.0),
                warnings_count=0,
                errors_count=0,
                notes=tuple(scores.get("notes", [])),
            )
        except Exception as e:
            raise ProviderError(f"Cloud evaluation failed: {e}", self.provider_id, retryable=True) from e

    async def health_check(self) -> ProviderHealth:
        h = await self._router.health_check()
        return ProviderHealth(
            provider_id=self.provider_id,
            available=h.available,
            latency_ms=h.latency_ms,
            cost_per_1k_tokens=0.003,   # Claude Sonnet approximate
            error_rate=h.error_rate,
            last_checked=h.last_checked,
        )


# ---------------------------------------------------------------------------
# HybridGenerationRouter — orchestration; no HTTP
# ---------------------------------------------------------------------------

class HybridGenerationRouter:
    """
    Orchestrates generation requests across multiple providers using a RoutingPolicy.

    The router:
    1. Calls health_check() on all registered providers
    2. Delegates to RoutingPolicy.select_provider() to pick the winner
    3. Calls generate() on the selected provider
    4. On ProviderError, marks provider as degraded and tries the next candidate

    Retry: if the selected provider fails, the router tries the next healthy
    provider from the policy's preference list before raising NoProviderAvailableError.
    """

    def __init__(
        self,
        providers: list[GenerationProvider],
        policy: RoutingPolicy | None = None,
    ):
        self._providers: dict[str, GenerationProvider] = {p.provider_id: p for p in providers}
        self._policy = policy or RoutingPolicy.default()
        self._degraded: dict[str, float] = {}   # provider_id → timestamp of last failure

    async def generate(
        self,
        task_type: TaskType,
        prompt: str,
        output_schema: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Route a generation request to the best available provider.

        Args:
            task_type:     Semantic task category (determines routing rule).
            prompt:        The instruction prompt.
            output_schema: Optional JSON schema for structured output.
            context:       Passed through to the provider.

        Returns:
            Provider response dict with at minimum {"content": ...}.

        Raises:
            NoProviderAvailableError: If no provider is healthy for this task.
        """
        healths = await self._all_health_checks()
        rule = self._policy.get_rule(task_type)
        candidates = (
            list(rule.preferred_providers) + list(rule.fallback_providers)
            if rule else list(self._providers.keys())
        )

        tried: list[str] = []
        for provider_id in candidates:
            if provider_id not in self._providers:
                continue
            health = healths.get(provider_id)
            if not health or not health.is_healthy():
                logger.debug(f"Skipping {provider_id}: unhealthy")
                continue
            provider = self._providers[provider_id]
            try:
                result = await provider.generate(prompt, output_schema, context)
                logger.debug(f"Generated via {provider_id}")
                return result
            except ProviderError as e:
                logger.warning(f"Provider {provider_id} failed: {e}")
                tried.append(provider_id)
                self._degraded[provider_id] = time.time()
                if not e.retryable:
                    raise
                continue

        raise NoProviderAvailableError(task_type, tried)

    async def health_check_all(self) -> dict[str, ProviderHealth]:
        """Return health snapshots for all registered providers."""
        return await self._all_health_checks()

    async def _all_health_checks(self) -> dict[str, ProviderHealth]:
        results = await asyncio.gather(
            *[p.health_check() for p in self._providers.values()],
            return_exceptions=True,
        )
        healths: dict[str, ProviderHealth] = {}
        for provider, result in zip(self._providers.values(), results):
            if isinstance(result, ProviderHealth):
                healths[provider.provider_id] = result
            else:
                healths[provider.provider_id] = ProviderHealth(
                    provider_id=provider.provider_id, available=False, last_checked=time.time()
                )
        return healths

    @classmethod
    def from_env(cls, policy: RoutingPolicy | None = None) -> "HybridGenerationRouter":
        """
        Create a production router from environment variables.
        Order is configured dynamically via MODEL_PROVIDER_ORDER.
        """
        order_str = os.getenv("MODEL_PROVIDER_ORDER", "ollama,gemini,openrouter")
        provider_names = [p.strip().lower() for p in order_str.split(",") if p.strip()]

        providers: list[GenerationProvider] = []
        for name in provider_names:
            if name == "ollama":
                providers.append(OllamaProvider())
            elif name == "gemini":
                providers.append(GeminiProvider())
            elif name == "openrouter":
                providers.append(OpenRouterProvider())

        # Zero-cost local fallback option is always present at the end if none match
        if not providers:
            providers = [OllamaProvider(), OpenRouterProvider()]

        return cls(providers=providers, policy=policy)

    @classmethod
    def mock(cls) -> "HybridGenerationRouter":
        """Create a fully mocked router for CI/testing. No network calls."""
        policy = RoutingPolicy.ci_deterministic()
        return cls(providers=[MockGenerationProvider()], policy=policy)


# ---------------------------------------------------------------------------
# HybridEvaluationRouter — policy-driven; no HTTP
# ---------------------------------------------------------------------------

class HybridEvaluationRouter:
    """
    Orchestrates evaluation requests across HeuristicEvaluationProvider
    (always-on, rule-based) and CloudEvaluationProvider (LLM, optional).

    Strategy:
        1. Always run HeuristicEvaluationProvider (no LLM, zero latency, always available).
        2. If cloud is available and the task requires measured_score:
           run CloudEvaluationProvider and merge results.
        3. Return a merged EvaluationMetrics where:
           - heuristic_score comes from heuristic provider
           - measured_score comes from cloud provider (or None if unavailable)
    """

    def __init__(
        self,
        heuristic: EvaluationProvider | None = None,
        cloud: EvaluationProvider | None = None,
        require_cloud: bool = False,
    ):
        self._heuristic = heuristic or HeuristicEvaluationProvider()
        self._cloud = cloud
        self._require_cloud = require_cloud

    async def evaluate(
        self,
        manifest: SceneManifest,
        compiled_targets: dict[str, Any],
        task_type: TaskType = TaskType.MANIFEST_EVAL,
        context: dict[str, Any] | None = None,
    ) -> EvaluationMetrics:
        """
        Run evaluation. Always returns a valid EvaluationMetrics.
        Cloud evaluation is best-effort — degraded gracefully on failure.
        """
        # Step 1: Heuristic evaluation (always runs)
        heuristic_metrics = await self._heuristic.evaluate(manifest, compiled_targets, context)

        # Step 2: Cloud evaluation (optional, best-effort)
        cloud_metrics: EvaluationMetrics | None = None
        if self._cloud is not None:
            try:
                health = await self._cloud.health_check()
                if health.is_healthy():
                    cloud_metrics = await self._cloud.evaluate(manifest, compiled_targets, context)
            except Exception as e:
                logger.warning(f"Cloud evaluation failed, using heuristic only: {e}")
                if self._require_cloud:
                    raise

        # Step 3: Merge
        if cloud_metrics is None:
            return heuristic_metrics

        from dataclasses import replace
        return replace(
            heuristic_metrics,
            measured_score=cloud_metrics.measured_score,
            coherence=cloud_metrics.coherence or heuristic_metrics.coherence,
            completeness=cloud_metrics.completeness or heuristic_metrics.completeness,
            cinematic_quality=cloud_metrics.cinematic_quality or heuristic_metrics.cinematic_quality,
            notes=heuristic_metrics.notes + cloud_metrics.notes,
        )

    async def health_check_all(self) -> dict[str, ProviderHealth]:
        """Return health of all registered evaluation providers."""
        healths: dict[str, ProviderHealth] = {}
        h_health = await self._heuristic.health_check()
        healths[h_health.provider_id] = h_health
        if self._cloud:
            try:
                c_health = await self._cloud.health_check()
                healths[c_health.provider_id] = c_health
            except Exception:
                pass
        return healths

    @classmethod
    def from_env(cls) -> "HybridEvaluationRouter":
        """
        Create production evaluation router.
        Heuristic always active; cloud active only if OPENROUTER_API_KEY is set.
        """
        heuristic = HeuristicEvaluationProvider()
        cloud: EvaluationProvider | None = None
        if os.getenv("OPENROUTER_API_KEY"):
            cloud = CloudEvaluationProvider()
        return cls(heuristic=heuristic, cloud=cloud, require_cloud=False)

    @classmethod
    def mock(cls) -> "HybridEvaluationRouter":
        """Fully mocked evaluation router. No network calls."""
        return cls(
            heuristic=HeuristicEvaluationProvider(),
            cloud=MockEvaluationProvider(),
            require_cloud=False,
        )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _self_test() -> None:
    import asyncio

    print("=== cinematic_model_router.py self-test ===\n")

    # 1. OllamaProvider health check (graceful if not running)
    async def _test_ollama():
        provider = OllamaProvider()
        health = await provider.health_check()
        if health.available:
            print(f"✓ OllamaProvider: available — model '{provider.config.model}' found "
                  f"(latency {health.latency_ms:.0f}ms)")
        else:
            print("✓ OllamaProvider: not running — health_check returned available=False gracefully")

    asyncio.run(_test_ollama())

    # 2. HybridGenerationRouter.mock() — no network
    async def _test_hybrid_gen():
        router = HybridGenerationRouter.mock()
        result = await router.generate(
            task_type=TaskType.IR_GENERATION,
            prompt="Describe a scene where Rain enters an ancient shrine",
        )
        assert "content" in result
        print("✓ HybridGenerationRouter.mock() generates without network")

    asyncio.run(_test_hybrid_gen())

    # 3. HybridGenerationRouter fallback — simulate Ollama down
    async def _test_fallback():
        mock_primary = MockGenerationProvider(response_override=None)
        # Patch health to return unavailable
        original_health = mock_primary.health_check

        async def _unhealthy():
            return ProviderHealth(provider_id="mock_generation", available=False)
        mock_primary.health_check = _unhealthy

        mock_secondary = MockGenerationProvider(
            response_override={"content": {"fallback": True}}
        )
        mock_secondary.provider_id = "mock_fallback"

        from router_protocol import TaskRoutingRule, RoutingMode
        policy = RoutingPolicy(rules={
            TaskType.IR_GENERATION: TaskRoutingRule(
                task_type=TaskType.IR_GENERATION,
                mode=RoutingMode.LOCAL_FIRST,
                preferred_providers=("mock_generation",),
                fallback_providers=("mock_fallback",),
            )
        })
        router = HybridGenerationRouter(providers=[mock_primary, mock_secondary], policy=policy)
        result = await router.generate(TaskType.IR_GENERATION, "test")
        assert result["content"] == {"fallback": True}, f"Expected fallback content, got {result}"
        print("✓ HybridGenerationRouter correctly skips unhealthy provider and uses fallback")

    asyncio.run(_test_fallback())

    # 4. HybridEvaluationRouter.mock() — heuristic + mock cloud, merged
    async def _test_hybrid_eval():
        from parser_protocol import MockParser
        from scene_manifest import BeatBlock, CameraInstruction, SceneBlock

        manifest = SceneManifest(
            purpose="Rain confronts her heritage",
            scene=SceneBlock(id="s1", location="Shrine"),
            timeline=(
                BeatBlock(id="b1", order=0, description="Rain pauses", duration_seconds=3.0,
                          camera=CameraInstruction(shot_size="WS")),
            ),
            camera_package={"style": "anamorphic"},
            lighting_package={"key": "practical"},
        )
        targets = {"flow_omni": {"prompt": "Rain stands at the shrine entrance..."}}

        router = HybridEvaluationRouter.mock()
        metrics = await router.evaluate(manifest, targets)

        assert metrics.heuristic_score > 0.0, "Heuristic score must be positive"
        assert metrics.measured_score is not None, "Mock cloud must provide measured_score"
        assert metrics.is_passing(), f"Expected passing metrics, got score={metrics.heuristic_score}"
        print(f"✓ HybridEvaluationRouter merged: heuristic={metrics.heuristic_score:.3f}, "
              f"measured={metrics.measured_score:.3f}")

    asyncio.run(_test_hybrid_eval())

    # 5. CloudEvaluationProvider graceful degradation — no API key
    async def _test_cloud_degradation():
        # CloudEvaluationProvider with empty API key should return available=False on health_check
        provider = CloudEvaluationProvider(
            openrouter=OpenRouterProvider(config=OpenRouterConfig(api_key=""))
        )
        health = await provider.health_check()
        assert health.available is False
        print("✓ CloudEvaluationProvider returns available=False when no API key configured")

    asyncio.run(_test_cloud_degradation())

    # 6. Protocol satisfaction
    from router_protocol import GenerationProvider, EvaluationProvider
    assert isinstance(OllamaProvider(), GenerationProvider)
    assert isinstance(GeminiProvider(), GenerationProvider)
    assert isinstance(OpenRouterProvider(), GenerationProvider)
    assert isinstance(CloudEvaluationProvider(), EvaluationProvider)
    assert isinstance(HeuristicEvaluationProvider(), EvaluationProvider)
    print("✓ All concrete providers satisfy their respective Protocols")

    print("\n=== All tests passed ✓ ===")


if __name__ == "__main__":
    _self_test()

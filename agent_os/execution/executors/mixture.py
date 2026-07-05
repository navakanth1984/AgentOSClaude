"""
MixtureExecutor — Mixture-of-Agents: fan out one prompt across N models in
parallel, then run it through the selected aggregation strategy.

Internally: FanOut(models) -> Aggregator(fast|standard|verified) -> ExecutionResult.
This is the first "advanced" executor on the execution framework, not a
special-cased feature — Debate/Auto plug into the same ExecutionManager later.
"""

import asyncio
import os
import random
import sys
import time
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from openrouter_client import call_openrouter_async, backend_available

from ..manifest import new_manifest
from ..providers.capabilities import resolve_profile
from ..aggregation import get_aggregator
from .base import ExecutionRequest, StatusCallback

MAX_CONCURRENCY = 3
MAX_RETRIES = 4


def estimate_cost(models: list[str], prompt_tokens: int, completion_tokens: int) -> tuple[int, float]:
    # Cost proxy estimation (chars / 4 = approx tokens)
    # Cost assumption: $0.002 per 1K tokens (blended average for premium models)
    total_tokens = prompt_tokens * len(models) + completion_tokens
    cost_usd = (total_tokens / 1000.0) * 0.002
    return total_tokens, cost_usd


async def _fan_out_one(model: str, system: str, user: str, api_key: str,
                        max_tokens: int, semaphore: asyncio.Semaphore,
                        status_cb: StatusCallback) -> dict:
    async with semaphore:
        t0 = time.time()
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                text = await call_openrouter_async(model, system, user, api_key, max_tokens)
                if status_cb:
                    status_cb("fanout", {"model": model, "status": "done"})
                return {"model": model, "result": text, "error": None,
                        "latency_ms": (time.time() - t0) * 1000}
            except urllib.error.HTTPError as e:
                last_error = str(e)
                if e.code == 429 and attempt < MAX_RETRIES - 1:
                    wait = (2 ** (attempt + 2)) + random.uniform(1, 3)
                    await asyncio.sleep(wait)
                else:
                    break
            except Exception as e:
                last_error = str(e)
                break

    if status_cb:
        status_cb("fanout", {"model": model, "status": "error", "error": last_error})
    return {"model": model, "result": "", "error": last_error, "latency_ms": (time.time() - t0) * 1000}


class MixtureExecutor:
    async def execute(self, request: ExecutionRequest, status_cb: StatusCallback = None) -> dict:
        t_start = time.perf_counter()
        if not backend_available():
            return {"error": "No LLM backend available — set OPENROUTER_API_KEY/GEMINI_API_KEY or run local Ollama."}

        models = request.models or (resolve_profile(request.profile) if request.profile else [])
        if request.max_models > 0:
            models = models[:request.max_models]
            
        if len(models) < 2:
            return {"error": "Mixture mode needs at least 2 models (via 'models' or a 'profile')."}

        api_key = request.api_key or os.environ.get("OPENROUTER_API_KEY", "")
        manifest = new_manifest(
            mode=request.mode,
            requested_mode=request.requested_mode or request.mode, 
            models=models, 
            aggregation=request.aggregation, 
            category=request.category,
            expected_profile=request.expected_profile,
            planned_mode=request.planned_mode,
            executed_mode=request.executed_mode,
            routing_trace=request.routing_trace
        )

        if status_cb:
            status_cb("fanout", {"models": models, "status": "starting"})

        semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
        fanout_results = await asyncio.gather(*[
            _fan_out_one(m, request.system, request.prompt, api_key, request.max_tokens, semaphore, status_cb)
            for m in models
        ])
        manifest.per_model = fanout_results
        manifest.add_event("fanout_complete")

        successful = [r for r in fanout_results if not r["error"] and r["result"]]
        if not successful:
            manifest.latency_ms = (time.perf_counter() - t_start) * 1000
            manifest.add_event("execution_failed")
            manifest.save()
            return {"error": "All models failed in mixture fan-out.", **manifest.to_dict()}
        if len(successful) == 1:
            # Only one model responded — nothing to aggregate, return it directly.
            manifest.final = successful[0]["result"]
            manifest.winner = successful[0]["model"]
            manifest.consensus_score = 1.0
            manifest.latency_ms = (time.perf_counter() - t_start) * 1000
            manifest.add_event("execution_finished", note="single_survivor")
            manifest.save()
            if status_cb:
                status_cb("done", {})
            return manifest.to_dict()

        aggregator = get_aggregator(request.aggregation)
        judge_model = successful[0]["model"]
        agg_result = await aggregator.aggregate(
            request.prompt, successful, api_key, judge_model, status_cb=status_cb
        )

        manifest.final = agg_result["final"]
        manifest.consensus_score = agg_result["confidence"]
        manifest.conflicts = agg_result["conflicts"]
        manifest.winner = judge_model
        manifest.aggregation_trace = agg_result["trace"]
        manifest.verification = agg_result.get("verification")
        manifest.latency_ms = (time.perf_counter() - t_start) * 1000
        
        prompt_chars = len(request.system) + len(request.prompt)
        response_chars = sum(len(r.get("result", "")) for r in fanout_results) + len(manifest.final)
        
        prompt_tokens_est = prompt_chars // 4
        completion_tokens_est = response_chars // 4
        
        est_tokens, est_cost = estimate_cost(models, prompt_tokens_est, completion_tokens_est)
        manifest.estimated_tokens = est_tokens
        manifest.estimated_cost_usd = est_cost
        
        manifest.add_event("execution_finished")
        manifest.save()

        if status_cb:
            status_cb("done", {})

        return manifest.to_dict()

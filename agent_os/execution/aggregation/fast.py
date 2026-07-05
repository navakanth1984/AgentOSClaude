"""FastAggregator — single synthesizer call over concatenated raw outputs.
Lowest cost/latency of the three aggregation strategies."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from openrouter_client import call_openrouter_async

from .base import AggregationResult
from .confidence import compute_confidence


class FastAggregator:
    async def aggregate(self, prompt, per_model, api_key, judge_model, status_cb=None) -> AggregationResult:
        if status_cb:
            status_cb("synthesizing", {})

        reports = "\n\n".join(
            f"--- Model: {m['model']} ---\n{m['result']}"
            for m in per_model if m.get("result")
        )
        system = (
            "You are a synthesis agent. You are given the same prompt answered "
            "independently by several different models. Merge them into a single, "
            "best final answer. Prefer points multiple models agree on; where they "
            "disagree, pick the more well-supported claim rather than averaging."
        )
        user = f"Original prompt:\n{prompt}\n\nModel responses:\n{reports}"

        final = await call_openrouter_async(judge_model, system, user, api_key, max_tokens=1200)
        confidence, conflicts = compute_confidence(per_model)

        return {
            "final": final,
            "confidence": confidence,
            "conflicts": conflicts,
            "trace": {"stage": "fast", "synthesizer_model": judge_model},
        }

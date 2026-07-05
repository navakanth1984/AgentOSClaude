"""StandardAggregator — normalize -> agreement/conflict analysis -> synthesize.
Default aggregation mode: richer than Fast, cheaper than Verified."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from openrouter_client import call_openrouter_async

from .base import AggregationResult
from .confidence import compute_confidence


class StandardAggregator:
    async def aggregate(self, prompt, per_model, api_key, judge_model, status_cb=None) -> AggregationResult:
        if status_cb:
            status_cb("analyzing", {})

        reports = "\n\n".join(
            f"--- Model: {m['model']} ---\n{m['result']}"
            for m in per_model if m.get("result")
        )

        analysis_system = (
            "You are an agreement analyzer. Compare the model responses below and "
            "produce a short structured breakdown: (1) Common points all/most models "
            "agree on, (2) Unique insights only one model raised, (3) Direct "
            "contradictions between models, if any."
        )
        analysis_user = f"Original prompt:\n{prompt}\n\nModel responses:\n{reports}"
        analysis = await call_openrouter_async(
            judge_model, analysis_system, analysis_user, api_key, max_tokens=800
        )

        if status_cb:
            status_cb("synthesizing", {})

        synth_system = (
            "You are a synthesis agent. Using the agreement analysis provided, write "
            "the single best final answer to the original prompt. Prioritize common "
            "points, incorporate unique insights that add value, and resolve any "
            "contradictions by favoring the better-supported claim."
        )
        synth_user = (
            f"Original prompt:\n{prompt}\n\n"
            f"Agreement analysis:\n{analysis}\n\n"
            f"Raw model responses:\n{reports}"
        )
        final = await call_openrouter_async(judge_model, synth_system, synth_user, api_key, max_tokens=1200)

        confidence, conflicts = compute_confidence(per_model)

        return {
            "final": final,
            "confidence": confidence,
            "conflicts": conflicts,
            "trace": {"stage": "standard", "analysis": analysis, "synthesizer_model": judge_model},
        }

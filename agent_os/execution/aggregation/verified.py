"""VerifiedAggregator — standard pipeline + a final judge/verifier pass that
checks the synthesis against the original per-model responses and produces a
parsed judge score (0..1) that feeds into the evidence-based confidence
calculation, rather than the synthesizer inventing its own confidence."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from openrouter_client import call_openrouter_async

from .base import AggregationResult
from .standard import StandardAggregator
from .confidence import compute_confidence

_SCORE_RE = re.compile(r"score\s*[:=]?\s*(\d(?:\.\d+)?)", re.IGNORECASE)


def _parse_judge_score(text: str) -> float | None:
    match = _SCORE_RE.search(text)
    if not match:
        return None
    value = float(match.group(1))
    return min(value, 1.0) if value <= 1.0 else min(value / 10.0, 1.0)


class VerifiedAggregator:
    def __init__(self):
        self._standard = StandardAggregator()

    async def aggregate(self, prompt, per_model, api_key, judge_model, status_cb=None) -> AggregationResult:
        base = await self._standard.aggregate(prompt, per_model, api_key, judge_model, status_cb)

        if status_cb:
            status_cb("verifying", {})

        verify_system = (
            "You are a strict verifier. You will be given an original prompt, the raw "
            "responses from several models, and a synthesized final answer. Check the "
            "final answer for unsupported claims or hallucinations not backed by any "
            "of the original responses. Respond with a short critique, then end with "
            "a single line: Score: <0.0-1.0> reflecting how well-supported the final "
            "answer is."
        )
        reports = "\n\n".join(
            f"--- Model: {m['model']} ---\n{m['result']}" for m in per_model if m.get("result")
        )
        verify_user = (
            f"Original prompt:\n{prompt}\n\nRaw responses:\n{reports}\n\n"
            f"Synthesized final answer:\n{base['final']}"
        )
        verification_text = await call_openrouter_async(
            judge_model, verify_system, verify_user, api_key, max_tokens=500
        )
        judge_score = _parse_judge_score(verification_text)

        confidence, conflicts = compute_confidence(per_model, judge_score=judge_score)

        base["confidence"] = confidence
        base["conflicts"] = conflicts
        base["verification"] = {"critique": verification_text, "judge_score": judge_score}
        base["trace"]["stage"] = "verified"
        return base

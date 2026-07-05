"""
Evidence-based confidence scoring.

Per review feedback: confidence must come from measurable signals (pairwise
agreement, conflict count, judge score) — never an LLM asked to "rate its own
confidence 0-1", which just invents a plausible-looking number.
"""

from difflib import SequenceMatcher

CONFLICT_SIMILARITY_THRESHOLD = 0.35  # pairs below this ratio count as a "conflict"


def pairwise_agreement(per_model: list[dict]) -> tuple[float, list[str]]:
    """
    Returns (agreement_ratio 0..1, conflict_pairs) computed from raw textual
    similarity between successful model outputs. Cheap and deterministic —
    no extra LLM call required for this signal.
    """
    texts = [m["result"] for m in per_model if m.get("result")]
    if len(texts) < 2:
        return (1.0 if texts else 0.0), []

    ratios = []
    conflicts = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            ratio = SequenceMatcher(None, texts[i], texts[j]).quick_ratio()
            ratios.append(ratio)
            if ratio < CONFLICT_SIMILARITY_THRESHOLD:
                conflicts.append(f"model[{i}] vs model[{j}] (similarity={ratio:.2f})")

    return (sum(ratios) / len(ratios)), conflicts


def compute_confidence(
    per_model: list[dict],
    judge_score: float | None = None,
) -> tuple[float, list[str]]:
    """
    Combines pairwise agreement with an optional judge score (0..1, parsed
    from a verifier pass) into a single confidence figure. Weighted average,
    not an invented number — every input is a measured or explicitly-parsed
    signal.
    """
    agreement, conflicts = pairwise_agreement(per_model)
    if judge_score is None:
        return round(agreement, 3), conflicts
    combined = 0.5 * agreement + 0.5 * judge_score
    return round(combined, 3), conflicts

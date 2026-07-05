"""Aggregator protocol — each strategy takes the per-model results for one
prompt and returns an AggregationResult with at least {final, confidence, trace}."""

from typing import Optional, Protocol, TypedDict


class AggregationResult(TypedDict, total=False):
    final: str
    confidence: float
    conflicts: list[str]
    trace: dict
    verification: Optional[dict]


class Aggregator(Protocol):
    async def aggregate(
        self,
        prompt: str,
        per_model: list[dict],   # [{"model": ..., "result": ...}, ...]
        api_key: str,
        judge_model: str,
        status_cb=None,
    ) -> AggregationResult:
        ...

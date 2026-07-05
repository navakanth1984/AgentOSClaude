"""Shared ExecutionRequest and Executor protocol for all execution modes."""

from dataclasses import dataclass, field
from typing import Callable, Optional, Protocol


@dataclass
class ExecutionRequest:
    prompt: str
    mode: str = "single"
    requested_mode: Optional[str] = None
    planned_mode: Optional[str] = None
    executed_mode: Optional[str] = None
    routing_trace: dict = field(default_factory=dict)
    models: list[str] = field(default_factory=list)
    profile: Optional[str] = None          # e.g. "Best Overall", "Coding" — resolved via providers/capabilities.py
    expected_profile: Optional[str] = None # original expected profile for the prompt
    aggregation: str = "standard"           # "fast" | "standard" | "verified" — mixture only
    system: str = "You are a helpful, precise assistant."
    max_tokens: int = 800
    api_key: str = ""
    category: Optional[str] = None
    max_models: int = 3


# StatusCallback(stage: str, detail: dict) -> None — used to surface streaming-style
# progress ("GPT ✓ / Claude … / Gemini …") to the /execute/status polling route.
StatusCallback = Optional[Callable[[str, dict], None]]


class Executor(Protocol):
    async def execute(self, request: ExecutionRequest, status_cb: StatusCallback = None) -> dict:
        ...

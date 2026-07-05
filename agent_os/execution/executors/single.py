"""SingleExecutor — one model, one call. Thin wrapper so ExecutionManager can
treat "single model" as just another execution mode instead of a special case."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from openrouter_client import call_openrouter_async

from ..manifest import new_manifest
from .base import ExecutionRequest, StatusCallback


class SingleExecutor:
    async def execute(self, request: ExecutionRequest, status_cb: StatusCallback = None) -> dict:
        model = (request.models or ["anthropic/claude-sonnet-4-5"])[0]
        manifest = new_manifest(mode="single", models=[model], category=request.category)

        if status_cb:
            status_cb("running", {"model": model, "status": "pending"})

        t_start = time.perf_counter()
        text = await call_openrouter_async(
            model, request.system, request.prompt, request.api_key, request.max_tokens
        )
        latency_ms = (time.perf_counter() - t_start) * 1000

        manifest.per_model = [{"model": model, "result": text, "latency_ms": latency_ms}]
        manifest.final = text
        manifest.winner = model
        manifest.latency_ms = latency_ms
        manifest.add_event("execution_finished")
        manifest.save()

        if status_cb:
            status_cb("done", {"model": model, "status": "done"})

        return manifest.to_dict()

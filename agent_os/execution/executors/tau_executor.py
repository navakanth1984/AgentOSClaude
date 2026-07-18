"""
tau_executor.py — Specialized executor running Tau agent loops inside Agent OS.
"""

import sys
import time
from os import environ
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..manifest import new_manifest
from .base import ExecutionRequest, StatusCallback

# Import Tau classes
try:
    from tau_agent import AgentHarness, AgentHarnessConfig
    from tau_agent.messages import UserMessage
    from tau_ai import AnthropicConfig, OpenAICompatibleConfig, AnthropicProvider, OpenAICompatibleProvider
    _TAU_AVAILABLE = True
except ImportError:
    _TAU_AVAILABLE = False


class TauExecutor:
    """
    Executes tasks using the tau-ai AgentHarness framework.
    """

    async def execute(self, request: ExecutionRequest, status_cb: StatusCallback = None) -> dict:
        t_start = time.perf_counter()
        if not _TAU_AVAILABLE:
            return {"error": "tau-ai is not installed/available in the environment."}

        model = (request.models or ["anthropic/claude-sonnet-4-5"])[0]
        
        manifest = new_manifest(
            mode=request.mode,
            requested_mode=request.requested_mode or request.mode,
            models=[model],
            category=request.category,
            planned_mode=request.planned_mode,
            executed_mode=request.executed_mode,
            routing_trace=request.routing_trace
        )

        if status_cb:
            status_cb("running", {"stage": "tau_agent_init"})

        # Initialize the correct configuration and provider required by AgentHarnessConfig
        model_lower = model.lower()
        if "claude" in model_lower or "anthropic" in model_lower:
            key = request.api_key or environ.get("ANTHROPIC_API_KEY", "")
            if not key:
                key = environ.get("OPENROUTER_API_KEY", "dummy_key")
            provider_config = AnthropicConfig(api_key=key)
            provider_instance = AnthropicProvider(provider_config)
        else:
            key = request.api_key or environ.get("OPENROUTER_API_KEY", "")
            if not key:
                key = environ.get("GEMINI_API_KEY", "dummy_key")
            
            # Map default base URL if pointing to OpenRouter
            base_url = "https://openrouter.ai/api/v1" if "openrouter" in model_lower or key.startswith("sk-or-") else "https://api.openai.com/v1"
            provider_config = OpenAICompatibleConfig(
                api_key=key,
                base_url=base_url
            )
            provider_instance = OpenAICompatibleProvider(provider_config)

        config = AgentHarnessConfig(
            provider=provider_instance,
            model=model,
            system=request.system,
            tools=[]
        )

        harness = AgentHarness(config)
        
        if status_cb:
            status_cb("running", {"stage": "tau_agent_running"})

        # Collect response events from prompt
        response_text = ""
        
        # harness.prompt(prompt) returns AsyncIterator[AgentEvent]
        # Iterate over harness events
        async for event in harness.prompt(request.prompt):
            from tau_agent.events import MessageDeltaEvent
            if isinstance(event, MessageDeltaEvent):
                response_text += event.delta

        manifest.final = response_text
        manifest.add_event("execution_finished")
        manifest.save()

        # Clean up provider resources
        if hasattr(provider_instance, "aclose"):
            await provider_instance.aclose()

        if status_cb:
            status_cb("done", {"stage": "done"})

        merged = manifest.to_dict()
        merged["response"] = response_text
        merged["execution_time"] = time.perf_counter() - t_start
        return merged

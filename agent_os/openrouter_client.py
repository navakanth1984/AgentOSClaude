"""
openrouter_client.py — Shared OpenRouter API transport layer for Agent OS

Single source of truth for all OpenRouter HTTP calls across the codebase.
Both workflow.py (swarm agents) and goal_mode.py (planning/checking) import
from here instead of maintaining their own copies.

Usage:
    from openrouter_client import call_openrouter

    # Synchronous (urllib — no extra dependencies):
    text = call_openrouter(model, system, user, api_key)

    # Async wrapper (runs sync call in executor):
    text = await call_openrouter_async(model, system, user, api_key)
"""

import json
import os
import asyncio
import urllib.request
from typing import Optional


def call_openrouter(
    model: str,
    system: str,
    user: str,
    api_key: str = "",
    max_tokens: int = 800,
    temperature: float = 0.3,
) -> str:
    """
    Single synchronous OpenRouter LLM call via urllib (zero extra deps).
    Returns the assistant's reply text, or raises on HTTP / JSON error.

    Args:
        model:       OpenRouter model ID, e.g. "anthropic/claude-sonnet-4.6"
        system:      System prompt string
        user:        User turn content
        api_key:     OpenRouter API key (falls back to OPENROUTER_API_KEY env var)
        max_tokens:  Max response tokens (default 800)
        temperature: Sampling temperature (default 0.3)

    Raises:
        ValueError:  if no API key is available
        urllib.error.HTTPError: on non-2xx response
        KeyError:    if response JSON is malformed
    """
    api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set — add it to .env")

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
            "HTTP-Referer":  "https://agent-os",
            "X-Title":       "Agent OS",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()


async def call_openrouter_async(
    model: str,
    system: str,
    user: str,
    api_key: str = "",
    max_tokens: int = 800,
    temperature: float = 0.3,
) -> str:
    """
    Async wrapper around call_openrouter — runs the sync urllib call in
    the default thread-pool executor so it doesn't block the event loop.

    Use this inside async functions (e.g. _swarm_agent, execute_step).
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: call_openrouter(model, system, user, api_key, max_tokens, temperature),
    )

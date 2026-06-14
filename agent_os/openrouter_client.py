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
    Single synchronous LLM call via urllib. Directs natively to Google Gemini API
    if GEMINI_API_KEY is present and model contains 'gemini'. Otherwise, falls back
    to OpenRouter. If OpenRouter fails with 402 or 429, falls back to native Gemini.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    
    use_native = False
    if gemini_key:
        if "gemini" in model.lower():
            use_native = True
        elif not os.environ.get("OPENROUTER_API_KEY", ""):
            use_native = True
            
    if use_native:
        model_name = model.split("/")[-1] if "/" in model else model
        if "gemini" not in model_name.lower():
            model_name = "gemini-2.5-flash"
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
        
        payload = json.dumps({
            "systemInstruction": {
                "parts": [{"text": system}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }).encode("utf-8")
        
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"[ERROR] Native Gemini call failed: {e}")
            if hasattr(e, "read"):
                try:
                    print(f"[ERROR] Response body: {e.read().decode('utf-8')}")
                except Exception:
                    pass
            if not os.environ.get("OPENROUTER_API_KEY", ""):
                raise e

    api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set — add it to .env or configure native GEMINI_API_KEY")

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
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as he:
        print(f"[WARNING] OpenRouter failed with code {he.code} ({he.reason}) for model '{model}'.")
        
        # Fallback 1: Native Gemini
        if gemini_key:
            print("[INFO] Fallback 1: Attempting native Gemini API (gemini-2.5-flash)...")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            payload_gemini = json.dumps({
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
                "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature}
            }).encode("utf-8")
            req_gem = urllib.request.Request(url, data=payload_gemini, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req_gem, timeout=60) as r:
                    data = json.loads(r.read().decode("utf-8"))
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception as native_err:
                print(f"[ERROR] Native Gemini fallback also failed: {native_err}")
        
        # Fallback 2: OpenRouter Free Model
        if api_key and model != "openrouter/free":
            fallback_model = "openrouter/free"
            print(f"[INFO] Fallback 2: Attempting OpenRouter free model '{fallback_model}'...")
            payload_free = json.dumps({
                "model": fallback_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }).encode("utf-8")
            req_free = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=payload_free,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type":  "application/json",
                    "HTTP-Referer":  "https://agent-os",
                    "X-Title":       "Agent OS Fallback",
                },
            )
            try:
                with urllib.request.urlopen(req_free, timeout=60) as r:
                    data = json.loads(r.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"].strip()
            except Exception as free_err:
                print(f"[ERROR] OpenRouter free fallback also failed: {free_err}")

        # If everything fails, raise the original error
        raise he


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

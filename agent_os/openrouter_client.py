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
import urllib.error
from typing import Optional

# Check GenAI SDK availability for Vertex AI routing
try:
    from google import genai
    from google.genai import types
    _GENAI_SDK_AVAILABLE = True
except ImportError:
    _GENAI_SDK_AVAILABLE = False

_VERTEX_CLIENT = None


# ── Offline / local backend (Ollama) ──────────────────────────────────────────
# Lets the swarm + goal runner work with zero internet and zero API keys.
# Configure via .env:  OLLAMA_HOST (default http://localhost:11434)
#                      OLLAMA_MODEL (default llama3.2)

def _ollama_host() -> str:
    return os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")


def _ollama_reachable(timeout: float = 1.5) -> bool:
    """True if a local Ollama server answers /api/tags."""
    try:
        with urllib.request.urlopen(f"{_ollama_host()}/api/tags", timeout=timeout):
            return True
    except Exception:
        return False


def _call_ollama(
    system: str,
    user: str,
    max_tokens: int = 800,
    temperature: float = 0.3,
) -> str:
    """Single chat call to a local Ollama model. Raises on failure."""
    model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{_ollama_host()}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
        return data["message"]["content"].strip()


def backend_available() -> bool:
    """
    True if *any* LLM backend is usable right now — a cloud key, Vertex AI,
    or a reachable local Ollama. The swarm/goal gates use this instead of
    hard-checking OPENROUTER_API_KEY so they run on whatever is configured.
    """
    if os.environ.get("OPENROUTER_API_KEY"):
        return True
    if os.environ.get("GEMINI_API_KEY"):
        return True
    if os.environ.get("USE_VERTEX_AI", "").lower() in ("true", "1", "yes") \
            and os.environ.get("VERTEX_PROJECT_ID"):
        return True
    return _ollama_reachable()

def call_openrouter(
    model: str,
    system: str,
    user: str,
    api_key: str = "",
    max_tokens: int = 800,
    temperature: float = 0.3,
) -> str:
    """
    Single LLM call. Routes through Google Vertex AI using GCP credits if configured,
    otherwise directs natively to Google Gemini AI Studio, with a fallback to OpenRouter.
    """
    # ─── Vertex AI Credit Routing (Option A) ───
    use_vertex = os.environ.get("USE_VERTEX_AI", "").lower() in ("true", "1", "yes")
    vertex_project = os.environ.get("VERTEX_PROJECT_ID", "")
    
    if use_vertex and vertex_project and _GENAI_SDK_AVAILABLE and "gemini" in model.lower():
        model_name = model.split("/")[-1] if "/" in model else model
        if "gemini" not in model_name.lower():
            model_name = "gemini-2.5-flash"
            
        location = os.environ.get("VERTEX_LOCATION", "us-central1")
        
        try:
            client = genai.Client(
                vertexai=True,
                project=vertex_project,
                location=location
            )
            config = types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=max_tokens,
                temperature=temperature
            )
            response = client.models.generate_content(
                model=model_name,
                contents=user,
                config=config
            )
            return (response.text or "").strip()
        except Exception as ve:
            print(f"[WARNING] Vertex AI call failed ({ve}) — falling back to standard pathways.")

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
        # No cloud key at all — fall back to local Ollama if it's running (offline mode).
        if _ollama_reachable():
            print("[INFO] No cloud key — routing to local Ollama (offline mode).")
            return _call_ollama(system, user, max_tokens, temperature)
        raise ValueError(
            "No LLM backend available — set OPENROUTER_API_KEY or GEMINI_API_KEY in .env, "
            "or run a local Ollama server (offline mode)."
        )

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

        # Fallback 3: local Ollama (offline) — last resort when all cloud paths fail.
        if _ollama_reachable():
            print("[INFO] Fallback 3: routing to local Ollama (offline mode)...")
            try:
                return _call_ollama(system, user, max_tokens, temperature)
            except Exception as ollama_err:
                print(f"[ERROR] Ollama fallback also failed: {ollama_err}")

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

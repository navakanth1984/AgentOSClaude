"""
creative_pipeline.py — AI Filmmaking Pipeline for Agent OS
Integrates Stage 01 (Screenplay), Stage 02 (Direction/Vocal texture),
Stage 03 (Cinematography/Visual Metronome), and Stage 04 (Audiography/Sound Design).
Supports calling local LLMs (Ollama) with automatic fallback to online models (Gemini / OpenRouter).
"""

import json
import os
import urllib.request
from pathlib import Path
from typing import Optional


# Load environment variables
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

from openrouter_client import call_openrouter

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_LOCAL_MODEL = "llama3"
DEFAULT_ONLINE_MODEL = "google/gemini-2.5-flash"


def check_ollama() -> bool:
    """Check if Ollama local server is running on port 11434."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def call_llm(system: str, user: str, model: Optional[str] = None) -> str:
    """
    Tries to call a local model (Ollama) if running, otherwise falls back to online (Gemini/OpenRouter).
    """
    if check_ollama():
        local_model = DEFAULT_LOCAL_MODEL
        if model:
            # Map selected online model to a clean local model name
            m_lower = model.lower()
            if "llama" in m_lower:
                local_model = "llama3"
            elif "gemma" in m_lower:
                local_model = "gemma"
            elif "qwen" in m_lower:
                local_model = "qwen"
            elif "mistral" in m_lower:
                local_model = "mistral"
            else:
                # If it doesn't match any known family, clean it up
                local_model = model.split("/")[-1] if "/" in model else model

        print(f"[Creative Pipeline] Local Ollama detected. Using: {local_model}")
        payload = json.dumps({
            "model": local_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "stream": False
        }).encode("utf-8")
        
        req = urllib.request.Request(
            OLLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                res = json.loads(r.read().decode("utf-8"))
                return res["message"]["content"].strip()
        except Exception as e:
            print(f"[WARNING] Local Ollama call failed ({e}). Falling back to online models...")
            
    online_model = model or DEFAULT_ONLINE_MODEL
    print(f"[Creative Pipeline] Using Online model: {online_model}")
    return call_openrouter(
        model=online_model,
        system=system,
        user=user,
        max_tokens=2000,
        temperature=0.7
    )


def generate_screenplay(prompt: str, context: str = "", model: Optional[str] = None) -> str:
    """Generate a screenplay scene incorporating McKee's Story principles and vocal cues."""
    system = (
        "You are the Master Screenplay Architect. Write a cinematic scene following McKee's Story principles. "
        "Inject subtle vocal cues in the action lines (subtextual, hoarse, restrained, suppressed anger where applicable). "
        "Maintain subtextual, never on-the-nose dialogue. Output in standard screenplay format with Scene Metadata at the end."
    )
    user_prompt = f"Prompt: {prompt}\n\nContext:\n{context}" if context else f"Prompt: {prompt}"
    return call_llm(system, user_prompt, model)


def generate_audiography(scene_script: str, context: str = "", model: Optional[str] = None) -> str:
    """Generate a detailed sound design and audiography plan incorporating the Dhurandhar methods."""
    system = (
        "You are a Director of Audiography. Given a screenplay scene, design a detailed soundscape plan. "
        "Incorporate: \n"
        "1. Vocal textures (e.g., Biryani Method, gym exhaustion, smoking, or low-mid EQ matching visual color grade).\n"
        "2. Foley & Ambience (e.g., room tones, specific footsteps, spatial positioning).\n"
        "3. VFX Sound Defense (pre-mapping helicopter/vehicle flight paths, crowd expansions from 100 to 10k).\n"
        "4. Dolby Atmos Spatial Map (overhead/surround channels).\n"
        "5. Background Score vs. Sound Effects frequency balancing.\n"
        "Output using the Cinematic Audiography & Sound Design Plan format."
    )
    user_prompt = f"Scene Script:\n{scene_script}\n\nContext:\n{context}" if context else f"Scene Script:\n{scene_script}"
    return call_llm(system, user_prompt, model)


def generate_visual_prompt(scene_or_shot: str, context: str = "", model: Optional[str] = None) -> str:
    """Generate high-fidelity visual prompts for Midjourney/Flux/Veo based on cinematography rules."""
    system = (
        "You are a Cinematic VFX Prompter. Translate the scene or shot description into production-ready "
        "visual prompts for AI image/video generators (Midjourney, Flux, Veo). Spec out specific camera lens (wide vs portrait), "
        "camera persona (Steadicam, handheld), lighting (key/fill contrast, color temperature), and environmental textures. "
        "Ensure the visual prompt communicates the visual metronome and atmosphere."
    )
    user_prompt = f"Scene/Shot:\n{scene_or_shot}\n\nContext:\n{context}" if context else f"Scene/Shot:\n{scene_or_shot}"
    return call_llm(system, user_prompt, model)

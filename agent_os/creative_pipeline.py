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
from typing import Callable, Optional


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


def generate_video_prompts(prompt: str, context: str = "", num_shots: int = 20, model: Optional[str] = None) -> str:
    """Generate a numbered list of video/shot prompts for AI video generators (Veo, Higgsfield, Runway)."""
    system = (
        "You are a Cinematic Shot Director. Generate a numbered sequence of production-ready video prompts "
        "for AI video generators (Google Veo, Higgsfield, Runway, Kling). Each shot prompt must specify: "
        "camera movement (dolly/pan/tilt/crane/handheld), lens type, subject framing, lighting mood, "
        "color palette, duration (2-8s), and emotional tone. Output each shot on its own numbered line."
    )
    user_prompt = (
        f"Create {num_shots} shot prompts for: {prompt}"
        + (f"\n\nContext:\n{context}" if context else "")
    )
    return call_llm(system, user_prompt, model)


def generate_audio_design_prompts(prompt: str, context: str = "", model: Optional[str] = None) -> str:
    """Generate full audio design specification: music cues, foley, ambience, and Dolby Atmos spatial map."""
    system = (
        "You are a Director of Audiography. Design a complete audio specification including: "
        "1. Background score cues (BPM, key, instrumentation, emotional arc). "
        "2. Foley map (footsteps, textures, impact sounds with spatial positions). "
        "3. Ambience layers (room tones, environment, crowd dynamics). "
        "4. Dolby Atmos spatial map (overhead/surround/LFE assignments). "
        "5. Sound effects library list with frequency ranges. "
        "6. Vocal texture notes (Biryani Method, mic placement, EQ matching visual grade). "
        "Output as a structured audio design document."
    )
    user_prompt = (
        f"Design the audio specification for: {prompt}"
        + (f"\n\nContext:\n{context}" if context else "")
    )
    return call_llm(system, user_prompt, model)


def generate_image_prompts(prompt: str, context: str = "", num_images: int = 20, model: Optional[str] = None) -> str:
    """Generate numbered image prompts for AI image generators (Midjourney, Flux, DALL-E, Firefly)."""
    system = (
        "You are a Visual Art Director specialising in AI image generation. "
        "Generate a numbered list of detailed image prompts for Midjourney, Flux, DALL-E, or Adobe Firefly. "
        "Each prompt must include: subject description, art style, lighting setup, colour palette, "
        "camera/lens analogue (e.g. 85mm portrait, wide-angle), mood keywords, and negative prompt hints. "
        "Number each prompt clearly."
    )
    user_prompt = (
        f"Create {num_images} image prompts for: {prompt}"
        + (f"\n\nContext:\n{context}" if context else "")
    )
    return call_llm(system, user_prompt, model)


# ── Long-form chunked generation ────────────────────────────────────────────

_LONGFORM_SYSTEMS = {
    "screenplay": (
        "You are the Master Screenplay Architect. Write in standard screenplay format "
        "(INT./EXT. sluglines, action blocks, CHARACTER dialogue with parentheticals). "
        "Follow McKee's Story principles: every scene turns the value charge. "
        "Inject subtle vocal cues (hoarse, restrained, suppressed anger) in action lines. "
        "Keep dialogue subtext-heavy, never on-the-nose. "
        "End the chunk mid-action if needed — a continuation prompt will follow."
    ),
    "novel": (
        "You are the OpenClaw Novelist. Write immersive literary prose. "
        "Use all five senses in scene setting. Keep internal monologue layered. "
        "Dialogue must carry subtext. Pacing: mix long atmospheric paragraphs with short punchy beats. "
        "End the chunk at a natural paragraph break — a continuation prompt will follow."
    ),
    "video_prompts": (
        "You are a Cinematic Shot Director. Generate numbered shot prompts for AI video generators "
        "(Google Veo, Higgsfield, Runway). Each prompt: camera movement, lens, framing, lighting, "
        "colour palette, duration (2-8s), emotional tone. One shot per line, numbered."
    ),
    "audio_design": (
        "You are a Director of Audiography. Generate a numbered list of audio design cues: "
        "music cue (BPM, key, mood), foley items, ambience layers, Dolby Atmos positions, SFX. "
        "Each entry numbered and formatted as: [CUE-N] TYPE | Description | Spatial position."
    ),
    "image_prompts": (
        "You are a Visual Art Director. Generate numbered image prompts for Midjourney/Flux/Firefly. "
        "Each prompt: subject, art style, lighting, colour palette, lens analogue, mood. One prompt per line, numbered."
    ),
}

# Approximate words per page by mode
_WORDS_PER_PAGE = {
    "screenplay": 200,    # ~1 min screen time per page
    "novel": 300,
    "video_prompts": 50,  # ~5 shots per page
    "audio_design": 80,
    "image_prompts": 60,
}

# Words per LLM chunk call
_CHUNK_TARGET_WORDS = {
    "screenplay": 1200,
    "novel": 1800,
    "video_prompts": 500,
    "audio_design": 600,
    "image_prompts": 500,
}

# Frontend/subtab names that don't match backend mode keys. The dashboard's
# "Novelist Swarm" long-form subtab sends mode="novelist", but the engine keys
# the novel prose system prompt under "novel". Normalise before lookup.
_MODE_ALIASES = {
    "novelist": "novel",
}

# LLMs reliably under-produce against their per-chunk word target (a "1200-word"
# chunk often comes back as ~250 words), so a computed chunk count of N yields
# roughly N/3 pages in practice. Generate 3× the chunks so a 300-page request
# actually lands near 300 pages instead of ~30. Applies to every page selection.
_CHUNK_MULTIPLIER = 3


def _summarise_chunk(text: str, model: Optional[str] = None) -> str:
    """Produce a short continuity seed from the last chunk for the next one."""
    system = "Summarise the following creative content in 3-5 sentences, capturing: key story beats, character emotional states, setting, and where it ended. This will be used as continuity context for the next section."
    return call_llm(system, f"Content:\n{text[-3000:]}", model)


def generate_longform(
    mode: str,
    prompt: str,
    context: str = "",
    target_pages: int = 30,
    model: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> str:
    """
    Generate long-form creative content in chunks with continuity carry-forward.

    Each chunk calls the LLM with a continuity seed from the previous chunk.
    Suitable for 30-300 page screenplays, novels, or large prompt batches.
    """
    mode = _MODE_ALIASES.get(mode, mode)
    if mode not in _LONGFORM_SYSTEMS:
        raise ValueError(f"Unknown mode: {mode}. Choose from {list(_LONGFORM_SYSTEMS)}")

    words_per_page = _WORDS_PER_PAGE.get(mode, 250)
    chunk_words = _CHUNK_TARGET_WORDS.get(mode, 1000)
    total_words = target_pages * words_per_page
    num_chunks = max(1, round(total_words / chunk_words) * _CHUNK_MULTIPLIER)

    system = _LONGFORM_SYSTEMS[mode]
    full_text: list[str] = []
    continuity_seed = context

    print(f"[LongForm] mode={mode} target_pages={target_pages} -> {num_chunks} chunks (~{chunk_words} words each)")

    for i in range(num_chunks):
        chunk_num = i + 1
        is_first = i == 0
        is_last = i == num_chunks - 1

        if is_first:
            user_prompt = (
                f"CONCEPT:\n{prompt}\n\n"
                + (f"CONTEXT:\n{context}\n\n" if context else "")
                + f"Write chunk 1 of {num_chunks}. Target approximately {chunk_words} words."
                + (" Begin from the very start." if is_first else "")
                + (" This is the final chunk — bring the narrative to a satisfying close." if is_last else "")
            )
        else:
            user_prompt = (
                f"ORIGINAL CONCEPT:\n{prompt}\n\n"
                f"CONTINUITY FROM PREVIOUS CHUNK:\n{continuity_seed}\n\n"
                f"Write chunk {chunk_num} of {num_chunks}. Target approximately {chunk_words} words. "
                f"Continue directly from where the previous chunk left off."
                + (" This is the final chunk — bring the narrative to a satisfying close." if is_last else "")
            )

        print(f"[LongForm] Generating chunk {chunk_num}/{num_chunks}…")
        chunk_text = call_llm(system, user_prompt, model)
        full_text.append(chunk_text)

        if progress_callback:
            progress_callback(chunk_num, num_chunks, chunk_text)

        # Build continuity seed for next chunk (not needed after the last)
        if not is_last:
            continuity_seed = _summarise_chunk(chunk_text, model)

    separator = "\n\n" + ("─" * 60) + "\n\n"
    return separator.join(full_text)

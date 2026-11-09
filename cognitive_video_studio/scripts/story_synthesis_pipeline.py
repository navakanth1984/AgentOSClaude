"""
Story Synthesis Pipeline for Multi-Take Video Consolidation
===========================================================
This pipeline solves the problem of inferring a global story context (macro-narrative)
across 50-100+ raw, fragmented, out-of-order production camera takes.

It combines modular open-source building blocks:
1. Audio Extraction & Speech Translation (faster-whisper)
2. Director / Slate Filtering (identifying "Action", "Cut", false starts)
3. Character Face Clustering (OpenCV / InsightFace embeddings)
4. Hierarchical Narrative Synthesis (Structured LLM prompting)
"""

import os
import sys
import json
import glob
import wave
import numpy as np
from pathlib import Path

def extract_dialogue_from_take(audio_wav_path: str):
    """
    Transcribes and translates dialogue from a take's audio track using faster-whisper.
    Filters out technical director calls (Action, Cut, Slate).
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return {"error": "faster-whisper not installed in current env"}

    model = WhisperModel("base", device="cpu", compute_type="int8")

    # Read WAV normalized samples
    with wave.open(audio_wav_path, 'rb') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    if sampwidth == 2:
        audio_np = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        audio_np = np.frombuffer(raw_bytes, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        audio_np = np.frombuffer(raw_bytes, dtype=np.float32)

    if n_channels > 1:
        audio_np = audio_np.reshape(-1, n_channels).mean(axis=1)

    segments, info = model.transcribe(
        audio_np, 
        task="translate", # Translates regional dialects (Telugu, Hindi, etc.) into English
        beam_size=5
    )

    dialogue_lines = []
    director_calls = []

    for seg in segments:
        text = seg.text.strip()
        lower_text = text.lower()
        # Detect director cues vs character dialogue
        if any(cue in lower_text for cue in ["action", "cut", "rolling", "slate", "sound speed", "hold on", "reset"]):
            director_calls.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "cue": text})
        else:
            dialogue_lines.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "text": text})

    return {
        "detected_language": info.language,
        "language_probability": round(info.language_probability, 3),
        "dialogue": dialogue_lines,
        "director_calls": director_calls
    }

def build_narrative_synthesis_prompt(takes_metadata: list) -> str:
    """
    Constructs the master LLM consolidation prompt from 50-100 takes.
    """
    prompt = """You are a Master Screenplay Analyst and Film Director's Narrative Copilot.
Below is the consolidated transcript, character presence matrix, and scene action summaries
extracted from a multi-day film shoot comprising raw camera takes.

Your task is to infer the GLOBAL MACRO STORY CONTEXT across all takes and output a formal Story Bible in JSON format.

### Input Take Dossiers:
"""
    for take in takes_metadata:
        prompt += f"\n--- Take: {take.get('id')} ({take.get('sourceFile')}) ---\n"
        prompt += f"Visual Setting: {take.get('visual_summary', 'Interior room, floor setup')}\n"
        prompt += f"Characters Present: {', '.join(take.get('characters', []))}\n"
        prompt += f"Translated Dialogue:\n"
        for line in take.get('dialogue', []):
            prompt += f"  [{line['start']}s - {line['end']}s]: \"{line['text']}\"\n"

    prompt += """
### Required Output JSON Format:
{
  "title": "<Working Title>",
  "logline": "<One or two sentence summary of protagonist, incident, central conflict, and stakes>",
  "coreConflict": "<The fundamental dramatic collision>",
  "theme": "<Universal emotional and thematic takeaway>",
  "setting": "<Primary physical environments and atmosphere>",
  "confidenceScore": <integer 0-100>,
  "characters": [
    {
      "id": "char_01",
      "name": "<Character Name / Role>",
      "relationship": "<Relational dynamic>",
      "appearance": "<Visual attire & staging cues>",
      "dramaticNeed": "<What they are fighting for in this scene>",
      "totalTakesPresent": <count>
    }
  ],
  "acts": [
    {
      "actNumber": 1,
      "title": "<Act 1 Title>",
      "dramaticObjective": "<Dramatic purpose>",
      "takeRange": "<Takes X - Y>"
    }
  ]
}
"""
    return prompt

if __name__ == "__main__":
    print("Story Synthesis Pipeline initialized.")

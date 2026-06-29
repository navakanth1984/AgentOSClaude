"""DEPRECATED — legacy monolithic audiobook pipeline.

Superseded by the V1.1 speech subsystem:
  - book-level orchestration: agent_os/speech/audiobook.py  (build_audiobook / `cli audiobook`)
  - synthesis + caching + routing: agent_os/speech/ (SpeechService DAG)
  - engines: agent_os/speech/engines/ (kokoro, piper, sarvam)

This module (and agent_os/tts/) is kept only for backward compatibility and is
slated for removal. Do not build new features here. See wiki/agent-os-speech-pipeline.md.
"""
import os
import json
import hashlib
import time
import warnings
from pathlib import Path
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import soundfile as sf
import subprocess

from agent_os.openrouter_client import call_openrouter
from agent_os.tts import kokoro, gcp, sarvam

warnings.warn(
    "audiobook_pipeline is deprecated; use agent_os.speech.audiobook.build_audiobook "
    "(CLI: `python -m agent_os.cli audiobook <input>`).",
    DeprecationWarning, stacklevel=2,
)

@dataclass
class TTSPolicy:
    engine: str = "kokoro"
    voice: str = "af_nova"
    parallel_jobs: int = 4
    use_cache: bool = True
    export_mp3: bool = False

def normalize_text(text: str) -> str:
    """
    Clean smart quotes, normalize punctuation, remove duplicate spaces.
    """
    replacements = {
        '“': '"', '”': '"',
        '‘': "'", '’': "'",
        '…': '...',
        '—': '-', '–': '-'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove duplicate spaces
    text = " ".join(text.split())
    return text

def extract_dialogue(text: str) -> list:
    """
    Use Gemini via openrouter_client to extract dialogue and narration into structured JSON.
    """
    system_prompt = '''You are an expert audiobook prep processor.
Your task is to take a raw text (screenplay or novel snippet) and convert it into a JSON array of spoken segments.
Strip out all stage directions, camera angles, and unreadable formatting.
For novels, split into reasonable paragraphs.

Output ONLY a JSON array with this format for each segment:
[
  {
    "speaker": "John" (or "Narrator"),
    "emotion": "neutral",
    "text": "Hello, world."
  }
]
No markdown blocks, just the raw JSON array. Ensure it is valid JSON.
'''
    
    try:
        response = call_openrouter(
            model="google/gemini-2.5-flash",
            system=system_prompt,
            user=text,
            max_tokens=8000
        )
        
        # Clean up any potential markdown code blocks if the model didn't listen
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
            
        data = json.loads(response.strip())
        return data
    except Exception as e:
        print(f"[Error] Gemini Parsing Failed: {e}")
        return []

def chunk_dialogue(dialogue: list, max_words=200) -> list:
    """
    Ensure no individual JSON segment is too long for the TTS engine.
    Splits segments containing > max_words into smaller segments.
    """
    chunked = []
    for item in dialogue:
        words = item.get("text", "").split()
        if len(words) <= max_words:
            chunked.append(item)
        else:
            # Split into chunks of approx max_words
            current_chunk = []
            for word in words:
                current_chunk.append(word)
                # Split roughly at max_words, preferably at a sentence boundary
                if len(current_chunk) >= max_words and word.endswith(('.', '?', '!', '"', "'")):
                    new_item = dict(item)
                    new_item["text"] = " ".join(current_chunk)
                    chunked.append(new_item)
                    current_chunk = []
            
            if current_chunk:
                new_item = dict(item)
                new_item["text"] = " ".join(current_chunk)
                chunked.append(new_item)
    return chunked

def synthesize_chunk(item: dict, chunk_id: int, policy: TTSPolicy, cache_dir: Path, output_dir: Path) -> dict:
    """
    Synthesize a single text chunk, utilizing the cache if enabled.
    Returns metadata about the generated chunk.
    """
    text = item.get("text", "").strip()
    if not text:
        return {"id": chunk_id, "success": False, "error": "Empty text"}
        
    text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]
    cache_file = cache_dir / f"{text_hash}.wav"
    output_file = output_dir / f"{chunk_id:04d}.wav"
    
    result = {
        "id": chunk_id,
        "text": text,
        "speaker": item.get("speaker", "Narrator"),
        "hash": text_hash,
        "file": str(output_file.name),
        "success": False
    }

    try:
        # Check cache
        if policy.use_cache and cache_file.exists():
            # Copy from cache to output
            data, sr = sf.read(str(cache_file))
            sf.write(str(output_file), data, sr)
            result["success"] = True
            result["cached"] = True
            return result
            
        # Synthesize based on engine
        if policy.engine == "kokoro":
            # Just use the default voice for now, though we could map speakers to voices
            samples, sr = kokoro.synthesize(text, voice_name=policy.voice)
        elif policy.engine == "gcp":
            samples, sr = gcp.synthesize(text, voice_name=policy.voice)
        elif policy.engine == "sarvam":
            samples, sr = sarvam.synthesize(text, voice_name=policy.voice)
        else:
            raise ValueError(f"Unknown engine {policy.engine}")
            
        # Write to output and cache
        sf.write(str(output_file), samples, sr)
        if policy.use_cache:
            sf.write(str(cache_file), samples, sr)
            
        result["success"] = True
        result["cached"] = False
        
    except Exception as e:
        result["error"] = str(e)
        
    return result

def merge_wavs(chunk_paths: list, output_path: Path):
    """
    Merge multiple wav files into one using numpy and soundfile.
    """
    all_data = []
    target_sr = None
    
    for cp in chunk_paths:
        data, sr = sf.read(str(cp))
        if target_sr is None:
            target_sr = sr
        elif target_sr != sr:
            # Resampling could go here if needed, but assuming uniform generation
            print(f"Warning: Sample rate mismatch in {cp}. Expected {target_sr}, got {sr}")
            continue
            
        all_data.append(data)
        
    if all_data:
        merged = np.concatenate(all_data)
        sf.write(str(output_path), merged, int(target_sr or 24000))
        return True
    return False

def export_mp3(wav_path: Path, mp3_path: Path):
    """
    Use ffmpeg to export WAV to MP3 if available.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", "-qscale:a", "2", str(mp3_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: ffmpeg not found or failed. MP3 export skipped.")
        return False

def process_audiobook(input_text: str, book_name: str, policy: TTSPolicy, base_dir: Path):
    """
    Master pipeline orchestrator.
    """
    print(f"Starting audiobook pipeline for '{book_name}'...")
    
    # 1. Directories
    book_dir = base_dir / "audiobooks" / book_name
    chunks_dir = book_dir / "chunks"
    cache_dir = base_dir / "cache"
    
    for d in [chunks_dir, cache_dir]:
        d.mkdir(parents=True, exist_ok=True)
        
    manifest_path = book_dir / "manifest.json"
    transcript_path = book_dir / "transcript.json"
    
    # 2. Pre-processing
    print("Normalizing text...")
    text = normalize_text(input_text)
    
    print("Extracting dialogue via Gemini...")
    dialogue = extract_dialogue(text)
    if not dialogue:
        print("Failed to extract dialogue. Aborting.")
        return
        
    print("Chunking long segments...")
    chunked_dialogue = chunk_dialogue(dialogue)
    
    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(chunked_dialogue, f, indent=2)
        
    # 3. Parallel Synthesis
    print(f"Synthesizing {len(chunked_dialogue)} chunks using {policy.engine} (parallel={policy.parallel_jobs})...")
    
    results = []
    with ThreadPoolExecutor(max_workers=policy.parallel_jobs) as executor:
        futures = []
        for i, item in enumerate(chunked_dialogue):
            # Skip if resuming and file exists
            output_file = chunks_dir / f"{i:04d}.wav"
            if policy.use_cache and output_file.exists():
                print(f"Skipping {i:04d} (already exists)")
                # Minimal mock result
                results.append({
                    "id": i,
                    "file": str(output_file.name),
                    "success": True,
                    "cached": True
                })
                continue
                
            futures.append(executor.submit(synthesize_chunk, item, i, policy, cache_dir, chunks_dir))
            
        for future in futures:
            res = future.result()
            results.append(res)
            status = "Cached" if res.get("cached") else "Generated"
            if res.get("success"):
                print(f" Chunk {res['id']:04d} -> {status}")
            else:
                print(f" Chunk {res['id']:04d} -> FAILED: {res.get('error')}")

    # 4. Merge
    print("Merging WAV files...")
    results.sort(key=lambda x: x["id"])
    valid_chunks = [chunks_dir / str(r["file"]) for r in results if r.get("success")]
    
    merged_wav = book_dir / "merged.wav"
    if merge_wavs(valid_chunks, merged_wav):
        print(f"Merged successfully: {merged_wav}")
        
        if policy.export_mp3:
            print("Exporting MP3...")
            merged_mp3 = book_dir / "merged.mp3"
            if export_mp3(merged_wav, merged_mp3):
                print(f"Exported MP3: {merged_mp3}")
                
    # 5. Manifest
    manifest = {
        "title": book_name,
        "engine": policy.engine,
        "voice": policy.voice,
        "chunks_total": len(chunked_dialogue),
        "chunks_success": len(valid_chunks),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Audiobook pipeline complete. Saved to {book_dir}")

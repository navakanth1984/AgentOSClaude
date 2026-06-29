"""Audiobook orchestration on top of the hardened SpeechService DAG.

This is the book-level layer the legacy `audiobook_pipeline.py` used to provide,
but built on the V1.1 pipeline (typed contracts, deterministic caching, per-voice
routing, resumability) instead of the old monolith.

Responsibilities (only what SpeechService doesn't do):
  - resolve a book into ordered chapters (a single file, or every .txt/.md in a dir)
  - run each chapter through SpeechService (one job per chapter)
  - stitch chapter WAVs into one book WAV (with inter-chapter silence)
  - optional MP3 export via ffmpeg
  - write a stable `audiobooks/<name>/` layout + manifest

SpeechService still owns synthesis, caching, and per-chapter resumability, so a
re-run skips already-synthesized chunks for free.
"""
import os
import json
import time
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any

import numpy as np
import soundfile as sf

import agent_os.env_boot  # noqa: F401 — keys from .env
from agent_os.speech.service import SpeechService
from agent_os.speech.schema.jobs import SpeechJobStore, JobState

CHAPTER_GAP_SEC = 0.7

# Per-engine default speaker when the caller passes "default"/None.
_DEFAULT_SPEAKERS = {"kokoro": "af_heart", "sarvam": "rohan", "piper": "default"}


def _resolve_chapters(input_path: str) -> List[Path]:
    p = Path(input_path)
    if p.is_dir():
        files = sorted(f for f in p.iterdir() if f.suffix.lower() in (".txt", ".md"))
        if not files:
            raise FileNotFoundError(f"No .txt/.md chapters found in directory: {p}")
        return files
    if p.is_file():
        return [p]
    raise FileNotFoundError(f"Input path not found: {p}")


def _chapter_wav(job_output_dir: str) -> Optional[Path]:
    """SpeechService writes the merged chapter as Chapter_0.wav; fall back to any wav."""
    direct = Path(job_output_dir) / "Chapter_0.wav"
    if direct.exists():
        return direct
    wavs = sorted(Path(job_output_dir).glob("*.wav"))
    return wavs[0] if wavs else None


def _concat_wavs(wavs: List[Path], out_path: Path, gap_sec: float = CHAPTER_GAP_SEC) -> Dict[str, Any]:
    parts: List[np.ndarray] = []
    sr0: Optional[int] = None
    for w in wavs:
        data, sr = sf.read(str(w), dtype="int16")
        if sr0 is None:
            sr0 = sr
        elif sr != sr0:
            # Hard fail rather than silently dropping a chapter (merge stage would skip it).
            raise ValueError(
                f"Sample-rate mismatch: {w.name} is {sr}Hz but book is {sr0}Hz. "
                f"Use one engine per book."
            )
        if parts:
            parts.append(np.zeros(int(gap_sec * sr0), dtype="int16"))
        parts.append(data)
    book = np.concatenate(parts) if parts else np.zeros(0, dtype="int16")
    sf.write(str(out_path), book, sr0 or 24000)
    return {"sample_rate": sr0 or 24000, "duration_sec": round(len(book) / (sr0 or 24000), 2)}


def _to_mp3(wav_path: Path, mp3_path: Path) -> bool:
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame",
             "-qscale:a", "2", str(mp3_path)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[audiobook] ffmpeg unavailable — MP3 export skipped.")
        return False


def build_audiobook(
    input_path: str,
    book_name: Optional[str] = None,
    engine: str = "kokoro",
    voice: str = "default",
    export_mp3: bool = False,
    parser: Optional[str] = None,
    base_dir: str = "audiobooks",
) -> Dict[str, Any]:
    """Generate a full audiobook. Returns a manifest dict (also written to disk)."""
    chapters = _resolve_chapters(input_path)
    src = Path(input_path)
    book_name = book_name or (src.stem if src.is_file() else src.name)
    if not voice or voice == "default":
        voice = _DEFAULT_SPEAKERS.get(engine, "default")

    book_dir = Path(base_dir) / book_name
    chapters_dir = book_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    print(f"[audiobook] '{book_name}': {len(chapters)} chapter(s), engine={engine}, voice={voice}")

    chapter_wavs: List[Path] = []
    chapter_meta: List[Dict[str, Any]] = []
    for i, cf in enumerate(chapters, start=1):
        payload: Dict[str, Any] = {"text_path": str(cf), "engine": engine, "voice": voice}
        if parser:
            payload["parser"] = parser
        out_dir = str(chapters_dir / f"{i:03d}_{cf.stem}")
        job = SpeechService.create_job(payload, output_dir=out_dir)
        print(f"[audiobook]   chapter {i}/{len(chapters)}: {cf.name} -> job {job.job_id[:8]}")
        SpeechService.run_job(job.job_id, background=False)
        done = SpeechJobStore.load(job.job_id)
        if done is None:
            raise RuntimeError(f"Chapter '{cf.name}' job disappeared after run; aborting book.")
        wav = _chapter_wav(done.output_directory)
        if done.state != JobState.COMPLETED or not wav:
            raise RuntimeError(f"Chapter '{cf.name}' failed (state={done.state.value}); aborting book.")
        chapter_wavs.append(wav)
        chapter_meta.append({"index": i, "source": cf.name, "wav": str(wav),
                             "job_id": done.job_id})

    book_wav = book_dir / f"{book_name}.wav"
    audio_info = _concat_wavs(chapter_wavs, book_wav)
    print(f"[audiobook] merged -> {book_wav} ({audio_info['duration_sec']}s @ {audio_info['sample_rate']}Hz)")

    book_mp3: Optional[str] = None
    if export_mp3:
        mp3 = book_dir / f"{book_name}.mp3"
        if _to_mp3(book_wav, mp3):
            book_mp3 = str(mp3)
            print(f"[audiobook] exported -> {mp3}")

    manifest = {
        "book": book_name,
        "engine": engine,
        "voice": voice,
        "parser": parser or "production",
        "chapters": chapter_meta,
        "chapter_count": len(chapter_meta),
        "book_wav": str(book_wav),
        "book_mp3": book_mp3,
        "duration_sec": audio_info["duration_sec"],
        "sample_rate": audio_info["sample_rate"],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(book_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"[audiobook] done -> {book_dir}")
    return manifest

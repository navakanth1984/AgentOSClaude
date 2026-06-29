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
import re
import concurrent.futures
from pathlib import Path
from typing import List, Optional, Dict, Any

import numpy as np
import soundfile as sf

import agent_os.env_boot  # noqa: F401 — keys from .env
from agent_os.speech.service import SpeechService
from agent_os.speech.schema.jobs import SpeechJobStore, JobState

CHAPTER_GAP_SEC = 0.7

# A markerless document longer than this is split into bounded synthetic chapters.
# A whole book processed as one chapter becomes ~800+ synthesis chunks, which
# fragments kokoro's per-chunk ONNX rebuild (OpenBLAS abort) and balloons sarvam's
# sequential API calls (one failure aborts the book). ~5k chars keeps each chapter
# well under the empirically safe per-job chunk count.
MAX_MARKERLESS_CHAPTER_CHARS = 5000

# Per-engine default speaker when the caller passes "default"/None.
_DEFAULT_SPEAKERS = {"kokoro": "af_heart", "sarvam": "rohan", "piper": "default"}


def _split_text_by_budget(text: str, budget: int) -> List[str]:
    """Pack paragraphs/lines into parts of at most `budget` chars, never splitting
    a line across parts. A single line longer than `budget` becomes its own part."""
    parts: List[str] = []
    buf: List[str] = []
    size = 0
    for line in text.splitlines(keepends=True):
        if buf and size + len(line) > budget:
            parts.append("".join(buf))
            buf, size = [], 0
        buf.append(line)
        size += len(line)
    if buf:
        parts.append("".join(buf))
    return [p for p in (s.strip() for s in parts) if p]


def _split_in_file_chapters(input_file: Path, book_dir: Path) -> List[Path]:
    """
    Parses input_file, splits it by chapter markers (e.g. 'Chapter 1', 'CHAPTER II'),
    writes each chapter to a separate file, and returns the list of Paths.
    If no chapter markers are found, returns the input_file as a single-element list.
    """
    ext = input_file.suffix.lower()
    if ext == ".docx":
        try:
            import docx
            doc = docx.Document(str(input_file))
            content = "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            raise RuntimeError(f"Failed to parse DOCX {input_file}: {e}")
    elif ext == ".pdf":
        try:
            import fitz  # type: ignore
            doc = fitz.open(str(input_file))
            content = "\n".join(page.get_text() for page in doc)
        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF {input_file}: {e}")
    else:
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()
    
    
    # Pattern matching "Chapter X" or "CHAPTER X" at the start of a line
    pattern = re.compile(r'^(?:Chapter|CHAPTER)\s+[0-9IVXLCDMivxlcdm]+.*$', re.MULTILINE | re.IGNORECASE)
    matches = list(pattern.finditer(content))
    
    if not matches:
        # Try a fallback pattern: lines starting with "Chapter" or "CHAPTER"
        pattern = re.compile(r'^(?:Chapter|CHAPTER)\b.*$', re.MULTILINE | re.IGNORECASE)
        matches = list(pattern.finditer(content))
        
    if not matches:
        # No chapter markers. Small inputs stay a single chapter (prior behaviour).
        # Large inputs are split into bounded synthetic chapters so each SpeechService
        # job processes a sane number of chunks — see MAX_MARKERLESS_CHAPTER_CHARS.
        if len(content) <= MAX_MARKERLESS_CHAPTER_CHARS:
            return [input_file]
        src_chapters_dir = book_dir / "src_chapters"
        src_chapters_dir.mkdir(parents=True, exist_ok=True)
        parts = _split_text_by_budget(content, MAX_MARKERLESS_CHAPTER_CHARS)
        chapters_paths = []
        for idx, part in enumerate(parts):
            part_path = src_chapters_dir / f"{idx + 1:03d}_part.txt"
            with open(part_path, "w", encoding="utf-8") as out_f:
                out_f.write(part)
            chapters_paths.append(part_path)
        print(f"[audiobook] No chapter markers found; split {len(content)} chars "
              f"into {len(chapters_paths)} bounded chapters (<= {MAX_MARKERLESS_CHAPTER_CHARS} chars each).")
        return chapters_paths

    chapters_paths = []
    src_chapters_dir = book_dir / "src_chapters"
    src_chapters_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if there is text before the first chapter marker
    preface_text = content[:matches[0].start()].strip()
    if preface_text:
        preface_path = src_chapters_dir / "000_preface.txt"
        with open(preface_path, "w", encoding="utf-8") as out_f:
            out_f.write(preface_text)
        chapters_paths.append(preface_path)
        
    for idx, match in enumerate(matches):
        start_idx = match.start()
        end_idx = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        chapter_text = content[start_idx:end_idx].strip()
        
        header_line = match.group(0).strip()
        # Clean header for filename
        clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', header_line)[:50]
        chapter_filename = f"{idx + 1:03d}_{clean_name}.txt"
        chapter_path = src_chapters_dir / chapter_filename
        
        with open(chapter_path, "w", encoding="utf-8") as out_f:
            out_f.write(chapter_text)
        chapters_paths.append(chapter_path)
        
    return chapters_paths


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
    max_workers: int = 2,
) -> Dict[str, Any]:
    """Generate a full audiobook. Returns a manifest dict (also written to disk)."""
    src = Path(input_path)
    book_name = book_name or (src.stem if src.is_file() else src.name)
    book_dir = Path(base_dir) / book_name

    # Resolve chapters with in-file splitting support
    if src.is_dir():
        chapters = _resolve_chapters(input_path)
    elif src.is_file():
        chapters = _split_in_file_chapters(src, book_dir)
    else:
        raise FileNotFoundError(f"Input path not found: {input_path}")

    if not voice or voice == "default":
        voice = _DEFAULT_SPEAKERS.get(engine, "default")

    chapters_dir = book_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    print(f"[audiobook] '{book_name}': {len(chapters)} chapter(s), engine={engine}, voice={voice}, max_workers={max_workers}")

    def process_chapter(args) -> tuple[int, Path, Dict[str, Any]]:
        i, cf = args
        out_dir = str(chapters_dir / f"{i:03d}_{cf.stem}")
        wav = _chapter_wav(out_dir)
        job_json_path = Path(out_dir) / "job.json"
        
        # Resume: skip already completed chapters
        if wav and wav.exists() and job_json_path.exists():
            try:
                with open(job_json_path, "r", encoding="utf-8") as f:
                    job_data = json.load(f)
                if job_data.get("state") == "completed":
                    print(f"[audiobook]   chapter {i}: {cf.name} -> already completed (skipping)")
                    return i, wav, {"index": i, "source": cf.name, "wav": str(wav), "job_id": job_data.get("job_id")}
            except Exception:
                pass

        payload: Dict[str, Any] = {"text_path": str(cf), "engine": engine, "voice": voice}
        if parser:
            payload["parser"] = parser
            
        job = SpeechService.create_job(payload, output_dir=out_dir)
        print(f"[audiobook]   chapter {i}: {cf.name} -> job {job.job_id[:8]}")
        SpeechService.run_job(job.job_id, background=False)
        
        done = SpeechJobStore.load(job.job_id)
        if done is None:
            raise RuntimeError(f"Chapter '{cf.name}' job disappeared after run; aborting book.")
        wav = _chapter_wav(done.output_directory)
        if done.state != JobState.COMPLETED or not wav:
            raise RuntimeError(f"Chapter '{cf.name}' failed (state={done.state.value}); aborting book.")
            
        return i, wav, {"index": i, "source": cf.name, "wav": str(wav), "job_id": done.job_id}

    # Execute in parallel or sequential
    results = []
    if max_workers > 1 and len(chapters) > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(process_chapter, (i, cf)) for i, cf in enumerate(chapters, start=1)]
            results = [f.result() for f in futures]
    else:
        for i, cf in enumerate(chapters, start=1):
            results.append(process_chapter((i, cf)))

    # Keep output in original sequence
    results.sort(key=lambda x: x[0])
    chapter_wavs = [r[1] for r in results]
    chapter_meta = [r[2] for r in results]

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

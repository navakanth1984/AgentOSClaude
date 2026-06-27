"""Performance profiling for the synthesis stage.

Design note on concurrency: workers never mutate shared metric state. Each
worker returns its own ChunkMetric; the ThreadPoolExecutor join is a
happens-before barrier, so the main thread aggregates single-threaded and
race-free. Peak RSS/CPU (not derivable from per-chunk returns) are collected by
a single ResourceSampler thread that writes only to its own locals and is read
after join().
"""
import json
import os
import platform
import threading
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any

PROFILE_SCHEMA_VERSION = "1.0"


@dataclass
class ChunkMetric:
    chunk_id: int
    thread_id: int
    wall_time_sec: float
    audio_sec: float
    cache_hit: bool
    start_ts: float  # perf_counter at worker entry; orders cold vs steady chunks


class ResourceSampler(threading.Thread):
    """Polls process RSS/CPU on a fixed interval, tracking high-water marks.

    Single-writer by construction: only this thread mutates peak_*; the caller
    reads after stop()+join(). No locks required.
    """

    def __init__(self, interval_sec: float = 0.1):
        super().__init__(daemon=True)
        self.interval_sec = interval_sec
        self._stop_event = threading.Event()
        self.peak_rss_mb = 0.0
        self.peak_cpu_percent = 0.0
        self._proc: Any = None
        try:
            import psutil
            self._proc = psutil.Process(os.getpid())
            self._proc.cpu_percent(None)  # prime; first call always returns 0.0
        except Exception:
            self._proc = None

    def run(self):
        if self._proc is None:
            return
        while not self._stop_event.is_set():
            try:
                mem = self._proc.memory_info()
                peak_bytes = getattr(mem, "peak_wset", None)
                if peak_bytes is None:
                    peak_bytes = mem.rss
                rss_mb = peak_bytes / (1024 * 1024)
                self.peak_rss_mb = max(self.peak_rss_mb, rss_mb)
                self.peak_cpu_percent = max(self.peak_cpu_percent, self._proc.cpu_percent(None))
            except Exception:
                pass
            self._stop_event.wait(self.interval_sec)

    def stop(self):
        self._stop_event.set()


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def collect_environment(model_path: Optional[str] = None,
                        include_model_checksum: bool = True) -> Dict[str, Any]:
    """Capture enough metadata to explain a benchmark difference months later."""
    env: Dict[str, Any] = {
        "python": platform.python_version(),
        "os": platform.platform(),
        "cpu": _safe(platform.processor, "unknown") or "unknown",
        "onnxruntime": _safe(lambda: __import__("onnxruntime").__version__),
        "kokoro_onnx": _safe(lambda: __import__("kokoro_onnx").__version__),
        "git_commit": _safe(lambda: __import__("subprocess").check_output(
            ["git", "rev-parse", "HEAD"], stderr=__import__("subprocess").DEVNULL
        ).decode().strip()),
    }
    if include_model_checksum and model_path and Path(model_path).is_file():
        env["model_sha256"] = _safe(lambda: _sha256_file(model_path))
    return env


def _sha256_file(path: str) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def build_performance_profile(
    engine_info: Dict[str, Any],
    cold_start_warmup_ms: float,
    session_reused: bool,
    chunk_metrics: List[ChunkMetric],
    synth_wall_sec: float,
    peak_rss_mb: float,
    peak_cpu_percent: float,
    worker_count: int,
    environment: Dict[str, Any],
    benchmark: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    total_chunks = len(chunk_metrics)
    hits = [m for m in chunk_metrics if m.cache_hit]
    misses = [m for m in chunk_metrics if not m.cache_hit]
    total_audio_sec = round(sum(m.audio_sec for m in chunk_metrics), 3)

    # Stage-level throughput RTF: wall clock of the whole (concurrent) phase
    # over the total audio produced. Accounts for parallelism correctly.
    rtf = round(synth_wall_sec / total_audio_sec, 4) if total_audio_sec > 0 else None

    # Per-chunk RTF is serial within a thread, so it's meaningful to average.
    # Use misses only (cache hits have ~0 synth time and would skew it low).
    per_chunk_rtf = [m.wall_time_sec / m.audio_sec for m in misses if m.audio_sec > 0]
    average_chunk_rtf = round(sum(per_chunk_rtf) / len(per_chunk_rtf), 4) if per_chunk_rtf else None

    # Steady-state excludes the earliest-starting miss (absorbs residual warmup).
    first_chunk_latency_ms = None
    steady_state_rtf = None
    if misses:
        first = min(misses, key=lambda m: m.start_ts)
        first_chunk_latency_ms = round(first.wall_time_sec * 1000, 1)
        steady = [m.wall_time_sec / m.audio_sec for m in misses
                  if m is not first and m.audio_sec > 0]
        steady_state_rtf = round(sum(steady) / len(steady), 4) if steady else None

    # Per-worker distribution — bucket thread ids into stable worker_N labels.
    by_thread: Dict[int, List[ChunkMetric]] = {}
    for m in chunk_metrics:
        by_thread.setdefault(m.thread_id, []).append(m)
    distribution = {}
    for i, tid in enumerate(sorted(by_thread)):
        ms = by_thread[tid]
        distribution[f"worker_{i}"] = {
            "chunks": len(ms),
            "audio_sec": round(sum(x.audio_sec for x in ms), 3),
            "wall_time_sec": round(sum(x.wall_time_sec for x in ms), 3),
            "cache_hits": sum(1 for x in ms if x.cache_hit),
        }

    # Load-balance score: how evenly chunks spread across the workers that ran.
    import statistics
    counts = [len(ms) for ms in by_thread.values()]
    load_balance = {
        "active_workers": len(counts),
        "mean_chunks_per_worker": round(statistics.mean(counts), 2) if counts else None,
        "stddev_chunks_per_worker": round(statistics.pstdev(counts), 2) if len(counts) > 1 else 0.0,
        "max_min_ratio": round(max(counts) / min(counts), 2) if counts and min(counts) > 0 else None,
    }

    cache_total = len(hits) + len(misses)
    cache_hit_ratio = round(len(hits) / cache_total, 3) if cache_total else None

    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "benchmark": benchmark or {"tier": None, "corpus": None, "generator_version": None},
        "engine": engine_info,
        "startup": {
            "cold_start_warmup_ms": round(cold_start_warmup_ms, 1),
            "first_chunk_latency_ms": first_chunk_latency_ms,
            "session_reused": session_reused,
        },
        "synthesis": {
            "chunks": total_chunks,
            "cache_hits": len(hits),
            "cache_misses": len(misses),
            "total_audio_sec": total_audio_sec,
            "wall_time_sec": round(synth_wall_sec, 3),
            "rtf": rtf,
            "average_chunk_rtf": average_chunk_rtf,
            "steady_state_rtf": steady_state_rtf,
            "cache_hit_ratio": cache_hit_ratio,
        },
        "resources": {
            "peak_rss_mb": round(peak_rss_mb, 1),
            "peak_cpu_percent": round(peak_cpu_percent, 1),
        },
        "workers": {
            "count": worker_count,
            "load_balance": load_balance,
            "distribution": distribution,
        },
        "environment": environment,
    }


def write_performance_profile(metrics_dir: str, profile: Dict[str, Any]) -> str:
    path = Path(metrics_dir)
    path.mkdir(parents=True, exist_ok=True)
    out = path / "performance_profile.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    return str(out)


def append_execution_history(metrics_dir: str, profile: Dict[str, Any]) -> str:
    """Append one compact summary object per run for trend analysis."""
    path = Path(metrics_dir)
    path.mkdir(parents=True, exist_ok=True)
    out = path / "execution_history.json"

    syn = profile["synthesis"]
    cache_total = syn["cache_hits"] + syn["cache_misses"]
    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "git_commit": profile["environment"].get("git_commit"),
        "engine": profile["engine"].get("name"),
        "provider": profile["engine"].get("provider"),
        "rtf": syn["rtf"],
        "warmup_ms": profile["startup"]["cold_start_warmup_ms"],
        "peak_rss_mb": profile["resources"]["peak_rss_mb"],
        "cache_hit_ratio": round(syn["cache_hits"] / cache_total, 3) if cache_total else None,
    }

    history: List[Any] = []
    if out.is_file():
        history = _safe(lambda: json.load(open(out, encoding="utf-8")), []) or []
    history.append(summary)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    return str(out)

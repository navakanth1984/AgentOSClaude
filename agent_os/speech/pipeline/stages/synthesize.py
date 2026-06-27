import json
import concurrent.futures
import threading
from dataclasses import replace
from time import perf_counter
from typing import Any, Dict, List, Tuple
from pathlib import Path

from agent_os.speech.schema.models import ExecutionPlanEntry
from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.pipeline.interfaces import TTSEngine
from agent_os.speech.pipeline.profiling import (
    ChunkMetric, ResourceSampler, collect_environment,
    build_performance_profile, write_performance_profile, append_execution_history,
)


class SynthesizeStage:
    """
    Execution engine for TTS synthesis.
    Acts as a 'boring executor': reads plan, synthesizes missing chunks in parallel, writes audio.

    Emits a deterministic performance_profile.json side-artifact (see profiling.py).
    The volatile metrics are written to disk only; the stage output returns the
    stable file path so downstream fingerprints stay deterministic.
    """

    def name(self) -> str:
        return "synthesize"

    def run(self, context: StageContext, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inputs:
            inputs["route"]["execution_plan"]: List[ExecutionPlanEntry]
        Context:
            context.config["tts_engine"]: Instance of TTSEngine
            context.config["max_workers"]: int
            context.config["profile_model_checksum"]: bool (default True)
        """
        from agent_os.speech.schema.models import ensure_execution_plan
        execution_plan: List[ExecutionPlanEntry] = ensure_execution_plan(inputs["route"]["execution_plan"])

        # 1. Setup Engine
        engine: TTSEngine = context.config["tts_engine"]
        max_workers = context.config.get("max_workers", 4)

        # Ensure cache directory exists
        Path(context.cache_dir).mkdir(parents=True, exist_ok=True)

        # Concurrency locks (serialize writes to the *same* cache file only)
        cache_locks = {}
        locks_lock = threading.Lock()

        import scipy.io.wavfile as wavfile
        import soundfile as sf

        # Resource sampler runs for the whole stage (model load + synthesis) so it
        # captures the true RSS high-water mark, which often occurs during warmup.
        sampler = ResourceSampler(interval_sec=0.1)
        sampler.start()

        # Engine lifecycle — isolate cold-start (graph compilation) cost.
        session_reused = getattr(engine, "kokoro", None) is not None
        engine.initialize()
        engine.validate_model()
        warm_t0 = perf_counter()
        engine.warmup()
        cold_start_warmup_ms = (perf_counter() - warm_t0) * 1000.0

        def is_valid_cache(path: Path) -> bool:
            if not path.exists():
                return False
            if path.stat().st_size == 0:
                return False
            try:
                info = sf.info(str(path))
                if info.frames <= 0 or info.samplerate <= 0:
                    return False
                return True
            except Exception:
                return False

        def process_chunk(entry: ExecutionPlanEntry) -> Tuple[ExecutionPlanEntry, ChunkMetric]:
            start_ts = perf_counter()
            tid = threading.get_ident()
            output_path = Path(entry.expected_output_path)

            def metric(audio_sec: float, cache_hit: bool) -> ChunkMetric:
                return ChunkMetric(
                    chunk_id=entry.chunk_id, thread_id=tid,
                    wall_time_sec=perf_counter() - start_ts,
                    audio_sec=audio_sec, cache_hit=cache_hit, start_ts=start_ts,
                )

            with locks_lock:
                if entry.cache_key not in cache_locks:
                    cache_locks[entry.cache_key] = threading.Lock()
                chunk_lock = cache_locks[entry.cache_key]

            with chunk_lock:
                # Cache hit?
                if is_valid_cache(output_path):
                    audio_sec = 0.0
                    try:
                        audio_sec = sf.info(str(output_path)).duration
                    except Exception:
                        pass
                    return replace(entry, status="completed"), metric(audio_sec, True)

                # Synthesis with retry
                retries = 2
                for attempt in range(retries + 1):
                    try:
                        sample_rate, audio_array = engine.synthesize(
                            text=entry.text,
                            voice=entry.voice,
                            speed=entry.speed,
                            language=entry.language,
                        )
                        wavfile.write(str(output_path), sample_rate, audio_array)
                        audio_sec = len(audio_array) / sample_rate if sample_rate else 0.0
                        return replace(entry, status="completed"), metric(audio_sec, False)
                    except Exception as e:
                        if attempt == retries:
                            print(f"Failed to synthesize chunk {entry.chunk_id}: {e}")
                            return replace(entry, status="failed"), metric(0.0, False)
                # Defensive: the loop always returns above, but make it explicit.
                return replace(entry, status="failed"), metric(0.0, False)

        # Parallel execution. map() returns in submission order; the join below is a
        # happens-before barrier, so all aggregation happens single-threaded.
        synth_t0 = perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            pairs = list(pool.map(process_chunk, execution_plan))
        synth_wall_sec = perf_counter() - synth_t0

        results: List[ExecutionPlanEntry] = [p[0] for p in pairs]
        chunk_metrics: List[ChunkMetric] = [p[1] for p in pairs]

        sampler.stop()
        sampler.join(timeout=1.0)

        # Determine overall status
        failed_chunks = [r.chunk_id for r in results if r.status == "failed"]
        if failed_chunks:
            raise RuntimeError(f"Synthesis failed for chunks: {failed_chunks}")
        overall_status = "success"

        synthesized_raw = {
            "status": overall_status,
            "failed_chunks": failed_chunks,
            "chunks": [
                {
                    "chunk_id": r.chunk_id,
                    "chapter_id": r.chapter_id,
                    "engine": r.engine,
                    "voice": r.voice,
                    "cache_key": r.cache_key,
                    "expected_output_path": r.expected_output_path,
                    "status": r.status,
                }
                for r in results
            ],
        }

        # --- Performance profile (best-effort; never fail synthesis over telemetry) ---
        profile_path = None
        try:
            eng_field = execution_plan[0].engine if execution_plan else None
            engine_info = {
                "name": getattr(eng_field, "value", eng_field) or "unknown",
                "version": _engine_version(engine),
                "provider": getattr(engine, "active_provider", "unknown"),
            }
            environment = collect_environment(
                model_path=str(getattr(engine, "model_path", "") or ""),
                include_model_checksum=context.config.get("profile_model_checksum", True),
            )
            profile = build_performance_profile(
                engine_info=engine_info,
                cold_start_warmup_ms=cold_start_warmup_ms,
                session_reused=session_reused,
                chunk_metrics=chunk_metrics,
                synth_wall_sec=synth_wall_sec,
                peak_rss_mb=sampler.peak_rss_mb,
                peak_cpu_percent=sampler.peak_cpu_percent,
                worker_count=max_workers,
                environment=environment,
                benchmark=context.config.get("benchmark"),
            )
            metrics_dir = str(Path(context.project_dir) / "metrics")
            profile_path = write_performance_profile(metrics_dir, profile)
            append_execution_history(metrics_dir, profile)
        except Exception as e:
            print(f"[SynthesizeStage] Profiling failed (non-fatal): {e}")

        # Shutdown engine
        engine.shutdown()

        return {
            "execution_plan": results,
            "synthesized_raw": json.dumps(synthesized_raw, indent=2),
            # Stable path only — volatile metrics live on disk, keeping downstream
            # (trim/merge) fingerprints deterministic.
            "performance_profile": profile_path,
        }


def _engine_version(engine) -> str:
    """Best-effort engine version, e.g. parse 'kokoro-v0_19.onnx' -> '0.19'."""
    import re
    name = str(getattr(getattr(engine, "model_path", ""), "name", "") or "")
    m = re.search(r"v(\d+)[._](\d+)", name)
    return f"{m.group(1)}.{m.group(2)}" if m else "unknown"

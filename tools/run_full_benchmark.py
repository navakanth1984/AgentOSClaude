"""Full-pipeline benchmark: corpus -> BenchmarkParser -> Segment -> ... -> Merge.

Deterministic input (BenchmarkParser, no LLM), real execution engine. Emits the
standard performance_profile.json via SynthesizeStage. Reusable for the worker
sweep by varying --workers.

Usage:
    python tools/run_full_benchmark.py --tier medium --workers 2
    python tools/run_full_benchmark.py --tier smoke --workers 1 --engine dummy
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_os.speech.pipeline.executor import Executor, StageContext
from agent_os.speech.pipeline.graph import DAG
from agent_os.speech.pipeline.stages.normalize import NormalizeStage
from agent_os.speech.pipeline.stages.parse import ParseStage
from agent_os.speech.pipeline.stages.segment import SegmentStage
from agent_os.speech.pipeline.stages.context import ContextStage
from agent_os.speech.pipeline.stages.route import RouteStage
from agent_os.speech.pipeline.stages.synthesize import SynthesizeStage
from agent_os.speech.pipeline.stages.trim import TrimStage
from agent_os.speech.pipeline.stages.merge import MergeStage
from agent_os.speech.schema.models import EngineCapabilities, EngineName, Language


def _dummy_engine_and_caps():
    import numpy as np

    class DummyEngine:
        kokoro = None
        active_provider = "DummyProvider"
        def initialize(self): pass
        def validate_model(self): pass
        def warmup(self): pass
        def shutdown(self): pass
        def synthesize(self, text, voice, speed, language):
            return 24000, np.zeros(24000, dtype=np.int16)

    caps = EngineCapabilities(
        engine_name=EngineName.KOKORO, supported_languages=[Language.EN],
        supported_voices={"af": {"gender": "unknown"}}, supports_emotions=False,
    )
    return DummyEngine(), caps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="medium")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--engine", choices=["kokoro", "dummy"], default="kokoro")
    args = ap.parse_args()

    corpus_path = Path("corpus") / args.tier / "chapter.txt"
    if not corpus_path.is_file():
        raise SystemExit(f"corpus not found: {corpus_path} (run generate_benchmark_corpus.py --tier {args.tier})")

    project_dir = os.path.abspath(f"corpus_output_bench/{args.tier}_w{args.workers}_{args.engine}")
    cache_dir = os.path.join(project_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)

    if args.engine == "kokoro":
        from agent_os.speech.engines.kokoro_engine import KokoroEngine
        engine = KokoroEngine()
        engine.validate_model()
        capabilities = engine.get_capabilities()
    else:
        engine, capabilities = _dummy_engine_and_caps()

    config = {
        "input_path": str(corpus_path),
        "chapter_id": args.tier,
        "parser": "benchmark",
        "benchmark": {"tier": args.tier, "corpus": "chapter.txt", "generator_version": "1.0"},
        "engine_capabilities": capabilities,
        "tts_engine": engine,
        "max_workers": args.workers,
        "profile_model_checksum": False,  # keep sweep iterations fast
    }
    ctx = StageContext(project_dir=project_dir, cache_dir=cache_dir, config=config, artifacts={}, metrics={})

    dag = DAG()
    dag.add_node("normalize", NormalizeStage())
    dag.add_node("parse", ParseStage(), depends_on=["normalize"])
    dag.add_node("segment", SegmentStage(), depends_on=["parse"])
    dag.add_node("context", ContextStage(), depends_on=["segment"])
    dag.add_node("route", RouteStage(), depends_on=["context", "parse"])
    dag.add_node("synthesize", SynthesizeStage(), depends_on=["route"])
    dag.add_node("trim", TrimStage(), depends_on=["synthesize"])
    dag.add_node("merge", MergeStage(), depends_on=["trim"])

    print(f"=== Full benchmark: tier={args.tier} workers={args.workers} engine={args.engine} ===")
    t0 = time.perf_counter()
    Executor(dag, ctx).run()
    wall = time.perf_counter() - t0

    profile_path = Path(project_dir) / "metrics" / "performance_profile.json"
    if profile_path.is_file():
        p = json.load(open(profile_path, encoding="utf-8"))
        syn = p["synthesis"]; lb = p["workers"]["load_balance"]
        print("\n--- Profile summary ---")
        print(f"chunks={syn['chunks']} hits={syn['cache_hits']} misses={syn['cache_misses']} "
              f"hit_ratio={syn['cache_hit_ratio']}")
        print(f"stage_rtf={syn['rtf']} avg_chunk_rtf={syn['average_chunk_rtf']} "
              f"steady_state_rtf={syn['steady_state_rtf']}")
        print(f"warmup_ms={p['startup']['cold_start_warmup_ms']} "
              f"first_chunk_ms={p['startup']['first_chunk_latency_ms']}")
        print(f"peak_rss_mb={p['resources']['peak_rss_mb']} active_workers={lb['active_workers']} "
              f"load_balance(max/min)={lb['max_min_ratio']} stddev={lb['stddev_chunks_per_worker']}")
        print(f"total pipeline wall={wall:.2f}s; profile at {profile_path}")
    else:
        print("No profile produced (synthesize may have been a cache hit).")


if __name__ == "__main__":
    main()

import os
import json
import numpy as np
from typing import Tuple
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
from agent_os.speech.pipeline.interfaces import TTSEngine
from agent_os.speech.schema.models import EngineCapabilities

from agent_os.speech.engines.kokoro_engine import KokoroEngine
import time
import psutil

def run_acceptance_test():
    project_dir = os.path.abspath("corpus_output_kokoro")
    os.makedirs(project_dir, exist_ok=True)
    cache_dir = os.path.join(project_dir, "cache")
    
    with open("corpus/chapter_1.txt", "r", encoding="utf-8") as f:
        text = f.read()

    print("Initializing TTS Engine...")
    engine = KokoroEngine()
    engine.validate_model()
    engine.warmup()
    capabilities = engine.get_capabilities()

    config = {
        "input_text": text,
        "chapter_id": "chapter_1",
        "engine_capabilities": capabilities,
        "tts_engine": engine,
        "max_workers": 2,
        "benchmark": {"tier": "smoke", "corpus": "chapter_1.txt", "generator_version": None},
    }

    context = StageContext(
        project_dir=project_dir,
        cache_dir=cache_dir,
        config=config,
        artifacts={},
        metrics={}
    )

    dag = DAG()
    dag.add_node("normalize", NormalizeStage())
    dag.add_node("parse", ParseStage(), depends_on=["normalize"])
    dag.add_node("segment", SegmentStage(), depends_on=["parse"])
    dag.add_node("context", ContextStage(), depends_on=["segment"])
    dag.add_node("route", RouteStage(), depends_on=["context", "parse"])
    dag.add_node("synthesize", SynthesizeStage(), depends_on=["route"])
    dag.add_node("trim", TrimStage(), depends_on=["synthesize"])
    dag.add_node("merge", MergeStage(), depends_on=["trim"])

    print("\n--- Starting V1 Acceptance Test Pipeline ---")
    t0 = time.time()
    executor = Executor(dag, context)
    executor.run()
    t1 = time.time()
    
    total_time = t1 - t0
    
    mem = psutil.Process(os.getpid()).memory_info()
    # peak_wset is Windows-only; fall back to RSS on POSIX platforms.
    peak_bytes = getattr(mem, "peak_wset", None)
    if peak_bytes is None:
        peak_bytes = mem.rss
    peak_ram = peak_bytes / (1024 * 1024)

    print("\n--- Pipeline Execution Complete ---")
    merge_output = context.artifacts.get("merge", {})
    if "merged_manifest" in merge_output:
        print(f"Success! Final audio saved. Manifest:\n{merge_output['merged_manifest']}")
        # Calculate RTF (Real-Time Factor)
        import wave
        import json
        manifest_list = json.loads(merge_output["merged_manifest"])
        final_wav = manifest_list[0]["output_path"]
        with wave.open(final_wav, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
            
        rtf = total_time / duration if duration > 0 else 0
        print(f"\n--- Profiling ---")
        print(f"Total execution time: {total_time:.2f} s")
        print(f"Total audio duration: {duration:.2f} s")
        print(f"Real-Time Factor (RTF): {rtf:.3f} (Time per second of audio)")
        print(f"Peak RAM: {peak_ram:.2f} MB")
        
    else:
        print("Failed to produce final audio.")

if __name__ == "__main__":
    run_acceptance_test()

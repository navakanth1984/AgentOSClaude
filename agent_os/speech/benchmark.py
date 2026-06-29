import time
import os
import psutil
import tempfile
from pathlib import Path

from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.pipeline.stages.synthesize import SynthesizeStage
from agent_os.speech.schema.models import ExecutionPlanEntry, EngineName, Language
import soundfile as sf

class DummyEngineForBenchmarking:
    """Mock engine just to test benchmark harness overhead without Kokoro blocking."""
    def validate_model(self): pass
    def initialize(self): pass
    def warmup(self): pass
    def shutdown(self): pass
    def synthesize(self, text, voice, speed, language):
        import numpy as np
        # 1 second of audio at 24kHz
        return 24000, np.zeros(24000, dtype=np.int16)

def run_benchmark():
    print("=======================================")
    print(" Agent OS Speech Benchmark Harness")
    print("=======================================")
    
    # Check if psutil is available for metrics
    process = psutil.Process(os.getpid())
    
    # We will use DummyTTSEngine if Kokoro isn't available, but let's try Kokoro first.
    try:
        from agent_os.speech.engines.kokoro_engine import KokoroEngine
        engine = KokoroEngine()
        engine.validate_model()
        engine_provider = lambda name: KokoroEngine()
        print("Engine: Kokoro TTS")
    except Exception as e:
        print(f"Engine: Mock (Kokoro not available: {e})")
        engine_provider = lambda name: DummyEngineForBenchmarking()
        
    num_chunks = 10
    print(f"Target chunks: {num_chunks}")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        plan = []
        for i in range(num_chunks):
            plan.append(ExecutionPlanEntry(
                chunk_id=i,
                chapter_id="benchmark",
                text=f"This is test sentence number {i} for benchmarking the synthesis engine.",
                engine=EngineName.KOKORO,
                voice="af_heart",
                language=Language.EN,
                speed=1.0,
                pitch=1.0,
                volume_gain_db=0.0,
                cache_key=f"bench_chunk_{i}",
                expected_output_path=str(Path(tmp_dir) / f"bench_chunk_{i}.wav"),
                pause_before_ms=0,
                pause_after_ms=0,
                status="pending"
            ))
            
        ctx = StageContext(project_dir=tmp_dir, cache_dir=tmp_dir, config={"tts_engine": engine_provider("mock"), "max_workers": 4}, artifacts={}, metrics={})
        ctx.artifacts["route"] = {"execution_plan": plan}
        
        stage = SynthesizeStage()
        
        mem_before = process.memory_info().rss / (1024 * 1024)
        
        # We also want to measure time to first chunk (latency).
        # SynthesizeStage currently returns all chunks at once.
        # For true latency, we would hook into the executor, but for this benchmark,
        # we'll measure the overall stage time.
        
        start_time = time.perf_counter()
        
        result = stage.run(ctx, ctx.artifacts)
        
        end_time = time.perf_counter()
        
        mem_after = process.memory_info().rss / (1024 * 1024)
        
        total_time = end_time - start_time
        
        # Calculate Audio Duration
        total_audio_sec = 0.0
        for entry in result["execution_plan"]:
            try:
                data, sr = sf.read(entry.expected_output_path)
                total_audio_sec += len(data) / sr
            except Exception:
                pass
                
        rtf = total_time / total_audio_sec if total_audio_sec > 0 else 0
        throughput = num_chunks / total_time if total_time > 0 else 0
        
        print("\n--- Benchmark Results ---")
        print(f"Total time      : {total_time:.3f}s")
        print(f"Audio duration  : {total_audio_sec:.3f}s")
        print(f"RTF             : {rtf:.3f}x")
        print(f"Throughput      : {throughput:.2f} chunks/sec")
        print(f"Memory increase : {mem_after - mem_before:.2f} MB")
        print("=======================================")
        
        # Save results to JSON artifact
        results = {
            "timestamp": time.time(),
            "engine": engine.__class__.__name__ if 'engine' in locals() else "Mock",
            "num_chunks": num_chunks,
            "total_time_sec": total_time,
            "audio_duration_sec": total_audio_sec,
            "rtf": rtf,
            "throughput_chunks_per_sec": throughput,
            "memory_increase_mb": mem_after - mem_before
        }
        
        import json
        output_path = Path("benchmark_results.json")
        if output_path.exists():
            with open(output_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = []
            
        history.append(results)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
            
        print(f"Results saved to {output_path.absolute()}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run TTS engine benchmark")
    parser.add_argument("--engine", choices=["kokoro", "piper", "mock"], default="kokoro", help="Engine to test")
    parser.add_argument("--chunks", type=int, default=10, help="Number of chunks to synthesize")
    args = parser.parse_args()
    
    print("=======================================")
    print(" Agent OS Speech Benchmark Harness")
    print("=======================================")
    
    # Check if psutil is available for metrics
    process = psutil.Process(os.getpid())
    
    engine = None
    if args.engine == "piper":
        try:
            from agent_os.speech.engines.piper_engine import PiperEngine
            engine = PiperEngine()
            engine.validate_model()
            engine_provider = lambda name: PiperEngine()
            print("Engine: Piper TTS")
            engine_name = EngineName.PIPER
            voice_name = "default" # Use whatever is available
        except Exception as e:
            print(f"Engine: Mock (Piper not available: {e})")
            engine_provider = lambda name: DummyEngineForBenchmarking()
            engine_name = EngineName.PIPER
            voice_name = "default"
    elif args.engine == "kokoro":
        try:
            from agent_os.speech.engines.kokoro_engine import KokoroEngine
            engine = KokoroEngine()
            engine.validate_model()
            engine_provider = lambda name: KokoroEngine()
            print("Engine: Kokoro TTS")
            engine_name = EngineName.KOKORO
            voice_name = "af_heart"
        except Exception as e:
            print(f"Engine: Mock (Kokoro not available: {e})")
            engine_provider = lambda name: DummyEngineForBenchmarking()
            engine_name = EngineName.KOKORO
            voice_name = "af_heart"
    else:
        engine_provider = lambda name: DummyEngineForBenchmarking()
        print("Engine: Mock")
        engine_name = EngineName.GCP
        voice_name = "mock"
        
    num_chunks = args.chunks
    print(f"Target chunks: {num_chunks}")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        plan = []
        for i in range(num_chunks):
            plan.append(ExecutionPlanEntry(
                chunk_id=i,
                chapter_id="benchmark",
                text=f"This is test sentence number {i} for benchmarking the synthesis engine.",
                engine=engine_name,
                voice=voice_name,
                language=Language.EN,
                speed=1.0,
                pitch=1.0,
                volume_gain_db=0.0,
                cache_key=f"bench_chunk_{i}",
                expected_output_path=str(Path(tmp_dir) / f"bench_chunk_{i}.wav"),
                pause_before_ms=0,
                pause_after_ms=0,
                status="pending"
            ))
            
        ctx = StageContext(project_dir=tmp_dir, cache_dir=tmp_dir, config={"tts_engine": engine_provider("mock"), "max_workers": 4}, artifacts={}, metrics={})
        ctx.artifacts["route"] = {"execution_plan": plan}
        
        stage = SynthesizeStage()
        
        mem_before = process.memory_info().rss / (1024 * 1024)
        
        start_time = time.perf_counter()
        
        result = stage.run(ctx, ctx.artifacts)
        
        end_time = time.perf_counter()
        
        mem_after = process.memory_info().rss / (1024 * 1024)
        
        total_time = end_time - start_time
        
        # Calculate Audio Duration
        total_audio_sec = 0.0
        for entry in result["execution_plan"]:
            try:
                data, sr = sf.read(entry.expected_output_path)
                total_audio_sec += len(data) / sr
            except Exception:
                pass
                
        rtf = total_time / total_audio_sec if total_audio_sec > 0 else 0
        throughput = num_chunks / total_time if total_time > 0 else 0
        
        print("\n--- Benchmark Results ---")
        print(f"Total time      : {total_time:.3f}s")
        print(f"Audio duration  : {total_audio_sec:.3f}s")
        print(f"RTF             : {rtf:.3f}x")
        print(f"Throughput      : {throughput:.2f} chunks/sec")
        print(f"Memory increase : {mem_after - mem_before:.2f} MB")
        print("=======================================")
        
        # Save results to JSON artifact
        results = {
            "timestamp": time.time(),
            "engine": type(engine).__name__ if 'engine' in locals() and engine is not None else "Mock",
            "num_chunks": num_chunks,
            "total_time_sec": total_time,
            "audio_duration_sec": total_audio_sec,
            "rtf": rtf,
            "throughput_chunks_per_sec": throughput,
            "memory_increase_mb": mem_after - mem_before
        }
        
        import json
        output_path = Path("benchmark_results.json")
        if output_path.exists():
            with open(output_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = []
            
        history.append(results)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
            
        print(f"Results saved to {output_path.absolute()}")

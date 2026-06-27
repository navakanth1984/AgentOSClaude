import argparse
import sys
import time
from agent_os.speech.engines.kokoro_engine import KokoroEngine

def doctor_speech():
    print("Speech Engine Health")
    print("--------------------")
    
    engine = KokoroEngine()
    
    import re
    version = "unknown"
    try:
        m = re.search(r"v(\d+)[._](\d+)", "kokoro-v0_19.onnx") # fallback
        if getattr(engine, "model_path", None):
            m = re.search(r"v(\d+)[._](\d+)", engine.model_path.name)
        if m:
            version = f"{m.group(1)}.{m.group(2)}"
    except Exception:
        pass

    print("Engine:")
    print("  Kokoro ONNX")
    print(f"  Version: {version}")
    
    print("\nModel:")
    try:
        engine.validate_model()
        print(f"  {engine.model_path.name} (OK Found)")
        from agent_os.speech.pipeline.profiling import _sha256_file
        print(f"  Checksum: {_sha256_file(str(engine.model_path))}")
    except Exception as e:
        print(f"  [ERROR] {e}")
        print("\nStatus:\n  FAILED")
        return
        
    capabilities = engine.get_capabilities()
    
    print("\nLanguages:")
    langs = [lang.value if hasattr(lang, "value") else str(lang) for lang in capabilities.supported_languages]
    print(f"  {', '.join(langs)}")
    
    print("\nSample Rate:")
    print(f"  {capabilities.sample_rate} Hz")
    
    print("\nVoices:")
    num_voices = len(capabilities.supported_voices)
    print(f"  {num_voices} detected (OK Found)")
    
    print("\nWarmup:")
    t0 = time.time()
    try:
        engine.warmup()
        t1 = time.time()
        print(f"  PASS ({(t1-t0)*1000:.0f} ms)")
    except Exception as e:
        print(f"  [ERROR] {e}")
        print("\nStatus:\n  FAILED")
        return
        
    print("\nProvider:")
    print(f"  {engine.active_provider}")
        
    print("\nInference:")
    try:
        voices = list(capabilities.supported_voices.keys())
        voice = voices[0] if voices else "af"
        _, audio = engine.synthesize("Hello world.", voice, 1.0, "en")
        if len(audio) > 0:
            print("  PASS")
        else:
            print("  FAILED (Empty audio)")
    except Exception as e:
        print(f"  [ERROR] {e}")
        print("\nStatus:\n  FAILED")
        return
        
    print("\nRecommendation:")
    import os
    import platform
    import hashlib
    cpu = os.cpu_count() or 1
    # Ensure platform matches collect_environment
    env_str = f"{platform.platform()}-{platform.processor() or 'unknown'}-{cpu}"
    env_hash = hashlib.sha256(env_str.encode()).hexdigest()[:12]
    print(f"  Environment Hash: {env_hash}")
    import json
    from pathlib import Path
    rec_file = Path("benchmark_results/thread_matrix_medium_kokoro.json")
    if rec_file.is_file():
        try:
            data = json.load(open(rec_file, encoding="utf-8"))
            rec = data.get("recommendation", {})
            if rec and rec.get("environment_hash") == env_hash:
                print(f"  [Measured] Use {rec['workers']} workers, {rec['ort_intra_threads']} intra-op threads")
            else:
                print("  [Note] Benchmark recommendation exists but for a different environment.")
        except Exception:
            pass
    else:
        print("  Run `python tools/aggregate_matrix.py` on your grid to generate hardware-specific tuning.")

    print("\nStatus:")
    print("  READY")

def main():
    parser = argparse.ArgumentParser(description="Agent OS CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # benchmark command
    benchmark_parser = subparsers.add_parser("benchmark", help="Run benchmarks")
    benchmark_parser.add_argument("target", choices=["speech"], help="Benchmark target")
    
    # doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Run health checks")
    doctor_parser.add_argument("target", choices=["speech"], help="Health check target")
    
    args = parser.parse_args()
    
    if args.command == "benchmark":
        if args.target == "speech":
            from agent_os.speech.benchmark import run_benchmark
            run_benchmark()
        else:
            print(f"Unknown benchmark target: {args.target}")
            return 1
    elif args.command == "doctor":
        if args.target == "speech":
            doctor_speech()
        else:
            print(f"Unknown doctor target: {args.target}")
            return 1
    else:
        parser.print_help()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())

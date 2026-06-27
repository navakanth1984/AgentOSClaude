"""Tests for SynthesizeStage performance instrumentation (no real TTS engine)."""
import json
import os
import tempfile
from pathlib import Path

import numpy as np

from agent_os.speech.schema.models import ExecutionPlanEntry, EngineName, Language
from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.pipeline.stages.synthesize import SynthesizeStage


class FakeEngine:
    """Minimal TTSEngine: 1.0s of silence per call, tracks call count."""
    def __init__(self):
        self.kokoro = None
        self.active_provider = "CPUExecutionProvider"
        self.model_path = Path("kokoro-v0_19.onnx")
        self.synth_calls = 0

    def initialize(self): pass
    def validate_model(self): pass
    def warmup(self): self.kokoro = object()
    def shutdown(self): pass

    def synthesize(self, text, voice, speed, language):
        self.synth_calls += 1
        return 24000, np.zeros(24000, dtype=np.int16)  # 1.0 sec


def _plan(cache_dir, n=8):
    plan = []
    for i in range(n):
        key = f"k{i}"
        plan.append(ExecutionPlanEntry(
            chunk_id=i, chapter_id="c1", text=f"line {i}.", engine=EngineName.KOKORO,
            voice="af", language=Language.EN, speed=1.0, pitch=1.0, volume_gain_db=0.0,
            cache_key=key, expected_output_path=str(Path(cache_dir) / f"{key}.wav"),
            pause_before_ms=0, pause_after_ms=0, status="pending",
        ))
    return plan


def _ctx(project_dir, cache_dir, engine, workers=4):
    return StageContext(
        project_dir=project_dir, cache_dir=cache_dir,
        config={"tts_engine": engine, "max_workers": workers,
                "profile_model_checksum": False},  # keep test fast
        artifacts={}, metrics={},
    )


def main():
    d = tempfile.mkdtemp(prefix="perf_profile_test_")
    cache_dir = os.path.join(d, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    metrics_dir = Path(d) / "metrics"

    engine = FakeEngine()
    plan = _plan(cache_dir, n=8)

    # ---- COLD run: everything synthesized ----
    out1 = SynthesizeStage().run(_ctx(d, cache_dir, engine), {"route": {"execution_plan": plan}})
    prof = json.load(open(metrics_dir / "performance_profile.json", encoding="utf-8"))

    assert prof["schema_version"] == "1.0"
    assert prof["synthesis"]["chunks"] == 8
    assert prof["synthesis"]["cache_misses"] == 8 and prof["synthesis"]["cache_hits"] == 0
    assert prof["synthesis"]["total_audio_sec"] == 8.0
    assert prof["startup"]["cold_start_warmup_ms"] is not None
    assert prof["startup"]["session_reused"] is False
    assert prof["engine"]["version"] == "0.19"
    # race-free aggregation: per-worker chunk counts must sum to the total
    dist = prof["workers"]["distribution"]
    assert sum(w["chunks"] for w in dist.values()) == 8, dist
    print(f"[PASS] cold profile: rtf={prof['synthesis']['rtf']} "
          f"avg_chunk_rtf={prof['synthesis']['average_chunk_rtf']} "
          f"workers={len(dist)} warmup_ms={prof['startup']['cold_start_warmup_ms']}")

    # ---- WARM run: same plan, wavs already on disk -> all cache hits ----
    engine2 = FakeEngine()
    out2 = SynthesizeStage().run(_ctx(d, cache_dir, engine2), {"route": {"execution_plan": plan}})
    prof2 = json.load(open(metrics_dir / "performance_profile.json", encoding="utf-8"))
    assert prof2["synthesis"]["cache_hits"] == 8, prof2["synthesis"]
    assert engine2.synth_calls == 0, "warm run should not synthesize"
    print(f"[PASS] warm profile: cache_hits={prof2['synthesis']['cache_hits']} "
          f"synth_calls={engine2.synth_calls}")

    # ---- execution_history appends one object per run ----
    history = json.load(open(metrics_dir / "execution_history.json", encoding="utf-8"))
    assert len(history) == 2, f"expected 2 history entries, got {len(history)}"
    assert "cache_hit_ratio" in history[-1]
    print(f"[PASS] execution_history grew to {len(history)} entries; last={history[-1]['cache_hit_ratio']=}")

    # ---- downstream fingerprint stability: returned profile path is identical ----
    assert out1["performance_profile"] == out2["performance_profile"], "profile path must be stable"
    assert out1["performance_profile"].endswith("performance_profile.json")
    print("[PASS] performance_profile path is stable across runs (deterministic downstream input)")

    print("\nAll performance-profile tests passed.")


if __name__ == "__main__":
    main()

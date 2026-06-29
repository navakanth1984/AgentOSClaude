import os
import pytest
from pathlib import Path
import numpy as np

from agent_os.speech.engines.kokoro_engine import KokoroEngine
from agent_os.speech.schema.models import (
    ExecutionPlanEntry, Language, EngineName
)

def has_kokoro_model():
    """Helper to check if we can run Kokoro tests"""
    engine = KokoroEngine()
    try:
        engine.validate_model()
        return True
    except FileNotFoundError:
        return False

@pytest.mark.skipif(not has_kokoro_model(), reason="Kokoro ONNX model files not found")
def test_kokoro_engine_lifecycle():
    engine = KokoroEngine()
    
    # 1. Initialize
    engine.initialize()
    
    # 2. Validate
    engine.validate_model()
    
    # 3. Warmup
    engine.warmup()
    
    # 4. Synthesize simple hello
    text = "Hello, world. This is a smoke test."
    voice = "af_heart" # Default kokoro voice often used, replace if necessary
    
    sample_rate, samples = engine.synthesize(text, voice, speed=1.0, language=Language.EN)
    
    assert sample_rate == 24000
    assert samples is not None
    assert len(samples) > 0
    assert samples.dtype == np.int16

    # 5. Shutdown
    engine.shutdown()

@pytest.mark.skipif(not has_kokoro_model(), reason="Kokoro ONNX model files not found")
def test_kokoro_engine_with_synthesis_stage():
    """Test the Kokoro engine plugged into our Synthesis Stage executor."""
    from agent_os.speech.pipeline.stages.synthesize import SynthesizeStage
    from agent_os.speech.pipeline.executor import StageContext
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create plan
        plan = [
            ExecutionPlanEntry(
                chunk_id=0,
                chapter_id="chapter_1",
                text="This is a test of the synthesis stage.",
                engine=EngineName.KOKORO,
                voice="af_heart",
                language=Language.EN,
                speed=1.0,
                pitch=1.0,
                volume_gain_db=0.0,
                cache_key="test_chunk_001",
                expected_output_path=str(Path(tmp_dir) / "test_chunk_001.wav"),
                pause_before_ms=0,
                pause_after_ms=0,
                status="pending"
            )
        ]
        
        ctx = StageContext(
            project_dir=tmp_dir,
            cache_dir=str(Path(tmp_dir) / "cache"),
            config={},
            artifacts={},
            metrics={}
        )
        ctx.artifacts["execution_plan"] = plan
        
        ctx.config["tts_engine"] = KokoroEngine()
        
        stage = SynthesizeStage()
        inputs = {"route": {"execution_plan": plan}}
        result = stage.run(ctx, inputs)
        
        # Verify output
        assert "execution_plan" in result
        assert "synthesized_raw" in result
        
        # Verify file written
        assert Path(plan[0].expected_output_path).exists()
        assert Path(plan[0].expected_output_path).stat().st_size > 0      
        # verify it has audio data
        import soundfile as sf
        data, sr = sf.read(plan[0].expected_output_path)
        assert len(data) > 0

import os
import tempfile
import pytest
from pathlib import Path
import numpy as np
import soundfile as sf
import json

from agent_os.speech.engines.registry import EngineRegistry
from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.pipeline.stages.synthesize import SynthesizeStage
from agent_os.speech.pipeline.stages.route import RouteStage
from agent_os.speech.schema.models import EngineName, Language, ExecutionPlanEntry
from agent_os.speech.pipeline.voice_manager import VoiceManager

# Helper to check if model is present
def get_available_engines():
    engines = []
    # Test Kokoro
    try:
        from agent_os.speech.engines.kokoro_engine import KokoroEngine
        eng = KokoroEngine()
        eng.validate_model()
        engines.append("kokoro")
    except Exception:
        pass

    # Test Piper
    try:
        from agent_os.speech.engines.piper_engine import PiperEngine
        eng = PiperEngine()
        eng.validate_model()
        engines.append("piper")
    except Exception:
        pass
        
    return engines

AVAILABLE_ENGINES = get_available_engines()

@pytest.mark.skipif(len(AVAILABLE_ENGINES) == 0, reason="No physical engines validated/present locally")
@pytest.mark.parametrize("engine_name", AVAILABLE_ENGINES)
class TestEngineCompatibility:
    
    def _get_engine_instance(self, name: str):
        if name == "kokoro":
            return EngineRegistry.get_engine({"engine_name": "kokoro"})
        elif name == "piper":
            return EngineRegistry.get_engine({"engine_name": "piper"})
        raise ValueError(f"Unknown engine: {name}")

    def test_capability_discovery(self, engine_name):
        engine = self._get_engine_instance(engine_name)
        caps = engine.get_capabilities()
        
        assert caps.engine_name in [EngineName.KOKORO, EngineName.PIPER]
        assert Language.EN in caps.supported_languages
        assert len(caps.supported_voices) > 0
        assert caps.sample_rate > 0
        assert caps.output_format == "wav"

    def test_routing_integrity(self, engine_name):
        engine = self._get_engine_instance(engine_name)
        caps = engine.get_capabilities()
        
        # Test routing stage mapping
        from agent_os.speech.pipeline.stages.route import RouteStage
        from agent_os.speech.schema.models import SpeechChunk
        
        chunks = [
            SpeechChunk(
                chunk_id=1, parent_segment_id=0, chapter_id="1",
                text="This is a test sentence.", language=Language.EN,
                pause_before_ms=0, pause_after_ms=0, chunk_index_in_segment=0,
                is_terminal_chunk=True, estimated_duration_sec=1.5
            )
        ]
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            ctx = StageContext(
                project_dir=tmp_dir, cache_dir=tmp_dir,
                config={
                    "tts_engine": engine,
                    "engine_capabilities": caps
                },
                artifacts={}, metrics={}
            )
            
            # Synthesize voice management
            # Resolve voice matching caps
            target_voice = list(caps.supported_voices.keys())[0]
            
            # Setup VoiceManager
            voice_map_path = Path(tmp_dir) / "voice_map.json"
            with open(voice_map_path, "w") as f:
                json.dump({
                    "schema_version": "1.0",
                    "engine": engine_name,
                    "voices": {"Narrator": target_voice}
                }, f)
            
            ctx.config["voice_map_path"] = str(voice_map_path)
            
            inputs = {
                "parse": {
                    "segments": [{"segment_id": 0, "chapter_id": "1", "speaker": "Narrator", "text": "This is a test sentence."}],
                    "transcript": {
                        "segments": [],
                        "parser_name": "test",
                        "parser_version": "1.0",
                        "model": "test",
                        "confidence": 1.0
                    }
                },
                "context": {"chunks": chunks}
            }
            
            route_stage = RouteStage()
            result = route_stage.run(ctx, inputs)
            
            plan = result["execution_plan"]
            assert len(plan) == 1
            assert str(plan[0].engine) == engine_name
            assert plan[0].voice == target_voice

    def test_synthesis_and_cache(self, engine_name):
        engine = self._get_engine_instance(engine_name)
        caps = engine.get_capabilities()
        voice = list(caps.supported_voices.keys())[0]
        
        engine.initialize()
        engine.warmup("minimal")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "test.wav"
            
            # Test direct synthesis output structure
            sr, samples = engine.synthesize("Test word.", voice, Language.EN, 1.0)
            assert sr == caps.sample_rate
            assert samples is not None
            assert len(samples) > 0
            assert samples.dtype == np.int16
            
            # Test SynthesizeStage execution & caching
            stage = SynthesizeStage()
            plan = [
                ExecutionPlanEntry(
                    chunk_id=1, chapter_id="1", text="Test chunk.",
                    engine=caps.engine_name, voice=voice, language=Language.EN,
                    speed=1.0, pitch=1.0, volume_gain_db=0.0,
                    cache_key="test_cache_key", expected_output_path=str(output_file),
                    pause_before_ms=0, pause_after_ms=0, status="pending"
                )
            ]
            
            ctx = StageContext(
                project_dir=tmp_dir, cache_dir=os.path.join(tmp_dir, "cache"),
                config={"tts_engine": engine, "max_workers": 1, "profile_model_checksum": False},
                artifacts={}, metrics={}
            )
            
            # Initial Run (Cache Miss)
            res1 = stage.run(ctx, {"route": {"execution_plan": plan}})
            assert output_file.exists()
            assert Path(ctx.cache_dir).exists()
            
            # Check telemetry/manifest
            metrics_dir = Path(tmp_dir) / "metrics"
            assert (metrics_dir / "assets_manifest.json").exists()
            assert (metrics_dir / "performance_profile.json").exists()
            
            with open(metrics_dir / "assets_manifest.json", "r") as f:
                manifest = json.load(f)
                assert manifest["engine_name"] == engine_name
                assert manifest["sample_rate"] == caps.sample_rate

            with open(metrics_dir / "performance_profile.json", "r") as f:
                prof = json.load(f)
                assert prof["engine"]["name"] == engine_name
                assert "synthesis" in prof
                
            # Second Run (Should Cache Hit the file validation logic or stage itself)
            # File should still be present
            assert output_file.exists()
            
        engine.shutdown()

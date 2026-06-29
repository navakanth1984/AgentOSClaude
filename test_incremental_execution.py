import os
import tempfile
import pytest
from pathlib import Path
import numpy as np
import soundfile as sf

from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.pipeline.graph import DAG
from agent_os.speech.pipeline.stages.normalize import NormalizeStage
from agent_os.speech.pipeline.stages.parse import ParseStage
from agent_os.speech.pipeline.stages.segment import SegmentStage
from agent_os.speech.pipeline.stages.context import ContextStage
from agent_os.speech.pipeline.stages.route import RouteStage
from agent_os.speech.pipeline.stages.synthesize import SynthesizeStage
from agent_os.speech.pipeline.stages.trim import TrimStage
from agent_os.speech.pipeline.stages.append import AppendStage
from agent_os.speech.pipeline.incremental_executor import IncrementalExecutor

from agent_os.speech.schema.models import EngineCapabilities, EngineName, Language
from agent_os.speech.pipeline.interfaces import TTSEngine

class FakeEngine(TTSEngine):
    def validate_model(self): pass
    def initialize(self): pass
    def warmup(self, profile="minimal"): pass
    def shutdown(self): pass
    def get_capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            engine_name=EngineName.KOKORO,
            supported_languages=[Language.EN],
            supported_voices={"af_heart": {}},
            max_text_length=500,
            max_concurrent_requests=1,
            supports_streaming=False,
            supports_emotions=False,
            supports_pitch=False,
            supports_speed=True,
            sample_rate=24000,
            output_format="wav"
        )
    def supports_language(self, language: Language) -> bool: return True
    def supports_voice(self, voice: str) -> bool: return True
    def synthesize(self, text: str, voice: str, language: Language, speed: float) -> tuple[int, np.ndarray]:
        # Generate 1/10 second of silent audio at 24kHz
        return 24000, np.zeros(2400, dtype=np.int16)

def test_incremental_execution_flow():
    with tempfile.TemporaryDirectory() as tmp_dir:
        project_dir = os.path.join(tmp_dir, "project")
        cache_dir = os.path.join(tmp_dir, "cache")
        os.makedirs(project_dir, exist_ok=True)
        
        text = "This is sentence one. This is sentence two. This is sentence three."
        
        engine = FakeEngine()
        capabilities = engine.get_capabilities()
        
        config = {
            "input_text": text,
            "chapter_id": "0",
            "engine_capabilities": capabilities,
            "tts_engine": engine,
            "max_workers": 1,
            "trim": {"frame_ms": 20, "multiplier": 3.0, "minimum_threshold": 50.0},
            "parser": "benchmark"
        }
        
        from agent_os.speech.schema.jobs import EventBus

        events_emitted = []
        def listener(event):
            events_emitted.append(event)
            print(f"[TEST EVENT] {event.event_type} - {event.to_json()}")

        bus = EventBus()
        bus.subscribe(listener)

        context = StageContext(
            project_dir=project_dir,
            cache_dir=cache_dir,
            config=config,
            artifacts={},
            metrics={},
            event_bus=bus,
            run_id="test_run_123"
        )
        
        dag = DAG()
        dag.add_node("normalize", NormalizeStage())
        dag.add_node("parse", ParseStage(), depends_on=["normalize"])
        dag.add_node("segment", SegmentStage(), depends_on=["parse"])
        dag.add_node("context", ContextStage(), depends_on=["segment"])
        dag.add_node("route", RouteStage(), depends_on=["context", "parse"])
        dag.add_node("synthesize", SynthesizeStage(), depends_on=["route"])
        dag.add_node("trim", TrimStage(), depends_on=["synthesize"])
        dag.add_node("append", AppendStage(), depends_on=["trim"])
        
        executor = IncrementalExecutor(dag, context)
        executor.run()
        
        # Verify events
        event_types = [e.event_type for e in events_emitted]
        assert "pipeline_started" in event_types
        assert "chunk_started" in event_types
        assert "chunk_synthesized" in event_types
        assert "chunk_trimmed" in event_types
        assert "chunk_appended" in event_types
        assert "chapter_progress" in event_types
        assert "chapter_completed" in event_types
        assert "pipeline_completed" in event_types
        
        # Verify output WAV file
        output_file = Path(project_dir) / "Chapter_0.wav"
        assert output_file.exists()
        assert output_file.stat().st_size > 0
        
        data, sr = sf.read(str(output_file))
        assert sr == 24000
        assert len(data) > 0

import os
import pytest
import numpy as np
from typing import Tuple
from pathlib import Path

from agent_os.speech.schema.models import DialogueSegment, ParseResult, EngineCapabilities, Language, EngineName
from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.pipeline.stages.segment import SegmentStage
from agent_os.speech.pipeline.stages.route import RouteStage
from agent_os.speech.pipeline.stages.synthesize import SynthesizeStage
from agent_os.speech.pipeline.stages.trim import TrimStage
from agent_os.speech.pipeline.stages.merge import MergeStage
from agent_os.speech.pipeline.interfaces import TTSEngine

class DummyTTSEngine(TTSEngine):
    def initialize(self) -> None:
        pass
        
    def validate_model(self) -> None:
        pass
        
    def warmup(self, profile: str = "minimal") -> None:
        pass
        
    def get_capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            engine_name=EngineName.KOKORO,
            supported_languages=[Language.EN],
            supported_voices={"v1": {}},
            max_text_length=500
        )

    def supports_language(self, language: Language) -> bool:
        return language == Language.EN

    def supports_voice(self, voice: str) -> bool:
        return voice == "v1"

    def synthesize(self, text: str, voice: str, language: Language, speed: float) -> Tuple[int, np.ndarray]:
        # Generate a 1-second 440Hz sine wave, padded with 0.1s silence at both ends
        sample_rate = 24000
        t = np.linspace(0, 1.0, sample_rate)
        # Sine wave
        wave = np.sin(2 * np.pi * 440 * t)
        
        # Convert to int16
        wave_int16 = (wave * 32767).astype(np.int16)
        
        # Prepend and append silence
        silence = np.zeros(int(sample_rate * 0.1), dtype=np.int16)
        
        final_wave = np.concatenate([silence, wave_int16, silence])
        
        return sample_rate, final_wave
        
    def shutdown(self) -> None:
        pass

@pytest.fixture
def vertical_slice_transcript():
    segments = [
        DialogueSegment(
            segment_id=1,
            chapter_id="1",
            speaker="Narrator",
            text="First chunk.",
            language=Language.EN,
            pause_after_ms=500
        ),
        DialogueSegment(
            segment_id=2,
            chapter_id="1",
            speaker="John",
            text="Second chunk.",
            language=Language.EN
        )
    ]
    return ParseResult(
        segments=segments,
        parser_name="TestParser",
        parser_version="1.0",
        model="test-model",
        confidence=1.0
    )

def test_full_synthesis_slice(vertical_slice_transcript, tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    cache_dir = project_dir / "cache"
    
    capabilities = EngineCapabilities(
        engine_name=EngineName.KOKORO,
        supported_languages=[Language.EN],
        supported_voices={
            "v1": {"gender": "male"}
        },
        max_text_length=500
    )
    
    config = {
        "engine_capabilities": capabilities,
        "tts_engine": DummyTTSEngine(),
        "max_workers": 2,
        "trim": {
            "frame_ms": 20,
            "multiplier": 3.0,
            "minimum_threshold": 10.0
        }
    }
    
    # 1. Segment
    seg_stage = SegmentStage()
    seg_context = StageContext(project_dir=str(project_dir), cache_dir=str(cache_dir), config=config, artifacts={}, metrics={})
    seg_inputs = {"parse": {"transcript": vertical_slice_transcript}}
    seg_result = seg_stage.run(seg_context, seg_inputs)
    
    # 2. Route
    route_stage = RouteStage()
    route_context = StageContext(project_dir=str(project_dir), cache_dir=str(cache_dir), config=config, artifacts={}, metrics={})
    route_inputs = {"segment": seg_result, "parse": {"transcript": vertical_slice_transcript}}
    route_result = route_stage.run(route_context, route_inputs)
    
    assert len(route_result["execution_plan"]) == 2
    assert route_result["execution_plan"][0].pause_after_ms == 500
    
    # 3. Synthesize
    syn_stage = SynthesizeStage()
    syn_context = StageContext(project_dir=str(project_dir), cache_dir=str(cache_dir), config=config, artifacts={}, metrics={})
    syn_inputs = {"route": route_result}
    syn_result = syn_stage.run(syn_context, syn_inputs)
    
    assert len(syn_result["execution_plan"]) == 2
    for entry in syn_result["execution_plan"]:
        assert entry.status == "completed"
        assert Path(entry.expected_output_path).exists()
        
    # 4. Trim
    trim_stage = TrimStage()
    trim_context = StageContext(project_dir=str(project_dir), cache_dir=str(cache_dir), config=config, artifacts={}, metrics={})
    trim_inputs = {"synthesize": syn_result}
    trim_result = trim_stage.run(trim_context, trim_inputs)
    
    assert len(trim_result["execution_plan"]) == 2
    
    # 5. Merge
    merge_stage = MergeStage()
    merge_context = StageContext(project_dir=str(project_dir), cache_dir=str(cache_dir), config=config, artifacts={}, metrics={})
    merge_inputs = {"trim": trim_result}
    merge_result = merge_stage.run(merge_context, merge_inputs)
    
    final_output = project_dir / "Chapter_1.wav"
    assert final_output.exists()
    
    # Validate length roughly
    # 2 chunks * 1 sec sine + 0.5 sec pause = ~2.5 sec
    from scipy.io import wavfile
    rate, data = wavfile.read(str(final_output))
    duration = len(data) / rate
    assert 2.0 < duration < 3.0

if __name__ == "__main__":
    pytest.main(["-v", __file__])

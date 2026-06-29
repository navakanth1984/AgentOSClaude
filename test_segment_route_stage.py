import os
import pytest
from pathlib import Path

from agent_os.speech.schema.models import DialogueSegment, ParseResult, EngineCapabilities, VoiceMap, Language, EngineName
from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.pipeline.stages.segment import SegmentStage
from agent_os.speech.pipeline.stages.route import RouteStage

@pytest.fixture
def dummy_transcript():
    segments = [
        DialogueSegment(
            segment_id=1,
            chapter_id="1",
            speaker="Narrator",
            text="The quick brown fox jumps over the lazy dog. It was a bright cold day in April, and the clocks were striking thirteen.",
            language=Language.EN
        ),
        DialogueSegment(
            segment_id=2,
            chapter_id="1",
            speaker="John",
            text="Hello there!",
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

@pytest.fixture
def dummy_capabilities():
    return EngineCapabilities(
        engine_name=EngineName.KOKORO,
        supported_languages=[Language.EN],
        supported_voices={
            "af_nova": {"gender": "female"},
            "am_michael": {"gender": "male"}
        },
        max_text_length=500
    )

def test_segment_stage_splitting(dummy_transcript):
    context = StageContext(
        project_dir="tests/speech",
        cache_dir="tests/speech/cache",
        artifacts={},
        metrics={},
        config={
            "engine_capabilities": EngineCapabilities(
                engine_name=EngineName.KOKORO,
                supported_languages=[Language.EN],
                supported_voices={},
                max_text_length=50
            )
        }
    )
    inputs = {"parse": {"transcript": dummy_transcript}}
    
    stage = SegmentStage()
    
    result = stage.run(context, inputs)
    chunks = result["chunks"]
    
    assert len(chunks) == 4
    assert chunks[0].parent_segment_id == 1
    assert chunks[0].chunk_index_in_segment == 0
    assert chunks[0].is_terminal_chunk == False
    
    assert chunks[1].parent_segment_id == 1
    assert chunks[1].chunk_index_in_segment == 1
    assert chunks[1].is_terminal_chunk == False
    
    assert chunks[2].parent_segment_id == 1
    assert chunks[2].chunk_index_in_segment == 2
    assert chunks[2].is_terminal_chunk == True
    
    assert chunks[3].parent_segment_id == 2
    assert chunks[3].is_terminal_chunk == True

def test_route_stage_lockfile(dummy_transcript, dummy_capabilities, tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    
    # First, run SegmentStage
    seg_stage = SegmentStage()
    seg_context = StageContext(
        project_dir=str(project_dir),
        cache_dir=str(project_dir / "cache"),
        artifacts={},
        metrics={},
        config={}
    )
    seg_inputs = {"parse": {"transcript": dummy_transcript}}
    seg_result = seg_stage.run(seg_context, seg_inputs)
    
    # Now run RouteStage
    route_stage = RouteStage()
    route_context = StageContext(
        project_dir=str(project_dir),
        cache_dir=str(project_dir / "cache"),
        artifacts={},
        metrics={},
        config={"engine_capabilities": dummy_capabilities}
    )
    route_inputs = {
        "parse": {"transcript": dummy_transcript},
        "segment": seg_result
    }
    
    # This should generate voice_map.json
    route_result = route_stage.run(route_context, route_inputs)
    
    lockfile_path = project_dir / "voice_map.json"
    assert lockfile_path.exists()
    
    execution_plan = route_result["execution_plan"]
    assert len(execution_plan) == len(seg_result["chunks"])
    
    # Verify the mapping matches the lockfile
    import json
    with open(lockfile_path, "r") as f:
        voice_map = json.load(f)
        
    assert execution_plan[0].voice == voice_map["voices"]["Narrator"]
    assert execution_plan[1].voice == voice_map["voices"]["John"]

if __name__ == "__main__":
    pytest.main(["-v", __file__])

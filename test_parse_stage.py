import os
import pytest
from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.pipeline.stages.parse import ParseStage

# These tests run offline via the EXPLICIT mock opt-in (allow_mock_parse=True).
# Without that flag, ParseStage now fails loudly when GEMINI_API_KEY is unset
# instead of silently synthesizing "Mock text" — see parsers.py._call_gemini.

def test_screenplay_classification():
    with open("tests/speech/fixtures/screenplay_simple.txt", "r", encoding="utf-8") as f:
        text = f.read()
        
    context = StageContext(
        project_dir="tests/speech",
        cache_dir="tests/speech/cache",
        artifacts={},
        metrics={},
        config={"parse_policy": "fast", "allow_mock_parse": True}
    )

    inputs = {"normalize": {"normalized_text": text}}
    
    stage = ParseStage()
    result = stage.run(context, inputs)
    
    classification = result["classification"]
    assert classification.document_type == "screenplay"
    
    transcript = result["transcript"]
    assert transcript.parser_name == "ScreenplayParser"
    assert transcript.model == "gemini-2.5-flash"
    
def test_novel_classification():
    with open("tests/speech/fixtures/novel_simple.txt", "r", encoding="utf-8") as f:
        text = f.read()
        
    context = StageContext(
        project_dir="tests/speech",
        cache_dir="tests/speech/cache",
        artifacts={},
        metrics={},
        config={"parse_policy": "fast", "allow_mock_parse": True}
    )

    inputs = {"normalize": {"normalized_text": text}}
    
    stage = ParseStage()
    result = stage.run(context, inputs)
    
    classification = result["classification"]
    assert classification.document_type == "novel"
    
    transcript = result["transcript"]
    assert transcript.parser_name == "NovelParser"
    assert transcript.model == "gemini-2.5-flash"

if __name__ == "__main__":
    pytest.main(["-v", __file__])

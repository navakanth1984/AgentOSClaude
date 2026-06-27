"""Regression tests for cache-key stability and the normalize input contract.

Run with no TTS engine / no network.
"""
import os
import json
import tempfile

from agent_os.speech.schema.models import (
    SpeechChunk, ParseResult, DialogueSegment, EngineCapabilities, EngineName, Language,
)
from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.pipeline.stages.route import RouteStage, strip_performance_tags
from agent_os.speech.pipeline.stages.normalize import NormalizeStage


def _run_route(engine_field):
    """engine_field simulates fresh(enum) vs lockfile(str) voice_map.engine."""
    chunks = [SpeechChunk(1, 1, "c1", "[breath] Hello there.", Language.EN, 0, 0, 0, True, 1.0)]
    transcript = ParseResult(
        segments=[DialogueSegment(1, "c1", "Narrator")],
        parser_name="x", parser_version="1", model="m", confidence=1.0,
    )
    caps = EngineCapabilities(
        engine_name=EngineName.KOKORO, supported_languages=[Language.EN],
        supported_voices={"af": {"gender": "f"}}, supports_emotions=False,
    )
    d = tempfile.mkdtemp(prefix="route_test_")
    with open(os.path.join(d, "voice_map.json"), "w") as f:
        json.dump({"schema_version": "1.0", "engine": engine_field, "voices": {"Narrator": "af"}}, f)
    ctx = StageContext(project_dir=d, cache_dir=d,
                       config={"engine_capabilities": caps}, artifacts={}, metrics={})
    return RouteStage().run(ctx, {"segment": {"chunks": chunks}, "parse": {"transcript": transcript}})


def test_cache_key_enum_equals_string():
    enum_key = _run_route(EngineName.KOKORO)["execution_plan"][0].cache_key
    str_key = _run_route("kokoro")["execution_plan"][0].cache_key
    assert enum_key == str_key, f"cache_key drifted: {enum_key} != {str_key}"


def test_tags_stripped_for_non_emotion_engine():
    text = _run_route("kokoro")["execution_plan"][0].text
    assert "[breath]" not in text, f"performance tag leaked into synthesized text: {text!r}"


def test_strip_spares_legit_parentheticals():
    s = "The result (see chapter 2) was clear."
    assert strip_performance_tags(s) == s


def test_normalize_input_text_is_literal_not_path():
    probe = "normalize_probe.txt"
    with open(probe, "w", encoding="utf-8") as f:
        f.write("FILE CONTENTS")
    try:
        ctx = StageContext(project_dir=".", cache_dir=".",
                           config={"input_text": probe}, artifacts={}, metrics={})
        out = NormalizeStage().run(ctx, {})
        assert out["normalized_text"] == probe, f"input_text was read as a file: {out['normalized_text']!r}"
    finally:
        os.remove(probe)


def test_normalize_rejects_both_inputs():
    ctx = StageContext(project_dir=".", cache_dir=".",
                       config={"input_text": "a", "input_path": "b"}, artifacts={}, metrics={})
    try:
        NormalizeStage().run(ctx, {})
    except ValueError:
        return
    raise AssertionError("expected ValueError when both input_text and input_path are set")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"[PASS] {fn.__name__}")
    print(f"\nAll {len(fns)} tests passed.")

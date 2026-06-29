import hashlib
import json
import re
from enum import Enum
from typing import Any, Dict, List
from pathlib import Path

from agent_os.speech.schema.models import SpeechChunk, EngineCapabilities, VoiceMap, ParseResult, ExecutionPlanEntry
from agent_os.speech.pipeline.executor import StageContext


def _enum_value(x: Any) -> Any:
    """Normalize an enum to its value for stable string interpolation.

    `class E(str, Enum)` interpolates inconsistently: f"{E.X}" yields "E.X" on
    3.12 but the bare value when reloaded from JSON. Cache keys must not depend
    on which path produced the object, so always pin .value.
    """
    return x.value if isinstance(x, Enum) else x


# Square-bracket cues ([breath], [sigh], [clears throat], [pause]) injected by
# ContextStage. Square brackets never appear in normal narration, so strip all.
_BRACKET_CUE = re.compile(r"\[[^\]]*\]")
# Parenthetical performance directions — strip only those matching the injected
# emotional vocabulary so legitimate prose parentheticals like "(see ch. 2)" survive.
_PAREN_DIRECTION = re.compile(
    r"\((?:[^)]*?(?:whisper|shout|trembl|excited|nervous|sob|cry|laugh|sigh|"
    r"breath|pause|softly|angr|gentl|quietly|loudly|mutter|stammer)[^)]*?)\)",
    re.IGNORECASE,
)


def strip_performance_tags(text: str) -> str:
    """Remove performance cues so engines without emotion support don't speak them."""
    text = _BRACKET_CUE.sub("", text)
    text = _PAREN_DIRECTION.sub("", text)
    # Tidy the gaps the removals leave behind.
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)  # space before punctuation
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

from agent_os.speech.pipeline.voice_manager import VoiceManager

class RouteStage:
    """
    Maps SpeechChunks to final execution RouteDecisions based on the 
    project's static voice_map.json lockfile.
    """
    
    def name(self) -> str:
        return "route"

    def run(self, context: StageContext, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute RouteStage.
        
        Inputs:
            inputs["segment"]["chunks"]: List[SpeechChunk]
            inputs["parse"]["transcript"]: ParseResult (needed for speaker mapping lookup)
            
        Context:
            context.config["engine_capabilities"]: EngineCapabilities
        """
        # Allow fallback if ContextStage is bypassed or not in the DAG
        from agent_os.speech.schema.models import ensure_speech_chunks, ensure_parse_result
        chunks_source = inputs.get("context") or inputs.get("segment")
        if chunks_source is None:
            raise ValueError("RouteStage requires a 'context' or 'segment' input with chunks")
        chunks: List[SpeechChunk] = ensure_speech_chunks(chunks_source["chunks"])
        transcript: ParseResult = ensure_parse_result(inputs["parse"]["transcript"])
        capabilities: EngineCapabilities = context.config["engine_capabilities"]
        
        # 1. Enforce or Load VoiceMap Lockfile via VoiceManager
        voice_map = VoiceManager.ensure_lockfile(context.project_dir, transcript, capabilities)
        
        # We need a quick lookup of parent_segment_id -> speaker
        segment_to_speaker = {s.segment_id: s.speaker for s in transcript.segments}
        
        execution_plan: List[ExecutionPlanEntry] = []
        
        # Engines that can't interpret performance cues would speak them aloud,
        # so strip tags before they reach synthesis (and before hashing).
        supports_emotions = getattr(capabilities, "supports_emotions", False)

        # 2. Map Chunks to ExecutionPlanEntry
        for chunk in chunks:
            speaker = segment_to_speaker.get(chunk.parent_segment_id, "Narrator")
            voice_id = VoiceManager.resolve_voice(speaker, voice_map, capabilities)

            spoken_text = chunk.text if supports_emotions else strip_performance_tags(chunk.text)

            # Normalization for hashing: lowercase, remove extra spaces
            normalized_text = re.sub(r'\s+', ' ', spoken_text.strip().lower())

            speed = float(context.config.get("speed", 1.0))
            pitch = float(context.config.get("pitch", 1.0))
            volume_gain_db = float(context.config.get("volume_gain_db", 0.0))
            language = chunk.language
            engine_version = "1.0"

            hash_input = f"{voice_map.schema_version}|{_enum_value(voice_map.engine)}|{engine_version}|{voice_id}|{_enum_value(language)}|{speed}|{pitch}|{normalized_text}"
            cache_key = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
            
            expected_output_path = str(Path(context.cache_dir) / f"{cache_key}.wav")
            
            entry = ExecutionPlanEntry(
                chunk_id=chunk.chunk_id,
                chapter_id=chunk.chapter_id,
                text=spoken_text,
                engine=voice_map.engine,
                voice=voice_id,
                language=language,
                speed=speed,
                pitch=pitch,
                volume_gain_db=volume_gain_db,
                cache_key=cache_key,
                expected_output_path=expected_output_path,
                pause_before_ms=chunk.pause_before_ms,
                pause_after_ms=chunk.pause_after_ms,
                status="pending"
            )
            execution_plan.append(entry)
            
        # Serialize for artifact dumping
        execution_plan_raw = [
            {
                "chunk_id": d.chunk_id,
                "chapter_id": d.chapter_id,
                "text": d.text,
                "engine": d.engine,
                "voice": d.voice,
                "language": d.language,
                "speed": d.speed,
                "pitch": d.pitch,
                "volume_gain_db": d.volume_gain_db,
                "cache_key": d.cache_key,
                "expected_output_path": d.expected_output_path,
                "pause_before_ms": d.pause_before_ms,
                "pause_after_ms": d.pause_after_ms,
                "status": d.status
            }
            for d in execution_plan
        ]
        
        return {
            "execution_plan": execution_plan,
            "execution_plan_raw": json.dumps(execution_plan_raw, indent=2)
        }

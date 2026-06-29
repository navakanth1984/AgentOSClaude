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

class VoiceAssignmentPolicy:
    """
    Handles the generation of a deterministic voice lockfile (voice_map.json)
    if one does not already exist.
    """
    
    @staticmethod
    def ensure_lockfile(project_dir: str, transcript: ParseResult, capabilities: EngineCapabilities) -> VoiceMap:
        lockfile_path = Path(project_dir) / "voice_map.json"
        
        if lockfile_path.exists():
            with open(lockfile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return VoiceMap(
                schema_version=data.get("schema_version", "1.0"),
                engine=data.get("engine", capabilities.engine_name),
                voices=data.get("voices", {})
            )
            
        # Needs generation
        print("voice_map.json not found. Generating default VoiceAssignmentPolicy lockfile...")
        
        voices = {}
        
        # Identify all unique speakers
        speakers = set()
        for segment in transcript.segments:
            speakers.add(segment.speaker)
            
        # Simple assignment heuristic
        available_voices = list(capabilities.supported_voices.keys())
        voice_index = 0
        
        for speaker in sorted(list(speakers)):
            # Fallback to cycling available voices if we have more speakers than voices
            v = available_voices[voice_index % len(available_voices)]
            voices[speaker] = v
            # If we know it's a Narrator, maybe we explicitly prefer the first stable voice,
            # but for a heuristic we'll just assign linearly.
            voice_index += 1
            
        voice_map = VoiceMap(
            schema_version="1.0",
            engine=capabilities.engine_name,
            voices=voices
        )
        
        # Write to disk
        lockfile_path.parent.mkdir(parents=True, exist_ok=True)
        with open(lockfile_path, "w", encoding="utf-8") as f:
            json.dump({
                "schema_version": voice_map.schema_version,
                "engine": voice_map.engine,
                "voices": voice_map.voices
            }, f, indent=4)
            
        return voice_map


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
        
        # 1. Enforce or Load VoiceMap Lockfile
        voice_map = VoiceAssignmentPolicy.ensure_lockfile(context.project_dir, transcript, capabilities)
        
        # We need a quick lookup of parent_segment_id -> speaker
        segment_to_speaker = {s.segment_id: s.speaker for s in transcript.segments}
        
        execution_plan: List[ExecutionPlanEntry] = []
        
        # Engines that can't interpret performance cues would speak them aloud,
        # so strip tags before they reach synthesis (and before hashing).
        supports_emotions = getattr(capabilities, "supports_emotions", False)

        # 2. Map Chunks to ExecutionPlanEntry
        for chunk in chunks:
            speaker = segment_to_speaker.get(chunk.parent_segment_id, "Narrator")
            voice_id = voice_map.voices.get(speaker, list(capabilities.supported_voices.keys())[0]) # fallback to first

            spoken_text = chunk.text if supports_emotions else strip_performance_tags(chunk.text)

            # Normalization for hashing: lowercase, remove extra spaces
            normalized_text = re.sub(r'\s+', ' ', spoken_text.strip().lower())

            # SHA256(schema_version + engine + engine_version + voice + language + speed + pitch + normalized_text)
            # Default speed/pitch for now
            speed, pitch, volume_gain_db = 1.0, 1.0, 0.0
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

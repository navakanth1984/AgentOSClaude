from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

SCHEMA_VERSION = "1.0"
PIPELINE_VERSION = "1.0"
ENGINE_API_VERSION = "1.0"

class Emotion(str, Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    SURPRISED = "surprised"

class Language(str, Enum):
    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"
    HI = "hi"
    TE = "te"
    JA = "ja"
    ZH = "zh"

class EngineName(str, Enum):
    KOKORO = "kokoro"
    GCP = "gcp"
    SARVAM = "sarvam"

@dataclass(frozen=True, slots=True)
class DialogueSegment:
    segment_id: int
    chapter_id: str
    speaker: str = "Narrator"
    text: str = ""
    language: Language = Language.EN
    emotion: Optional[Emotion] = None
    confidence: float = 1.0
    importance: float = 1.0
    pause_before_ms: int = 0
    pause_after_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ExecutionPlanEntry:
    chunk_id: int
    chapter_id: str
    text: str
    engine: EngineName
    voice: str
    language: Language
    speed: float
    pitch: float
    volume_gain_db: float
    cache_key: str
    expected_output_path: str
    pause_before_ms: int
    pause_after_ms: int
    status: str

@dataclass(frozen=True, slots=True)
class SpeechChunk:
    chunk_id: int
    parent_segment_id: int
    chapter_id: str
    text: str
    language: Language
    pause_before_ms: int
    pause_after_ms: int
    chunk_index_in_segment: int
    is_terminal_chunk: bool
    estimated_duration_sec: float

@dataclass(frozen=True, slots=True)
class VoiceMap:
    schema_version: str
    engine: EngineName
    voices: Dict[str, str]  # speaker_name -> voice_id


@dataclass(frozen=True, slots=True)
class EngineCapabilities:
    engine_name: EngineName
    supported_languages: List[Language]
    supported_voices: Dict[str, Dict[str, Any]]
    max_text_length: int = 500
    max_concurrent_requests: int = 1
    supports_streaming: bool = False
    supports_emotions: bool = False
    supports_pitch: bool = False
    supports_speed: bool = True
    sample_rate: int = 24000
    output_format: str = "wav"
    cost_per_char: float = 0.0

@dataclass(frozen=True, slots=True)
class SpeechProject:
    project_name: str
    pipeline_version: str
    schema_version: str
    created_at: str
    source_file: str
    chapters: int
    language: Language
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class ArtifactMetadata:
    name: str
    fingerprint: str
    producer_stage: str
    stage_version: str
    created_at: str
    input_fingerprint: str

@dataclass(frozen=True, slots=True)
class StageMetrics:
    stage: str
    duration_ms: float
    cache_hit: bool
    input_size: int
    output_size: int

@dataclass(frozen=True, slots=True)
class PipelineManifest:
    pipeline_version: str
    config_hash: str
    fingerprints: Dict[str, str]
    engines: Dict[str, str]

class ParsePolicy(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    QUALITY = "quality"

@dataclass(frozen=True, slots=True)
class ClassificationResult:
    document_type: str
    confidence: float

@dataclass(frozen=True, slots=True)
class ParseResult:
    segments: List[DialogueSegment]
    parser_name: str
    parser_version: str
    model: str
    confidence: float

def ensure_parse_result(obj) -> ParseResult:
    if isinstance(obj, ParseResult):
        return obj
    if isinstance(obj, dict):
        segs = []
        for s in obj.get("segments", []):
            if isinstance(s, dict):
                lang_str = s.get("language")
                lang = Language(lang_str) if lang_str else Language.EN
                em_str = s.get("emotion")
                emotion = Emotion(em_str) if em_str else None
                segs.append(DialogueSegment(
                    segment_id=s.get("segment_id", 0),
                    chapter_id=s.get("chapter_id", ""),
                    speaker=s.get("speaker", "Narrator"),
                    text=s.get("text", ""),
                    language=lang,
                    emotion=emotion,
                    confidence=s.get("confidence", 1.0),
                    importance=s.get("importance", 1.0),
                    pause_before_ms=s.get("pause_before_ms", 0),
                    pause_after_ms=s.get("pause_after_ms", 0),
                    metadata=s.get("metadata", {})
                ))
            else:
                segs.append(s)
        return ParseResult(
            segments=segs,
            parser_name=obj.get("parser_name", ""),
            parser_version=obj.get("parser_version", ""),
            model=obj.get("model", ""),
            confidence=obj.get("confidence", 1.0)
        )
    return obj

def ensure_execution_plan(obj) -> List[ExecutionPlanEntry]:
    """Reconstruct a list of ExecutionPlanEntry from cache-reloaded dicts.

    The executor serializes stage outputs to JSON (dataclasses.asdict) and, on a
    cache hit, reloads them as plain dicts. synthesize/trim/merge consume the
    execution plan as dataclasses, so they must call this on their inputs the
    same way route/segment/context call ensure_* on theirs.
    """
    if isinstance(obj, list):
        entries = []
        for e in obj:
            if isinstance(e, ExecutionPlanEntry):
                entries.append(e)
            elif isinstance(e, dict):
                eng_str = e.get("engine")
                engine = EngineName(eng_str) if eng_str is not None else EngineName.KOKORO
                lang_str = e.get("language")
                language = Language(lang_str) if lang_str else Language.EN
                entries.append(ExecutionPlanEntry(
                    chunk_id=e.get("chunk_id", 0),
                    chapter_id=e.get("chapter_id", ""),
                    text=e.get("text", ""),
                    engine=engine,
                    voice=e.get("voice", ""),
                    language=language,
                    speed=e.get("speed", 1.0),
                    pitch=e.get("pitch", 1.0),
                    volume_gain_db=e.get("volume_gain_db", 0.0),
                    cache_key=e.get("cache_key", ""),
                    expected_output_path=e.get("expected_output_path", ""),
                    pause_before_ms=e.get("pause_before_ms", 0),
                    pause_after_ms=e.get("pause_after_ms", 0),
                    status=e.get("status", "pending"),
                ))
            else:
                entries.append(e)
        return entries
    return obj


def ensure_speech_chunks(obj) -> List[SpeechChunk]:
    if isinstance(obj, list):
        chunks = []
        for c in obj:
            if isinstance(c, SpeechChunk):
                chunks.append(c)
            elif isinstance(c, dict):
                lang_str = c.get("language")
                lang = Language(lang_str) if lang_str else Language.EN
                chunks.append(SpeechChunk(
                    chunk_id=c.get("chunk_id", 0),
                    parent_segment_id=c.get("parent_segment_id", 0),
                    chapter_id=c.get("chapter_id", ""),
                    text=c.get("text", ""),
                    language=lang,
                    pause_before_ms=c.get("pause_before_ms", 0),
                    pause_after_ms=c.get("pause_after_ms", 0),
                    chunk_index_in_segment=c.get("chunk_index_in_segment", 0),
                    is_terminal_chunk=c.get("is_terminal_chunk", True),
                    estimated_duration_sec=c.get("estimated_duration_sec", 0.0)
                ))
        return chunks
    return obj



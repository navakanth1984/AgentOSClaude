import os
import json
import agent_os.env_boot  # noqa: F401 — load .env so GEMINI_API_KEY is visible
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from google import genai
from google.genai import types

from agent_os.speech.schema.models import DialogueSegment, ParseResult, ParsePolicy, Language

_LANG_VALUES = {l.value for l in Language}

# Pydantic schema for structured extraction
class ExtractedSegment(BaseModel):
    speaker: str = Field(description="Name of the character speaking, or 'Narrator' for action/descriptions")
    text: str = Field(description="The exact text being spoken or described")
    emotion: Optional[str] = Field(None, description="Inferred emotion of the speaker")
    language: str = Field("en", description="Language code")
    confidence: float = Field(1.0, description="Confidence in this extraction")

class ExtractionResult(BaseModel):
    segments: List[ExtractedSegment]

class BaseParser:
    def __init__(self, policy: ParsePolicy = ParsePolicy.BALANCED, allow_mock: bool = False):
        self.policy = policy
        # Explicit, opt-in offline mock. NEVER a silent fallback: production must
        # fail loudly when the API key is missing rather than synthesize fake audio.
        self.allow_mock = allow_mock
        self.model_name = self._resolve_model()
        # Initialize GenAI client
        api_key = os.environ.get("GEMINI_API_KEY")
        self.client: Optional[genai.Client] = genai.Client(api_key=api_key) if api_key else None
        
    def _resolve_model(self) -> str:
        if self.policy == ParsePolicy.FAST:
            return "gemini-2.5-flash"
        elif self.policy == ParsePolicy.QUALITY:
            return "gemini-2.5-pro"
        return "gemini-2.5-flash" # Default to balanced
        
    def parse(self, text: str, chapter_id: str = "0") -> Tuple[ParseResult, str]:
        raise NotImplementedError
        
    def _call_gemini(self, prompt: str, text: str) -> Tuple[List[DialogueSegment], str]:
        full_prompt = prompt.replace("{{text}}", text)
        
        if not self.client:
            if not self.allow_mock:
                # Loud failure beats silently synthesizing "Mock text" as audio.
                raise RuntimeError(
                    "GEMINI_API_KEY is not set, so the production parser cannot run. "
                    "Set GEMINI_API_KEY to use the real parser, or select the deterministic "
                    "offline parser with config {'parser': 'benchmark'}. (Tests may opt into a "
                    "stub with config {'allow_mock_parse': True}.)"
                )
            # Explicit opt-in stub (tests only)
            raw_json = json.dumps({"segments": [{"speaker": "Mock", "text": "Mock text", "language": "en", "confidence": 1.0}]})
            segments = [
                DialogueSegment(
                    segment_id=1,
                    chapter_id="0",
                    speaker="Mock",
                    text="Mock text"
                )
            ]
            return segments, raw_json

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractionResult,
                    temperature=0.1
                )
            )
            
            raw_json: str = response.text or "{}"

            # Let's parse with Pydantic
            data = ExtractionResult.model_validate_json(raw_json)
            
            # Map back to our strict frozen dataclass
            segments = []
            for i, seg in enumerate(data.segments):
                segments.append(DialogueSegment(
                    segment_id=i+1,
                    chapter_id="0",
                    speaker=seg.speaker,
                    text=seg.text,
                    # We would map emotion string to Emotion enum here if needed
                    language=Language(seg.language) if seg.language in _LANG_VALUES else Language.EN,
                    confidence=seg.confidence
                ))
                
            return segments, raw_json
        except Exception as e:
            # Do NOT return the error as a speakable segment — that would synthesize
            # "API Error: ..." into the audiobook and report success. Fail loudly.
            raise RuntimeError(f"Gemini parse failed ({self.model_name}): {e}") from e

class ScreenplayParser(BaseParser):
    version = "1.0"
    
    def parse(self, text: str, chapter_id: str = "0") -> Tuple[ParseResult, str]:
        with open("agent_os/speech/prompts/screenplay_v1.md", "r", encoding="utf-8") as f:
            prompt = f.read()
            
        segments, raw = self._call_gemini(prompt, text)
        
        result = ParseResult(
            segments=segments,
            parser_name="ScreenplayParser",
            parser_version=self.version,
            model=self.model_name,
            confidence=0.98
        )
        return result, raw

class NovelParser(BaseParser):
    version = "1.0"
    
    def parse(self, text: str, chapter_id: str = "0") -> Tuple[ParseResult, str]:
        with open("agent_os/speech/prompts/novel_v1.md", "r", encoding="utf-8") as f:
            prompt = f.read()
            
        segments, raw = self._call_gemini(prompt, text)
        
        result = ParseResult(
            segments=segments,
            parser_name="NovelParser",
            parser_version=self.version,
            model=self.model_name,
            confidence=0.95
        )
        return result, raw

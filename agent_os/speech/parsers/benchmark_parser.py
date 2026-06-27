"""Deterministic, offline parser for benchmarking — NOT a production parser.

Contract (intentionally narrow):
- deterministic: same text in -> same segments out, byte-for-byte
- offline: no LLM, no network, no API key
- boring: every paragraph becomes one Narrator DialogueSegment; it does not
  detect speakers, emotion, or language.

Its only job is to turn a corpus into a stable multi-segment workload so the
execution engine (Segment -> Route -> Synthesize) can be benchmarked without
depending on the Gemini parser. Do not extend it toward language understanding.
"""
import json
from typing import List, Tuple

from agent_os.speech.schema.models import DialogueSegment, ParseResult, Language

PARSER_VERSION = "1.0"


class BenchmarkParser:
    version = PARSER_VERSION

    def parse(self, text: str, chapter_id: str = "0") -> Tuple[ParseResult, str]:
        # NormalizeStage guarantees paragraphs are separated by exactly two newlines.
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        segments: List[DialogueSegment] = []
        for i, para in enumerate(paragraphs, start=1):
            segments.append(DialogueSegment(
                segment_id=i,
                chapter_id=str(chapter_id),
                speaker="Narrator",
                text=para,
                language=Language.EN,
            ))

        raw = json.dumps(
            [{"segment_id": s.segment_id, "chapter_id": s.chapter_id,
              "speaker": s.speaker, "text": s.text, "language": s.language.value}
             for s in segments],
            indent=2, sort_keys=True,
        )

        result = ParseResult(
            segments=segments,
            parser_name="BenchmarkParser",
            parser_version=self.version,
            model="none",
            confidence=1.0,
        )
        return result, raw

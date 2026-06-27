import json
import re
from typing import Any, Dict, List, Optional
from pathlib import Path

from agent_os.speech.schema.models import DialogueSegment, SpeechChunk, ParseResult, EngineCapabilities
from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.pipeline.splitters import RegexSentenceSplitter

class SegmentStage:
    """
    Splits DialogueSegment objects into semantic SpeechChunk objects 
    to fit within TTS engine constraints while preserving sentences.
    """
    
    # 500 chars is typical for Kokoro and stable local models
    MAX_CHUNK_LENGTH = 500
    
    def name(self) -> str:
        return "segment"

    def _estimate_duration(self, text: str, words_per_minute: int = 150) -> float:
        """Heuristic duration estimation based on characters and average reading speed."""
        # words_per_minute (default 150), ~5 chars per word + spaces
        chars_per_second = (words_per_minute * 6) / 60.0
        base_sec = len(text) / chars_per_second
        # Add slight penalty for punctuation pauses
        punctuation_count = len(re.findall(r'[,.!?—]', text))
        return round(base_sec + (punctuation_count * 0.2), 2)
        
    def run(self, context: StageContext, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the SegmentStage.
        
        Inputs:
            inputs["parse"]["transcript"]: ParseResult containing DialogueSegments
            
        Outputs:
            chunks: List[SpeechChunk]
            chunks_raw: JSON serialized string of the chunks for artifact dumping
        """
        from agent_os.speech.schema.models import ensure_parse_result
        parse_result: ParseResult = ensure_parse_result(inputs["parse"]["transcript"])
        segments: List[DialogueSegment] = parse_result.segments
        
        capabilities: Optional[EngineCapabilities] = context.config.get("engine_capabilities")
        max_chunk_length = getattr(capabilities, "max_text_length", 500) if capabilities else 500
        words_per_minute = context.config.get("words_per_minute", 150)
        
        splitter = context.config.get("sentence_splitter", RegexSentenceSplitter(max_chunk_length=max_chunk_length))
        
        chunks: List[SpeechChunk] = []
        global_chunk_id = 1
        
        for segment in segments:
            text = segment.text.strip()
            
            if not text:
                continue
                
            # Quick pass: if it's already short enough, it's one chunk
            if len(text) <= max_chunk_length:
                chunk = SpeechChunk(
                    chunk_id=global_chunk_id,
                    parent_segment_id=segment.segment_id,
                    chapter_id=str(segment.chapter_id),
                    text=text,
                    language=segment.language,
                    pause_before_ms=segment.pause_before_ms,
                    pause_after_ms=segment.pause_after_ms,
                    chunk_index_in_segment=0,
                    is_terminal_chunk=True,
                    estimated_duration_sec=self._estimate_duration(text, words_per_minute)
                )
                chunks.append(chunk)
                global_chunk_id += 1
                continue
                
            # Needs splitting
            sentences = splitter.split(text)
            
            # Now pack sentences into chunks without exceeding length
            current_chunk_text = ""
            chunk_index = 0
            
            for i, sentence in enumerate(sentences):
                # If a single sentence *still* exceeds length, we have to hard-split it
                # or just accept the long chunk and let the TTS engine fail/truncate.
                # Here we just pack it and trust the comma fallback worked as much as possible.
                
                # If adding this sentence exceeds length, flush the current buffer
                if current_chunk_text and (len(current_chunk_text) + 1 + len(sentence)) > max_chunk_length:
                    chunk = SpeechChunk(
                        chunk_id=global_chunk_id,
                        parent_segment_id=segment.segment_id,
                        chapter_id=str(segment.chapter_id),
                        text=current_chunk_text.strip(),
                        language=segment.language,
                        pause_before_ms=segment.pause_before_ms if chunk_index == 0 else 0,
                        pause_after_ms=0,
                        chunk_index_in_segment=chunk_index,
                        is_terminal_chunk=False,
                        estimated_duration_sec=self._estimate_duration(current_chunk_text, words_per_minute)
                    )
                    chunks.append(chunk)
                    global_chunk_id += 1
                    chunk_index += 1
                    current_chunk_text = sentence
                else:
                    if current_chunk_text:
                        current_chunk_text += " " + sentence
                    else:
                        current_chunk_text = sentence
                        
            # Flush remaining
            if current_chunk_text:
                chunk = SpeechChunk(
                    chunk_id=global_chunk_id,
                    parent_segment_id=segment.segment_id,
                    chapter_id=str(segment.chapter_id),
                    text=current_chunk_text.strip(),
                    language=segment.language,
                    pause_before_ms=segment.pause_before_ms if chunk_index == 0 else 0,
                    pause_after_ms=segment.pause_after_ms,
                    chunk_index_in_segment=chunk_index,
                    is_terminal_chunk=True,
                    estimated_duration_sec=self._estimate_duration(current_chunk_text, words_per_minute)
                )
                chunks.append(chunk)
                global_chunk_id += 1
                
        # Serialize to JSON dicts for artifact caching
        chunks_raw = [
            {
                "chunk_id": c.chunk_id,
                "parent_segment_id": c.parent_segment_id,
                "chapter_id": c.chapter_id,
                "text": c.text,
                "language": c.language,
                "pause_before_ms": c.pause_before_ms,
                "pause_after_ms": c.pause_after_ms,
                "chunk_index_in_segment": c.chunk_index_in_segment,
                "is_terminal_chunk": c.is_terminal_chunk,
                "estimated_duration_sec": c.estimated_duration_sec
            }
            for c in chunks
        ]
        
        return {
            "chunks": chunks,
            "chunks_raw": json.dumps(chunks_raw, indent=2)
        }

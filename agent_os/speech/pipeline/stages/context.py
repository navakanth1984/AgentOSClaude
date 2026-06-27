import os
import json
import hashlib
from typing import Any, Dict, List
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from agent_os.speech.schema.models import SpeechChunk
from agent_os.speech.pipeline.executor import StageContext

class TaggedSpeechChunk(BaseModel):
    chunk_id: int
    emotion_tagged_text: str = Field(description="The rewritten text including emotional tags like [breath], (sighs), [clears throat], or pauses where appropriate.")

class EmotionTaggingResult(BaseModel):
    tagged_chunks: List[TaggedSpeechChunk]

class ContextStage:
    """
    Enriches SpeechChunk text using Gemini Flash to add emotional context,
    pauses, and human-like realistic speech patterns (breaths, stumbles).
    """
    version = "1.0"

    def name(self) -> str:
        return "context"

    @staticmethod
    def _write_manifest(project_dir: str, stats: Dict[str, Any]) -> str:
        """Persist tagging provenance so every run is auditable on disk."""
        from pathlib import Path
        path = Path(project_dir) / "context_manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {"schema_version": "1.0", **stats}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        return str(path)

    def run(self, context: StageContext, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inputs:
            inputs["segment"]["chunks"]: List[SpeechChunk]
        """
        from agent_os.speech.schema.models import ensure_speech_chunks
        chunks: List[SpeechChunk] = ensure_speech_chunks(inputs["segment"]["chunks"])
        
        # Determine if we should bypass or if genai is available
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("[ContextStage] No GEMINI_API_KEY found. Skipping emotional tag injection.")
            skip_stats = {
                "status": "skipped_no_api_key",
                "model": None,
                "temperature": None,
                "total_chunks": len(chunks),
                "tagged_chunks": 0,
                "fell_back_to_raw": len(chunks),
                "failed_batches": 0,
                "total_batches": 0,
                "tagging_fingerprint": None,
            }
            manifest_path = self._write_manifest(context.project_dir, skip_stats)
            return {"chunks": chunks, "tagging_stats": skip_stats, "context_manifest": manifest_path}

        client = genai.Client(api_key=api_key)
        model_name = "gemini-2.5-flash"  # Highly efficient for large context tagging

        # Prepare system prompt for emotional tagging
        system_instruction = (
            "You are an expert voice director and dialogue polisher for audiobooks. "
            "Your task is to enrich dialogue and narration with emotional cues and natural human flaws "
            "to make them sound hyper-realistic when spoken. "
            "Inject cues such as [breath], [sigh], [clears throat], [pause], and emotional qualifiers like "
            "(whispering), (shouting), (voice trembling), or (excitedly). "
            "Also introduce minor natural flaws (e.g., slight word repetitions or stumbles) "
            "where characters are nervous or emotional. Do not overdo it. "
            "Return the tagged text mapped to the original chunk_id."
        )

        # Batch process to maintain continuity and optimize tokens
        batch_size = 10
        chunk_dict = {c.chunk_id: c for c in chunks}
        tagged_texts = {}
        failed_batches = 0
        total_batches = 0

        for i in range(0, len(chunks), batch_size):
            total_batches += 1
            batch = chunks[i:i + batch_size]
            
            # Construct input content showing context of speech
            input_data = []
            for c in batch:
                input_data.append({
                    "chunk_id": c.chunk_id,
                    "text": c.text,
                    "language": str(c.language)
                })

            prompt = f"Tag the following speech chunks for realistic audio output:\n{json.dumps(input_data, indent=2)}"

            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        response_schema=EmotionTaggingResult,
                        temperature=0.0  # determinism: the pipeline is content-addressed
                    )
                )

                if not response.text:
                    raise ValueError("empty response from model")
                result = EmotionTaggingResult.model_validate_json(response.text)
                for tc in result.tagged_chunks:
                    tagged_texts[tc.chunk_id] = tc.emotion_tagged_text

            except Exception as e:
                failed_batches += 1
                print(f"[ContextStage] Error processing batch starting at chunk index {i}: {e}")

        # Construct new SpeechChunk list with tagged texts
        enriched_chunks = []
        from dataclasses import replace
        for c in chunks:
            tagged_txt = tagged_texts.get(c.chunk_id, c.text)
            enriched_chunks.append(replace(c, text=tagged_txt))

        # Re-serialize for artifacts
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
            for c in enriched_chunks
        ]

        # Record which tagging variant was produced. A temperature-0 LLM is
        # *mostly* reproducible but not guaranteed across model revisions, so the
        # fingerprint makes the variant visible and auditable downstream.
        tagging_fingerprint = hashlib.sha256(
            json.dumps({c.chunk_id: c.text for c in enriched_chunks}, sort_keys=True).encode("utf-8")
        ).hexdigest()

        tagged_count = sum(1 for c in chunks if c.chunk_id in tagged_texts)
        tagging_stats = {
            "status": "ok" if not failed_batches else "degraded",
            "model": model_name,
            "temperature": 0.0,
            "total_chunks": len(chunks),
            "tagged_chunks": tagged_count,
            "fell_back_to_raw": len(chunks) - tagged_count,
            "failed_batches": failed_batches,
            "total_batches": total_batches,
            "tagging_fingerprint": tagging_fingerprint,
        }
        if failed_batches:
            print(f"[ContextStage] DEGRADED: {failed_batches}/{total_batches} batches failed; "
                  f"{tagging_stats['fell_back_to_raw']} chunks fell back to untagged text.")

        manifest_path = self._write_manifest(context.project_dir, tagging_stats)

        return {
            "chunks": enriched_chunks,
            "chunks_raw": json.dumps(chunks_raw, indent=2),
            "tagging_stats": tagging_stats,
            "context_manifest": manifest_path,
        }

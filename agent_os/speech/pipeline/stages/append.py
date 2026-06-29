import json
import numpy as np
from scipy.io import wavfile
from typing import Any, Dict, List
from pathlib import Path

from agent_os.speech.schema.models import ExecutionPlanEntry
from agent_os.speech.pipeline.executor import StageContext

class AppendStage:
    """
    Appends a single chunk (or set of chunks) to the final chapter audio file.
    Inserts silent gaps based on pause_before_ms and pause_after_ms.
    Emits ChunkAppended and ChapterCompleted events.
    """
    
    def name(self) -> str:
        return "append"

    def _generate_silence(self, duration_ms: int, sample_rate: int, dtype: np.dtype) -> np.ndarray:
        if duration_ms <= 0:
            return np.array([], dtype=dtype)
        num_samples = int(sample_rate * (duration_ms / 1000.0))
        return np.zeros(num_samples, dtype=dtype)

    def run(self, context: StageContext, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inputs:
            inputs["trim"]["execution_plan"]: List[ExecutionPlanEntry]
        """
        from agent_os.speech.schema.models import ensure_execution_plan
        from agent_os.speech.schema.events import ChunkAppended, ChapterCompleted
        import time

        execution_plan: List[ExecutionPlanEntry] = ensure_execution_plan(inputs["trim"]["execution_plan"])
        
        # In incremental execution, we typically get one chunk at a time.
        # But we will support appending whatever is passed.
        completed_manifest = []

        for entry in execution_plan:
            if entry.status != "completed":
                continue
                
            input_path = Path(entry.expected_output_path)
            if not input_path.exists():
                print(f"[AppendStage] Warning: expected file {input_path} not found.")
                continue

            try:
                sample_rate, new_data = wavfile.read(str(input_path))
            except Exception as e:
                print(f"[AppendStage] Failed to read {input_path}: {e}")
                continue

            chapter_id = entry.chapter_id
            output_path = Path(context.project_dir) / f"Chapter_{chapter_id}.wav"

            # Prepare new audio segment with silences
            segments = []
            if entry.pause_before_ms > 0:
                segments.append(self._generate_silence(entry.pause_before_ms, sample_rate, new_data.dtype))
            segments.append(new_data)
            if entry.pause_after_ms > 0:
                segments.append(self._generate_silence(entry.pause_after_ms, sample_rate, new_data.dtype))

            new_segment_audio = np.concatenate(segments)

            # Read existing file or start fresh
            if output_path.exists():
                try:
                    existing_sr, existing_data = wavfile.read(str(output_path))
                    if existing_sr != sample_rate:
                        raise ValueError(f"Sample rate mismatch: existing {existing_sr}, new {sample_rate}")
                    if existing_data.dtype != new_data.dtype:
                        raise ValueError(f"Dtype mismatch: existing {existing_data.dtype}, new {new_data.dtype}")
                    
                    combined_audio = np.concatenate([existing_data, new_segment_audio])
                except Exception as e:
                    print(f"[AppendStage] Error reading existing file {output_path}, overwriting: {e}")
                    combined_audio = new_segment_audio
            else:
                combined_audio = new_segment_audio

            # Write combined file back
            wavfile.write(str(output_path), sample_rate, combined_audio)

            duration_sec = len(combined_audio) / sample_rate
            
            # Emit ChunkAppended event
            context.emit_event(ChunkAppended(
                run_id=context.run_id,
                timestamp=time.time(),
                chunk_id=entry.chunk_id,
                accumulated_duration_sec=duration_sec,
                output_path=str(output_path)
            ))

            completed_manifest.append({
                "chunk_id": entry.chunk_id,
                "chapter_id": chapter_id,
                "output_path": str(output_path),
                "duration_sec": duration_sec
            })

        return {
            "appended_manifest": json.dumps(completed_manifest, indent=2)
        }

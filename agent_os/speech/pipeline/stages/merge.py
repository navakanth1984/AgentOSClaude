import json
import numpy as np
from scipy.io import wavfile
from typing import Any, Dict, List
from pathlib import Path
from collections import defaultdict

from agent_os.speech.schema.models import ExecutionPlanEntry
from agent_os.speech.pipeline.executor import StageContext

class MergeStage:
    """
    Concatenates trimmed chunks into final chapter audio files.
    Inserts silent gaps based on pause_before_ms and pause_after_ms from the ExecutionPlan.
    """
    
    def name(self) -> str:
        return "merge"

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
        execution_plan: List[ExecutionPlanEntry] = ensure_execution_plan(inputs["trim"]["execution_plan"])
        
        # Check for failed chunks
        failed_chunks = [entry.chunk_id for entry in execution_plan if entry.status == "failed"]
        if failed_chunks:
            raise RuntimeError(f"MergeStage aborted: {len(failed_chunks)} chunks failed during synthesis: {failed_chunks}")
        
        # Group by chapter
        chapters = defaultdict(list)
        for entry in execution_plan:
            if entry.status == "completed":
                chapters[entry.chapter_id].append(entry)
                
        merged_manifest = []
        
        for chapter_id, entries in chapters.items():
            # Sort by chunk_id to ensure chronological order
            entries.sort(key=lambda x: x.chunk_id)
            
            chapter_audio = []
            target_sample_rate = None
            target_dtype = None
            
            for entry in entries:
                input_path = Path(entry.expected_output_path)
                
                try:
                    sample_rate, data = wavfile.read(str(input_path))
                except Exception as e:
                    print(f"Failed to read {input_path} during merge: {e}")
                    continue
                    
                # Audio validation (sample rate and dtype consistency)
                if target_sample_rate is None:
                    target_sample_rate = sample_rate
                    target_dtype = data.dtype
                else:
                    if target_sample_rate != sample_rate:
                        raise ValueError(f"Sample rate mismatch in {entry.expected_output_path}: expected {target_sample_rate}, got {sample_rate}")
                    if target_dtype != data.dtype:
                        raise ValueError(f"Dtype mismatch in {entry.expected_output_path}: expected {target_dtype}, got {data.dtype}")
                        
                # Invariant: both are set on the first successful read above.
                assert target_sample_rate is not None and target_dtype is not None

                # Ensure mono for now
                if len(data.shape) > 1:
                    raise ValueError(f"Expected mono audio, but got {data.shape[1]} channels in {entry.expected_output_path}")
                    
                # Generate pauses
                if entry.pause_before_ms > 0:
                    chapter_audio.append(self._generate_silence(entry.pause_before_ms, target_sample_rate, target_dtype))
                    
                chapter_audio.append(data)
                
                if entry.pause_after_ms > 0:
                    chapter_audio.append(self._generate_silence(entry.pause_after_ms, target_sample_rate, target_dtype))
                    
            if not chapter_audio or target_sample_rate is None:
                continue

            final_audio = np.concatenate(chapter_audio)
            
            # Save final file
            # E.g., <project_dir>/Chapter_1.wav
            output_path = Path(context.project_dir) / f"Chapter_{chapter_id}.wav"
            wavfile.write(str(output_path), target_sample_rate, final_audio)
            
            merged_manifest.append({
                "chapter_id": chapter_id,
                "output_path": str(output_path),
                "duration_sec": len(final_audio) / target_sample_rate
            })
            
        return {
            "merged_manifest": json.dumps(merged_manifest, indent=2)
        }

import json
import numpy as np
from scipy.io import wavfile
from typing import Any, Dict, List
from pathlib import Path
from dataclasses import replace

from agent_os.speech.schema.models import ExecutionPlanEntry
from agent_os.speech.pipeline.executor import StageContext

class TrimStage:
    """
    Trims silence from the beginning and end of synthesized audio chunks.
    Uses a dynamic noise-floor approach rather than fixed amplitude.
    """
    
    def name(self) -> str:
        return "trim"

    def _rms(self, frame: np.ndarray) -> float:
        # RMS = sqrt(mean(square(frame)))
        # Careful with overflow on int16 arrays, cast to float first
        if len(frame) == 0:
            return 0.0
        return float(np.sqrt(np.mean(frame.astype(np.float64)**2)))

    def run(self, context: StageContext, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inputs:
            inputs["synthesize"]["execution_plan"]: List[ExecutionPlanEntry]
        """
        from agent_os.speech.schema.models import ensure_execution_plan
        execution_plan: List[ExecutionPlanEntry] = ensure_execution_plan(inputs["synthesize"]["execution_plan"])
        
        # Config options
        trim_config = context.config.get("trim", {})
        frame_ms = trim_config.get("frame_ms", 20)
        multiplier = trim_config.get("multiplier", 3.0)
        min_threshold = trim_config.get("minimum_threshold", 50.0)
        
        trimmed_dir = Path(context.project_dir) / "trimmed"
        trimmed_dir.mkdir(parents=True, exist_ok=True)
        
        trimmed_plan: List[ExecutionPlanEntry] = []
        
        for entry in execution_plan:
            if entry.status != "completed":
                trimmed_plan.append(entry)
                continue
                
            input_path = Path(entry.expected_output_path)
            output_path = trimmed_dir / f"trimmed_{input_path.name}"
            
            # Read audio
            sample_rate, data = wavfile.read(str(input_path))
            
            if len(data) == 0:
                trimmed_plan.append(replace(entry, expected_output_path=str(output_path)))
                wavfile.write(str(output_path), sample_rate, data)
                continue
                
            frame_length = int(sample_rate * (frame_ms / 1000.0))
            
            # Estimate noise floor by looking at the first 100ms or 5 frames
            # Assuming it starts with relative silence
            num_noise_frames = min(5, len(data) // frame_length)
            noise_floor = 0.0
            if num_noise_frames > 0:
                noise_rms_vals = [
                    self._rms(data[i*frame_length : (i+1)*frame_length])
                    for i in range(num_noise_frames)
                ]
                noise_floor = sum(noise_rms_vals) / len(noise_rms_vals)
                
            dynamic_threshold = max(noise_floor * multiplier, min_threshold)
            
            # Find start
            start_idx = 0
            for i in range(0, len(data), frame_length):
                frame = data[i : i+frame_length]
                if self._rms(frame) > dynamic_threshold:
                    # Give a small buffer of 1 frame before the sound starts
                    start_idx = max(0, i - frame_length)
                    break
                    
            # Find end
            end_idx = len(data)
            for i in range(len(data) - frame_length, -1, -frame_length):
                frame = data[i : i+frame_length]
                if self._rms(frame) > dynamic_threshold:
                    end_idx = min(len(data), i + 2*frame_length)
                    break
                    
            # Trim
            trimmed_data = data[start_idx:end_idx]
            
            # Write
            wavfile.write(str(output_path), sample_rate, trimmed_data)
            
            trimmed_plan.append(replace(entry, expected_output_path=str(output_path)))
            
        trimmed_raw = [
            {
                "chunk_id": r.chunk_id,
                "chapter_id": r.chapter_id,
                "expected_output_path": r.expected_output_path
            }
            for r in trimmed_plan
        ]
        
        return {
            "execution_plan": trimmed_plan,
            "trimmed_raw": json.dumps(trimmed_raw, indent=2)
        }

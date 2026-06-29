import os
import tempfile
import time
from pathlib import Path
import pytest
import numpy as np

from agent_os.speech.service import SpeechService
from agent_os.speech.schema.jobs import SpeechJobStore, JobState, EventBus
from agent_os.speech.schema.models import EngineCapabilities, EngineName, Language
from agent_os.speech.pipeline.interfaces import TTSEngine

class FakeEngine(TTSEngine):
    def validate_model(self): pass
    def initialize(self): pass
    def warmup(self, profile="minimal"): pass
    def shutdown(self): pass
    def get_capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            engine_name=EngineName.KOKORO,
            supported_languages=[Language.EN],
            supported_voices={"af_heart": {}},
            max_text_length=500,
            max_concurrent_requests=1,
            supports_streaming=False,
            supports_emotions=False,
            supports_pitch=False,
            supports_speed=True,
            sample_rate=24000,
            output_format="wav"
        )
    def supports_language(self, language: Language) -> bool: return True
    def supports_voice(self, voice: str) -> bool: return True
    def synthesize(self, text: str, voice: str, language: Language, speed: float) -> tuple[int, np.ndarray]:
        return 24000, np.zeros(2400, dtype=np.int16)

def test_speech_service_lifecycle():
    from unittest.mock import patch
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Mock EngineRegistry to return FakeEngine
        with patch("agent_os.speech.engines.registry.EngineRegistry.get_engine", return_value=FakeEngine()):
            
            # 1. Create text file
            text_file = Path(tmp_dir) / "input.txt"
            text_file.write_text("Hello. This is service test.")
            
            payload = {
                "text_path": str(text_file),
                "engine": "kokoro",
                "voice": "af_heart"
            }
            
            # Modify os.getcwd to save jobs in temp dir
            with patch("os.getcwd", return_value=tmp_dir):
                # 2. Create Job
                job = SpeechService.create_job(payload, output_dir=os.path.join(tmp_dir, "outputs"))
                assert job.state == JobState.QUEUED
                assert Path(job.output_directory).exists()
                
                # Check saved details
                loaded = SpeechJobStore.load(job.job_id)
                assert loaded is not None
                assert loaded.state == JobState.QUEUED
                
                # 3. Run Job
                bus = EventBus()
                events = []
                def listener(evt):
                    events.append(evt)
                bus.subscribe(listener)
                
                SpeechService.run_job(job.job_id, background=False, custom_bus=bus)
                
                # Verify completed details
                completed_job = SpeechService.get_job(job.job_id)
                assert completed_job is not None
                assert completed_job.state == JobState.COMPLETED
                
                # Verify final files
                assert (Path(completed_job.output_directory) / "Chapter_0.wav").exists()
                assert (Path(completed_job.output_directory) / "events.jsonl").exists()
                assert (Path(completed_job.output_directory) / "job.json").exists()
                
                assert len(events) > 0
                assert events[0].event_type == "pipeline_started"

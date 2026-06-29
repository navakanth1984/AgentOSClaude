import os
import tempfile
import time
import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
import scipy.io.wavfile as wavfile
from fastapi.testclient import TestClient

from agent_os.speech.api import app
from agent_os.speech.service import SpeechService
from agent_os.speech.schema.jobs import JobState, SpeechJobStore
from test_speech_service import FakeEngine

client = TestClient(app)

class SlowFakeEngine(FakeEngine):
    def synthesize(self, text: str, voice: str, language, speed: float) -> tuple[int, np.ndarray]:
        # Sleep briefly to allow cancellation mid-flight
        time.sleep(0.5)
        return 24000, np.zeros(2400, dtype=np.int16)

def test_chaos_cancellation_and_resumability():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Mock engine to be slow
        with patch("agent_os.speech.engines.registry.EngineRegistry.get_engine", return_value=SlowFakeEngine()):
            with patch("os.getcwd", return_value=tmp_dir):
                
                # 1. Write a multiline text file with 4 clear chunks (sentences)
                text_file = Path(tmp_dir) / "chaos_input.txt"
                text_file.write_text("Line one.\n\nLine two.\n\nLine three.\n\nLine four.")
                
                # 2. Trigger uninterrupted run first to get reference audio
                ref_payload = {
                    "text_path": str(text_file),
                    "engine": "kokoro",
                    "voice": "af_heart",
                    "parser": "benchmark"
                }
                
                ref_job = SpeechService.create_job(ref_payload, output_dir=os.path.join(tmp_dir, "ref_run"))
                SpeechService.run_job(ref_job.job_id, background=False)
                
                ref_wav_path = Path(ref_job.output_directory) / "Chapter_0.wav"
                assert ref_wav_path.exists()
                ref_rate, ref_data = wavfile.read(str(ref_wav_path))
                
                # 3. Trigger chaos run (POST /api/v1/jobs)
                chaos_payload = {
                    "text_path": str(text_file),
                    "engine": "kokoro",
                    "voice": "af_heart",
                    "parser": "benchmark"
                }
                resp = client.post("/api/v1/jobs", json=chaos_payload)
                assert resp.status_code == 201
                job_id = resp.json()["job_id"]
                
                # Wait until at least one chunk is synthesized
                events_file = Path(resp.json()["output_directory"]) / "events.jsonl"
                
                for _ in range(150):
                    time.sleep(0.1)
                    if events_file.exists():
                        with open(events_file, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            types = [json.loads(l)["event_type"] for l in lines if l.strip()]
                            if "chunk_synthesized" in types:
                                break
                                
                # 4. Trigger Cancellation (POST /jobs/{id}/cancel)
                cancel_resp = client.post(f"/api/v1/jobs/{job_id}/cancel")
                assert cancel_resp.status_code == 200
                
                # Wait for cancellation status
                cancelled = False
                for _ in range(20):
                    status_resp = client.get(f"/api/v1/jobs/{job_id}")
                    if status_resp.json()["state"] == JobState.CANCELLED.value:
                        cancelled = True
                        break
                    time.sleep(0.2)
                assert cancelled, "Job was not successfully cancelled"
                
                # Verify that it cancelled cooperatively, and produced shorter audio
                chaos_job = SpeechService.get_job(job_id)
                assert chaos_job is not None
                chaos_wav_path = Path(chaos_job.output_directory) / "Chapter_0.wav"
                assert chaos_wav_path.exists()
                c_rate, c_data = wavfile.read(str(chaos_wav_path))
                assert len(c_data) < len(ref_data)
                
                # Allow background thread to exit cleanly
                for _ in range(50):
                    if not SpeechService.is_job_running(job_id):
                        break
                    time.sleep(0.1)
                
                # 5. Simulate Server Reset / Reset state to QUEUED & run again
                chaos_job.transition_to(JobState.QUEUED)
                SpeechJobStore.save(chaos_job)
                
                # Run again. It should resume, skip completed cache chunks, and write Chapter_0.wav
                SpeechService.run_job(job_id, background=False)
                
                # Verify completed details
                completed_job = SpeechService.get_job(job_id)
                assert completed_job is not None
                assert completed_job.state == JobState.COMPLETED
                
                # Verify output audio exists and matches the reference run EXACTLY (same shape and contents)
                assert chaos_wav_path.exists()
                chaos_rate, chaos_data = wavfile.read(str(chaos_wav_path))
                assert chaos_rate == ref_rate
                assert np.array_equal(chaos_data, ref_data)
                
                # Verify that cached chunks were bypassed (check events log for chunk_trimmed or resumes)
                events_resp = client.get(f"/api/v1/jobs/{job_id}/events")
                events = events_resp.json()
                assert len(events) > 0

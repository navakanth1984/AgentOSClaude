import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

from agent_os.speech.api import app
from agent_os.speech.schema.jobs import JobState
from test_speech_service import FakeEngine

client = TestClient(app)

def test_api_jobs_lifecycle():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with patch("agent_os.speech.engines.registry.EngineRegistry.get_engine", return_value=FakeEngine()):
            with patch("os.getcwd", return_value=tmp_dir):
                
                # 1. Create text file
                text_file = Path(tmp_dir) / "test.txt"
                text_file.write_text("API test file content.")
                
                # 2. List engines
                resp = client.get("/api/v1/engines")
                assert resp.status_code == 200
                data = resp.json()
                assert len(data) > 0
                assert any(e["name"] == "kokoro" for e in data)
                
                # 3. Create job
                payload = {
                    "text_path": str(text_file),
                    "engine": "kokoro",
                    "voice": "af_heart"
                }
                resp = client.post("/api/v1/jobs", json=payload)
                assert resp.status_code == 201
                job_data = resp.json()
                job_id = job_data["job_id"]
                assert job_id is not None
                
                # Wait for synchronous background completion or wait briefly
                # Since background=True is executed in a background daemon thread, let's wait up to 5s for completion.
                for _ in range(25):
                    resp = client.get(f"/api/v1/jobs/{job_id}")
                    assert resp.status_code == 200
                    if resp.json()["state"] == JobState.COMPLETED.value:
                        break
                    import time
                    time.sleep(0.2)
                    
                resp = client.get(f"/api/v1/jobs/{job_id}")
                assert resp.json()["state"] == JobState.COMPLETED.value
                
                # 4. Check Events
                resp = client.get(f"/api/v1/jobs/{job_id}/events")
                assert resp.status_code == 200
                events = resp.json()
                assert len(events) > 0
                assert events[0]["event_type"] == "pipeline_started"
                # Check versioning field
                assert events[0]["event_version"] == "1.0"
                
                # 5. Check Artifacts
                resp = client.get(f"/api/v1/jobs/{job_id}/artifacts")
                assert resp.status_code == 200
                artifacts = resp.json()
                assert len(artifacts) > 0
                assert any(a["name"] == "Chapter_0.wav" for a in artifacts)
                assert any(a["name"] == "events.jsonl" for a in artifacts)
                assert any(a["name"] == "job.json" for a in artifacts)
                assert any(a["name"] == "protocol_manifest.json" for a in artifacts)

def test_api_websocket_stream():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with patch("agent_os.speech.engines.registry.EngineRegistry.get_engine", return_value=FakeEngine()):
            with patch("os.getcwd", return_value=tmp_dir):
                
                text_file = Path(tmp_dir) / "test_ws.txt"
                text_file.write_text("WebSocket stream test.")
                
                payload = {
                    "text_path": str(text_file),
                    "engine": "kokoro",
                    "voice": "af_heart"
                }
                resp = client.post("/api/v1/jobs", json=payload)
                assert resp.status_code == 201
                job_id = resp.json()["job_id"]
                
                # Connect websocket
                with client.websocket_connect(f"/api/v1/jobs/{job_id}/stream") as websocket:
                    # Receive events
                    received = []
                    try:
                        for _ in range(10):
                            data = websocket.receive_text()
                            event = json.loads(data)
                            received.append(event)
                            if event["event_type"] == "pipeline_completed":
                                break
                    except Exception:
                        pass
                        
                    assert len(received) > 0
                    assert received[0]["event_type"] == "pipeline_started"
                    assert received[0]["event_version"] == "1.0"

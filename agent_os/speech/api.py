import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, status
from pydantic import BaseModel

from agent_os.speech.service import SpeechService
from agent_os.speech.schema.jobs import JobState, SpeechJobStore
from agent_os.speech.engines.registry import EngineRegistry

app = FastAPI(
    title="Agent OS Speech API",
    description="REST & WebSocket interface for the Speech execution platform",
    version="1.0"
)

class JobCreatePayload(BaseModel):
    text_path: str
    engine: str = "kokoro"
    voice: str = "default"

class JobResponse(BaseModel):
    job_id: str
    state: str
    output_directory: str
    assets_manifest: Optional[Dict[str, Any]] = None

@app.post("/api/v1/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreatePayload):
    # Verify input text file exists
    text_file = Path(payload.text_path)
    if not text_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text file {payload.text_path} not found."
        )
    
    # Create the job via SpeechService
    job = SpeechService.create_job(payload.model_dump())
    
    # Kick off in background using SpeechService's threading model
    SpeechService.run_job(job.job_id, background=True)
    
    return JobResponse(
        job_id=job.job_id,
        state=job.state.value,
        output_directory=job.output_directory,
        assets_manifest=job.assets_manifest
    )

@app.get("/api/v1/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str):
    job = SpeechService.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found."
        )
    return JobResponse(
        job_id=job.job_id,
        state=job.state.value,
        output_directory=job.output_directory,
        assets_manifest=job.assets_manifest
    )

@app.post("/api/v1/jobs/{job_id}/cancel")
def cancel_job(job_id: str):
    job = SpeechService.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found."
        )
    SpeechService.cancel_job(job_id)
    return {"message": f"Cancellation request sent for job {job_id}."}

@app.get("/api/v1/jobs/{job_id}/events")
def get_job_events(job_id: str) -> List[Dict[str, Any]]:
    events = SpeechService.get_events(job_id)
    if not events:
        # Check if job exists
        job = SpeechService.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found."
            )
    return events

@app.get("/api/v1/jobs/{job_id}/artifacts")
def get_job_artifacts(job_id: str) -> List[Dict[str, Any]]:
    job = SpeechService.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found."
        )
    
    output_path = Path(job.output_directory)
    if not output_path.exists():
        return []
        
    artifacts = []
    for f in output_path.glob("**/*"):
        if f.is_file():
            artifacts.append({
                "name": f.name,
                "relative_path": str(f.relative_to(output_path)),
                "size_bytes": f.stat().st_size
            })
    return artifacts

@app.get("/api/v1/engines")
def list_engines() -> List[Dict[str, Any]]:
    engines = []
    # Query EngineRegistry capabilities
    for name in ["kokoro", "piper"]:
        try:
            engine = EngineRegistry.get_engine({"engine_name": name})
            caps = engine.get_capabilities()
            engines.append({
                "name": name,
                "supported_languages": [lang.value for lang in caps.supported_languages],
                "supported_voices": list(caps.supported_voices.keys()),
                "sample_rate": caps.sample_rate,
                "output_format": caps.output_format
            })
        except Exception:
            pass
    return engines

@app.websocket("/api/v1/jobs/{job_id}/stream")
async def stream_job_events(websocket: WebSocket, job_id: str):
    await websocket.accept()
    job = SpeechService.get_job(job_id)
    if not job:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Job not found")
        return
        
    events_path = Path(job.output_directory) / "events.jsonl"
    
    # Send existing lines
    sent_count = 0
    if events_path.exists():
        with open(events_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    await websocket.send_text(line.strip())
                    sent_count += 1
                    
    # Tail the events file
    last_size = events_path.stat().st_size if events_path.exists() else 0
    try:
        while True:
            job = SpeechService.get_job(job_id)
            if not job:
                break
                
            if events_path.exists():
                current_size = events_path.stat().st_size
                if current_size > last_size:
                    with open(events_path, "r", encoding="utf-8") as f:
                        f.seek(last_size)
                        for line in f:
                            if line.strip():
                                await websocket.send_text(line.strip())
                    last_size = current_size
            
            # Stop stream once job terminal state is reached AND file has been fully read
            if job.state in [JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED]:
                # Final check for any lingering writes
                if events_path.exists():
                    current_size = events_path.stat().st_size
                    if current_size > last_size:
                        with open(events_path, "r", encoding="utf-8") as f:
                            f.seek(last_size)
                            for line in f:
                                if line.strip():
                                    await websocket.send_text(line.strip())
                break
                
            await asyncio.sleep(0.2)
    except Exception:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass

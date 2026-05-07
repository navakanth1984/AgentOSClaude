import sqlite3
import json
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
import sys
from pathlib import Path
import shutil
from datetime import datetime
import traceback
import time

import base64

# ... (rest of imports)

# Check if LTX dependencies are available
try:
    # Add ltx_video_source to path to import ltx_video modules
    sys.path.append(str(Path(__file__).parent.parent / "ltx_video_source"))
    from ltx_video.inference import infer, InferenceConfig
    HAS_LTX = True
except ImportError:
    HAS_LTX = False
    class InferenceConfig:
        def __init__(self, **kwargs):
            for k, v in kwargs.items(): setattr(self, k, v)
    
    def infer(config):
        print(f"MOCK INFERENCE for prompt: {config.prompt}")
        time.sleep(5) # Simulate work
        # Create a valid minimal MP4 file (1-second black video)
        MINIMAL_MP4_B64 = "AAAAIGZ0eXBpc29tAAACAGlzb21pbmYxbXA0MgAAAChmcmVlAAAAH21kYXQAAAGUAbXBlZzRfc3Bfdm9jYV9kZWNvZGVyAAABy21vb3YAAABsbXZoZAAAAAAAAAAAAAAAAAAAA+gAAAAAAAEAAAEAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAI0dHJhawAAAFx0a2hkAAAAAwAAAAAAAAAAAAAAAQAAAAAAAAPoAAAAAAAAAAAAAAAAAQAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAbWRpYQAAACBtZGhkAAAAAAAAAAAAAAAAAAB9AAAC7xUAAAAAADHWhGxlAAAAHWhkbHIAAAAAAAAAAHZpZGUAAAAAAAAAAAAAAABWaWRlb0hhbmRsZXIAAAAB321pbmYAAAAUdm1oZAAAAAEAAAAAAAAAAAAAACRkaW5mAAAAHGRyZWYAAAAAAAAAAQAAAAx1cmwgAAAAAQAAAbVzdGJsAAAAr3N0c2QAAAAAAAAAAQAAAJ9tcDR2AAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAHgAeABIAAAASAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGP//AAAALWVzZHMAAAAAAAMcAAEABYAAABYBAf8BBAAAABYFAf8GBAAAABYHAf8IAAAAAAAhAAAAGHN0dHMAAAAAAAAAAQAAAAEAAAB9AAAAFHN0c3oAAAAAAAAAAAAAAAEAAABMc3RzYwAAAAAAAAABAAAAAQAAAAEAAAABAAAAFHN0Y28AAAAAAAAAAQAAADQAAAAIdWR0YQAAABptZXRhAAAAAAAAACFoZGxyAAAAAAAAAABtZGlyAAAAAAAAAAAAAAAAAAAAAA=="
        
        job_dir = Path(config.output_path)
        job_dir.mkdir(parents=True, exist_ok=True)
        with open(job_dir / "mock_video.mp4", "wb") as f:
            f.write(base64.b64decode(MINIMAL_MP4_B64))


from agents import NexusOrchestrator

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "LTX-Video API is running", "mode": "Mock" if not HAS_LTX else "Production"}

# Initialize Agent Swarm
nexus = NexusOrchestrator()

# Temporary storage for uploads and outputs
UPLOAD_DIR = Path("uploads").absolute()
OUTPUT_DIR = Path("outputs").absolute()
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files with absolute path
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = "jobs.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT,
                prompt TEXT,
                output_url TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

init_db()

def update_job_status(job_id: str, status: str, output_url: str = None, error: str = None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, output_url = ?, error = ? WHERE job_id = ?",
            (status, output_url, error, job_id)
        )

class GenerationStatus(BaseModel):
    job_id: str
    status: str
    output_url: Optional[str] = None
    error: Optional[str] = None

def run_inference(job_id: str, config: InferenceConfig):
    try:
        update_job_status(job_id, "processing")
        job_output_dir = OUTPUT_DIR / job_id
        config.output_path = str(job_output_dir)
        job_output_dir.mkdir(parents=True, exist_ok=True)
        
        infer(config)
        
        generated_files = list(job_output_dir.glob("*.mp4")) + list(job_output_dir.glob("*.png"))
        
        if generated_files:
            filename = generated_files[0].name
            # Log absolute path for debugging
            print(f"Generated file absolute path: {generated_files[0].absolute()}")
            output_url = f"/outputs/{job_id}/{filename}"
            update_job_status(job_id, "completed", output_url=output_url)
        else:
            update_job_status(job_id, "failed", error="No output file generated.")
            
    except Exception as e:
        traceback.print_exc()
        update_job_status(job_id, "failed", error=str(e))

@app.post("/generate", response_model=GenerationStatus)
async def generate(
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),
    negative_prompt: str = Form("worst quality, inconsistent motion, blurry, jittery, distorted"),
    seed: int = Form(171198),
    height: int = Form(704),
    width: int = Form(1216),
    num_frames: int = Form(121),
    frame_rate: int = Form(30),
    offload_to_cpu: bool = Form(False),
    pipeline_config: str = Form("configs/ltxv-2b-0.9.8-distilled.yaml"),
    input_media: Optional[UploadFile] = File(None),
    user_tier: str = Form("free")
):
    try:
        # Run prompt through Agent Swarm (Security, Legal, Director)
        pipeline_data = nexus.run_pipeline(prompt, user_tier)
        final_prompt = pipeline_data["final_prompt"]
        legal_metadata = pipeline_data["legal_metadata"]
        
        job_id = str(uuid.uuid4())
        
        # Store job with legal metadata
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO jobs (job_id, status, prompt, error) VALUES (?, ?, ?, ?)",
                (job_id, "pending", prompt, f"License: {legal_metadata['license']}")
            )
        
        input_media_path = None
        if input_media:
            input_media_path = UPLOAD_DIR / f"{job_id}_{input_media.filename}"
            with input_media_path.open("wb") as buffer:
                shutil.copyfileobj(input_media.file, buffer)
            input_media_path = str(input_media_path)
        
        config = InferenceConfig(
            prompt=final_prompt, # Use enhanced prompt from Director Agent
            negative_prompt=negative_prompt,
            seed=seed,
            height=height,
            width=width,
            num_frames=num_frames,
            frame_rate=frame_rate,
            offload_to_cpu=offload_to_cpu,
            input_media_path=input_media_path,
            pipeline_config=pipeline_config
        )
        
        background_tasks.add_task(run_inference, job_id, config)
        return GenerationStatus(job_id=job_id, status="pending")
        
    except Exception as e:
        # If an agent rejects the request (Security/Legal), raise a 400
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/status/{job_id}", response_model=GenerationStatus)
async def get_status(job_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT status, output_url, error FROM jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        
    if not row:
        return GenerationStatus(job_id=job_id, status="not_found", error="Job ID not found")
    
    return GenerationStatus(
        job_id=job_id,
        status=row[0],
        output_url=row[1],
        error=row[2]
    )

@app.get("/history", response_model=List[GenerationStatus])
async def get_history():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT job_id, status, output_url, error FROM jobs ORDER BY created_at DESC LIMIT 20")
        rows = cursor.fetchall()
    
    return [
        GenerationStatus(job_id=r[0], status=r[1], output_url=r[2], error=r[3])
        for r in rows
    ]

@app.get("/configs")
async def get_available_configs():
    configs_dir = Path(__file__).parent.parent / "ltx_video_source" / "configs"
    configs = [f"configs/{f.name}" for f in configs_dir.glob("*.yaml")]
    return {"configs": configs}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import os
import uuid
import time
import threading
from typing import Dict, Any, List, Optional
from pathlib import Path

from agent_os.speech.schema.jobs import SpeechJob, JobState, SpeechJobStore, EventBus
from agent_os.speech.engines.registry import EngineRegistry
from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.pipeline.graph import DAG
from agent_os.speech.pipeline.stages.normalize import NormalizeStage
from agent_os.speech.pipeline.stages.parse import ParseStage
from agent_os.speech.pipeline.stages.segment import SegmentStage
from agent_os.speech.pipeline.stages.context import ContextStage
from agent_os.speech.pipeline.stages.route import RouteStage
from agent_os.speech.pipeline.stages.synthesize import SynthesizeStage
from agent_os.speech.pipeline.stages.trim import TrimStage
from agent_os.speech.pipeline.stages.append import AppendStage
from agent_os.speech.pipeline.incremental_executor import IncrementalExecutor

class SpeechService:
    _active_threads: Dict[str, threading.Thread] = {}

    @classmethod
    def is_job_running(cls, job_id: str) -> bool:
        return job_id in cls._active_threads

    @staticmethod
    def create_job(payload: Dict[str, Any], output_dir: Optional[str] = None) -> SpeechJob:
        job_id = str(uuid.uuid4())
        if not output_dir:
            output_dir = os.path.abspath(os.path.join("jobs", job_id))
        os.makedirs(output_dir, exist_ok=True)

        job = SpeechJob(
            job_id=job_id,
            request_payload=payload,
            output_directory=output_dir,
            state=JobState.QUEUED
        )
        SpeechJobStore.save(job)
        
        # Write unified protocol manifest
        import json
        manifest_data = {
            "protocols": {
                "events": "1.0",
                "benchmark": "1.0",
                "assets_manifest": "1.0",
                "performance_profile": "1.1",
                "job": "1.0"
            },
            "speech_framework_version": "1.2.0"
        }
        with open(os.path.join(output_dir, "protocol_manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        return job

    @classmethod
    def run_job(cls, job_id: str, background: bool = False, custom_bus: Optional[EventBus] = None) -> None:
        job = SpeechJobStore.load(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found.")

        if background:
            t = threading.Thread(target=cls._execute, args=(job_id, custom_bus))
            t.daemon = True
            cls._active_threads[job_id] = t
            t.start()
        else:
            cls._execute(job_id, custom_bus)

    @classmethod
    def _execute(cls, job_id: str, custom_bus: Optional[EventBus] = None) -> None:
        try:
            cls._execute_inner(job_id, custom_bus)
        finally:
            cls._active_threads.pop(job_id, None)

    @classmethod
    def _execute_inner(cls, job_id: str, custom_bus: Optional[EventBus] = None) -> None:
        job = SpeechJobStore.load(job_id)
        if not job:
            return

        payload = job.request_payload
        text_path = payload.get("text_path")
        engine_name = payload.get("engine", "kokoro")
        voice_name = payload.get("voice", "default")
        if not text_path or not isinstance(text_path, str):
            job.transition_to(JobState.FAILED)
            SpeechJobStore.save(job)
            return
            
        # Load text
        try:
            with open(text_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            job.transition_to(JobState.FAILED)
            SpeechJobStore.save(job)
            return

        # Load Engine
        try:
            engine = EngineRegistry.get_engine({"engine_name": engine_name})
            engine.initialize()
            engine.validate_model()
            engine.warmup("minimal")
            caps = engine.get_capabilities()
        except Exception as e:
            job.transition_to(JobState.FAILED)
            SpeechJobStore.save(job)
            return

        # Setup EventBus
        bus = custom_bus or EventBus()
        
        def job_event_listener(event):
            job.record_event(event)
            # Write structured events.jsonl
            events_file = Path(job.output_directory) / "events.jsonl"
            try:
                with open(events_file, "a", encoding="utf-8") as f:
                    import json
                    f.write(json.dumps(event.to_json()) + "\n")
            except Exception:
                pass

            if event.event_type == "pipeline_started":
                job.transition_to(JobState.PLANNING)
            elif event.event_type == "chunk_started" and job.state == JobState.PLANNING:
                job.transition_to(JobState.SYNTHESIZING)
            elif event.event_type == "pipeline_completed":
                job.transition_to(JobState.COMPLETED)
            SpeechJobStore.save(job)

        bus.subscribe(job_event_listener)

        config = {
            "input_text": text,
            "chapter_id": "0",
            "engine_capabilities": caps,
            "tts_engine": engine,
            "max_workers": 2,
            **{k: v for k, v in payload.items() if k not in ["text_path", "engine", "voice"]}
        }
        
        ctx = StageContext(
            project_dir=job.output_directory,
            cache_dir=os.path.join(job.output_directory, "cache"),
            config=config,
            artifacts={},
            metrics={},
            event_bus=bus,
            run_id=job_id
        )

        dag = DAG()
        dag.add_node("normalize", NormalizeStage())
        dag.add_node("parse", ParseStage(), depends_on=["normalize"])
        dag.add_node("segment", SegmentStage(), depends_on=["parse"])
        dag.add_node("context", ContextStage(), depends_on=["segment"])
        dag.add_node("route", RouteStage(), depends_on=["context", "parse"])
        dag.add_node("synthesize", SynthesizeStage(), depends_on=["route"])
        dag.add_node("trim", TrimStage(), depends_on=["synthesize"])
        dag.add_node("append", AppendStage(), depends_on=["trim"])
        
        executor = IncrementalExecutor(dag, ctx)
        
        try:
            executor.run()
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Check if job was cancelled cooperatively
            current_job = SpeechJobStore.load(job_id)
            if current_job and current_job.state == JobState.CANCELLED:
                return
            job.transition_to(JobState.FAILED)
            SpeechJobStore.save(job)
            return

        # Record completion
        current_job = SpeechJobStore.load(job_id)
        if current_job and current_job.state == JobState.CANCELLED:
            return

        job.transition_to(JobState.COMPLETED)
        job.assets_manifest = {
            "engine": engine_name,
            "voice": voice_name,
            "output_directory": job.output_directory
        }
        SpeechJobStore.save(job)

        # Write final job.json in output directory directly
        with open(os.path.join(job.output_directory, "job.json"), "w", encoding="utf-8") as f:
            import json
            json.dump(job.to_dict(), f, indent=2)

        # Copy telemetry artifacts to the job dir
        metrics_src = Path(job.output_directory) / "metrics"
        if metrics_src.exists():
            for f in metrics_src.glob("*"):
                if f.is_file():
                    import shutil
                    shutil.copy(str(f), str(Path(job.output_directory) / f.name))

    @staticmethod
    def cancel_job(job_id: str) -> None:
        job = SpeechJobStore.load(job_id)
        if job:
            job.transition_to(JobState.CANCELLED)
            SpeechJobStore.save(job)

    @staticmethod
    def get_job(job_id: str) -> Optional[SpeechJob]:
        return SpeechJobStore.load(job_id)

    @staticmethod
    def get_events(job_id: str) -> List[Dict[str, Any]]:
        job = SpeechJobStore.load(job_id)
        return job.event_log if job else []

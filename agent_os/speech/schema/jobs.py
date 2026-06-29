from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time
import os
from pathlib import Path

from agent_os.speech.schema.models import ExecutionPlanEntry
from agent_os.speech.schema.events import PipelineEvent

class JobState(str, Enum):
    QUEUED = "queued"
    PLANNING = "planning"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class SpeechJob:
    job_id: str
    request_payload: Dict[str, Any]
    output_directory: str
    state: JobState = JobState.QUEUED
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    execution_plan: Optional[List[ExecutionPlanEntry]] = None
    assets_manifest: Optional[Dict[str, Any]] = None
    performance_profile: Optional[Dict[str, Any]] = None
    event_log: List[Dict[str, Any]] = field(default_factory=list)

    def transition_to(self, new_state: JobState) -> None:
        self.state = new_state
        self.updated_at = time.time()

    def record_event(self, event: PipelineEvent) -> None:
        self.event_log.append(event.to_json())
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "state": self.state.value,
            "request_payload": self.request_payload,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "execution_plan": [e.__dict__ for e in self.execution_plan] if self.execution_plan else None,
            "assets_manifest": self.assets_manifest,
            "performance_profile": self.performance_profile,
            "event_log": self.event_log,
            "output_directory": self.output_directory
        }

class EventBus:
    def __init__(self):
        self.listeners = []

    def subscribe(self, callback) -> None:
        if callback not in self.listeners:
            self.listeners.append(callback)

    def unsubscribe(self, callback) -> None:
        if callback in self.listeners:
            self.listeners.remove(callback)

    def publish(self, event: PipelineEvent) -> None:
        for listener in self.event_listeners if hasattr(self, 'event_listeners') else self.listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"[EventBus] Listener invocation error: {e}")

class SpeechJobStore:
    @staticmethod
    def get_job_dir(job_id: str) -> Path:
        p = Path(os.getcwd()) / "jobs" / job_id
        p.mkdir(parents=True, exist_ok=True)
        return p

    @classmethod
    def save(cls, job: SpeechJob) -> None:
        import json
        job_dir = cls.get_job_dir(job.job_id)
        job_file = job_dir / "job.json"
        with open(job_file, "w", encoding="utf-8") as f:
            json.dump(job.to_dict(), f, indent=2)

    @classmethod
    def load(cls, job_id: str) -> Optional[SpeechJob]:
        import json
        p = Path(os.getcwd()) / "jobs" / job_id / "job.json"
        if not p.is_file():
            return None
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
            
        plan = None
        if d.get("execution_plan"):
            plan = []
            from agent_os.speech.schema.models import ExecutionPlanEntry, EngineName, Language
            for e in d["execution_plan"]:
                plan.append(ExecutionPlanEntry(
                    chunk_id=e.get("chunk_id", 0),
                    chapter_id=e.get("chapter_id", ""),
                    text=e.get("text", ""),
                    engine=EngineName(e.get("engine", "kokoro")),
                    voice=e.get("voice", ""),
                    language=Language(e.get("language", "en")),
                    speed=e.get("speed", 1.0),
                    pitch=e.get("pitch", 1.0),
                    volume_gain_db=e.get("volume_gain_db", 0.0),
                    cache_key=e.get("cache_key", ""),
                    expected_output_path=e.get("expected_output_path", ""),
                    pause_before_ms=e.get("pause_before_ms", 0),
                    pause_after_ms=e.get("pause_after_ms", 0),
                    status=e.get("status", "pending")
                ))
                
        return SpeechJob(
            job_id=d["job_id"],
            request_payload=d["request_payload"],
            output_directory=d["output_directory"],
            state=JobState(d["state"]),
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            execution_plan=plan,
            assets_manifest=d.get("assets_manifest"),
            performance_profile=d.get("performance_profile"),
            event_log=d.get("event_log", [])
        )

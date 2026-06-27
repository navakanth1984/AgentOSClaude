from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time

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
        for listener in self.listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"[EventBus] Listener invocation error: {e}")

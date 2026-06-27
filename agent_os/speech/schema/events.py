from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class PipelineEvent:
    event_type: str
    run_id: str
    timestamp: float

    def to_json(self) -> Dict[str, Any]:
        return {
            "event_version": "1.0",
            "event_type": self.event_type,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            **{k: v for k, v in self.__dict__.items() if k not in ["event_type", "run_id", "timestamp"]}
        }

@dataclass
class PipelineStarted(PipelineEvent):
    def __init__(self, run_id: str, timestamp: float):
        super().__init__("pipeline_started", run_id, timestamp)

@dataclass
class ChunkStarted(PipelineEvent):
    chunk_id: int
    def __init__(self, run_id: str, timestamp: float, chunk_id: int):
        super().__init__("chunk_started", run_id, timestamp)
        self.chunk_id = chunk_id

@dataclass
class ChunkSynthesized(PipelineEvent):
    chunk_id: int
    sample_rate: int
    duration_sec: float
    def __init__(self, run_id: str, timestamp: float, chunk_id: int, sample_rate: int, duration_sec: float):
        super().__init__("chunk_synthesized", run_id, timestamp)
        self.chunk_id = chunk_id
        self.sample_rate = sample_rate
        self.duration_sec = duration_sec

@dataclass
class ChunkTrimmed(PipelineEvent):
    chunk_id: int
    duration_sec: float
    def __init__(self, run_id: str, timestamp: float, chunk_id: int, duration_sec: float):
        super().__init__("chunk_trimmed", run_id, timestamp)
        self.chunk_id = chunk_id
        self.duration_sec = duration_sec

@dataclass
class ChunkAppended(PipelineEvent):
    chunk_id: int
    accumulated_duration_sec: float
    output_path: str
    def __init__(self, run_id: str, timestamp: float, chunk_id: int, accumulated_duration_sec: float, output_path: str):
        super().__init__("chunk_appended", run_id, timestamp)
        self.chunk_id = chunk_id
        self.accumulated_duration_sec = accumulated_duration_sec
        self.output_path = output_path

@dataclass
class ChapterProgress(PipelineEvent):
    chapter_id: str
    completed_chunks: int
    total_chunks: int
    def __init__(self, run_id: str, timestamp: float, chapter_id: str, completed_chunks: int, total_chunks: int):
        super().__init__("chapter_progress", run_id, timestamp)
        self.chapter_id = chapter_id
        self.completed_chunks = completed_chunks
        self.total_chunks = total_chunks

@dataclass
class ChapterCompleted(PipelineEvent):
    chapter_id: str
    output_path: str
    def __init__(self, run_id: str, timestamp: float, chapter_id: str, output_path: str):
        super().__init__("chapter_completed", run_id, timestamp)
        self.chapter_id = chapter_id
        self.output_path = output_path

@dataclass
class PipelineCompleted(PipelineEvent):
    total_duration_sec: float
    def __init__(self, run_id: str, timestamp: float, total_duration_sec: float):
        super().__init__("pipeline_completed", run_id, timestamp)
        self.total_duration_sec = total_duration_sec

import time
from agent_os.speech.schema.jobs import SpeechJob, JobState
from agent_os.speech.schema.events import PipelineStarted, ChunkStarted, PipelineCompleted

def test_speech_job_lifecycle_and_serialization():
    job = SpeechJob(
        job_id="job_test_123",
        request_payload={"text": "Hello world"},
        output_directory="/tmp/output"
    )
    
    assert job.state == JobState.QUEUED
    assert len(job.event_log) == 0
    
    # Transition to PLANNING
    job.transition_to(JobState.PLANNING)
    assert job.state == JobState.PLANNING
    
    # Record events
    evt1 = PipelineStarted(run_id="job_test_123", timestamp=time.time())
    job.record_event(evt1)
    
    evt2 = ChunkStarted(run_id="job_test_123", timestamp=time.time(), chunk_id=0)
    job.record_event(evt2)
    
    assert len(job.event_log) == 2
    assert job.event_log[0]["event_type"] == "pipeline_started"
    assert job.event_log[1]["event_type"] == "chunk_started"
    assert job.event_log[1]["chunk_id"] == 0
    
    # Transition to COMPLETED
    job.transition_to(JobState.COMPLETED)
    assert job.state == JobState.COMPLETED
    
    # Check dict representation
    d = job.to_dict()
    assert d["job_id"] == "job_test_123"
    assert d["state"] == "completed"
    assert d["request_payload"] == {"text": "Hello world"}
    assert len(d["event_log"]) == 2
    assert d["output_directory"] == "/tmp/output"

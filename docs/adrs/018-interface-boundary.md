# ADR-018: Interface Boundary and SpeechService Isolation

## Context

As we introduce additional interaction surfaces to the speech subsystem (CLI, REST API, WebSocket streams, and future web/desktop frontends), there is a high risk of architectural drift and orchestration duplication. Each client layer might independently handle task queuing, state transitions, event formatting, or disk layout behaviors.

To prevent this:
1. We must enforce a strict boundary between interface clients (CLI, REST, WebSocket) and the execution core.
2. We need a unified **Domain Service** layer (`SpeechService`) that wraps all lifecycle orchestrations (`create_job`, `run_job`, `cancel_job`, `get_job`, `get_events`).
3. Interface adapters must interact *exclusively* via this domain service, passing and receiving domain models (`SpeechJob`, `PipelineEvent`) and immutable output directories.

## Proposed Design

### 1. The SpeechService Class

We define a central domain service `SpeechService` acting as the single controller for speech workloads.

```python
class SpeechService:
    @staticmethod
    def create_job(payload: Dict[str, Any], output_dir: Optional[str] = None) -> SpeechJob: ...
    
    @staticmethod
    def run_job(job_id: str, background: bool = True) -> None: ...
    
    @staticmethod
    def cancel_job(job_id: str) -> None: ...
    
    @staticmethod
    def get_job(job_id: str) -> Optional[SpeechJob]: ...
    
    @staticmethod
    def get_events(job_id: str) -> List[Dict[str, Any]]: ...
```

### 2. Interface Layer Decoupling

Under this model:
- **No client interface** (such as FastAPI controllers or `agent_os/cli.py`) will import execution stages (`SynthesizeStage`, `TrimStage`, `AppendStage`) or build execution graphs directly.
- **FastAPI Controllers** only invoke `SpeechService.create_job` and then `SpeechService.run_job`.
- **CLI Commands** invoke `SpeechService` methods, register console listeners on the job's `EventBus`, and present results.

### 3. Cooperative Cancellation Invariant

Cancellation must be handled cooperatively and gracefully:
- When a job is cancelled (via `cancel_job` or `KeyboardInterrupt`), the execution loop completes the current running task, refrains from queueing new chunks, flushes the final manifests to disk, and transitions the state to `CANCELLED` cleanly.
- Thread killing or process killing is strictly prohibited to prevent artifact corruption.

### 4. Self-Contained Job Directories

A completed job directory will maintain a standardized, self-contained layout:
```
jobs/
  <job_id>/
    job.json               # Serialized SpeechJob details
    events.jsonl           # Structured, versioned line-delimited lifecycle events
    assets_manifest.json   # Copied from the pipeline's telemetry output
    performance_profile.json
```

## Consequences

- **Pros**:
  - Codebases for CLI, REST endpoints, and WebSockets become minimal.
  - State machine changes inside `SpeechService` immediately propagate to all interfaces.
  - Simplified multi-user execution planning and sandbox development.
- **Cons**:
  - Adds a thin abstraction layer between CLI commands and the executor, but the maintenance reduction outweighs this minor cost.

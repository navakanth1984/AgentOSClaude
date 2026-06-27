# ADR-017: Job Lifecycle & Interface Boundary

## Context

As the Speech Subsystem transitions from a local library to a service platform consumed by CLIs, REST controllers, WebSockets, and desktop interfaces, we need a unified entity that acts as the single source of truth for execution bookkeeping. 

Without a formalized model:
1. Each interface must implement its own polling, status checks, and metadata tracking.
2. Artifacts (performance profiles, generated WAV files, manifests) are disjointed and difficult to query uniformly.
3. State transitions (planning vs. synthesis vs. completion) are implicit rather than deterministic.

We also need to formalize the event dispatching mechanism into an explicit `EventBus` component rather than relying on a callback list directly inside `StageContext`.

## Proposed Design

### 1. The SpeechJob Model

We introduce `SpeechJob` as the canonical model representing a single execution request and all its associated telemetry and artifacts.

```
SpeechJob
 ├── job_id: str (UUID)
 ├── state: JobState (Enum)
 ├── request_payload: Dict[str, Any]
 ├── created_at: float
 ├── updated_at: float
 ├── execution_plan: Optional[List[ExecutionPlanEntry]]
 ├── assets_manifest: Optional[Dict[str, Any]]
 ├── performance_profile: Optional[Dict[str, Any]]
 ├── event_log: List[Dict[str, Any]]
 └── output_directory: str
```

### 2. Job States

A job moves through a strict state machine:
```
[QUEUED] ──> [PLANNING] ──> [SYNTHESIZING] ──> [COMPLETED]
                              │                   ▲
                              └──> [FAILED]       │
                              │                   │
                              └──> [CANCELLED] ───┘
```
- **QUEUED**: Job created, waiting in scheduling queue.
- **PLANNING**: Pipeline executing upfront structural stages (`Parse`, `Segment`, `Route`).
- **SYNTHESIZING**: Pipeline executing incremental synthesis loop.
- **COMPLETED**: Chapter audio successfully written and merged/appended.
- **FAILED**: Any stage encountered a fatal runtime exception.
- **CANCELLED**: Aborted by user request.

### 3. The EventBus Class

Instead of stages writing to `StageContext.event_listeners` list directly, we establish `EventBus`:
- `EventBus` registers `EventListener` subscribers (e.g. `ConsoleListener`, `FileListener`, `WebSocketForwarder`).
- `EventBus.publish(event)` broadcasts events asynchronously or synchronously to all registered listeners.
- Events themselves are mapped to State Transitions:
  - `PipelineStarted` -> Transition to `PLANNING`.
  - `ChunkStarted` (first chunk) -> Transition to `SYNTHESIZING`.
  - `PipelineCompleted` -> Transition to `COMPLETED` or `FAILED`.

### 4. Interface Boundaries

CLI, REST endpoints, and WebSockets will consume `SpeechJob` directly:
- **CLI**: Runs a job, subscribes a `ConsoleProgressBarListener` to the event bus, prints the live status of the job, and prints the location of the final completed artifacts.
- **REST**: Exposes `POST /jobs` returning a queued `SpeechJob` instantly, and `GET /jobs/{id}` returning the current `SpeechJob` status and manifest links.
- **WebSocket**: Receives `ws://.../jobs/{id}/stream` and forwards all `EventBus` publications for that `job_id` directly down the socket.

## Consequences

- **Pros**:
  - Unified contracts across CLI, API, and Web UI.
  - High degree of determinism. Telemetry is fully self-contained inside the job.
  - Clean separation of concerns: The executor runs the pipeline, the `EventBus` broadcasts lifecycle changes, and the interfaces are simple consumers of these broadcasts.
- **Cons**:
  - Requires maintaining a state tracker or in-memory job database for the REST server.

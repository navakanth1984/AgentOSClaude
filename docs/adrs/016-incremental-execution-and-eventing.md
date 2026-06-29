# ADR-016: Incremental Execution and Eventing Protocol

## Context

The Speech Pipeline currently operates as a fully batch-oriented process:
```
Text -> Parse -> Segment -> Route -> Synthesize -> Trim -> Merge -> File
```
While this works well for batch processing and overall throughput, it exhibits high Time-to-First-Byte (TTFB) latency. For interactive use cases (e.g. real-time speech assistant, page-by-page screen reader), the user needs to hear audio immediately.

Instead of making the pipeline completely lazy or changing the frozen `MergeStage`, we need a design that supports:
1. **Incremental Execution**: Generating and processing chunks iteratively (e.g. chunk-by-chunk pipelining).
2. **Event Emission**: Emitting structured events at each lifecycle boundary so that consumers (such as CLI, REST APIs, or frontend layers) can respond reactively.
3. **Immutability of existing Stages**: Leaving the core batch stages unchanged, implementing incremental mechanics as progressive extensions.

## Proposed Design

### 1. The AppendStage and Incremental Pipeline

We will introduce a new stage: `AppendStage` (which can also act as a `StreamingMergeStage`).
Rather than taking a full list of synthesized WAV files and joining them at the end, the `AppendStage` will be called iteratively or receive a generator of chunks.

To keep the pipeline run interface simple and uniform, `StageContext` will carry an event-bus or callback system. Stages can emit events onto `context.emit_event(event)`.

### 2. Pipeline Event Schema

We define the following events:
- `PipelineStarted(run_id: str)`
- `ChunkStarted(chunk_id: int)`
- `ChunkSynthesized(chunk_id: int, sample_rate: int, duration_sec: float)`
- `ChunkTrimmed(chunk_id: int, duration_sec: float)`
- `ChunkAppended(chunk_id: int, accumulated_duration_sec: float, output_path: str)`
- `ChapterProgress(chapter_id: str, completed_chunks: int, total_chunks: int)`
- `ChapterCompleted(chapter_id: str, output_path: str)`
- `PipelineCompleted(run_id: str, total_duration_sec: float)`

Each event will inherit from a base `PipelineEvent` class and be serializable to JSON.

### 3. TTSEngine Extension (Optional / Implementation specific)

To support engine-level streaming, the `TTSEngine` protocol can eventually return a generator of audio chunks for single synthesis requests. However, for Phase D, we will focus on chunk-level pipelining:
- In this model, the text is split into chunks (already done by `SegmentStage`).
- `RouteStage` plans all chunks.
- The executor invokes `SynthesizeStage` -> `TrimStage` -> `AppendStage` sequentially on each chunk *incrementally* rather than waiting for the entire set to be synthesized.

### 4. Co-existence of Batch and Streaming Executors

We will introduce `IncrementalExecutor` alongside the standard `BatchExecutor`. 
- `BatchExecutor` executes: `Segment` -> `Route` -> `Synthesize` -> `Trim` -> `Merge`.
- `IncrementalExecutor` executes:
  - `Segment` and `Route` up-front (since structure planning is cheap).
  - For each planned chunk:
    - Runs a micro-pipeline: `Synthesize` (single chunk) -> `Trim` (single chunk) -> `Append` (adds to target file / audio stream).
    - Emits appropriate chunk-level events.
  - Emits final chapter completion events.

This ensures:
1. No modifications are needed for `SynthesizeStage`, `TrimStage`, or the `MergeStage` as they can operate on a subset of (or single) chunks.
2. Baselines are preserved because the batch code path remains 100% untouched.

## Consequences

- **Pros**: 
  - Complete backwards compatibility.
  - Very low Time-to-First-Byte (TTFB) since the first chunk is synthesized, trimmed, and appended/streamed before the second chunk is even sent to the model.
  - Standardized event protocol makes UI development trivial and decodes complex WebSocket push logic.
- **Cons**:
  - Incremental merging into a single file requires append-mode writes or structural format updates (e.g. appending raw PCM frames, then writing the WAV header at the end). We will use a raw PCM buffer approach or a wrapper that updates WAV headers sequentially.

# Agent OS Speech Pipeline

> High-level architecture, milestones, and status of the Agent OS semantic-to-audio speech generation platform.

---

## Current Status
- **Latest Generation**: Generation 2
- **Latest Tagged Release**: v1.2.0
- **Qualification Level**: Tier 3: Production (Verified by Operational Qualification suite)
- **Active ADR Range**: ADR-014 - ADR-018
- **Current Development Phase**: Phase G5 Completed (Hexagonal deployment & Docker packaging)

---

## System Architecture

The Agent OS speech pipeline is an artifact-driven Directed Acyclic Graph (DAG) executor that transforms semantic text into final synthesized audio using stateful ML backends (Kokoro-ONNX and Piper).

```
                      Interfaces
                         
            CLI     │     REST     │   WebSocket
            
                        │
                        ▼
                  SpeechService
                        │
                        ▼
                SpeechJob / EventBus
                        │
                        ▼
               IncrementalExecutor
                        │
                        ▼
             Normalize -> Parse -> Context 
                        │
                        ▼
             Segment -> Route -> Synthesize
                        │
                        ▼
                Trim -> Append -> Merge
                        │
                        ▼
                    Artifacts
```

---

## Generation 1 (Frozen Architecture)
The Generation 1 architecture laid the core foundation for deterministic, execution-safe speech synthesis.

### Core Guarantees & Architecture
- **Deterministic Execution**: Byte-identical outcomes for a given text, engine, and voice.
- **Immutable Cache**: Synthesized and trimmed chunks inside `cache/` are never modified or overwritten.
- **Resumable Idempotency**: Interrupted jobs resume instantly by reusing cached WAVs; merged chapter files are discarded and regenerated purely from cached chunks.
- **Hexagonal Boundaries**: External clients interact strictly via standardized domain schemas.

### Production Validation & Qualification (Gen 1)
- **V1.0 - V1.1**: Deterministic execution DAG, real Kokoro-ONNX runtime integration, engine validation.
- **V1.2**: Reproducibility, deterministic fingerprinting, engine registries, and `doctor` diagnostics.
- **Phase C**: Frozen contracts first (ADR-014 / ADR-015), multi-engine abstraction, and integration of Piper TTS engine.

---

## Generation 2 (Service Layer & Evolution)
Generation 2 expands the framework into a scalable, observable, and multi-tenant backend service.

### Service Layer & API Boundaries
- **SpeechService**: The singular orchestration entry point. It constructs the `StageContext`, instantiates the pipeline `DAG`, and manages state transitions.
- **Hexagonal Interfaces**: 
  - **FastAPI REST API**: Endpoint at `/api/v1/jobs` to create, query, and cancel speech synthesis tasks.
  - **WebSockets**: Endpoint at `/api/v1/jobs/{job_id}/stream` to push real-time events (`ChapterProgress`, `WordBoundary`) and tail events stream.
  - **CLI Command Center**: Console wrapper (`python -m agent_os.cli`) calling `SpeechService` commands directly. Unused pipeline stage imports are fully pruned to maintain strict boundary isolation.

### Pipeline Execution & Observability
- **IncrementalExecutor**: Iteratively processes stages. Performs upfront steps (`normalize` -> `parse` -> `segment` -> `context` -> `route`) followed by an incremental chunk loop (`synthesize` -> `trim` -> `append`).
- **EventBus**: Thread-safe event bus managing subscription and asynchronous event dispatch. Events remain strictly observational.
- **VoiceManager**: Centralizes capability negotiation, speaker mapping, and default assignments. Safely decouples routing decisions from engine-specific logic.

### Qualification Evolution (Gen 2)
The qualification suite (`qualification.py`) evolved into a production-grade automated acceptance suite verifying:
- **Doctor Check**: Verifies presence and integrity of Kokoro and Piper weights.
- **Compatibility**: Validates protocol manifest schema structures.
- **Endurance**: Validates memory and thread stability over 50 sequential runs (verified memory RSS delta <50MB, thread leakage = 0).
- **Chaos / Recovery**: Validates cancellation and resumption bit-identity.
- **Interface Endurance**: Validates event load stability under high subscription concurrency.
- **Cache Lifecycle**: Checks cache directory query performance under heavy file count footprint (<5ms latency query ceiling).
- **Golden Corpus**: Performs regression checks against gold standard inputs.

---

## Generation 3 (Indian languages + Audiobook layer, 2026-06-29)

- **Silent mock-parse bug fixed.** The Gemini parser (`parsers.py`) silently returned a single "Mock text" segment when `GEMINI_API_KEY` was unset — which got synthesized as audio while the job reported success (a 739-char chapter became 0.47s). It now **raises** loudly; the stub is only reachable via an explicit `allow_mock_parse` config flag (tests use it). API errors re-raise instead of becoming speakable "API Error:" segments.
- **`.env` is now loaded.** `agent_os/env_boot.py` loads the repo-root `.env` into `os.environ` (idempotent, no override); imported by `registry.py`, `parsers.py`, and `cli.py`. Previously keys present in `.env` were invisible to the pipeline.
- **SarvamEngine** (`agent_os/speech/engines/sarvam_engine.py`) — cloud TTS (bulbul:v3, 22050 Hz) implementing the `TTSEngine` protocol; registered as `sarvam` in the registry and CLI. The `Language` enum gained 8 Indian languages (ta, bn, kn, ml, mr, od, pa, gu). All 11 Sarvam languages verified end-to-end (hi/bn/kn/ml/mr/od/pa/ta/te/gu/en).
- **Audiobook orchestrator** (`agent_os/speech/audiobook.py`, CLI `audiobook`) — book-level layer over `SpeechService`: resolves chapters (file or directory), runs one job per chapter, stitches WAVs with 0.7s gaps, optional MP3 (ffmpeg), writes `audiobooks/<name>/` + manifest. Hard-fails on sample-rate mismatch or a failed chapter. **One engine per book** (Sarvam 22 kHz vs Kokoro 24 kHz cannot mix).
- **Legacy deprecated, not deleted.** `agent_os/audiobook_pipeline.py` + `agent_os/tts/` carry `DeprecationWarning`s pointing to the new path. Still imported by `direct_tts.py` and `agent_os.py:486` — migrate those before removal.

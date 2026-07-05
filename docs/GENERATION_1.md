# Generation 1 Speech Subsystem Guarantees

This document freezes the architectural guarantees and operational baselines of the Generation 1 Speech Subsystem. Any future updates or architectural extensions must preserve these invariants or undergo a formal Architecture Decision Record (ADR) review.

## Core Architectural Guarantees

### 1. Deterministic Execution
- **Invariant:** For a given input text, engine, and voice, the generated chunk boundaries, execution routing, and intermediate tokens are 100% deterministic.
- **Verification:** Benchmarks and Golden Corpus runs must assert byte/hash and sample-count equivalence across execution cycles.

### 2. Immutable Chunk Artifacts
- **Invariant:** Once synthesized and trimmed, intermediate chunk files (`.wav` format) inside `cache/` are completely immutable. They are stored with deterministic fingerprint keys and are never overwritten or altered.

### 3. Resumable Execution (Idempotency)
- **Invariant:** A partially completed or interrupted speech job can be safely resumed.
- **Verification:**
  - `Chapter_{id}.wav` targets are discarded on resume and reconstructed purely from immutable cached chunk files.
  - The pipeline skips synthesis and trimming stages for chunks that already possess valid cache entries, resulting in identical outputs.

### 4. Engine Abstraction Interface
- **Invariant:** Engines must adhere strictly to the `TTSEngine` protocol. Native bindings (e.g. Kokoro, Piper) remain fully isolated from stage logic and pipelines.
- **Verification:** Compatibility validation runner verify new engine configurations before launch.

### 5. Stable Public Service Interfaces
- **Invariant:** All external adapters (CLI, REST API, WebSocket streams, Docker containers) communicate exclusively through standard domain models (`SpeechJob`, `EventBus`, `Executor`, `Artifacts`) in compliance with ADR-018.

### 6. Qualification Gates
- **Invariant:** Every release candidate must pass the qualification suite (`agent_os qualify speech`), executing Doctor, Compatibility, Endurance, Chaos, Interface Endurance, Cache Lifecycle, Golden Corpus, Benchmarks, and Acceptance validations.
- **Verification:** Runs must produce both human-readable HTML (`qualification_report.html`) and machine-readable JSON (`qualification_report.json`) artifacts, certifying target compliance (`Tier 2: Qualified` / `Tier 3: Production`).

---

## High-Level Architecture Flow

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
                   
      (WAV, JSON, Manifests, Reports, Telemetry)
```

---

## Guidelines for Evolution
- **G1 Maintenance:** Maintenance windows should focus on documentation, optimization, and usability without adding execution states or breaking API boundaries.
- **G2 Scaling:** Generation 2 extensions (e.g., distributed queues, observability backends, secure authorization) must build *on top of* these service boundaries as external adapters, leaving the Generation 1 execution core intact.

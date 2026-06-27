# ADR-014: TTSEngine Capability Contract

## Status
Accepted

## Context
As we introduce multiple TTS engines (starting with Piper alongside Kokoro), we must establish a rigid interface that every engine conforms to. Without a strict contract, each new engine could force upstream changes in the execution pipeline, breaking the abstraction. We need to formalize the engine lifecycle, capability advertisement, and execution boundaries.

## Decision
We define a formal `TTSEngine` Protocol with the following contract:

### Mandatory Lifecycle Methods
- `validate_model() -> None`: Validates model assets on disk without loading them. Should fail fast and raise `FileNotFoundError` or validation-specific exceptions if broken.
- `initialize() -> None`: Performs heavy allocations (e.g., loading ONNX sessions, weights).
- `warmup(profile: str) -> None`: Pre-executes or warms up graph shapes (e.g., accepting a `"minimal"` or `"representative"` profile).
- `shutdown() -> None`: Safely releases resources.

### Capability Methods
- `get_capabilities() -> EngineCapabilities`: Returns a standard dataclass detailing the engine's capabilities (sample rate, supported languages, voice list). Extra features (like emotions or interpolations) must be isolated into a generic dictionary (`extra_features`) to prevent protocol bloat.
- `supports_language(language: Language) -> bool`: Convenience wrapper around capabilities.
- `supports_voice(voice: str) -> bool`: Convenience wrapper around capabilities.

### Execution Method
- `synthesize(text: str, voice: str, language: Language, speed: float) -> Tuple[int, np.ndarray]`: The core execution path.

### Guarantees
- **Determinism:** `get_capabilities`, `supports_language`, and `supports_voice` must be deterministic and invariant after initialization.
- **Exceptions:** All methods should throw from a unified exception hierarchy (e.g., `EngineInitializationError`, `SynthesisError`) to allow higher-level fallback and recovery.
- **Caching:** Engines are prohibited from maintaining their own persistent disk caches for audio output; this is strictly the executor's responsibility.

## Consequences
- The pipeline (`SynthesizeStage`) relies solely on the protocol, avoiding any engine-specific branching.
- Adding a new engine (like Piper) will validate our abstraction if it requires zero changes to the pipeline execution framework.

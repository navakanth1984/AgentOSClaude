# ADR-015: VoiceManager Extraction

## Status
Accepted

## Context
Currently, the `RouteStage` contains embedded policy for selecting and mapping voices via the `VoiceAssignmentPolicy`. As capability negotiation and engine abstraction expand, leaving this logic inside `RouteStage` violates the single responsibility principle and clutters the execution framework.

## Decision
We will extract a standalone `VoiceManager` to handle all routing negotiations independently. 

### Responsibilities of `VoiceManager`
- **Voice Lookup:** Resolving voices requested in the execution plan against the engine's capabilities.
- **Speaker Mapping:** Maintaining speaker-to-voice mapping policies.
- **Capability Negotiation:** Ensuring requested configurations (languages, voices) are valid for the active engine using the `TTSEngine` protocol.
- **Lockfile Management:** Handling voice configurations and fallback selections securely.

### Re-structuring
`RouteStage` will be stripped of policy logic and will operate mechanically:
```
SpeechChunk -> VoiceManager.resolve(...) -> RouteDecision
```

## Consequences
- `RouteStage` becomes purely functional and much simpler to test.
- The `VoiceManager` can be easily mocked in tests for capability negotiation paths without needing full `EngineCapabilities` initialization.
- Capability negotiation becomes robust against newly added engines, as the `VoiceManager` natively handles fallback states using `EngineCapabilities`.

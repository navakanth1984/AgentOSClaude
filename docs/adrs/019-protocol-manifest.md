# ADR-019: Protocol Manifest Unification

## Context

The speech subsystem manages multiple versioned layers of artifacts (event schemas, benchmark protocols, schema versions, assets manifests, performance profiles). As the framework evolves, external clients (such as web frontends, desktop clients, or administrative CLI tools) must be able to read any job's output directory and instantly determine the compatibility versions of these formats without inspecting individual files.

To support this, we will introduce a single, unified `protocol_manifest.json` file generated inside each job's directory upon initialization.

## Proposed Design

### 1. The Protocol Manifest Format

The `protocol_manifest.json` will be written to the root of the job directory:

```json
{
  "protocols": {
    "events": "1.0",
    "benchmark": "1.0",
    "assets_manifest": "1.0",
    "performance_profile": "1.1",
    "job": "1.0"
  },
  "speech_framework_version": "1.2.0"
}
```

### 2. Lifecyle Writing

Upon calling `SpeechService.create_job()`, this manifest is generated and saved as an early artifact:
```
jobs/
  <job_id>/
    protocol_manifest.json
```

## Consequences

- **Pros**:
  - Immediate machine-readable protocol declaration.
  - Keeps backward compatibility queries deterministic for client frontends.
- **Cons**:
  - Adds one more small file to the job folder, but the self-contained clarity is well worth the storage.

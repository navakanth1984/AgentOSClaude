# Architecture Status — Speech Execution Framework

## Status

**Execution Framework V1.1 — Architecture Frozen**

The framework has transitioned from *validated with mocks* to *validated with a
production backend* (real Kokoro ONNX on `CPUExecutionProvider`). Subsequent work
is performance engineering, not architecture.

- Last architectural change: `NormalizeStage` input contract v1.2
- Validated backend: Kokoro ONNX v0.19 (`CPUExecutionProvider`)
- Baseline: see [BASELINE.md](BASELINE.md) (Tier: Smoke)

## Frozen Components

These contracts are stable. Code may be optimized internally, but the observable
contracts below must not change without an ADR (see *Future Changes*).

- **Executor** — content-addressed cache, cold/warm execution paths
  ([executor.py](../agent_os/speech/pipeline/executor.py))
- **DAG** — `add_node(name, stage, depends_on=[...])` is the single source of
  dependency truth ([graph.py](../agent_os/speech/pipeline/graph.py))
- **Stage interface** — every stage exposes `run(context, inputs) -> dict`;
  cross-stage data passes as typed dataclasses reconstructed at the boundary
  (`ensure_parse_result`, `ensure_speech_chunks`, `ensure_execution_plan`)
- **Artifact schema** — `models.py` dataclasses; `performance_profile` schema v1.0
  ([profiling.py](../agent_os/speech/pipeline/profiling.py));
  `context_manifest.json` schema v1.0
- **Fingerprinting contract** — stage fingerprint = f(stage, version, config,
  input artifacts); enums normalized to `.value`; unserializable types fail loud
  (no `str(obj)` fallback)

## Architectural Invariants

1. Stages operate on typed domain objects, never raw serialized dicts.
2. Cache keys represent **semantic** identity (enum value, normalized text), not
   Python object representation.
3. Volatile data (timings, timestamps) never enters an artifact that feeds a
   downstream fingerprint — only stable paths/values do.
4. Telemetry is best-effort and must never fail a synthesis run.

## Future Changes

Require an ADR if they alter:

- Stage boundaries or the `run(context, inputs) -> dict` interface
- Artifact contracts (`models.py` dataclasses, manifest/profile schemas)
- Cache fingerprint semantics

Internal optimizations (session reuse, threading strategy, batching, new
providers) do **not** require an ADR as long as the contracts above are preserved.

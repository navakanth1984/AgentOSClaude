# ADR-011: Engine Registration

## Status
Accepted

## Context
With the introduction of the EngineRegistry abstraction to support the Kokoro engine and eventually other engines (e.g., Piper, dummy), there is a temptation to use dynamic plugin discovery or reflection for engine imports. Dynamic discovery introduces unpredictability during engine initialization and complicates reproducibility.

## Decision
All engines must be explicitly registered through `EngineRegistry` without dynamic discovery, reflection, entrypoints, or auto-import mechanisms. 

## Consequences
- Maintains absolute deterministic behavior during engine startup.
- Preserves explicit dependencies and trace-ability for engines instantiated via configuration.

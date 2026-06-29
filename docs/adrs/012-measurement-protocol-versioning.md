# ADR-012: Measurement Protocol Versioning

## Status
Accepted

## Context
As the benchmarking mechanisms undergo refinement, the definition of what constitutes a "measurement" might change even if the structure of the resulting JSON artifact does not. To avoid conflating different methodologies that happen to share a schema, a clear distinction between the schema structure and the measurement protocol is necessary.

## Decision
Changing the benchmark methodology must increment the `protocol_version`, even if the underlying JSON `schema_version` remains unchanged.

## Consequences
- Consumers of benchmark output (such as aggregators) can correctly interpret the methodology used.
- Ensures forward compatibility when benchmarking conditions evolve while structurally remaining the same.

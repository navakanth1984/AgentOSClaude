# ADR-013: Recommendation Provenance

## Status
Accepted

## Context
Optimal engine thread settings and worker allocations are highly dependent on the host hardware. Blindly trusting a recommendation produced on a 12-core machine for a 4-core machine is fundamentally flawed. Any generated recommendation needs to carry explicit context about the conditions under which it was produced to be validated appropriately.

## Decision
Every generated recommendation must include explicit provenance information, including:
- Benchmark ID
- Protocol version
- Hardware fingerprint
- Confidence score

No recommendation can exist without provenance.

## Consequences
- Prevents cross-hardware recommendation pollution.
- The `doctor` command and the `EngineRegistry` will only suggest configuration adjustments when the host hardware fingerprint matches the recommendation fingerprint.

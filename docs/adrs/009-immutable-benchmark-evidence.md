# ADR-009: Immutable Benchmark Evidence

## Status
Accepted

## Context
As the speech subsystem moves into Phase C and optimizations (like additional engines or routing adjustments) are introduced, there is a risk that legacy benchmark outputs might be modified or "fixed" retrospectively to align with new formats. Since recommendations are derived products and the raw artifacts reflect empirical measurements from specific points in time, any modification to the raw output destroys its value as an immutable historical record.

## Decision
Raw benchmark artifacts are strictly append-only and immutable. Aggregators must never modify them. If a benchmark needs to be updated, it must be re-run to generate a new derived artifact.

## Consequences
- Protects the integrity of historical performance profiles and recommendations.
- Ensures absolute reproducibility of aggregations based on historical data.

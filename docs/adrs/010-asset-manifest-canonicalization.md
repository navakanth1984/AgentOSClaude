# ADR-010: Asset Manifest Canonicalization

## Status
Accepted

## Context
Previously, the `performance_profile.json` stored metadata about the engine version, checksums, and executable assets. Conceptually, this made the profile the source of truth for the assets. As the system scales and environments change, assets need to be treated as a first-class citizen independently from performance measurements.

## Decision
The `assets_manifest.json` is the canonical description of executable assets. The performance profile and other artifacts must reference it, rather than duplicating the values. The manifest describes the executable assets, while the benchmark describes what happened when those assets ran.

## Consequences
- Better separation of concerns between environment state and benchmark telemetry.
- Ensures a single source of truth for model checksums and versioning, improving the reproducibility and diagnosis capabilities of the pipeline.

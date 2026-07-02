# Cognitive Runtime Platform (CRP)

Measurement-first adaptive runtime. Phase 0 scope, non-goals, success
metrics, and architecture are frozen in
[the Phase 0 design spec](../docs/superpowers/specs/2026-07-02-crp-phase0-design.md).

## Layout
- `runtime/`   — Python core (`crp_runtime` package)
- `telemetry/` — Rust `crp-telemetry` crate (Tier-0 ring buffer, PyO3)
- `plugins/`   — representation plugins (Dense, Int8; Phase 0)
- `benchmarks/`— replayable workload harness (Plan 2)
- `docs/`      — SPEC pointer, ADRs, RFCs, risk register

## Dev setup
    pip install -e ./crp[dev]
    maturin develop -m crp/telemetry/Cargo.toml --release
    pytest crp/runtime/tests -v

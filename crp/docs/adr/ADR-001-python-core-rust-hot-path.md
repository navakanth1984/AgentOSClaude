# ADR-001: Python core + Rust hot path

**Status:** Accepted 2026-07-02

**Decision:** Orchestration, policy, and plugins in Python 3.12; only the
Tier-0 telemetry ring buffer in Rust (PyO3/maturin).

**Alternatives:** pure Python (cannot meet the 10 µs hard limit under GC
pauses); pure Rust (too slow to iterate for evidence-gathering).

**Trade-offs:** two toolchains; PyO3 call overhead is part of the measured
budget, not exempt from it.

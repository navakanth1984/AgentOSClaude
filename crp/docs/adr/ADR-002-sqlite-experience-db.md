# ADR-002: SQLite for experience database

**Status:** Accepted 2026-07-02

**Decision:** Experience replay database uses SQLite with WAL mode, not DuckDB or
other OLAP-optimized engines.

**Alternatives:** DuckDB (vectorized, excellent for read-heavy analytical workloads
but adds memory overhead and version fragility); embedded PostgreSQL (complexity);
pure in-memory (replay and offline analysis require persistence).

**Trade-offs:** DuckDB would be faster for range scans during training, but SQLite's
simplicity, stability, and zero-configuration deployment align with Phase 0's
measurement-first principle: we measure before optimizing the replay path.

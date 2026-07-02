# ADR-004: Deterministic scoring policy before learned policy

**Status:** Accepted 2026-07-02

**Decision:** Phase 0 telemetry aggregation uses fixed, deterministic scoring rules
(e.g., latency bands, reward bucketing). Learned policies deferred to Phase 1.

**Alternatives:** learned aggregation policy from day 1 (requires labeled training
data, increases Phase 0 complexity, risk of overfitting measurement artifacts).

**Trade-offs:** deterministic rules are less adaptive but fully interpretable, easier
to validate, and provide clean ground truth for measuring learned policy improvement
in later phases. Aligned with spec principle: freeze behavior, measure, then optimize.

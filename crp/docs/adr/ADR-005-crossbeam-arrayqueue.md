# ADR-005: crossbeam ArrayQueue instead of hand-rolled lock-free buffer

**Status:** Accepted 2026-07-02

**Decision:** The Tier-0 ring buffer wraps `crossbeam::queue::ArrayQueue`.

**Alternatives:** hand-written SPSC atomics ring (faster in theory, easy to
get subtly wrong); `std::sync::mpsc` (allocating, unbounded, can block).

**Trade-offs:** MPMC generality we don't need yet; accepted because
correctness beats micro-optimization until measurements say otherwise
(spec principle: measurement before optimization).

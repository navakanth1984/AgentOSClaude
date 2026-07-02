# ADR-003: Stable rank via randomized sketching

**Status:** Accepted 2026-07-02

**Decision:** Representation stability (stable rank / conditioning number) computed
via randomized projection sketches, not full SVD or eigendecomposition.

**Alternatives:** full SVD (O(n³) dense computation, impractical for large reward
matrices); power iteration (slow convergence); full spectrum (expensive).

**Trade-offs:** sketching introduces Monte Carlo error, but the error is controlled,
deterministic (seeded PRNG), and amortized across policy iterations. Measurement
validates approximation quality in situ; early results guide Tier-1 refinement.

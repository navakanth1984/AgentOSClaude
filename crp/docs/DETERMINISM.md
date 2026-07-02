# CRP Determinism Specification

Single source of truth for every determinism guarantee in CRP. Other
documents (Constitution, IR spec, compiler ABI, RFCs, gate reports) link
here instead of restating rules; if a statement elsewhere conflicts with
this file, this file wins and the other document has a defect.

## Invariants

1. **Replay determinism** — same workload spec + constraints + profile
   ⇒ identical decision (chosen, scores, rejections), 100% of the time.
   Verified field-by-field by `crp_runtime.replay.replay_run`; any
   divergence is a hard failure (spec §2a, R-004).
2. **Policy determinism** — the scoring policy contains no randomness, no
   time-dependence, and no learned state (Phase 0; changes require an RFC).
3. **Canonical serialization** — all stored decision inputs use canonical
   JSON: sorted keys, compact separators (`crp_runtime.experience.canonical_json`).
   Two semantically equal inputs must serialize byte-identically.
4. **Seeded workloads** — every workload derives all randomness from the
   `WorkloadSpec.seed`; a spec fully determines its tensors.
5. **Compiler determinism (Gate 2 contract)** — canonical IR → hash →
   template selection → plugin → manifest is a pure function: identical
   canonical IR documents must produce byte-identical artifacts. A
   difference is a compiler regression, by definition.
6. **Template immutability** — code-generation templates are versioned and
   immutable once released; changing behavior means a new template version.
7. **Hash invariants** — artifact hashes are computed over canonical bytes;
   anything covered by a hash (plugin source, manifest, IR) is immutable
   once recorded.
8. **Provenance (Gate 3 expectation)** — replay records will carry replay
   version, compiler version, plugin hash, manifest hash, and schema
   versions, so any replay can name exactly what produced its baseline.

## What determinism does NOT cover

- Wall-clock telemetry timestamps and measured latencies (environment-
  dependent by nature; excluded from replay comparison, governed by the
  Benchmark Spec instead).
- Cross-host bit-identity of floating-point results (BLAS/ISA variation);
  determinism guarantees are per-host unless an RFC tightens them.

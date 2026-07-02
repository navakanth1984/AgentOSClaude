# ROADMAP-R1 — Governed Computational Research Platform (Revised)

This document outlines the four R1 gates required to transition the CRP Evolutionary Research Platform from a Research Prototype (R0) to a production-ready, secure, and fully reproducible Research Subsystem (R1).

---

## Architecture Freeze — R1

> [!IMPORTANT]
> **Architecture Freeze — R1**
>
> Effective immediately, no new architectural capabilities, optimization engines, representation types, or research workflows will be added until R1 Success Criteria are satisfied.
>
> **Exceptions:**
> - Critical defects
> - Security fixes
> - Documentation corrections
> - RFC-approved specification clarifications
>
> All feature requests proposed during the R1 freeze are recorded as RFC candidates and deferred until the completion of R1 Success Criteria.

---

## The Four Gates to R1

### Gate 1: Process Isolation
- **Objective:** Prevent candidate plugins from destabilizing the host system or consuming excessive shared resources.
- **Acceptance Criteria:**
  - Sandbox crash (e.g. syntax error or segfault) must never terminate the host runtime.
  - OOM inside the sandbox must never affect CRP memory pools.
  - Timeout must always produce deterministic sandbox termination.
  - Maximum sandbox cleanup time must be `< 100 ms`.
- **Implementation:** Execute sandbox runs in isolated subprocesses using system-level process management rather than namespace overrides.
- **Verification:** Execute intentionally malformed/crashing plugins and assert that host resources are unaffected and sandbox exit status is cleanly caught.

### Gate 2: Versioned IR Compiler Pipeline
- **Objective:** Eliminate security risks of dynamic Python execution by compiling configurations from a restricted Intermediate Representation.
- **Acceptance Criteria:**
  - **Candidate-generated Python must never be executed directly. All executable plugins must be generated exclusively from a validated IR through audited code templates.**
  - Configurations must conform to a versioned IR schema.
- **Implementation:**
  - Define **IR v1 Spec** for allowable representations (`Quantization`, `Sparse`, `LowRank`, `TensorTrain`).
  - The compiler parses the IR configuration and generates standard python plugins by populating pre-audited templates.
- **Verification:** Assert that attempts to bypass the IR (e.g., injecting arbitrary python instructions) are rejected during validation.

### Gate 3: Complete Provenance Chain
- **Objective:** Retain complete historical environment and configuration details to guarantee reproducible context.
- **Acceptance Criteria:** Every recommendation bundle must store a complete, immutable provenance record.
- **Implementation:** Include the following schema in every bundle's metadata:
  - `crp_version`, `git_sha`, `plugin_version`, `dataset_version`
  - `hardware_profile`, `compiler_version`, `rng_seed`
  - `os_version`, `lockfile_hash`, `benchmark_version`, `replay_version`
- **Verification:** Compare generated bundle metadata against active environment profiles to confirm matching lockfile hashes and seeds.

### Gate 4: Replay Reproducibility Classification
- **Objective:** Validate bundle consistency using appropriate grading classes depending on the workload type.
- **Acceptance Criteria:** Every experiment bundle must successfully verify its replay outcome against the defined baseline.
- **Implementation:** Classify verification rules as:
  - **Deterministic Workloads:** Require exact byte-level reproduction matching `decision`, `scores`, `plugin`, and `telemetry` parameters.
  - **Statistical Workloads:** Performance metrics (`latency_ms`, `memory_bytes`, `accuracy_loss`) must lie within a strict `±2%` variance window.
- **Verification:** Run the bundle verification script on historical trial records to confirm exact and statistical validation thresholds are enforced.

---

## Future Roadmap (Post-R1)

> [!NOTE]
> **The following roadmap is aspirational and non-binding. Work may begin only after the R1 Success Criteria have been satisfied.**

### R2: Statistical Research
No generative AI or LLMs. Implement statistical heuristic analysis of past run records to identify optimization bottlenecks and queue IR specifications automatically.

### R3: Assisted Discovery
Introduce LLMs as one of several pluggable hypothesis generation sources, feeding declarative hypotheses directly into the IR compiler pipeline.

### R4: Research Economy
Implement utility-based scheduling where experiments compete for execution resources based on resource cost, priority, expected gain, and historical confidence.

### R5: Meta-Research
The platform monitors its own research effectiveness by scoring and ranking the success rate of different hypothesis generation engines over time.

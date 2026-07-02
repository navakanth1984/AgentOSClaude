# R1 Success Criteria

This document defines the exit criteria and completion targets for the Cognitive Runtime Platform (CRP) R1 milestone.

---

## Exit Criterion

> **R1 is complete when all four gates pass their acceptance tests, all regression suites are green, and at least one end-to-end Experiment Bundle has been promoted through the full human-reviewed workflow into the CRP codebase.**

---

## Gate-Specific Completion Targets

| Gate | Target Subsystem | Completion Criteria |
|---|---|---|
| **G1** | Sandbox Isolation | Subprocess evaluations catch intentionally induced faults (crashes, memory limits, and infinite loops) without destabilizing the host, completing cleanup in `< 100 ms`. |
| **G2** | IR Compiler Pipeline | A versioned IR compiler generates representation plugins using audited code templates, entirely replacing unrestricted dynamic python `exec()` calls. |
| **G3** | Provenance Chain | Every generated Experiment Bundle logs a complete environmental metadata footprint (Git SHA, RNG seed, locks, OS version, package lock hashes). |
| **G4** | Replay reproducibility | The verifier script enforces byte-identical outcomes on deterministic workloads and `±2%` metrics bounds on statistical workloads. |

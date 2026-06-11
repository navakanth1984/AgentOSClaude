---
date: 2026-06-11
tags: [agent-os, cgbench, simulations, quantum, security-dashboard]
project: "AI-Automation"
source: "CGBench Simulation Logs Database"
---

# CGBench Threat Simulation Dashboard

## Key Idea
Persistent audit log and scorecard metrics tracking ClawGlove and OpenClaw simulation behaviors on the Qiskit quantum engine.

## Details
*Last Updated: 2026-06-11 18:16:58*

### 1. Real-World CVE Battlefield Simulations (Phase 2)
Evaluates ClawGlove's threat escalation and quarantine policies against 27 real-world attack vectors.

| Timestamp | Backend | Block Rate | H_Escape | H_Quantum | Grade | PQC Signed |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-06-11 18:16:58 | local | 100.0% | -0.0000 | 3.5633 | G-5 (Provenance Certified) | ✅ Yes |
| 2026-06-11 18:15:33 | local | 100.0% | -0.0000 | 3.7303 | G-5 (Provenance Certified) | ✅ Yes |
| 2026-06-11 18:14:25 | local | 100.0% | -0.0000 | 3.7417 | G-5 (Provenance Certified) | ✅ Yes |
| 2026-06-11 18:13:45 | local | 100.0% | -0.0000 | 3.6136 | G-5 (Provenance Certified) | ✅ Yes |
| 2026-06-11 18:13:02 | local | 100.0% | -0.0000 | 3.7181 | G-5 (Provenance Certified) | ✅ Yes |
| 2026-06-11 07:31:28 | ibm | 100.0% | -0.0000 | 3.6945 | G-5 (Provenance Certified) | ✅ Yes |
| 2026-06-11 07:31:18 | local | 100.0% | -0.0000 | 3.8042 | G-5 (Provenance Certified) | ✅ Yes |
| 2026-06-11 01:23:25 | local | 100.0% | -0.0000 | 3.5428 | G-5 (Provenance Certified) | ✅ Yes |

### 2. OpenClaw vs ClawGlove Threat Simulations (Phase 1)
Evaluates the escalation behaviors between OpenClaw (attacker) and ClawGlove (governance).

| Timestamp | Backend | Block Rate | H_Escape | H_Gov | Dwell Time | Grade | PQC Signed |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-06-11 07:32:39 | ibm | 100.0% | 1.1995 | 1.6994 | 285.1ms | G-4 (Drift Certified) | ✅ Yes |
| 2026-06-11 07:31:38 | local | 100.0% | 1.1995 | 1.6994 | 295.5ms | G-4 (Drift Certified) | ✅ Yes |
| 2026-06-11 01:23:47 | local | 100.0% | 1.1995 | 1.6994 | 369.5ms | G-4 (Drift Certified) | ✅ Yes |

### 3. Lead-Behind Coevolution Simulations (Phase 3)
Measures ClawGlove's solo pre-evolution cycles and side-by-side (SBS) prediction precision.

| Timestamp | Pre/SBS Cycles | Lead Value | Safety Intact | Prediction Precision | Grade | PQC Signed |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-06-11 01:23:55 | 5 / 10 | 14 | ✅ Yes | 54.9% | G-4 (Anticipatory Drift Certified) | ✅ Yes |

## Action / Next Steps
- [ ] Run a new Phase 2 simulation from the dashboard simulations panel to update this scorecard.
- [ ] Verify PQC signatures on new logs.
- [ ] Check the correlation ratio on noisy backend runs.
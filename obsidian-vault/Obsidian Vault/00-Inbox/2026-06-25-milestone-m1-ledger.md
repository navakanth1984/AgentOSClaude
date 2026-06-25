---
date: 2026-06-25
tags: [mvct, nth-brain, evaluation, research-plan, milestone, pkm]
project: "NTH Brain / MVCT"
source: "Milestone M1 — Constitutional Answer Gating (MVCT V1 landed on master via PR #2)"
links: ["[[2026-06-25-mvct-v1-design-spec]]", "[[2026-06-23-transfer-detector-v0-brief]]", "[[2026-06-23-mvct-v1-blueprint]]"]
---

# Milestone M1 — Constitutional Answer Gating ("The Microscope")

> [!success] M1 Outcome
> The project now contains a **validated capability sensor** and a **constitutionally governed runtime** connected through a well-defined interface. The remaining uncertainty lies in **empirical validation with independent human ground truth**, not in the architectural mechanism itself.

The boundary crossed: from *architectural design* to *experimental software*. The achievement is not that MVCT V1 exists — it's that its central claim is now **testable** rather than arguable.

---

## 1. The Ledger — Established vs. Not Established

### ✅ Established (the architecture)
- **Sensor ↔ Governor separation** — `transfer-detector-v0` (sensor) and the Capability Auditor (governor) are decoupled via the `TransferSensor` seam.
- **Python-enforced constitutional runtime** — the LLM is a *witness*, not the authority. The `−∞` barrier is enforced by HMAC `PermissionToken`s + deterministic blocking, not by prompting.
- **PermissionToken authority model** — only the Auditor can mint; everything else verifies (Invariant 3).
- **Reproducible control-vs-experimental harness** — first-class A/B runner isolating the gate as the single variable.
- **Binary, falsifiable research claim** — answer release predicated on transfer classification, on one held-fixed domain.

### ❌ Not yet established (the frontier)
- **Real-learner performance** — never tested against live, unpredictable human inputs.
- **Cross-domain generalization** — anything outside `HouseplantKnowledgeProvider` is explicitly out-of-distribution.
- **Long-term autonomy gains** — unproven that this gating mechanism increases learner autonomy over time.
- **Educational superiority** — not shown to beat standard generation or human tutoring on outcomes.

---

## 2. Validation Roadmap

| Stage | Question | Status |
|-------|----------|--------|
| **A — Scripted reproducibility** | Does the gate behave correctly under deterministic scripted learners (zero invariant violations, stable unlock latency, reproducible A/B differences)? | **Current — done** (28 offline tests green) |
| **B — Blind human annotation & detector re-validation** | Do real learners produce detector trajectories like the scripted assumptions? Where are the false unlocks, missed transfers, ambiguous cases? | **Next** |
| **C — Controlled comparative study** | Does gated tutoring outperform ungated on the outcomes that matter — SAIR, unlock latency, retention, autonomy, dependency ratio? | Later |

Stage B is where the **synthetic ceiling becomes visible**. Its goal is not statistical significance — it is **discovering failure modes** that become the next detector's improvements.

---

## 3. Validation Protocol Principle — Independent Ground Truth

For Stage B to have scientific teeth, ground truth must be defined **independently of the detector**:

```text
Participant → Problem → Transcript → Detector ─┐
                                               ├─→ Disagreement Analysis → Revision
                          Blind Human Annotation┘   (κ computed only after both
                                                      streams are complete)
```

- Human annotation of learner transcripts must be **blind** to the machine's classification.
- Detector predictions stay hidden until after ground-truth labels are finalized.
- Agreement metrics (Cohen's κ) are computed only after both annotation streams are complete.

> [!danger] Permanent validation rule (all future detector versions)
> **The detector must never be evaluated against labels derived from its own output.**
> If annotators see the detector's call before labeling, it re-validates the machine's biases rather than its accuracy — the exact echo chamber `transfer-detector-v0`'s "κ_human FIRST" discipline was built to prevent.

---

## 4. Open Research Question

> **Under what conditions does demonstrated transfer justify constitutional answer release?**

Keeping the project oriented around this *question* — rather than a feature roadmap — is what holds the scope disciplined. If the gating mechanism survives empirical testing, it becomes a **reusable primitive**: future systems can swap the detector, enrich the policy layer, or add developmental controllers without changing the core governance pattern.

---

## Action / Next Steps
- [ ] Stage B: recruit a small pilot; collect real learner transcripts on the houseplant domain.
- [ ] Apply the blind annotation protocol; compute real κ_human and detector-vs-human agreement.
- [ ] Feed observed failure modes back into the detector (swap via `TransferSensor`, no tutor changes).
- [ ] Only then proceed to Stage C comparative study.

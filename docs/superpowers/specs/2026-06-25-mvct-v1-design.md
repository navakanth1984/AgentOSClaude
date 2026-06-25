---
date: 2026-06-25
tags: [mvct, nth-brain, cca, architecture, spec, learning-to-learn]
project: "NTH Brain / MVCT"
status: design-approved (with refinements)
supersedes_context:
  - "00-Inbox/2026-06-23-mvct-v1-blueprint.md (The Microscope)"
  - "00-Inbox/2026-06-23-transfer-detector-v0-brief.md (detector-first pivot)"
depends_on: "transfer-detector-v0 (validated: Construct 1.000 / Parity 0.900 / EAR 0.981)"
---

# MVCT V1 Design Spec — "The Microscope" (Binary Answer-Gate)

> **⚠ Scope discipline — read first.** MVCT V1 does **not** attempt to prove that Socratic tutoring is superior, nor that LLMs teach effectively. It evaluates **whether a validated capability detector can function as a constitutional gate governing answer release while preserving strict runtime invariants.** Everything below serves that one question.

## 1. Objective & The Single Falsifiable Claim

Deploy a Minimum Viable Cognitive Tutor that governs **one topic** and proves **one binary hypothesis**:

> **Can a validated capability detector serve as a constitutional gate that governs answer release — more effectively than an identical but ungated conversational tutor?**

The tutor strictly withholds the target answer until `transfer-detector-v0` classifies the learner's *own* reasoning as `transfer` (under a configurable policy), and releases the answer the instant that threshold is met.

### What is — and is NOT — being validated
This experiment validates exactly one thing: **a capability detector can act as a constitutional gate on answer release.** It deliberately does **not** attempt to validate "LLMs teach well," "Socratic dialogue works," or any claim about the six-layer CCA. Holding the claim this narrow is what makes the result attributable.

### CCA through-line
Conservation Law in binary form: **K_T (tutor supplies the answer) = 0 until K_L (learner demonstrates decomposition) is evidenced.** This V1 is the first validated *sensor → governor* coupling of the Constitutional Cybernetic Architecture; every higher CCA layer is deferred (see §9).

---

## 2. Scientific Design (the part that makes this evidence, not a demo)

### 2.1 Control vs. Experimental
The deliverable is a **comparative experiment**, run via a scripted runner so both arms see byte-identical inputs:

```text
CONTROL arm                      EXPERIMENTAL arm
  Learner script                   Learner script        (same script)
       ↓                                ↓
  Socratic LLM                     Socratic LLM           (same model, same prompt)
       ↓                                ↓
  Answer (ungated)                 TransferSensor → Auditor → Gate
                                        ↓
                                   Answer (gated)
```

Everything held constant — same model, same system prompt, same topic, same learner scripts — so any difference in outcome is attributable to **the gate alone**. Without this control, we can show the gated system *works* but cannot attribute improvement to gating.

### 2.2 Domain is a constraint, not a preference
> The houseplant domain ("Why is my houseplant dying?") is intentionally retained to preserve the detector's **validated operating distribution** and isolate the contribution of the constitutional gating architecture. Changing domains would change two variables at once and destroy identifiability.

### 2.3 Carried-forward risk: synthetic ceiling
The detector passed against a **synthetic** human ceiling (`κ_human_archetype = 1.000`; a `_QUARANTINE_synthetic_fill` corpus and `populate_gold_quotes_from_detector.py` exist). The detector has **not** survived contact with real human learners. The architecture therefore treats the detector as **swappable** (§3.1 `TransferSensor`) so a future real-human re-validation drops in without touching the tutor. V1 results are conditional on the synthetic ceiling and must be reported as such.

---

## 3. Architecture

A **new `mvct-v1/` package that imports `transfer-detector-v0`** as a dependency. The instrument stays pure ("NOT an educational product"); the tutor sits on top. The blueprint's 4 services collapse to 3 active services + supporting abstractions (Knowledge Graph dropped; interface retained).

```text
   Learner (terminal / scripted runner)
        │  text in
        ▼
┌───────────────────────────┐   PermissionToken (verify + expiry)
│   Socratic Interface      │◀──────────────────────────────┐
│   (LLM + Python guard)    │                                │
│   knows topic via ────────┼──▶ KnowledgeProvider           │
└──────────┬────────────────┘    (HouseplantKnowledgeProvider)│
           │ appends turn                                     │
           ▼                                                  │
   [ shared transcript ]                                      │
           │                                                  │
           ▼                                                  │
┌───────────────────────────┐   judge_transfer(transcript)   │
│   TransferSensor (adapter)│──────────────────────────▶ transfer-detector-v0
│                           │◀── {classification, confidence, evidence}
└──────────┬────────────────┘                                │
           ▼                                                  │
┌───────────────────────────┐  applies GatePolicy            │
│   Capability Auditor      │  MINTS PermissionToken ─────────┘
│   (sole token authority)  │
└──────────┬────────────────┘
           │ token + turn
     ┌─────┴─────────┐
     ▼               ▼
┌──────────┐   ┌──────────────────┐
│ Metrics  │   │ Internalization  │
│ Monitor  │   │ Ledger (+ SAIR)  │   both: sqlite3 (stdlib)
│ (runtime)│   │ (pedagogical)    │
└──────────┘   └──────────────────┘
```

### 3.1 TransferSensor (`sensor.py`) — coupling firewall
Thin adapter wrapping `judge_transfer(transcript, api_key)`. The Auditor depends on this interface, **not** on the detector module directly. Single seam for swapping in a real-human-validated detector later. Returns a normalized `SensorReading{classification, confidence, confidence_breakdown, evidence_quotes}`.

### 3.2 GatePolicy (`policy.py`) — threshold is an experimental variable
```python
@dataclass(frozen=True)
class GatePolicy:
    classification_required: str   # "transfer"
    confidence_floor: float        # 0.0 – 1.0
    unlock_strategy: str           # "binary" (V1)

STRICT   = GatePolicy("transfer", 0.90, "binary")
RESEARCH = GatePolicy("transfer", 0.65, "binary")
BINARY   = GatePolicy("transfer", 0.00, "binary")   # classification-only
```
Default = `STRICT` (documented in `config.py`). The threshold is **not** an architectural law; it is a tunable the experiment sweeps.

### 3.3 Capability Auditor (`auditor.py`) — sole unlock authority
- Calls `TransferSensor.read(transcript)`, applies the active `GatePolicy`.
- If satisfied, **mints a `PermissionToken`** (the only module permitted to do so).
- Returns `AuditResult{token | None, classification, confidence, evidence, reason}`.
- **Fail-closed:** any sensor/API failure → `none` → no token → answer stays locked. A governance gate must never *unlock* on failure.

### 3.4 PermissionToken (`permission.py`) — capability, not a boolean
Replaces `answer_unlocked=True`. HMAC-signed over its fields with a key held only inside the Auditor module:
```python
@dataclass(frozen=True)
class PermissionToken:
    issued_by: str          # "CapabilityAuditor"
    timestamp: float
    classification: str
    confidence: float
    expires_at_turn: int    # stale tokens cannot be replayed
    signature: str          # HMAC; verified by the Socratic Interface
```
Enforces **Invariant 3** structurally: only the Auditor can mint a valid token; every other module can only *verify* one. Mirrors capability-based OS design.

### 3.5 Socratic Interface (`socratic.py`) — model proposes, Python disposes
- LLM (`gemini-2.5-flash`, temp 0) generates the next tutor turn.
- **Locked mode** (no valid token): a deterministic guard blocks/refuses any turn that leaks the answer (§4). System prompt forbids enumerating the canonical independent variables — the tutor must *not* decompose for the learner (doing so would also trigger the detector's mimicry penalty on the next learner turn).
- **Unlocked mode** (valid, unexpired token): may deliver the canonical answer.
- The interface only acts on a token it has **verified**; it cannot read `answer_unlocked` because that field no longer exists.

### 3.6 KnowledgeProvider (`knowledge.py`) — abstraction kept, implementation trivial
```python
class KnowledgeProvider(Protocol):
    def scenario_prompt(self) -> str: ...
    def canonical_answer(self) -> str: ...
    def canonical_independent_variables(self) -> list[str]: ...
    def leak_blocklist(self) -> list[str]: ...   # answer terms + variable names
```
`HouseplantKnowledgeProvider` returns static content. Future graph/ontology/retrieval providers plug in without touching the Auditor or Interface.

### 3.7 Internalization Ledger (`ledger.py`) — pedagogical history
`sqlite3` (stdlib, zero new deps). Tables: `sessions`, `turns(role, text, classification, confidence, had_token)`, `ledger_entries(capability, ownership, atr, evidence_json, sair)`. Computes **SAIR** (§6). Session ends on unlock (success) or explicit quit (logs a failure state — the quit exit strategy).

### 3.8 Metrics Monitor (`monitor.py`) — runtime behavior (distinct from ledger)
Logs, per gate evaluation: detector output, unlock granted/denied, reason, **latency**, confidence, turn number. The ledger answers "what did the learner do?"; the monitor answers "how did the gate behave?" — separation makes debugging tractable.

### 3.9 Runtime (`loop.py` interactive · `runner.py` scripted)
- `loop.py` — interactive terminal demo.
- `runner.py` — replays an annotated learner script through both `--mode control` and `--mode experimental`; emits the comparison table. This is the experiment harness.
- `config.py` — default policy, model name, paths, HMAC key source.

---

## 4. The Three Constitutional Invariants
Enforced in the Python runtime, never trusted to LLM prompt adherence (the CCA's `−∞` barrier reduced to MVP form — an unreachable state).

- **Invariant 1 — No canonical answer tokens while locked.** Deterministic substring/normalized match against `leak_blocklist`. Fully enforceable.
- **Invariant 2 — No logically-equivalent complete solution while locked.** Enforced **best-effort** via the canonical-fact blocklist (the answer's key independent variables): if a locked turn names the canonical decomposition, it is blocked. *Honest limit:* perfect detection of paraphrased complete solutions is not deterministically decidable; the system-prompt constraint is the first line, the blocklist the second, and full semantic-equivalence detection is **deferred** (a known V1 gap, logged by the monitor for manual audit).
- **Invariant 3 — Unlock can only originate from the Auditor.** Enforced structurally by `PermissionToken` HMAC minting (§3.4).

---

## 5. Topic (`topics/houseplant.json`)
Reuses the detector's exact primary scenario. Supplies scenario prompt, `canonical_answer`, `canonical_independent_variables` (e.g. light, watering, drainage/soil, nutrients, pests/disease, temperature/humidity, root health), and the derived `leak_blocklist`. A code comment marks the domain as **mandatory** (in-distribution constraint), not a default.

---

## 6. Metrics

- **SAIR — Self-Initiated Asset Invocation Rate** = self-initiated decomposition uses / opportunities. Leading indicator of genuine transfer; blueprint target > 0.0 to prove baseline.
- **Unlock Latency** = `turn_transfer − turn_first_correct_reasoning`. `turn_first_correct_reasoning` is annotated in the learner script (ground truth); `turn_transfer` is when the gate actually unlocked. **Ideal = 0** (the claim is "release *immediately*"). Positive = gate hesitated; negative = gate unlocked early (a safety failure). Computable for scripted runs; for live sessions it requires a reference annotation (deferred).
- **Comparison output:** control vs. experimental on identical scripts — answer-exposure timing, SAIR, and any divergence attributable to the gate.

---

## 7. Testing Strategy
TDD, mirroring the detector's discipline (enforcement before prompt). All tests run **offline** via the detector's dry-run mock (no API key, deterministic, zero cost).

- `test_permission.py` — token mint/verify; tampered signature rejected; expired token rejected. **(write first)**
- `test_socratic_guard.py` — Invariant 1 & 2: an answer-leaking LLM stub is blocked while locked; passes when a valid token is present.
- `test_auditor.py` — sensor reading → policy → token mapping across `STRICT/RESEARCH/BINARY`; fail-closed on sensor error.
- `test_ledger.py` — SQLite integrity + SAIR math + quit→failure-state logging.
- `test_monitor.py` — runtime records incl. unlock-latency computation.
- `test_runner.py` — scripted control-vs-experimental harness: locked→unlocked transition occurs only in experimental; control exposes the answer unconditionally.

---

## 8. Dependencies & Layout
Python stdlib (`sqlite3`, `hmac`, `json`, `dataclasses`) + `transfer-detector-v0` (path/editable install: `pip install -e ../transfer-detector-v0`) + `google-generativeai` (already the detector's dependency; reused for the Socratic LLM — single provider, single `GEMINI_API_KEY`, Tier 1/2 per model-economics rule). **No** React, FastAPI, NetworkX, or vector/graph DB.

```text
mvct-v1/
├── pyproject.toml
├── config.py
├── sensor.py            # TransferSensor (coupling firewall)
├── policy.py            # GatePolicy + STRICT/RESEARCH/BINARY
├── permission.py        # PermissionToken (HMAC capability)
├── auditor.py           # Capability Auditor (sole minter)
├── socratic.py          # Socratic Interface (LLM + guard)
├── knowledge.py         # KnowledgeProvider + Houseplant impl
├── ledger.py            # Internalization Ledger (SAIR)
├── monitor.py           # Metrics Monitor (runtime)
├── loop.py              # interactive demo
├── runner.py            # scripted control vs experimental
├── topics/houseplant.json
├── scripts/             # annotated learner scripts (with turn_first_correct_reasoning)
└── tests/
```

---

## 9. Deferred to Later Versions (YAGNI / anti-scope)
Knowledge Graph implementation · Causal Memory · Developmental Controller (moving attractor) · graded scaffold-withdrawal (V1 is binary) · multi-topic / multi-asset · dynamic topic generation · web UI · full semantic-equivalence leak detection · live-session unlock-latency · real-human detector ceiling re-validation.

Each is admitted only when it supports a new falsifiable hypothesis — not in anticipation of future features.

---

## 10. Definition of Done (North Star)
> On the houseplant topic, the experimental tutor refuses to state the answer until the detector measures genuine decomposition (under the active GatePolicy) and releases it the moment it does; the control tutor exposes the answer unconditionally; the runner emits a comparison (SAIR + unlock-latency + exposure timing) — all reproducible offline via the dry-run mock, with the three invariants covered by passing tests.

---

## 11. Threat Model

| ID | Threat | Mitigation | Class |
|----|--------|-----------|-------|
| T1 | LLM leaks the answer while locked | Deterministic Python guard replaces the turn (Invariant 1) | Engineering |
| T2 | Detector unavailable / errors | Fail-closed: no token → stays locked (§3.3) | Engineering |
| T3 | Detector false positive (unlocks too early) | `GatePolicy` confidence floor; sweepable threshold (§3.2) | Research |
| T4 | A module bypasses the Auditor to unlock | HMAC `PermissionToken` — only the Auditor holds the minting key (Invariant 3) | Engineering |
| T5 | Equivalent-answer leakage (paraphrase) | Canonical-variable blocklist, best-effort (Invariant 2); known semantic gap | Engineering (partial) |
| T6 | Token replay across turns | `expires_at_turn` — stale tokens rejected (§3.4) | Engineering |

## 12. Risk Register — Engineering vs. Research

Engineering risks are bugs we can close; research risks are open empirical questions the experiment exists to probe. Separating them prevents "the code works" from being mistaken for "the hypothesis holds."

**Engineering risks (closable in V1):**
- API/LLM failure → fail-closed + injectable `llm_fn`.
- Prompt leakage → Python guard (T1).
- Token forgery / Auditor bypass → HMAC capability (T4).
- SQLite corruption / concurrency → single-process, per-run DB files.

**Research risks (open questions, NOT closable by code):**
- Detector construct validity — passed only a *synthetic* ceiling (§2.3).
- Domain generalization — houseplant held fixed precisely because this is unknown.
- Confidence calibration — is 0.90 meaningful? `GatePolicy` makes it a sweepable variable, not a verdict.
- Transfer-metric validity — does SAIR track internalization, or merely a proxy?

## 13. Success Hierarchy

Four independent levels; passing a lower level does **not** imply the next. This prevents implementation success from being read as scientific success.

| Level | Criterion | Evidence |
|-------|-----------|----------|
| Architecture | All three constitutional invariants hold | passing invariant tests |
| Runtime | Gate behaves correctly under every scripted test | `test_runner.py` green + monitor logs |
| Experiment | Control and experimental differ *only* by the gate | identical script/model/prompt, gate on/off |
| Research | Results support or refute the gating hypothesis | comparison metrics + real-human re-validation |

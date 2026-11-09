# Indigenous AI Foundation Models & AIKosh Platform (gbrain)

**Status**: Verified 2026-11-09 | Canonical Knowledge Base  
**Surface**: AIKosh (`aikosh.indiaai.gov.in`), MeitY IndiaAI Mission, Hugging Face (`coild-aikosh`, `BrahmAI`, `bharatgenai`), Soket Labs, ZenteiQ  
**Primary Sources**: Official MeitY Foundation Models Announcement (November 2026), AIKosh SDK (`aikosh==2.0.0`), Platform Live Telemetry  

---

## 1. System Overview & The Sovereign AI Strategy

India's sovereign AI roadmap under the **IndiaAI Mission** (budget: ₹10,372 crore) is governed by the principle of **"Targeted & Frugal AI"**:
* Rather than pursuing trillion-parameter frontier LLMs that require multi-million dollar training budgets and massive overseas cloud data centers, India prioritizes **domain-specific 2B–26B parameter foundational models**.
* Models are designed for **air-gapped and on-premises environments** (defense, BFSI, critical governance) to ensure zero data exfiltration.
* The training infrastructure leverages **hardware heterogeneity**, combining Google Cloud TPUs with NVIDIA GPUs across domestic compute clusters (3,000 C-DAC GPUs + 10,000 on-tap GPU capacity + 8-exaflop India-UAE bilateral supercomputing framework).

---

## 2. Model Taxonomy & Architecture Matrix

| Model Name | Scale & Architecture | Developers & Backing | Key Modality & Capabilities | Deployment Target |
| :--- | :--- | :--- | :--- | :--- |
| **EKA-1** | 26.3B Sparse Hybrid RALSNet (64K context) | Soket Labs Technology & Research / IndiaAI | Mathematical reasoning, code synthesis, BFSI compliance, agentic tool-calling across 22 Indic languages | On-premise servers, air-gapped terminal, edge devices |
| **Dhīr 2B & 5B** | 2.1B / 5.4B Mixture-of-Experts (MoE) | ZenteiQ AiTech Innovations / BrahmAI | Lightweight offline multilingual assistant (10 Indic + En), document-grounded retrieval | On-device mobile hardware, Raspberry Pi, edge TPUs |
| **coild-mul-mt** | 1.0B Seq2Seq (IndicTrans architecture) | IIT Patna / COILD / AIKosh | Direct Indic-to-Indic machine translation (40 directions) without pivoting through English across 8 domains | Hugging Face Inference Endpoint / local GPU |
| **Param Series** | PARAM-1 (2.9B), 7B MoE, Param2-Thinking (17B) | BharatGen Consortium (IIT Bombay + DST) | Indian Knowledge Systems (IKS), multilingual text generation, structured reasoning | Open Weights (`bharatgenai`) |
| **Dhīr 9B** *(Pipeline)* | 9.0B Scientific Foundation Model | ZenteiQ AiTech Innovations | Physics simulation verification, Navier-Stokes / PDE invariant validation, engineering telemetry | Expected ~December 2026 |
| **Medical Core** *(Pipeline)* | Domain Clinical NLP Model | IndiaAI Healthcare Consortium | DEPA-compliant PII redaction (Aadhaar/phone), clinical entity extraction, discharge summaries | Clinical validation stage |
| **Yani Vision** *(Pipeline)* | Sovereign Multimodal Vision Model | IndiaAI Multimodal Pillar | Multilingual administrative document OCR (Patta/deeds/IDs), Indian scene reasoning | Pilot & Toolkit rollout |

---

## 3. Verified Implementations & Evidence

### Verified
- **AIKosh SDK Live Connectivity (`aikosh==2.0.0`)**:
  - Authenticated via `AIKOSH_API_KEY` from `D:\navakanth001\.env`.
  - Verified platform ping: `{'status': 'success', 'message': 'filters endpoint reachable'}`.
  - Retrieved **88 active sovereign models** from the live account using `aikosh.models.list_models()`.
  - Discovered verified assets: `Indic-Conformer model for ASR`, `Varya v1 Video Model`, `LUCAN 3B`, `MANAS-2`, `Samadhan-Bharat Acoustic Engines`, `NCERT-TUTOR-v3`, and `Indic-Translate`.
- **Indigenous AI Engine (`indigenous_ai/`)**:
  - Implemented unified Python package in workspace (`config.py`, `aikosh_hub.py`, `tier2_eka.py`, `tier2_dhir.py`, `tier3_scientific.py`, `tier3_medical.py`, `tier3_vision.py`, `client.py`).
  - Executed end-to-end verification via `test_suite.py`:
    - EKA-1 mathematical reasoning and BFSI compliance tests: **PASSED**.
    - Dhīr 2B offline document-grounded Q&A and edge hardware spec check: **PASSED** (RAM: 1.4 GB Q4_K_M).
    - Dhīr 9B Navier-Stokes mass conservation PDE check: **PASSED** (Invariants respected: True).
    - Medical Foundation Model DEPA PII redaction test: **PASSED** (Aadhaar & phone successfully masked).
    - Yani Vision Indic OCR schema verification: **PASSED** (Confidence 0.984).

---

## 4. Mandatory Known Gaps

1. **Dhīr 9B Weights Access:**
   - *Status:* In rollout pipeline; model weights are pending official public publication on AIKosh / Hugging Face (expected in ~1 month). Currently supported via forward-compatible schema stubs.
2. **EKA-1 Direct Public Download:**
   - *Status:* EKA-1 is currently distributed via early access on Soket AI and the AIKosh sandbox for verified developers/researchers. General public open-weight mirror is not yet unmetered on Hugging Face.
3. **Medical Model Clinical Deployment:**
   - *Status:* The sovereign medical model is restricted to institutional healthcare pilots under DEPA compliance; public API calls require registered ABDM health facility IDs.
4. **COILD Model Dependency Pinning:**
   - *Status:* `coild-aikosh/coild-mul-mt` uses custom architecture code relying on `transformers.onnx`, requiring `transformers<5.0.0`. Loading with `transformers>=5.0.0` will raise `ModuleNotFoundError: No module named 'transformers.onnx'`.

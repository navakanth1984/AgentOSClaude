# Indigenous AI Foundation Models Integration (IndiaAI Mission / AIKosh)

This package integrates sovereign Indian foundation models released under the **IndiaAI Mission** (Ministry of Electronics and Information Technology - MeitY) and the **AIKosh** platform.

## Supported Models

### Tier 2 (Available & Active Sovereign Models)
- **EKA-1 (26.3B)**: Developed by Soket Labs. Sparse hybrid RALSNet architecture with 64K context window. Specialized in mathematical reasoning, algorithmic coding, BFSI compliance, and cybersecurity.
- **Dhīr 2B & Dhīr 5B**: Developed by ZenteiQ / BrahmAI. Compact Mixture-of-Experts (MoE) foundation models trained on Google Cloud TPUs under Apache 2.0. Built for zero-cloud offline mobile/edge execution and document-grounded retrieval.

### Tier 3 (Pipelines & Forward-Compatible Integration)
- **Dhīr 9B (Scientific)**: Combined language and physics-native foundation model designed for simulation telemetry and differential equation / Navier-Stokes validation.
- **Medical Core**: Clinical diagnostic and patient records model compliant with MeitY's **DEPA** (Data Empowerment and Protection Architecture).
- **Yani Vision Core**: Sovereign multimodal vision model for multilingual Indic document OCR (Patta, land records, invoices) and scene comprehension.

---

## Configuration

Set your environment variables in `.env` (or pass via `IndigenousConfig`):

```bash
# AIKosh Credentials
AIKOSH_API_KEY=your_aikosh_key_here
AIKOSH_BASE_URL=https://aikosh.indiaai.gov.in/api/v1

# Soket Labs (EKA-1)
SOKET_API_KEY=your_soket_key_here
SOKET_BASE_URL=https://api.soket.ai/v1

# ZenteiQ / BrahmAI (Dhir Series)
ZENTEIQ_API_KEY=your_zenteiq_key_here
ZENTEIQ_BASE_URL=https://api.brahmai.ai/v1

# Air-Gapped Mode (Optional: routes to local server like vLLM/llama.cpp)
AIRGAP_MODE=false
LOCAL_INFERENCE_URL=http://localhost:8000/v1
```

---

## Usage Examples

```python
from indigenous_ai import IndiaAIClient

client = IndiaAIClient()

# 1. EKA-1 Math & BFSI Reasoning
math_solution = client.eka.solve_math("Integrate x*exp(-x^2) dx from 0 to inf")
code = client.eka.generate_code("Implement a token bucket rate limiter in Python")
bfsi_analysis = client.eka.analyze_bfsi_workflow("Deploying AI underwriting under RBI norms")

# 2. Dhīr 2B/5B Offline Document QA
answer = client.dhir_2b.document_grounded_qa(
    context_document="Project Kavach is an indigenous Automatic Train Protection system.",
    question="What is Project Kavach?"
)

# 3. Dhīr 9B Scientific & Physics Verification
physics_check = client.scientific_9b.verify_physics_derivation(
    equation_latex=r"\nabla \cdot \mathbf{u} = 0",
    physical_domain="Incompressible Flow"
)

# 4. DEPA-Compliant Medical Records Processing
clinical_data = client.medical.extract_clinical_entities(
    "Patient presented with high fever. Aadhaar 4455 6677 8899, Phone 9876543210."
)
# Note: Aadhaar and Phone are automatically masked by DEPA privacy layers!

# 5. Yani Vision Model Document OCR
ocr_data = client.vision.process_document_ocr("land_patta.pdf", target_script="Devanagari")
```

---

## Running the Verification Test Suite

```bash
python indigenous_ai/test_suite.py
```

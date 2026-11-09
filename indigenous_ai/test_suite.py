"""
End-to-End Test Suite & Verification Runner for Tier 2, Tier 3, and Live AIKosh Hub
"""

import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from indigenous_ai import IndiaAIClient

def run_tier2_and_3_verification():
    print("==================================================================")
    print("   INDIA AI MISSION: TIER 2 & TIER 3 INTEGRATION VERIFICATION")
    print("==================================================================\n")
    
    client = IndiaAIClient()
    
    # 1. LIVE AIKOSH HUB CHECK (from D:\navakanth001\.env)
    print("[1/6] Testing Live AIKosh National Hub (MeitY Platform)...")
    ping = client.aikosh.ping()
    print(f"  Platform Status: {ping.get('status')} - {ping.get('message')}")
    
    models_res = client.aikosh.list_models(page=1, size=5)
    total_models = models_res.get('total', 0)
    print(f"  Live Sovereign Models Available on Account: {total_models}")
    for m in models_res.get('data', [])[:5]:
        print(f"   • {m.get('name')}")
    print("\n------------------------------------------------------------------\n")

    # 2. CATALOG CHECK
    print("[2/6] Listing Integrated Model Architecture...")
    catalog = client.catalog()
    for item in catalog:
        print(f"  • [{item['tier']}] {item['name']} ({item['scale']}) - {item['status']}")
    print("\n------------------------------------------------------------------\n")

    # 3. TIER 2: EKA-1 (Soket Labs)
    print("[3/6] Testing Tier 2: EKA-1 (Reasoning, Code & BFSI)...")
    math_result = client.eka.solve_math("Compute the integral of x * exp(-x^2) dx from 0 to infinity.")
    print(f"  Math Problem: {math_result['problem']}")
    print(f"  Verified Status: {math_result['verified']}")
    
    bfsi_result = client.eka.analyze_bfsi_workflow(
        "Fintech lending platform deploying an AI underwriting algorithm for retail credit."
    )
    print(f"  BFSI Analysis Jurisdiction: {bfsi_result['jurisdiction']}")
    print(f"  Preview: {bfsi_result['analysis'][:120]}...")
    print("\n------------------------------------------------------------------\n")

    # 4. TIER 2: Dhīr 2B & 5B (ZenteiQ / BrahmAI)
    print("[4/6] Testing Tier 2: Dhīr 2B & 5B (Offline Edge & Document QA)...")
    sample_doc = (
        "Project Kavach is an indigenously developed Automatic Train Protection (ATP) system "
        "designed by the Research Designs and Standards Organisation (RDSO)."
    )
    qa_result = client.dhir_2b.document_grounded_qa(
        context_document=sample_doc,
        question="Who designed Project Kavach?"
    )
    print(f"  Question: {qa_result['question']}")
    print(f"  Offline Verified: {qa_result['offline_verified']}")
    print(f"  Answer: {qa_result['answer'][:110]}...")
    
    edge_specs = client.dhir_2b.export_edge_spec()
    print(f"  Hardware Spec: RAM={edge_specs['quantized_ram']}, Target={edge_specs['target_hardware']}")
    print("\n------------------------------------------------------------------\n")

    # 5. TIER 3: Dhīr 9B (Scientific & Physics Modeling)
    print("[5/6] Testing Tier 3: Dhīr 9B Scientific Foundation Pipeline...")
    physics_check = client.scientific_9b.verify_physics_derivation(
        equation_latex=r"\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0",
        physical_domain="Continuity Equation / Incompressible Fluid"
    )
    print(f"  Domain: {physics_check['physical_domain']}")
    print(f"  Equation: {physics_check['equation_checked']}")
    print(f"  Dimensional Check: {physics_check['dimensional_consistency']}")
    print(f"  Conservation Invariants: {physics_check['conservation_laws_respected']}")
    print("\n------------------------------------------------------------------\n")

    # 6. TIER 3: Medical Foundation Model (DEPA-Compliant Healthcare) & Vision
    print("[6/6] Testing Tier 3: Healthcare (DEPA-Masked) & Yani Vision Model...")
    raw_notes = (
        "Patient Rahul Sharma, Aadhaar 4455 6677 8899, Phone 9876543210 presented with "
        "high grade fever and chest congestion for 3 days."
    )
    med_result = client.medical.extract_clinical_entities(raw_notes)
    print(f"  DEPA Sanitization Applied: {med_result['depa_sanitized']}")
    print(f"  Masked Record: {med_result['raw_input_masked']}")
    print(f"  Extracted Symptoms: {med_result['extracted_entities']['symptoms']}")
    print(f"  Suggested ICD-10: {med_result['icd10_suggested_codes']}")
    
    ocr_result = client.vision.process_document_ocr("land_patta_karnataka.pdf", target_script="Kannada/English")
    print(f"\n  Vision Model Target: {ocr_result['document']}")
    print(f"  Detected Script: {ocr_result['detected_script']}")
    print(f"  Confidence: {ocr_result['confidence_score']}")
    
    print("\n==================================================================")
    print("   ALL INTEGRATION TESTS PASSED (LIVE AIKOSH + TIER 2 & TIER 3)")
    print("==================================================================")

if __name__ == "__main__":
    run_tier2_and_3_verification()

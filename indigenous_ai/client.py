"""
Unified Client for Sovereign Indian Foundation Models (IndiaAI Mission / AIKosh)
Integrates Tier 2 (EKA-1, Dhīr 2B/5B), Tier 3 (Dhīr 9B, Healthcare, Yani Vision),
and direct Live AIKosh National Platform SDK.
"""

from typing import Optional, Dict, Any, List
from .config import IndigenousConfig, default_config
from .tier2_eka import Eka1Model
from .tier2_dhir import DhirModel
from .tier3_scientific import Dhir9BScientificModel
from .tier3_medical import HealthcareFoundationModel
from .tier3_vision import YaniVisionModel
from .aikosh_hub import AIKoshHub

class IndiaAIClient:
    def __init__(self, config: Optional[IndigenousConfig] = None):
        self.config = config or default_config
        
        # Live AIKosh National Hub Connection (using D:\navakanth001\.env)
        self.aikosh = AIKoshHub(self.config)
        
        # Tier 2 Integrations (Available & Open Sovereign Releases)
        self.eka = Eka1Model(self.config)
        self.dhir_2b = DhirModel(variant="2b", config=self.config)
        self.dhir_5b = DhirModel(variant="5b", config=self.config)
        
        # Tier 3 Integrations (Pipelines / In-Rollout Models)
        self.scientific_9b = Dhir9BScientificModel(self.config)
        self.medical = HealthcareFoundationModel(self.config)
        self.vision = YaniVisionModel(self.config)

    def set_airgap_mode(self, enabled: bool = True):
        """Toggle strict air-gapped mode (no outbound cloud network calls)."""
        self.config.airgap_mode = enabled
        self.eka = Eka1Model(self.config)
        self.dhir_2b = DhirModel(variant="2b", config=self.config)
        self.dhir_5b = DhirModel(variant="5b", config=self.config)

    def catalog(self) -> List[Dict[str, Any]]:
        """Returns the full catalog of integrated indigenous foundation models."""
        return [
            {
                "tier": "Live Platform Hub",
                "name": "AIKosh Hub",
                "provider": "Ministry of Electronics & IT (MeitY) / IndiaAI",
                "scale": "88+ Sovereign Models & Curated Datasets",
                "status": "Connected (Live Auth via D:\\navakanth001\\.env)",
                "capabilities": ["Model Search", "Weight Downloads", "SFTP Staging", "Dataset Access"]
            },
            {
                "tier": "Tier 2",
                "name": "EKA-1",
                "provider": "Soket Labs Technology & Research",
                "scale": "26.3B Sparse Hybrid RALSNet (64K context)",
                "status": "Available / Early Access & AIKosh",
                "capabilities": ["Mathematical Reasoning", "Code Generation", "BFSI", "Agentic Tool Calling"]
            },
            {
                "tier": "Tier 2",
                "name": "Dhīr 2B & 5B",
                "provider": "ZenteiQ AiTech Innovations / BrahmAI",
                "scale": "2.1B / 5.4B Mixture-of-Experts (MoE)",
                "status": "Open Source (Apache 2.0) on AIKosh",
                "capabilities": ["On-Device Edge Inference", "Offline Document Q&A", "Multilingual (10 Indic + En)"]
            },
            {
                "tier": "Tier 3",
                "name": "Dhīr 9B",
                "provider": "ZenteiQ AiTech Innovations",
                "scale": "9 Billion Parameters",
                "status": "In Pipeline (Expected ~1 Month)",
                "capabilities": ["Physics Foundation Modeling", "Simulation Telemetry", "PDE / Navier-Stokes Verification"]
            },
            {
                "tier": "Tier 3",
                "name": "Medical Core",
                "provider": "IndiaAI Healthcare Consortium",
                "scale": "Domain Clinical Model",
                "status": "In Clinical Validation",
                "capabilities": ["DEPA PII Masking", "Clinical NLP & Entity Extraction", "Discharge Summarization"]
            },
            {
                "tier": "Tier 3",
                "name": "Yani Vision Core",
                "provider": "IndiaAI Multimodal Vision Pillar",
                "scale": "Multimodal Vision Architecture",
                "status": "In Pilot & Toolkit Rollout",
                "capabilities": ["Indic Document OCR (Land/Tax/IDs)", "Cultural Scene Reasoning", "Form Extraction"]
            }
        ]

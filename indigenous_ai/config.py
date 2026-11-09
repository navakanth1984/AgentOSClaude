import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

def _find_env():
    candidates = [
        Path.cwd() / ".env.local",
        Path.cwd() / ".env",
        Path("D:/navakanth001/.env.local"),
        Path("D:/navakanth001/.env"),
        Path("c:/Users/navka/navakanth001/.env"),
        Path.home() / ".env"
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

env_file = _find_env()
if env_file:
    try:
        from dotenv import load_dotenv
        # Load both .env and .env.local if present in D:\navakanth001
        for extra in [Path("D:/navakanth001/.env"), Path("D:/navakanth001/.env.local"), env_file]:
            if extra.exists():
                load_dotenv(dotenv_path=extra, override=True)
    except ImportError:
        # Fallback manual parsing if dotenv is not present
        for extra in [Path("D:/navakanth001/.env"), Path("D:/navakanth001/.env.local"), env_file]:
            if extra.exists():
                try:
                    for line in extra.read_text(encoding="utf-8", errors="ignore").splitlines():
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ[k.strip()] = v.strip().strip("'\"")
                except Exception:
                    pass

@dataclass
class IndigenousConfig:
    # AIKosh National Hub (Loaded from D:\navakanth001\.env or .env.local)
    aikosh_api_key: Optional[str] = os.getenv("AIKOSH_API_KEY")
    aikosh_username: Optional[str] = os.getenv("aikosh_Username")
    aikosh_password: Optional[str] = os.getenv("aikosh_Password")
    aikosh_sftp_host: Optional[str] = os.getenv("aikosh_SFTP_HOST")
    aikosh_sftp_port: Optional[str] = os.getenv("aikosh_SFTP_PORT")
    aikosh_base_url: str = os.getenv("AIKOSH_BASE_URL", "https://aikosh.indiaai.gov.in/api/v1")
    
    # Hugging Face key for sovereign repositories (coild-aikosh, BrahmAI, bharatgenai)
    hf_key: Optional[str] = os.getenv("HF_KEY") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    
    # Sarvam AI
    sarvam_api_key: Optional[str] = os.getenv("SARVAM_API_KEY")
    
    # Soket Labs (EKA-1)
    soket_api_key: Optional[str] = os.getenv("SOKET_API_KEY")
    soket_base_url: str = os.getenv("SOKET_BASE_URL", "https://api.soket.ai/v1")
    
    # ZenteiQ / BrahmAI (Dhīr Series)
    zenteiq_api_key: Optional[str] = os.getenv("ZENTEIQ_API_KEY")
    zenteiq_base_url: str = os.getenv("ZENTEIQ_BASE_URL", "https://api.brahmai.ai/v1")
    
    # Air-Gapped & Local Edge Settings
    airgap_mode: bool = os.getenv("AIRGAP_MODE", "false").lower() in ("true", "1", "yes")
    local_inference_url: str = os.getenv("LOCAL_INFERENCE_URL", "http://localhost:8000/v1")
    
    # Fallback to Mock/Sandbox Simulation if keys are pending approval
    simulate_if_missing_key: bool = True

default_config = IndigenousConfig()

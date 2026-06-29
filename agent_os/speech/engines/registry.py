from typing import Dict, Any, Optional
import agent_os.env_boot  # noqa: F401 — load .env before any key lookup
from agent_os.speech.pipeline.interfaces import TTSEngine
from agent_os.speech.engines.kokoro_engine import KokoroEngine

class EngineRegistry:
    """Registry to resolve an engine configuration into a TTSEngine instance."""
    
    @staticmethod
    def get_engine(config: Dict[str, Any]) -> TTSEngine:
        """
        Resolves the engine based on configuration.
        Example config:
        {
            "engine_name": "kokoro",
            "ort_intra_threads": 4
        }
        """
        engine_name = config.get("engine_name", "kokoro").lower()
        
        if engine_name == "kokoro":
            ort_intra = config.get("ort_intra_threads")
            return KokoroEngine(ort_intra_threads=ort_intra)
        elif engine_name == "piper":
            model_path = config.get("piper_model_path")
            from agent_os.speech.engines.piper_engine import PiperEngine
            return PiperEngine(model_path=model_path)
        elif engine_name == "sarvam":
            from agent_os.speech.engines.sarvam_engine import SarvamEngine
            return SarvamEngine(
                api_key=config.get("sarvam_api_key"),
                model=config.get("sarvam_model", "bulbul:v3"),
                default_speaker=config.get("sarvam_default_speaker", "rohan"),
            )

        raise ValueError(f"Unknown engine name in config: {engine_name}")

def resolve_engine(config: Dict[str, Any]) -> TTSEngine:
    """Thin config->engine resolver."""
    return EngineRegistry.get_engine(config)

import os
import json
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List
import numpy as np
import time

from agent_os.speech.pipeline.interfaces import TTSEngine
from agent_os.speech.schema.models import EngineCapabilities, EngineName, Language

class KokoroEngine(TTSEngine):
    """
    Kokoro TTS Engine integration matching the TTSEngine Protocol.
    Manages ONNX model loading and synthesis.
    """
    
    def __init__(self, model_dir: Optional[str] = None):
        self.kokoro = None
        self.active_provider = "Unknown"
        self.capabilities_cache = None
        
        if model_dir:
            self.model_dir = Path(model_dir)
        elif os.environ.get("KOKORO_MODEL_DIR"):
            self.model_dir = Path(os.environ["KOKORO_MODEL_DIR"])
        else:
            project_dir = Path(os.getcwd()) / "agent_os" / "asset_library" / "models" / "kokoro"
            if project_dir.exists() and (project_dir / "kokoro-v0_19.onnx").exists():
                self.model_dir = project_dir
            else:
                self.model_dir = Path.home() / ".cache" / "kokoro"
                
    def validate_model(self) -> None:
        if not self.model_dir.exists():
            raise FileNotFoundError(f"Kokoro model directory not found at: {self.model_dir}")
            
        self.model_path = self.model_dir / "kokoro-v0_19.onnx"
        self.voices_path = self.model_dir / "voices.bin"
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Kokoro ONNX model not found: {self.model_path}")
            
        if not self.voices_path.exists():
            alt_voices_path = self.model_dir / "voices.json"
            if alt_voices_path.exists():
                self.voices_path = alt_voices_path
            else:
                raise FileNotFoundError(f"Kokoro voices file not found at: {self.voices_path} or {alt_voices_path}")
                
    def get_capabilities(self) -> EngineCapabilities:
        if self.capabilities_cache:
            return self.capabilities_cache
            
        self.validate_model()
        
        # We can dynamically get voices by loading the engine briefly,
        # or if we are already warmed up.
        from kokoro_onnx import Kokoro
        try:
            temp_k = self.kokoro if self.kokoro else Kokoro(str(self.model_path), str(self.voices_path))
            discovered_voices = temp_k.get_voices()
            voices_dict = {v: {"gender": "unknown"} for v in discovered_voices}
        except Exception as e:
            print(f"[KokoroEngine] Warning: Could not dynamically discover voices: {e}")
            voices_dict = {"af": {"gender": "female"}, "am": {"gender": "male"}}
        
        self.capabilities_cache = EngineCapabilities(
            engine_name=EngineName.KOKORO,
            supported_languages=[Language.EN, Language.FR, Language.ES, Language.HI, Language.JA, Language.ZH],
            supported_voices=voices_dict,
            max_text_length=500,
            max_concurrent_requests=4,
            supports_streaming=True,
            supports_emotions=False,
            supports_pitch=False,
            supports_speed=True,
            sample_rate=24000,
            output_format="wav"
        )
        return self.capabilities_cache

    def initialize(self) -> None:
        pass
        
    def warmup(self) -> None:
        from kokoro_onnx import Kokoro
        import onnxruntime as ort
        
        available_providers = ort.get_available_providers()
        target_providers = ["CUDAExecutionProvider", "CoreMLExecutionProvider", "CPUExecutionProvider"]
        providers = [p for p in target_providers if p in available_providers]
        if not providers:
            providers = ["CPUExecutionProvider"]
            
        print(f"[KokoroEngine] Requested Execution Providers: {providers}")
        
        # Kokoro instantiation
        self.kokoro = Kokoro(str(self.model_path), str(self.voices_path))
        
        try:
            active = self.kokoro.sess.get_providers()
            print(f"[KokoroEngine] ONNX Runtime Active Provider: {active[0] if active else 'Unknown'}")
            self.active_provider = active[0] if active else "Unknown"
        except AttributeError:
            pass

        print("[KokoroEngine] Warming up with dummy tensor inference...")
        try:
            voices = self.kokoro.get_voices()
            if voices:
                first_voice = next(iter(voices))
                # Using a word instead of space to avoid "need at least one array" exception
                self.synthesize("Warmup", first_voice, 1.0, "en")
        except Exception as e:
            print(f"[KokoroEngine] Warmup silent failure: {e}")
        print("[KokoroEngine] Warmup complete.")
        
    def synthesize(self, text: str, voice: str, speed: float, language: str) -> Tuple[int, np.ndarray]:
        if self.kokoro is None:
            raise RuntimeError("Kokoro engine not warmed up. Call warmup() first.")
            
        lang_code = language if language != "en" else "en-us"
        
        samples, sample_rate = self.kokoro.create(
            text=text,
            voice=voice,
            speed=speed,
            lang=lang_code
        )
        
        if samples.dtype != np.int16:
            samples = (samples * 32767).astype(np.int16)
            
        return sample_rate, samples

    def shutdown(self) -> None:
        self.kokoro = None

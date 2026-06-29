import os
import json
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List
import numpy as np
import time

from agent_os.speech.pipeline.interfaces import TTSEngine
from agent_os.speech.schema.models import EngineCapabilities, EngineName, Language

class PiperEngine(TTSEngine):
    """
    Piper TTS Engine integration matching the TTSEngine Protocol.
    Manages Piper model loading and synthesis.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.voice = None
        self.active_provider = "Unknown"
        self.capabilities_cache = None
        
        if model_path:
            self.model_path = Path(model_path)
            self.model_dir = self.model_path.parent
        elif os.environ.get("PIPER_MODEL_PATH"):
            self.model_path = Path(os.environ["PIPER_MODEL_PATH"])
            self.model_dir = self.model_path.parent
        else:
            project_dir = Path(os.getcwd()) / "agent_os" / "asset_library" / "models" / "piper"
            # Default to en_US-lessac-medium.onnx or similar
            self.model_dir = project_dir
            self.model_path = self.model_dir / "en_US-lessac-medium.onnx"
            
    def validate_model(self) -> None:
        if not self.model_dir.exists():
            raise FileNotFoundError(f"Piper model directory not found at: {self.model_dir}")
            
        self.config_path = self.model_dir / f"{self.model_path.name}.json"
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Piper ONNX model not found: {self.model_path}")
            
        if not self.config_path.exists():
            raise FileNotFoundError(f"Piper JSON config not found at: {self.config_path}")
                
    def get_capabilities(self) -> EngineCapabilities:
        if self.capabilities_cache:
            return self.capabilities_cache
            
        self.validate_model()
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            sample_rate = config.get("audio", {}).get("sample_rate", 22050)
            speakers = config.get("speaker_id_map", {})
            if not speakers:
                # single speaker model
                voices_dict = {"default": {"gender": "unknown"}}
            else:
                voices_dict = {speaker: {"gender": "unknown"} for speaker in speakers.keys()}
        except Exception as e:
            print(f"[PiperEngine] Warning: Could not read config: {e}")
            sample_rate = 22050
            voices_dict = {"default": {"gender": "unknown"}}
        
        self.capabilities_cache = EngineCapabilities(
            engine_name=EngineName.PIPER,
            supported_languages=[Language.EN], # Add more if model supports
            supported_voices=voices_dict,
            max_text_length=500,
            max_concurrent_requests=4,
            supports_streaming=True,
            supports_emotions=False,
            supports_pitch=False,
            supports_speed=True,
            sample_rate=sample_rate,
            output_format="wav"
        )
        return self.capabilities_cache

    def supports_language(self, language: Language) -> bool:
        caps = self.get_capabilities()
        return language in caps.supported_languages

    def supports_voice(self, voice: str) -> bool:
        caps = self.get_capabilities()
        return voice in caps.supported_voices

    def initialize(self) -> None:
        pass

    def warmup(self, profile: str = "minimal") -> None:
        from piper.voice import PiperVoice
        
        print(f"[PiperEngine] Warming up ({profile} profile)...")
        try:
            self.voice = PiperVoice.load(str(self.model_path), config_path=str(self.config_path))
            
            voices = list(self.get_capabilities().supported_voices.keys())
            first_voice = voices[0] if voices else "default"
            text_to_synth = "Warmup" if profile == "minimal" else "This is a representative chunk length for shape specialization warmup."
            # Only synthesize if we successfully loaded
            if self.voice:
                self.synthesize(text_to_synth, first_voice, Language.EN, 1.0)
        except Exception as e:
            print(f"[PiperEngine] Warmup silent failure: {e}")
        print("[PiperEngine] Warmup complete.")
        
    def synthesize(self, text: str, voice: str, language: Language, speed: float) -> Tuple[int, np.ndarray]:
        if self.voice is None:
            raise RuntimeError("Piper engine not warmed up. Call warmup() first.")
            
        caps = self.get_capabilities()
        
        speaker_id = None
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            speakers = config.get("speaker_id_map", {})
            if voice in speakers:
                speaker_id = speakers[voice]
        except:
            pass

        from piper.config import SynthesisConfig
        
        # Synthesize audio using piper
        # piper returns a generator of AudioChunk objects
        syn_config = SynthesisConfig(speaker_id=speaker_id, length_scale=1.0/speed)
        audio_stream = self.voice.synthesize(text, syn_config=syn_config)
        
        audio_bytes = b"".join(chunk.audio_int16_bytes for chunk in audio_stream)
        samples = np.frombuffer(audio_bytes, dtype=np.int16)
            
        return caps.sample_rate, samples

    def shutdown(self) -> None:
        self.voice = None

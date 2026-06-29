"""Sarvam cloud TTS engine (bulbul family) — Indian-language synthesis.

Implements the TTSEngine protocol (ADR-014) so it is a drop-in alongside Kokoro
and Piper. Unlike those, it is a network engine: there is no local model file,
so validate_model() checks for SARVAM_API_KEY instead.
"""
import os
import io
import base64
from typing import Tuple, Optional, List
import numpy as np

import agent_os.env_boot  # noqa: F401 — loads .env so SARVAM_API_KEY is visible
from agent_os.speech.pipeline.interfaces import TTSEngine
from agent_os.speech.schema.models import EngineCapabilities, EngineName, Language

# Languages Sarvam bulbul advertises (all verified 11/11 via direct probe).
_SARVAM_LANGS: List[Language] = [
    Language.EN, Language.HI, Language.BN, Language.KN, Language.ML,
    Language.MR, Language.OD, Language.PA, Language.TA, Language.TE, Language.GU,
]

# bulbul:v3 speakers (as returned by the API). "rohan" is verified across all 11 langs.
_SPEAKERS: List[str] = [
    "rohan", "ritu", "priya", "neha", "pooja", "simran", "kavya", "ishita", "shreya",
    "roopa", "tanya", "shruti", "suhani", "kavitha", "rupali", "niharika",
    "aditya", "ashutosh", "rahul", "amit", "dev", "ratan", "varun", "manan", "sumit",
    "kabir", "aayan", "shubh", "advait", "anand", "tarun", "sunny", "mani", "gokul",
    "vijay", "mohit", "rehan", "soham",
]


class SarvamEngine(TTSEngine):
    SAMPLE_RATE = 22050

    def __init__(self, api_key: Optional[str] = None, model: str = "bulbul:v3",
                 default_speaker: str = "rohan"):
        self.model = model
        self.api_key = api_key or os.environ.get("SARVAM_API_KEY")
        self.default_speaker = default_speaker
        self.client = None
        self.active_provider = "sarvam-cloud"
        self.capabilities_cache = None
        # Set after validate_model so profiling's _engine_version() has something.
        self.model_path = f"sarvam://{model}"

    # ---- lifecycle ----------------------------------------------------------
    def validate_model(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "SARVAM_API_KEY is not set (expected in .env). SarvamEngine cannot run."
            )

    def initialize(self) -> None:
        if self.client is None:
            from sarvamai import SarvamAI
            self.client = SarvamAI(api_subscription_key=self.api_key)

    def warmup(self, profile: str = "minimal") -> None:
        # Cloud engine: stateless requests, no graph to compile. Just ensure the
        # client and key exist so failures surface before chunk fan-out.
        self.validate_model()
        self.initialize()

    def shutdown(self) -> None:
        self.client = None

    # ---- capabilities -------------------------------------------------------
    def get_capabilities(self) -> EngineCapabilities:
        if self.capabilities_cache:
            return self.capabilities_cache
        self.capabilities_cache = EngineCapabilities(
            engine_name=EngineName.SARVAM,
            supported_languages=list(_SARVAM_LANGS),
            supported_voices={s: {"gender": "unknown"} for s in _SPEAKERS},
            max_text_length=1000,          # bulbul per-request soft limit
            max_concurrent_requests=2,     # be polite to the API
            supports_streaming=False,
            supports_emotions=False,
            supports_pitch=True,
            supports_speed=True,
            sample_rate=self.SAMPLE_RATE,
            output_format="wav",
        )
        return self.capabilities_cache

    def supports_language(self, language: Language) -> bool:
        return language in self.get_capabilities().supported_languages

    def supports_voice(self, voice: str) -> bool:
        return voice in self.get_capabilities().supported_voices

    # ---- synthesis ----------------------------------------------------------
    def _lang_code(self, language: Language) -> str:
        """Map our Language enum to Sarvam's '<code>-IN' convention."""
        return f"{language.value}-IN"

    def synthesize(self, text: str, voice: str, language: Language,
                   speed: float) -> Tuple[int, np.ndarray]:
        import soundfile as sf
        if self.client is None:
            self.initialize()
        client = self.client
        if client is None:
            raise RuntimeError("Sarvam client failed to initialize (missing SARVAM_API_KEY?).")

        speaker = voice if voice and voice != "default" else self.default_speaker
        if not self.supports_language(language):
            raise ValueError(f"Sarvam does not support language {language!r}")

        resp = client.text_to_speech.convert(
            text=text,
            target_language_code=self._lang_code(language),
            speaker=speaker,
            model=self.model,
            output_audio_codec="wav",
        )
        if not resp.audios:
            raise RuntimeError("Sarvam returned no audio for the chunk.")

        # Sarvam may split long input into several base64 WAV segments — join them.
        parts: List[np.ndarray] = []
        sr = self.SAMPLE_RATE
        for b64 in resp.audios:
            data, sr = sf.read(io.BytesIO(base64.b64decode(b64)), dtype="int16")
            parts.append(data)
        audio = parts[0] if len(parts) == 1 else np.concatenate(parts)
        return sr, audio

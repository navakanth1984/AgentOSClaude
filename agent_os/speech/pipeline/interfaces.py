from typing import Protocol, List, Tuple
import numpy as np
from agent_os.speech.schema.models import EngineCapabilities, Language

class SentenceSplitter(Protocol):
    """Protocol for splitting text into sentences."""
    def split(self, text: str) -> List[str]:
        ...

class TTSEngine(Protocol):
    """Protocol for TTS Engines (ADR-014)."""
    
    def validate_model(self) -> None:
        """
        Validates model presence and integrity without heavy allocations.
        Should raise FileNotFoundError or validation-specific exceptions if broken.
        """
        ...
        
    def initialize(self) -> None:
        """Performs heavy allocations (e.g. loading ONNX sessions, weights)."""
        ...

    def warmup(self, profile: str = "minimal") -> None:
        """
        Pre-executes or warms up graph shapes.
        profile could be 'minimal' or 'representative'.
        """
        ...

    def shutdown(self) -> None:
        """Safely releases resources."""
        ...

    def get_capabilities(self) -> EngineCapabilities:
        """Returns engine capabilities. Must be deterministic post-initialization."""
        ...

    def supports_language(self, language: Language) -> bool:
        """Convenience wrapper around get_capabilities."""
        ...

    def supports_voice(self, voice: str) -> bool:
        """Convenience wrapper around get_capabilities."""
        ...

    def synthesize(self, text: str, voice: str, language: Language, speed: float) -> Tuple[int, np.ndarray]:
        """The core execution path for synthesis."""
        ...

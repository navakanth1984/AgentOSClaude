from typing import Protocol, List, Tuple
import numpy as np

class SentenceSplitter(Protocol):
    """Protocol for splitting text into sentences."""
    def split(self, text: str) -> List[str]:
        ...

class TTSEngine(Protocol):
    """Protocol for TTS Engines."""
    def initialize(self) -> None:
        ...

    def validate_model(self) -> None:
        """
        Validates model presence and integrity (e.g., checks manifest.json, checksums).
        Should raise an exception if validation fails.
        """
        ...

    def warmup(self) -> None:
        ...

    def synthesize(self, text: str, voice: str, speed: float, language: str) -> Tuple[int, np.ndarray]:
        ...

    def shutdown(self) -> None:
        ...

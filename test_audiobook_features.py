import os
import json
import tempfile
from pathlib import Path
import numpy as np
import pytest
from unittest.mock import patch

from agent_os.speech.audiobook import _split_in_file_chapters, build_audiobook
from agent_os.speech.engines.sarvam_engine import SarvamEngine
from agent_os.speech.schema.models import Language, EngineName
from agent_os.speech.pipeline.interfaces import TTSEngine
from agent_os.speech.schema.models import EngineCapabilities

class MockEngine(TTSEngine):
    def validate_model(self): pass
    def initialize(self): pass
    def warmup(self, profile="minimal"): pass
    def shutdown(self): pass
    def get_capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            engine_name=EngineName.KOKORO,
            supported_languages=[Language.EN],
            supported_voices={"af_heart": {}},
            max_text_length=500,
            max_concurrent_requests=1,
            supports_streaming=False,
            supports_emotions=False,
            supports_pitch=False,
            supports_speed=True,
            sample_rate=24000,
            output_format="wav"
        )
    def supports_language(self, language: Language) -> bool: return True
    def supports_voice(self, voice: str) -> bool: return True
    def synthesize(self, text: str, voice: str, language: Language, speed: float) -> tuple[int, np.ndarray]:
        return 24000, np.zeros(2400, dtype=np.int16)

def test_split_in_file_chapters():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        text_content = (
            "Preface text here before any chapter.\n"
            "Chapter 1\n"
            "This is content of chapter one.\n"
            "CHAPTER 2\n"
            "This is content of chapter two.\n"
            "Chapter III: Adventure\n"
            "This is content of chapter three."
        )
        input_file = tmp_path / "book.txt"
        input_file.write_text(text_content, encoding="utf-8")
        
        chapters = _split_in_file_chapters(input_file, tmp_path)
        assert len(chapters) == 4  # preface + 3 chapters
        
        assert chapters[0].name == "000_preface.txt"
        assert "Preface text" in chapters[0].read_text(encoding="utf-8")
        
        assert "chapter one" in chapters[1].read_text(encoding="utf-8")
        assert "chapter two" in chapters[2].read_text(encoding="utf-8")
        assert "chapter three" in chapters[3].read_text(encoding="utf-8")

def test_build_audiobook_resume_and_parallel():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        text_content = (
            "Chapter 1\n"
            "First chapter text.\n"
            "Chapter 2\n"
            "Second chapter text."
        )
        input_file = tmp_path / "book.txt"
        input_file.write_text(text_content, encoding="utf-8")

        with patch("agent_os.speech.engines.registry.EngineRegistry.get_engine", return_value=MockEngine()):
            # 1. First run to build the book
            manifest1 = build_audiobook(
                input_path=str(input_file),
                book_name="my_test_book",
                engine="kokoro",
                voice="af_heart",
                parser="benchmark",
                base_dir=str(tmp_path),
                max_workers=2
            )
            assert manifest1["chapter_count"] == 2
            assert Path(manifest1["book_wav"]).exists()

            # 2. Second run: testing resume capability
            # We mock run_job to make sure it is NOT called again because chapters are already completed.
            with patch("agent_os.speech.service.SpeechService.run_job") as mock_run_job:
                manifest2 = build_audiobook(
                    input_path=str(input_file),
                    book_name="my_test_book",
                    engine="kokoro",
                    voice="af_heart",
                    parser="benchmark",
                    base_dir=str(tmp_path),
                    max_workers=1
                )
                assert manifest2["chapter_count"] == 2
                mock_run_job.assert_not_called()

def test_sarvam_engine_gender_and_chunking():
    # Test gender metadata is populated
    engine = SarvamEngine(api_key="dummy_key")
    caps = engine.get_capabilities()
    assert caps.supported_voices["rohan"]["gender"] == "male"
    assert caps.supported_voices["ritu"]["gender"] == "female"
    
    # Test text chunking > 1000 characters
    class DummyConvertResponse:
        def __init__(self):
            # Base64 for 1 second of silent 22050Hz 16-bit PCM WAV
            # WAV header + 44100 bytes of zero data
            import io
            import soundfile as sf
            wav_buf = io.BytesIO()
            sf.write(wav_buf, np.zeros(22050, dtype=np.int16), 22050, format="WAV")
            import base64
            self.audios = [base64.b64encode(wav_buf.getvalue()).decode("utf-8")]

    class MockTTS:
        def convert(self, **kwargs):
            assert "pace" in kwargs
            # Ensure text chunk is <= 1000 characters
            assert len(kwargs["text"]) <= 1000
            return DummyConvertResponse()

    class MockSarvamAI:
        def __init__(self, **kwargs):
            self.text_to_speech = MockTTS()

    with patch("sarvamai.SarvamAI", MockSarvamAI):
        engine.initialize()
        # Create a text string longer than 1000 characters
        long_text = ". ".join(["This is a long sentence to exceed limits"] * 40)
        assert len(long_text) > 1000
        
        sr, audio = engine.synthesize(
            text=long_text,
            voice="rohan",
            language=Language.HI,
            speed=1.2
        )
        assert sr == 22050
        assert len(audio) > 0

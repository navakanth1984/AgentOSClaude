import scipy.io.wavfile as wavfile
from pathlib import Path

from agent_os.speech.engines.kokoro_engine import KokoroEngine
from agent_os.speech.schema.models import Language

if __name__ == "__main__":
    text = "The spire remembers what the stars have forgotten... a bronze ghost in a hollow world."
    output = "rust_minar_scene/evolved_narration.wav"
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    try:
        engine = KokoroEngine()
        engine.validate_model()
        engine.warmup("minimal")
        sr, audio = engine.synthesize(text, "af_heart", Language.EN, 1.0)
        wavfile.write(output, sr, audio)
        print(f"Successfully saved to {output}")
    except Exception as e:
        print(f"Failed to synthesize: {e}")

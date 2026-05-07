import sys
import os
import soundfile as sf
from kokoro_onnx import Kokoro

# Paths to models
MODEL_PATH = r"C:\Users\navka\.cache\hyperframes\tts\models\kokoro-v1.0.onnx"
VOICES_PATH = r"C:\Users\navka\.cache\hyperframes\tts\voices\voices-v1.0.bin"

if not os.path.exists(MODEL_PATH):
    print(f"Model not found at {MODEL_PATH}")
    sys.exit(1)

kokoro = Kokoro(MODEL_PATH, VOICES_PATH)

scripts = [
    ("How can I trust you?", "am_adam", "arjun_01.wav"),
    ("I made mistakes. I am still learning.", "af_nova", "veda_01.wav"),
    ("How can you learn while lives are lost?", "am_adam", "arjun_02.wav"),
    ("I want to protect you. I will protect you.", "af_nova", "veda_02.wav"),
    ("How will you protect me... when you can’t even protect yourself?", "am_adam", "arjun_03.wav"),
    ("I might not be able to protect myself. But I will protect—", "af_nova", "veda_03.wav"),
    ("He is here.", "af_nova", "veda_04.wav")
]

for text, voice, output in scripts:
    print(f"Generating {output} ({voice}): {text}")
    samples, sample_rate = kokoro.create(text, voice=voice, speed=1.0, lang="en-us")
    sf.write(output, samples, sample_rate)
    print(f"Saved to {output}")

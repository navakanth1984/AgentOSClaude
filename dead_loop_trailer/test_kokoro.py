import os
print("Starting")
from kokoro_onnx import Kokoro
print("Imported")
MODEL_PATH = r"C:\Users\navka\.cache\hyperframes\tts\models\kokoro-v1.0.onnx"
VOICES_PATH = r"C:\Users\navka\.cache\hyperframes\tts\voices\voices-v1.0.bin"
print(f"Loading {MODEL_PATH}")
kokoro = Kokoro(MODEL_PATH, VOICES_PATH)
print("Loaded")

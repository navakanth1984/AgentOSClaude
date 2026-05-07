import sys
import os
import base64
import json
import requests
import soundfile as sf
from kokoro_onnx import Kokoro

def download_file(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {url}...")
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)

def synthesize(text, output_path, voice_name="af_nova"):
    model_path = "rust_minar_scene/kokoro.onnx"
    voices_path = "rust_minar_scene/voices.bin"

    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}.")
        return

    kokoro = Kokoro(model_path, voices_path)
    samples, sample_rate = kokoro.create(text, voice=voice_name, speed=1.0, lang="en-us")
    sf.write(output_path, samples, sample_rate)
    print(f"Successfully saved to {output_path}")

if __name__ == "__main__":
    text = "The spire remembers what the stars have forgotten... a bronze ghost in a hollow world."
    output = "rust_minar_scene/evolved_narration.wav"
    synthesize(text, output)

import os
import base64
from pathlib import Path
from sarvamai import SarvamAI

# Load .env file into environment if present
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip().strip("'\""))

api_key = os.getenv("SARVAM_API_KEY")
if not api_key:
    raise ValueError("SARVAM_API_KEY is not set.")

client = SarvamAI(api_subscription_key=api_key)

output_dir = Path(__file__).resolve().parent / "voice_samples"
output_dir.mkdir(exist_ok=True)

samples = [
    {
        "filename": "sample_english.wav",
        "text": "Welcome to Sarvam AI. Text-to-speech synthesis is operational.",
        "language_code": "en-IN",
        "speaker": "aditya",
    },
    {
        "filename": "sample_hindi.wav",
        "text": "सर्वम एआई में आपका स्वागत है। हमारी आवाज़ तकनीक सक्रिय है।",
        "language_code": "hi-IN",
        "speaker": "shreya",
    },
    {
        "filename": "sample_telugu.wav",
        "text": "సర్వం ఏఐకి స్వాగతం. మీ వాయిస్ నమూనాలు సిద్ధంగా ఉన్నాయి.",
        "language_code": "te-IN",
        "speaker": "kavitha",
    },
]

print("Starting voice sample generation with Sarvam AI Text-to-Speech (bulbul:v3)...")

for sample in samples:
    print(f"Generating {sample['filename']} ({sample['language_code']})...")
    res = client.text_to_speech.convert(
        text=sample["text"],
        language_code=sample["language_code"],
        speaker=sample["speaker"],
        model="bulbul:v3",
    )

    audio_bytes = base64.b64decode(res.audios[0])
    file_path = output_dir / sample["filename"]
    with open(file_path, "wb") as f:
        f.write(audio_bytes)
    
    print(f"Saved: {file_path.name} ({len(audio_bytes)} bytes)")

print("All voice samples successfully generated in:", output_dir)

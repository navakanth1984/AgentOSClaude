import os
from pathlib import Path
from sarvamai import SarvamAI

env_path = Path(".env")
if env_path.exists():
    with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

client = SarvamAI(api_subscription_key=os.getenv("SARVAM_API_KEY"))

dir_path = Path("voice_samples/mad_tillu_climax")
files = sorted([f for f in dir_path.glob("*.wav") if "master" not in f.name])

print(f"Checking {len(files)} files with Sarvam Speech-to-Text (Saaras)...")
for f in files:
    try:
        with open(f, "rb") as audio_file:
            res = client.speech_to_text.transcribe(
                file=audio_file,
                model="saaras:v3"
            )
            print(f"{f.name:<20}: \"{res.transcript}\"")
    except Exception as e:
        print(f"{f.name:<20}: ERROR: {e}")

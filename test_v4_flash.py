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

with open("voice_samples/mad_tillu_climax/mad_tillu_climax_master.wav", "rb") as f:
    res = client.speech_to_text.transcribe(
        file=f,
        model="saaras:v3"
    )
    print("Master Transcription:", res.transcript)

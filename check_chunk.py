import os, wave, io
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

with wave.open("voice_samples/mad_tillu_climax/mad_tillu_climax_master.wav", "rb") as w:
    rate = w.getframerate()
    w.setpos(50 * rate)
    frames = w.readframes(20 * rate)
    
buf = io.BytesIO()
with wave.open(buf, "wb") as w_chunk:
    w_chunk.setnchannels(1)
    w_chunk.setsampwidth(2)
    w_chunk.setframerate(22050)
    w_chunk.writeframes(frames)

buf.seek(0)
res = client.speech_to_text.transcribe(
    file=("chunk.wav", buf, "audio/wav"),
    model="saaras:v3"
)
print("10s to 30s Transcription:", res.transcript)

import os, base64
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

res1 = client.text_to_speech.convert(
    text="Aa rod teeyi. Stand ki towel enduku?",
    language_code="te-IN",
    speaker="mani",
    model="bulbul:v3"
)
print("te-IN audio bytes:", len(base64.b64decode(res1.audios[0])))

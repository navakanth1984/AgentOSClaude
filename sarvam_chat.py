import os
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
    raise ValueError("SARVAM_API_KEY is not set. Please add your API key to .env")

client = SarvamAI(api_subscription_key=api_key)

response = client.chat.completions(
    model="sarvam-105b-conversations",
    messages=[
        {"role": "user", "content": "Hello! Please introduce yourself in one short sentence."}
    ],
)

print(response.choices[0].message.content)

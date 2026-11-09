import os
import httpx
from pathlib import Path

env_path = Path("D:/navakanth001/.env")
if not env_path.exists():
    env_path = Path("C:/Users/navka/navakanth001/.env")

with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if line.startswith("OPENROUTER_API_KEY="):
            os.environ["OPENROUTER_API_KEY"] = line.strip().split("=", 1)[1].strip("'\"")

with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if line.startswith("ELEVENLABS_API_KEY="):
            os.environ["ELEVENLABS_API_KEY"] = line.strip().split("=", 1)[1].strip("'\"")

key = os.getenv("ELEVENLABS_API_KEY")
print("ElevenLabs Key found:", bool(key))

client = httpx.Client(timeout=15.0)
res = client.get(
    "https://api.elevenlabs.io/v1/user",
    headers={"xi-api-key": key}
)
print("ElevenLabs status:", res.status_code)
if res.status_code == 200:
    sub = res.json().get("subscription", {})
    chars = sub.get("character_limit", 0) - sub.get("character_count", 0)
    print(f"ElevenLabs tier: {sub.get('tier')}, characters available: {chars:,}")

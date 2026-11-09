import os
import base64
import time
from pathlib import Path
from sarvamai import SarvamAI

# Load .env
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

api_key = os.getenv("SARVAM_API_KEY")
if not api_key:
    raise ValueError("SARVAM_API_KEY is not set.")

client = SarvamAI(api_subscription_key=api_key)

output_dir = Path(__file__).resolve().parent / "voice_samples" / "tillu_auditions"
output_dir.mkdir(parents=True, exist_ok=True)

# Tillu audition line
audition_text = "Sir. First of all — congratulations. Second of all, you have come to the right man at the wrong time, which is lucky, because I am about to become very expensive."

# Male speakers available in bulbul:v3
male_speakers = [
    "sunny",
    "aditya",
    "kabir",
    "tarun",
    "varun",
    "dev",
    "shubh",
    "rohan",
    "rahul",
    "amit",
    "manan",
    "sumit",
    "aayan",
    "ashutosh",
    "advait",
    "anand",
    "mohit",
    "rehan",
    "soham",
    "vijay",
    "gokul",
    "mani",
    "ratan",
]

results = []

print(f"=== Auditioning Tillu Line across {len(male_speakers)} Speakers ===")
print(f"Line: \"{audition_text}\"\n")

for spk in male_speakers:
    filename = f"tillu_{spk}.wav"
    filepath = output_dir / filename
    print(f"Synthesizing [{spk}]... ", end="", flush=True)
    
    t0 = time.time()
    try:
        res = client.text_to_speech.convert(
            text=audition_text,
            language_code="en-IN",
            speaker=spk,
            pace=1.06,
            model="bulbul:v3",
        )
        audio_data = base64.b64decode(res.audios[0])
        with open(filepath, "wb") as f:
            f.write(audio_data)
        elapsed = time.time() - t0
        print(f"OK ({len(audio_data):,} bytes, {elapsed:.1f}s)")
        results.append({"speaker": spk, "file": filename, "path": str(filepath), "bytes": len(audio_data), "status": "success"})
    except Exception as e:
        print(f"FAILED: {e}")
        results.append({"speaker": spk, "file": filename, "status": "failed", "error": str(e)})

print(f"\nAll auditions complete! Generated in: {output_dir}")

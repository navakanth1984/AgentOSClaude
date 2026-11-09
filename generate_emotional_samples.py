import os
import base64
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

output_dir = Path(__file__).resolve().parent / "voice_samples" / "mani_emotional_tones"
output_dir.mkdir(parents=True, exist_ok=True)

variations = [
    {
        "filename": "mani_01_dry_deadpan.wav",
        "label": "Dry & Deadpan (Bone-dry, unimpressed, flat delivery)",
        "model": "bulbul:v3",
        "speaker": "mani",
        "text": "Sir. First of all, congratulations. Second of all, you have come to the right man at the wrong time. Which is lucky. Because I am about to become very expensive.",
        "pace": 0.90,
        "temperature": 0.12,
    },
    {
        "filename": "mani_02_sarcastic_witty.wav",
        "label": "Sarcastic & Witty (Smirking, sarcastic pauses, rhetorical lift)",
        "model": "bulbul:v3",
        "speaker": "mani",
        "text": "Sir... First of all? Congratulations! Second of all... you have come to the right man, at the completely wrong time... which is lucky! Because I am about to become... very, very expensive.",
        "pace": 1.10,
        "temperature": 0.85,
    },
    {
        "filename": "mani_03_emotionally_active.wav",
        "label": "Emotionally Active / Flamboyant (High-energy, punchy intonations)",
        "model": "bulbul:v3",
        "speaker": "mani",
        "text": "Sir! First of all — congratulations! Second of all, you have come to the right man at the wrong time... which is lucky! Because I am about to become very, very expensive!",
        "pace": 1.18,
        "temperature": 0.95,
    },
    {
        "filename": "mani_04_smug_slowburn.wav",
        "label": "Smug Slow-Burn (Deliberate pauses, calculating, cinematic weight)",
        "model": "bulbul:v3",
        "speaker": "mani",
        "text": "Sir... First of all... congratulations. Second of all... you have come to the right man at the wrong time. Which is lucky... because I am about to become... very expensive.",
        "pace": 0.82,
        "temperature": 0.35,
    },
]

# Also check an expressive persona from bulbul:v4-flash for comparison
try:
    variations.append({
        "filename": "v4_dev_conversational.wav",
        "label": "bulbul:v4-flash Persona (dev_en_conversational)",
        "model": "bulbul:v4-flash",
        "speaker": "dev_en_conversational",
        "text": "Sir... First of all? Congratulations. Second of all, you have come to the right man at the wrong time, which is lucky, because I am about to become very expensive.",
        "pace": 1.12,
        "temperature": 0.80,
    })
except Exception:
    pass

print("=== Generating Emotional & Tonal Variations for Mani ===")

for var in variations:
    filepath = output_dir / var["filename"]
    print(f"\nGenerating: {var['label']} -> {var['filename']}...")
    try:
        kwargs = {
            "text": var["text"],
            "language_code": "en-IN",
            "speaker": var["speaker"],
            "pace": var["pace"],
            "temperature": var["temperature"],
            "model": var["model"],
        }
        res = client.text_to_speech.convert(**kwargs)
        audio_data = base64.b64decode(res.audios[0])
        with open(filepath, "wb") as f:
            f.write(audio_data)
        print(f" Saved: {var['filename']} ({len(audio_data):,} bytes)")
    except Exception as e:
        print(f" Error: {e}")

print(f"\nAll variations generated in: {output_dir}")

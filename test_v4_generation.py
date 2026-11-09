import os
import base64
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

output_dir = Path("voice_samples/test_v4_native")
output_dir.mkdir(parents=True, exist_ok=True)

tests = [
    {
        "file": "father_confession_v4.wav",
        "speaker": "tarun_te_narration",
        "text": "లక్ష్మి... సావిత్రి... నేను రైల్వే పాయింట్స్ మ్యాన్ ని కాదు. నేను కొరియర్ ని. రెండు ఇళ్ళు... ఒక ఖాళీ పెట్టె... ముప్పై ఏళ్ళు నేను చెప్పిన ఒక్కటే నిజం: మీరంటే నాకు ఇష్టం. మిగతాదంతా అబద్ధం. నన్ను క్షమించొద్దు.",
        "lang": "te-IN"
    },
    {
        "file": "savitri_v4.wav",
        "speaker": "kavitha_te_conversation",
        "text": "దీపం ఆరిపోయింది. మీరంటే నాకు ఇంకా ఏ నమ్మకమూ లేదు.",
        "lang": "te-IN"
    },
    {
        "file": "tillu_v4.wav",
        "speaker": "tarun_te_narration",
        "text": "అన్నా! మీరు ఒక మాట అన్నారు కదా, మేము మూడు ఎంట్రీస్ అని? కరెక్ట్! మేము మూడు ఎంట్రీస్! ఈ రోజు మేము అకౌంట్ సెటిల్ చేస్తున్నాం!",
        "lang": "te-IN"
    }
]

for t in tests:
    print(f"Generating {t['file']} with {t['speaker']} (bulbul:v4-flash @ 24kHz)...")
    res = client.text_to_speech.convert(
        text=t["text"],
        language_code=t["lang"],
        speaker=t["speaker"],
        model="bulbul:v4-flash",
        speech_sample_rate=24000
    )
    data = base64.b64decode(res.audios[0])
    with open(output_dir / t["file"], "wb") as f:
        f.write(data)
    print(f"Saved {t['file']}: {len(data):,} bytes")

print("\n=== Transcribing Generated Files with Saaras:v3 ===")
for t in tests:
    fpath = output_dir / t["file"]
    with open(fpath, "rb") as audio:
        res = client.speech_to_text.transcribe(file=audio, model="saaras:v3")
        print(f"{t['file']}: \"{res.transcript}\"")

import os
import wave
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

output_dir = Path(__file__).resolve().parent / "voice_samples" / "mad_tillu_climax_v4_studio"
output_dir.mkdir(parents=True, exist_ok=True)

# Native Telugu script for 100% authentic pronunciation on bulbul:v4-flash @ 24kHz
script_v4 = [
    # Card 47: Anna's Speech
    {
        "id": "01_anna",
        "char": "ANNA",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 0.94,
        "text": "కుటుంబం అంటే ఏంటి అనుకుంటున్నారు? రక్తం కాదు. లెడ్జర్. ఎవ్రీవన్ ఈజ్ ఐదర్ ఎన్ అసెట్, లేదా డెట్."
    },
    {
        "id": "02_anna",
        "char": "ANNA",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 0.92,
        "text": "నువ్వు బ్రదర్ వి కాదు టిల్లూ... నీ తండ్రి లెడ్జర్ లో ఒక ఎంట్రీవి మాత్రమే."
    },

    # Card 48: The Father's Confession (Anjaneyulu)
    {
        "id": "03_anjaneyulu",
        "char": "ANJANEYULU",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 0.88,
        "text": "లక్ష్మీ... సావిత్రీ... నేను రైల్వే పాయింట్స్ మ్యాన్ ని కాదు. నేను కొరియర్ ని."
    },
    {
        "id": "04_anjaneyulu",
        "char": "ANJANEYULU",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 0.86,
        "text": "రెండు ఇళ్ళు... ఒక ఖాళీ పెట్టె... ముప్పై ఏళ్ళు నేను చెప్పిన ఒక్కటే నిజం: మీరంటే నాకు ఇష్టం. మిగతాదంతా అబద్ధం."
    },
    {
        "id": "05_anjaneyulu",
        "char": "ANJANEYULU",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 0.84,
        "text": "నన్ను క్షమించొద్దు."
    },

    # Card 49: The Two Wives Refusal
    {
        "id": "06_savitri",
        "char": "SAVITRI",
        "spk": "kavitha_te_conversation",
        "lang": "te-IN",
        "pace": 0.90,
        "text": "దీపం ఆరిపోయింది."
    },
    {
        "id": "07_lakshmi",
        "char": "LAKSHMI",
        "spk": "pooja_te_conversation",
        "lang": "te-IN",
        "pace": 0.92,
        "text": "అకౌంట్ క్లోజ్."
    },

    # Card 51: Junior Refuses Anna
    {
        "id": "08_junior",
        "char": "JUNIOR",
        "spk": "dev_en_conversational",
        "lang": "en-IN",
        "pace": 1.02,
        "text": "Anna gaaru. A son is just a cost centre. Your own words. This wedding is not mine, it is your business asset. I am resigning."
    },

    # Card 52: Settling the Account (Tillu, Laddu, Bunty)
    {
        "id": "09_tillu",
        "char": "TILLU",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 1.08,
        "text": "అన్నా! మీరు ఒక మాట అన్నారు కదా, మేము మూడు ఎంట్రీస్ అని? కరెక్ట్! మేము మూడు ఎంట్రీస్!"
    },
    {
        "id": "10_tillu",
        "char": "TILLU",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 1.08,
        "text": "ఈ రోజు మేము అకౌంట్ సెటిల్ చేస్తున్నాం! ఇది టిల్లు ఈవెంట్స్ కాంట్రాక్ట్ డబ్బులు. ఇది కంపెనీ అసెట్స్."
    },
    {
        "id": "11_laddu",
        "char": "LADDU",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 0.92,
        "text": "మా నాన్న ఎవరికీ ఏమీ బాకీ లేడు."
    },
    {
        "id": "12_bunty",
        "char": "BUNTY",
        "spk": "dev_en_conversational",
        "lang": "en-IN",
        "pace": 1.04,
        "text": "Take my passport too. My father's name is Ganesh Kumar Goud, and he is coming home with us."
    },
    {
        "id": "13_tillu",
        "char": "TILLU",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 0.95,
        "text": "మా నాన్న."
    },
    {
        "id": "14_laddu",
        "char": "LADDU",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 0.92,
        "text": "మా నాన్న."
    },
    {
        "id": "15_bunty",
        "char": "BUNTY",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 0.95,
        "text": "మా నాన్న."
    },

    # Card 53: Arrest & Final Box
    {
        "id": "16_ashok",
        "char": "ASHOK (IPS)",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 0.95,
        "text": "అన్నాగారూ... బ్యాంకాక్ పోలీస్ బయట వెయిట్ చేస్తోంది. స్టెప్ డౌన్."
    },
    {
        "id": "17_tillu",
        "char": "TILLU",
        "spk": "tarun_te_narration",
        "lang": "te-IN",
        "pace": 1.05,
        "text": "పెట్టెలో ఎప్పుడూ ఏమీ లేదు అన్నారు కదా అన్నా? ఇప్పుడు చూడు... పెట్టెలో రైల్వే ల్యాంప్ ఉంది, లెడ్జర్ ఉంది. ఈసారి... బాక్స్ ఫుల్ గా ఉంది!"
    }
]

print(f"=== Synthesizing Studio Climax with bulbul:v4-flash @ 24kHz ({len(script_v4)} lines) ===")

generated_files = []

for idx, item in enumerate(script_v4, start=1):
    filename = f"{item['id']}_{item['char'].replace(' ', '_').lower()}.wav"
    filepath = output_dir / filename
    print(f"[{idx:02d}/{len(script_v4)}] {item['char']} ({item['spk']}) ... ", end="", flush=True)
    
    t0 = time.time()
    try:
        res = client.text_to_speech.convert(
            text=item["text"],
            language_code=item["lang"],
            speaker=item["spk"],
            pace=item["pace"],
            speech_sample_rate=24000,
            model="bulbul:v4-flash",
        )
        audio_data = base64.b64decode(res.audios[0])
        with open(filepath, "wb") as f:
            f.write(audio_data)
        elapsed = time.time() - t0
        print(f"OK ({len(audio_data):,} B, {elapsed:.1f}s)")
        generated_files.append({"char": item["char"], "file": filepath})
    except Exception as e:
        print(f"FAILED: {e}")

# Assemble Master Audio Track
master_file = output_dir / "mad_tillu_climax_studio_v4_master.wav"
print(f"\nStitching Master Track: {master_file.name} (24,000 Hz Studio Quality)...")

with wave.open(str(generated_files[0]["file"]), "rb") as w0:
    params = w0.getparams()
    rate = params.framerate
    channels = params.nchannels
    width = params.sampwidth

default_silence = b"\x00" * int(rate * 0.40 * channels * width)
dramatic_silence = b"\x00" * int(rate * 0.85 * channels * width)
huge_silence = b"\x00" * int(rate * 1.30 * channels * width)

with wave.open(str(master_file), "wb") as w_out:
    w_out.setparams(params)
    for i, item in enumerate(generated_files):
        with wave.open(str(item["file"]), "rb") as w_in:
            w_out.writeframes(w_in.readframes(w_in.getnframes()))
        if i < len(generated_files) - 1:
            if i in [1, 4, 6, 7, 11, 14]:
                w_out.writeframes(huge_silence if i in [4, 7, 14] else dramatic_silence)
            else:
                w_out.writeframes(default_silence)

print(f" Master Track Complete: {master_file.stat().st_size:,} bytes")
print(f"All files saved to: {output_dir}")

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

output_dir = Path(__file__).resolve().parent / "voice_samples" / "mad_tillu_climax"
output_dir.mkdir(parents=True, exist_ok=True)

# Cards 47–53 Climax Script
script = [
    # Card 47: Anna's Speech (Vijay)
    {"char": "ANNA", "spk": "vijay", "pace": 0.92, "temp": 0.25, "lang": "te-IN", "text": "Kutumbam ante enti anukuntunnaru? Blood kaadu. Ledger. Everyone is either an asset or a debt."},
    {"char": "ANNA", "spk": "vijay", "pace": 0.90, "temp": 0.25, "lang": "te-IN", "text": "Nuvvu brother kaadu Tillu. Nee father ledger lo oka entry."},

    # Card 48: The Father's Confession on Mic (Ratan)
    {"char": "ANJANEYULU", "spk": "ratan", "pace": 0.88, "temp": 0.40, "lang": "te-IN", "text": "Lakshmi... Savitri... Nenu railway pointsman kaadu. Nenu courier ni."},
    {"char": "ANJANEYULU", "spk": "ratan", "pace": 0.86, "temp": 0.40, "lang": "te-IN", "text": "Rendu illu... oka empty box... Muppai samvatsaralu nenu cheppina okkate nijam: Meerante naaku istam. Migithadi antha abaddham."},
    {"char": "ANJANEYULU", "spk": "ratan", "pace": 0.85, "temp": 0.35, "lang": "te-IN", "text": "Nannu kshaminchoddhu."},

    # Card 49: The Two Wives Refusal
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.88, "temp": 0.35, "lang": "te-IN", "text": "Lamp aari poyindi."},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.92, "temp": 0.25, "lang": "te-IN", "text": "Account close."},

    # Card 51: Junior Refuses Anna
    {"char": "JUNIOR", "spk": "dev", "pace": 1.00, "temp": 0.35, "lang": "te-IN", "text": "Anna gaaru. A son is just a cost centre. Meeru cheppina maate kada? Ee wedding naadi kaadu... Mee business asset. I am leaving."},

    # Card 52: The Climax Payoff — Settling the Account (Tillu, Laddu, Bunty)
    {"char": "TILLU", "spk": "mani", "pace": 1.08, "temp": 0.85, "lang": "te-IN", "text": "Anna! Meeru oka maata annaru kada? Memu moodu entries ani? Correct! Memu moodu entries!"},
    {"char": "TILLU", "spk": "mani", "pace": 1.10, "temp": 0.88, "lang": "te-IN", "text": "Ee roju memu account settle chestunnam! Idi Tillu Events contract dabbulu. Idi company assets."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.92, "temp": 0.20, "lang": "te-IN", "text": "Maa nanna evariki emi baaki ledu."},
    {"char": "BUNTY", "spk": "sunny", "pace": 1.05, "temp": 0.60, "lang": "en-IN", "text": "Take my passport too. My father's name is Ganesh Kumar Goud. And he is coming home with us."},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.80, "lang": "te-IN", "text": "Maa nanna."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.90, "temp": 0.20, "lang": "te-IN", "text": "Maa nanna."},
    {"char": "BUNTY", "spk": "sunny", "pace": 1.00, "temp": 0.50, "lang": "te-IN", "text": "Maa nanna."},

    # Card 53: Arrest & Key Image (Ashok & Tillu)
    {"char": "ASHOK", "spk": "ashutosh", "pace": 0.95, "temp": 0.25, "lang": "te-IN", "text": "Anna gaaru. Bangkok police bayata wait chestundi. Step down."},
    {"char": "TILLU", "spk": "mani", "pace": 1.08, "temp": 0.85, "lang": "te-IN", "text": "Box lo eppudu emi ledu annaru kada Anna? Ippudu chudu. Box lo railway lamp undi, ledger undi. Ee sari... box full ga undi!"},
]

print(f"=== Synthesizing MAD TILLU Climax Sequence (Cards 47–53: {len(script)} Lines) ===")

generated_lines = []

for idx, item in enumerate(script, start=1):
    tag = f"{idx:02d}_{item['char'].lower()}"
    line_path = output_dir / f"{tag}.wav"
    print(f"[{idx:02d}/{len(script)}] {item['char']} ({item['spk']}): \"{item['text'][:40]}...\" ... ", end="", flush=True)
    
    t0 = time.time()
    try:
        res = client.text_to_speech.convert(
            text=item["text"],
            language_code=item["lang"],
            speaker=item["spk"],
            pace=item["pace"],
            temperature=item["temp"],
            model="bulbul:v3",
        )
        audio_data = base64.b64decode(res.audios[0])
        with open(line_path, "wb") as f:
            f.write(audio_data)
        elapsed = time.time() - t0
        print(f"OK ({len(audio_data):,} B, {elapsed:.1f}s)")
        generated_lines.append({"idx": idx, "char": item["char"], "file": line_path, "bytes": len(audio_data)})
    except Exception as e:
        print(f"FAILED: {e}")

print(f"\nAll {len(generated_lines)} lines synthesized successfully.")

# Assemble Master Track with cinematic pacing
master_path = output_dir / "mad_tillu_climax_master.wav"
print(f"\nAssembling Master Track: {master_path.name}...")

with wave.open(str(generated_lines[0]["file"]), 'rb') as w0:
    params = w0.getparams()
    rate = params.framerate
    channels = params.nchannels
    width = params.sampwidth

default_silence = b'\x00' * int(rate * 0.40 * channels * width)
long_silence = b'\x00' * int(rate * 0.80 * channels * width)
huge_silence = b'\x00' * int(rate * 1.20 * channels * width)

with wave.open(str(master_path), 'wb') as w_out:
    w_out.setparams(params)
    for i, item in enumerate(generated_lines):
        with wave.open(str(item["file"]), 'rb') as w_in:
            w_out.writeframes(w_in.readframes(w_in.getnframes()))
        if i < len(generated_lines) - 1:
            # Extended silence after father's confession, after the wives' verdicts, and before "Maa nanna" claims
            if item["char"] == "ANNA" and i == 1:
                w_out.writeframes(long_silence)
            elif item["char"] == "ANJANEYULU" and i == 4:
                w_out.writeframes(huge_silence)
            elif item["char"] == "LAKSHMI" and i == 6:
                w_out.writeframes(long_silence)
            elif item["char"] == "JUNIOR" and i == 7:
                w_out.writeframes(huge_silence)
            elif item["char"] == "BUNTY" and "passport" in script[i]["text"]:
                w_out.writeframes(long_silence)
            elif item["char"] == "BUNTY" and "Maa nanna" in script[i]["text"]:
                w_out.writeframes(huge_silence)
            else:
                w_out.writeframes(default_silence)

print(f" Master Climax Track Ready: {master_path.stat().st_size:,} bytes")
print(f"Saved to: {output_dir}")

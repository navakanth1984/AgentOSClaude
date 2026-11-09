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

output_dir = Path(__file__).resolve().parent / "voice_samples" / "mad_tillu_sequence4_interval"
output_dir.mkdir(parents=True, exist_ok=True)

# Sequence 4: The Police Station Interval (Cards 17–18)
script = [
    # Beat 1: The Two Complaints (Tillu, Laddu, Rao)
    {"char": "RAO", "spk": "ashutosh", "pace": 0.96, "temp": 0.35, "lang": "te-IN", "text": "Missing person. Rendu complaints. Okate peru."},
    {"char": "TILLU", "spk": "mani", "pace": 1.10, "temp": 0.85, "lang": "te-IN", "text": "Okate peru kaadu sir. Okate photo kuda."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.92, "temp": 0.20, "lang": "te-IN", "text": "Okate shirt."},
    {"char": "RAO", "spk": "ashutosh", "pace": 0.95, "temp": 0.30, "lang": "te-IN", "text": "Shirt?"},
    {"char": "LADDU", "spk": "rohan", "pace": 0.90, "temp": 0.20, "lang": "te-IN", "text": "Grey."},
    {"char": "RAO", "spk": "ashutosh", "pace": 0.92, "temp": 0.25, "lang": "te-IN", "text": "Grey shirt."},
    {"char": "TILLU", "spk": "mani", "pace": 1.08, "temp": 0.85, "lang": "te-IN", "text": "Sir, rendu complaints teesukokandi."},
    {"char": "RAO", "spk": "ashutosh", "pace": 0.95, "temp": 0.30, "lang": "te-IN", "text": "Enduku?"},
    {"char": "TILLU", "spk": "mani", "pace": 1.12, "temp": 0.88, "lang": "te-IN", "text": "Rendu complaints unte rendu files. Rendu files unte rendu officers. Rendu officers unte evaru maatladaru."},
    {"char": "RAO", "spk": "ashutosh", "pace": 0.95, "temp": 0.40, "lang": "te-IN", "text": "Nuvvu lawyer va?"},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.80, "lang": "te-IN", "text": "Kaadu sir. Event management."},

    # Beat 2: Lakshmi Enters
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.98, "temp": 0.30, "lang": "te-IN", "text": "Maa aayana missing."},
    {"char": "RAO", "spk": "ashutosh", "pace": 0.95, "temp": 0.25, "lang": "te-IN", "text": "Peru?"},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.98, "temp": 0.30, "lang": "te-IN", "text": "Anjaneyulu. Railway. Pointsman. Thirty-one years service."},
    {"char": "TILLU", "spk": "mani", "pace": 0.95, "temp": 0.70, "lang": "te-IN", "text": "Amma."},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 1.00, "temp": 0.35, "lang": "te-IN", "text": "Nuvvu ikkada enduku?"},
    {"char": "TILLU", "spk": "mani", "pace": 0.95, "temp": 0.70, "lang": "te-IN", "text": "Nanna kosam."},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 1.00, "temp": 0.35, "lang": "te-IN", "text": "Nanna kosam nuvvu police station ki vachava?"},
    {"char": "TILLU", "spk": "mani", "pace": 0.95, "temp": 0.70, "lang": "te-IN", "text": "Vachanu."},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 1.02, "temp": 0.35, "lang": "te-IN", "text": "Last week naaku cheppavu — Nanna tho matladataniki time ledu."},
    {"char": "TILLU", "spk": "mani", "pace": 1.02, "temp": 0.75, "lang": "te-IN", "text": "Amma, idi public place."},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.98, "temp": 0.30, "lang": "te-IN", "text": "Telusu. Anduke cheptunnanu."},

    # Beat 3: Savitri Arrives with Railway Lamp
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.92, "temp": 0.35, "lang": "te-IN", "text": "Meeru evaru?"},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.98, "temp": 0.30, "lang": "te-IN", "text": "Nenu evaru? Meeru evaru?"},
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.90, "temp": 0.35, "lang": "te-IN", "text": "Nenu Anjaneyulu gaari bhaarya."},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.92, "temp": 0.25, "lang": "te-IN", "text": "...Aa peru maa aayana peru."},
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.92, "temp": 0.35, "lang": "te-IN", "text": "Meeru aa peru ela cheptunnaru?"},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.95, "temp": 0.25, "lang": "te-IN", "text": "Nenu thirty-one years nundi cheptunnanu."},
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.92, "temp": 0.35, "lang": "te-IN", "text": "Nenu twenty-nine years nundi cheptunnanu."},

    # Beat 4: Inspector Rao's Interjection
    {"char": "RAO", "spk": "ashutosh", "pace": 0.90, "temp": 0.30, "lang": "te-IN", "text": "Rendu years gap undi."},
    {"char": "RAO", "spk": "ashutosh", "pace": 0.92, "temp": 0.40, "lang": "te-IN", "text": "Just... noting."},

    # Beat 5: Lamp vs Ledger & The Postings
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.95, "temp": 0.30, "lang": "te-IN", "text": "Aa lamp enduku?"},
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.90, "temp": 0.40, "lang": "te-IN", "text": "Ayana posting lo unnappudu raatri vasthaadu. Lamp veyyakapote daari kanipinchadu."},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.95, "temp": 0.30, "lang": "te-IN", "text": "Ayana Hyderabad lo unde."},
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.92, "temp": 0.35, "lang": "te-IN", "text": "Ayana Vizag lo unde."},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.95, "temp": 0.25, "lang": "te-IN", "text": "Ninety-four lo Hyderabad."},
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.92, "temp": 0.30, "lang": "te-IN", "text": "Ninety-four lo Vizag."},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.92, "temp": 0.25, "lang": "te-IN", "text": "...Rendu chotala undi undali."},
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.90, "temp": 0.30, "lang": "te-IN", "text": "Ela?"},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.88, "temp": 0.20, "lang": "te-IN", "text": "Railway."},

    # Beat 6: The Interval Cut — Ledger Opens
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.90, "temp": 0.30, "lang": "te-IN", "text": "Meeru accounts pedataaru?"},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.92, "temp": 0.25, "lang": "te-IN", "text": "Pedatanu."},
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.90, "temp": 0.30, "lang": "te-IN", "text": "Nenu pettanu."},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.92, "temp": 0.25, "lang": "te-IN", "text": "Telusu."},
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.90, "temp": 0.35, "lang": "te-IN", "text": "Ela telusu?"},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.95, "temp": 0.30, "lang": "te-IN", "text": "Meeru lamp teesukocharu. Nenu ledger teesukocharu."},
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.88, "temp": 0.35, "lang": "te-IN", "text": "Andulo emi undi?"},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.92, "temp": 0.25, "lang": "te-IN", "text": "Twenty-five years of postings."},
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.88, "temp": 0.35, "lang": "te-IN", "text": "Chupinchandi."},
    {"char": "LAKSHMI", "spk": "shreya", "pace": 0.88, "temp": 0.25, "lang": "te-IN", "text": "Chupisthe... meeru chusi... maarchukoleru."},
    {"char": "SAVITRI", "spk": "kavitha", "pace": 0.85, "temp": 0.35, "lang": "te-IN", "text": "Naku telusu."},
]

print(f"=== Synthesizing MAD TILLU Sequence 4 (Interval: {len(script)} Lines) ===")

generated_lines = []

for idx, item in enumerate(script, start=1):
    tag = f"{idx:02d}_{item['char'].lower()}"
    line_path = output_dir / f"{tag}.wav"
    print(f"[{idx:02d}/{len(script)}] {item['char']} ({item['spk']}): \"{item['text']}\" ... ", end="", flush=True)
    
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

# Assemble Master Scene Track with dramatic interval timing
master_path = output_dir / "mad_tillu_sequence4_interval_master.wav"
print(f"\nAssembling Master Track: {master_path.name}...")

with wave.open(str(generated_lines[0]["file"]), 'rb') as w0:
    params = w0.getparams()
    rate = params.framerate
    channels = params.nchannels
    width = params.sampwidth

# Default pause: 0.42 seconds; dramatic pauses between key beats
default_silence = b'\x00' * int(rate * 0.42 * channels * width)
long_silence = b'\x00' * int(rate * 0.75 * channels * width)

with wave.open(str(master_path), 'wb') as w_out:
    w_out.setparams(params)
    for i, item in enumerate(generated_lines):
        with wave.open(str(item["file"]), 'rb') as w_in:
            w_out.writeframes(w_in.readframes(w_in.getnframes()))
        if i < len(generated_lines) - 1:
            # Add longer dramatic pause before Rao's 'Rendu years gap undi' and after 'Chupisthe...'
            if item["char"] == "SAVITRI" and "twenty-nine years" in script[i]["text"]:
                w_out.writeframes(long_silence)
            elif item["char"] == "RAO" and "noting" in script[i]["text"]:
                w_out.writeframes(long_silence)
            elif item["char"] == "LAKSHMI" and "Railway" in script[i]["text"]:
                w_out.writeframes(long_silence)
            elif item["char"] == "LAKSHMI" and "maarchukoleru" in script[i]["text"]:
                w_out.writeframes(long_silence)
            else:
                w_out.writeframes(default_silence)

print(f" Master Interval Scene Ready: {master_path.stat().st_size:,} bytes")
print(f"Saved to: {output_dir}")

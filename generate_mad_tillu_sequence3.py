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

output_dir = Path(__file__).resolve().parent / "voice_samples" / "mad_tillu_sequence3"
output_dir.mkdir(parents=True, exist_ok=True)

# Sequence 3 Dialogue Breakdown
script = [
    # --- Scene 12: The Collision ---
    {"char": "TILLU", "spk": "mani", "pace": 1.08, "temp": 0.85, "lang": "te-IN", "text": "Aa rod teeyi."},
    {"char": "SHIVA", "spk": "sunny", "pace": 1.02, "temp": 0.60, "lang": "te-IN", "text": "Rod kaadu. Stand."},
    {"char": "TILLU", "spk": "mani", "pace": 1.10, "temp": 0.85, "lang": "te-IN", "text": "Stand ki towel enduku?"},
    {"char": "SHIVA", "spk": "sunny", "pace": 1.00, "temp": 0.65, "lang": "te-IN", "text": "Stand ki dignity kavali."},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.80, "lang": "te-IN", "text": "Maa father ekkada?"},
    {"char": "LADDU", "spk": "rohan", "pace": 0.95, "temp": 0.20, "lang": "te-IN", "text": "Maa nanna ekkada?"},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.85, "lang": "te-IN", "text": "...Maa father."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.95, "temp": 0.20, "lang": "te-IN", "text": "Maa nanna."},
    {"char": "TILLU", "spk": "mani", "pace": 1.10, "temp": 0.85, "lang": "te-IN", "text": "Maa father. Bala Gangadhar Tilak gaari father! Sixty-two. Grey shirt. Knee problem."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.92, "temp": 0.20, "lang": "te-IN", "text": "Maa nanna. Sixty-two. Grey shirt. Knee problem."},
    {"char": "TILLU", "spk": "mani", "pace": 1.02, "temp": 0.80, "lang": "te-IN", "text": "Idi coincidence la undi..."},
    {"char": "MARCUS", "spk": "dev", "pace": 1.05, "temp": 0.50, "lang": "te-IN", "text": "Anna, coincidence ante rendu separate vishayalu."},
    {"char": "TILLU", "spk": "mani", "pace": 1.10, "temp": 0.85, "lang": "te-IN", "text": "Correct."},
    {"char": "TILLU", "spk": "mani", "pace": 1.08, "temp": 0.85, "lang": "te-IN", "text": "Nuvvu evaru?"},
    {"char": "LADDU", "spk": "rohan", "pace": 0.95, "temp": 0.20, "lang": "te-IN", "text": "Nenu Laddu. Ganesh. ECE."},
    {"char": "TILLU", "spk": "mani", "pace": 1.12, "temp": 0.88, "lang": "te-IN", "text": "ECE?"},
    {"char": "LADDU", "spk": "rohan", "pace": 0.95, "temp": 0.20, "lang": "te-IN", "text": "Engineering. Four years. Plus one extra year."},
    {"char": "TILLU", "spk": "mani", "pace": 1.10, "temp": 0.85, "lang": "te-IN", "text": "Okay. Laddu. Maa father ni nuvvu etthukellav. Ransom kosam."},
    {"char": "LADDU", "spk": "rohan", "pace": 1.00, "temp": 0.25, "lang": "te-IN", "text": "Maa nanna ni nuvvu etthukellav! City batch!"},
    {"char": "TILLU", "spk": "mani", "pace": 1.10, "temp": 0.85, "lang": "te-IN", "text": "Maa father ni evaru etthukellaru?"},
    {"char": "LADDU", "spk": "rohan", "pace": 0.95, "temp": 0.25, "lang": "te-IN", "text": "Maa nanna ni."},
    {"char": "TILLU", "spk": "mani", "pace": 1.10, "temp": 0.85, "lang": "te-IN", "text": "Maa nanna ni evaru etthukellaru?"},
    {"char": "LADDU", "spk": "rohan", "pace": 1.05, "temp": 0.35, "lang": "te-IN", "text": "NAA FATHER NI!"},
    {"char": "TILLU", "spk": "mani", "pace": 1.15, "temp": 0.90, "lang": "te-IN", "text": "NUVVU MAA FATHER NI ETTHUKELLAV!"},
    {"char": "LADDU", "spk": "rohan", "pace": 1.08, "temp": 0.35, "lang": "te-IN", "text": "NUVVU MAA NANNA NI ETTHUKELLAV!"},

    # --- Scene 13/14: Sweets, Bouncer, Ringing Phone ---
    {"char": "TILLU", "spk": "mani", "pace": 1.00, "temp": 0.80, "lang": "te-IN", "text": "Ivi ekkada konnaru?"},
    {"char": "COUSIN", "spk": "shubh", "pace": 0.95, "temp": 0.30, "lang": "te-IN", "text": "Maa amma chesindi."},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.85, "lang": "te-IN", "text": "Mee amma chesindi aa?"},
    {"char": "COUSIN", "spk": "shubh", "pace": 0.95, "temp": 0.30, "lang": "te-IN", "text": "Aunu."},
    {"char": "TILLU", "spk": "mani", "pace": 0.95, "temp": 0.80, "lang": "te-IN", "text": "...Chala bagunnai."},
    {"char": "TILLU", "spk": "mani", "pace": 1.08, "temp": 0.85, "lang": "te-IN", "text": "Aa newspaper enduku?"},
    {"char": "BOUNCER", "spk": "ashutosh", "pace": 0.90, "temp": 0.20, "lang": "te-IN", "text": "Chaduvutaniki anna."},
    {"char": "TILLU", "spk": "mani", "pace": 1.10, "temp": 0.85, "lang": "te-IN", "text": "Ippudu chaduvutunnava?"},
    {"char": "BOUNCER", "spk": "ashutosh", "pace": 0.90, "temp": 0.20, "lang": "te-IN", "text": "Aunu."},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.85, "lang": "te-IN", "text": "Cheppu."},
    {"char": "BOUNCER", "spk": "ashutosh", "pace": 0.85, "temp": 0.20, "lang": "te-IN", "text": "Hyderabad lo..."},
    {"char": "TILLU", "spk": "mani", "pace": 1.15, "temp": 0.85, "lang": "te-IN", "text": "Chalu!"},
    {"char": "TILLU", "spk": "mani", "pace": 1.10, "temp": 0.85, "lang": "te-IN", "text": "Vaddu."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.95, "temp": 0.20, "lang": "te-IN", "text": "Meeru vaddu."},

    # --- Scene 15/16: The Storeroom Arithmetic ---
    {"char": "TILLU", "spk": "mani", "pace": 1.00, "temp": 0.80, "lang": "te-IN", "text": "Aa photo."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.92, "temp": 0.20, "lang": "te-IN", "text": "Chusanu."},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.82, "lang": "te-IN", "text": "Inko sari chudu."},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.85, "lang": "te-IN", "text": "Rendu pellillu... Okate groom."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.92, "temp": 0.20, "lang": "te-IN", "text": "Rendu dates."},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.85, "lang": "te-IN", "text": "Cheppu."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.90, "temp": 0.20, "lang": "te-IN", "text": "Ninety-four. Ninety-six."},
    {"char": "TILLU", "spk": "mani", "pace": 1.02, "temp": 0.80, "lang": "te-IN", "text": "Nenu puttindhi... ninety-five."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.90, "temp": 0.20, "lang": "te-IN", "text": "Nenu puttindhi ninety-eight."},
    {"char": "TILLU", "spk": "mani", "pace": 0.95, "temp": 0.85, "lang": "te-IN", "text": "Ante... nenu... nuvvu..."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.85, "temp": 0.25, "lang": "te-IN", "text": "...Anna?"},
    {"char": "TILLU", "spk": "mani", "pace": 1.15, "temp": 0.90, "lang": "te-IN", "text": "Ayyo! Aa word vaddu!"},
    {"char": "LADDU", "spk": "rohan", "pace": 0.92, "temp": 0.20, "lang": "te-IN", "text": "Enduku?"},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.85, "lang": "te-IN", "text": "Vintha ga undi."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.92, "temp": 0.20, "lang": "te-IN", "text": "Nijame kada."},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.85, "lang": "te-IN", "text": "Nijam intha strange ga unda kudadu!"},
    {"char": "LADDU", "spk": "rohan", "pace": 0.88, "temp": 0.25, "lang": "te-IN", "text": "Evaru aa pillodu?"},
    {"char": "TILLU", "spk": "mani", "pace": 0.95, "temp": 0.75, "lang": "te-IN", "text": "Telidu."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.92, "temp": 0.20, "lang": "te-IN", "text": "Nuvvu telusukovali."},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.85, "lang": "te-IN", "text": "Nuvvu telusukovali."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.92, "temp": 0.25, "lang": "te-IN", "text": "Manam telusukovali."},
    {"char": "TILLU", "spk": "mani", "pace": 1.05, "temp": 0.85, "lang": "te-IN", "text": "'Manam'?"},
    {"char": "LADDU", "spk": "rohan", "pace": 0.90, "temp": 0.20, "lang": "te-IN", "text": "Manam."},
    {"char": "TILLU", "spk": "mani", "pace": 0.95, "temp": 0.80, "lang": "te-IN", "text": "Naa life lo first time... nenu oka lie cheppaledu."},
    {"char": "LADDU", "spk": "rohan", "pace": 0.90, "temp": 0.20, "lang": "te-IN", "text": "Adi nijam."},
    {"char": "TILLU", "spk": "mani", "pace": 1.00, "temp": 0.85, "lang": "te-IN", "text": "Telusu. Anduke bhayam ga undi."},
]

print(f"=== Synthesizing MAD TILLU Sequence 3 ({len(script)} Lines) ===")

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

print(f"\nCompleted line generation: {len(generated_lines)} files created.")

# Stitch into 2 Part Acts and 1 Master Mix
print("\n=== Stitching Master Audio Tracks ===")

def stitch_waves(file_list, output_file, pause_sec=0.35):
    if not file_list:
        return
    with wave.open(str(file_list[0]), 'rb') as w0:
        params = w0.getparams()
        rate = params.framerate
        channels = params.nchannels
        width = params.sampwidth

    silence = b'\x00' * int(rate * pause_sec * channels * width)
    with wave.open(str(output_file), 'wb') as w_out:
        w_out.setparams(params)
        for i, f in enumerate(file_list):
            with wave.open(str(f), 'rb') as w_in:
                w_out.writeframes(w_in.readframes(w_in.getnframes()))
            if i < len(file_list) - 1:
                w_out.writeframes(silence)
    print(f"Created: {output_file.name} ({output_file.stat().st_size:,} bytes)")

# Part 1: Cards 12-14 (Lines 1 to 38)
part1_files = [item["file"] for item in generated_lines[:38]]
stitch_waves(part1_files, output_dir / "01_convention_hall_collision.wav", pause_sec=0.35)

# Part 2: Cards 15-16 (Lines 39 onwards)
part2_files = [item["file"] for item in generated_lines[38:]]
stitch_waves(part2_files, output_dir / "02_storeroom_arithmetic.wav", pause_sec=0.45)

# Master Complete Sequence
all_files = [item["file"] for item in generated_lines]
stitch_waves(all_files, output_dir / "mad_tillu_sequence3_full_scene.wav", pause_sec=0.38)

print(f"\nAll files saved in: {output_dir}")

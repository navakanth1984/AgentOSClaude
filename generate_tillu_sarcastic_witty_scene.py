import os
import wave
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

output_dir = Path(__file__).resolve().parent / "voice_samples" / "tillu_sarcastic_witty_scene"
output_dir.mkdir(parents=True, exist_ok=True)

scene = [
    {
        "id": "01_tillu_intro",
        "character": "TILLU (Mani)",
        "speaker": "mani",
        "language_code": "en-IN",
        "text": "Sir... First of all? Congratulations! Second of all... you have come to the right man, at the completely wrong time... which is lucky! Because I am about to become... very, very expensive.",
        "pace": 1.10,
        "temperature": 0.85,
    },
    {
        "id": "02_father_quote",
        "character": "BRIDE'S FATHER (Ratan)",
        "speaker": "ratan",
        "language_code": "te-IN",
        "text": "కోట్ లో ఫార్టీ లాక్ ఉంది. Quote lo forty lakh undi.",
        "pace": 0.92,
        "temperature": 0.20,
    },
    {
        "id": "03_tillu_payoff",
        "character": "TILLU (Mani)",
        "speaker": "mani",
        "language_code": "en-IN",
        "text": "Correct! That is for the wedding... The forty is not the wedding, sir. The forty is the silence after the wedding! Three hundred relatives go home... the hall is empty... your daughter looks at you... what will you have?",
        "pace": 1.10,
        "temperature": 0.88,
    },
]

generated_files = []

print("=== Generating Full DJ Tillu Scene (Sarcastic & Witty Take) ===")

for line in scene:
    filename = f"{line['id']}.wav"
    filepath = output_dir / filename
    print(f"\nSynthesizing {line['character']} [pace={line['pace']}, temp={line['temperature']}]...")
    
    res = client.text_to_speech.convert(
        text=line["text"],
        language_code=line["language_code"],
        speaker=line["speaker"],
        pace=line["pace"],
        temperature=line["temperature"],
        model="bulbul:v3",
    )
    
    audio_data = base64.b64decode(res.audios[0])
    with open(filepath, "wb") as f:
        f.write(audio_data)
    
    print(f" Saved: {filename} ({len(audio_data):,} bytes)")
    generated_files.append(filepath)

# Stitch master scene with natural conversational timing
master_path = output_dir / "tillu_sarcastic_witty_master.wav"
print(f"\nAssembling Master Track: {master_path.name}...")

with wave.open(str(generated_files[0]), 'rb') as w_first:
    params = w_first.getparams()
    sample_rate = params.framerate
    n_channels = params.nchannels
    sampwidth = params.sampwidth

# 0.45 second comedic pause between character turns
silence_frames = int(sample_rate * 0.45)
silence_bytes = b'\x00' * (silence_frames * n_channels * sampwidth)

with wave.open(str(master_path), 'wb') as w_out:
    w_out.setparams(params)
    for i, fpath in enumerate(generated_files):
        with wave.open(str(fpath), 'rb') as w_in:
            w_out.writeframes(w_in.readframes(w_in.getnframes()))
        if i < len(generated_files) - 1:
            w_out.writeframes(silence_bytes)

print(f" Master Scene Ready: {master_path.stat().st_size:,} bytes")
print(f"All files saved to: {output_dir}")

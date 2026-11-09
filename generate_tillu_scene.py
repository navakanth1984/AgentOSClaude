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

output_dir = Path(__file__).resolve().parent / "voice_samples" / "tillu_scene"
output_dir.mkdir(parents=True, exist_ok=True)

dialogues = [
    {
        "id": "01_tillu",
        "character": "TILLU",
        "text": "Sir. First of all — congratulations. Second of all, you have come to the right man at the wrong time, which is lucky, because I am about to become very expensive.",
        "speaker": "tarun",  # Upbeat, youthful
        "language_code": "en-IN",
        "pace": 1.08,
    },
    {
        "id": "02_father",
        "character": "BRIDE'S FATHER",
        "text": "కోట్ లో ఫార్టీ లాక్ ఉంది. Quote lo forty lakh undi.",
        "speaker": "ratan",  # Mature, grounded
        "language_code": "te-IN",
        "pace": 0.95,
    },
    {
        "id": "03_tillu",
        "character": "TILLU",
        "text": "Correct. That is for the wedding. The forty is not the wedding, sir. The forty is the silence after the wedding. Three hundred relatives go home, the hall is empty, your daughter looks at you — what will you have?",
        "speaker": "tarun",
        "language_code": "en-IN",
        "pace": 1.05,
    },
]

generated_files = []

print("=== Generating Voice Track for DJ Tillu Scene ===")
for d in dialogues:
    filename = f"{d['id']}_{d['character'].replace(' ', '_').lower()}.wav"
    filepath = output_dir / filename
    print(f"\nSynthesizing {d['character']} using speaker '{d['speaker']}' ({d['language_code']})...")
    
    res = client.text_to_speech.convert(
        text=d["text"],
        language_code=d["language_code"],
        speaker=d["speaker"],
        pace=d["pace"],
        model="bulbul:v3",
    )
    
    audio_data = base64.b64decode(res.audios[0])
    with open(filepath, "wb") as f:
        f.write(audio_data)
    
    print(f" Saved: {filename} ({len(audio_data)} bytes)")
    generated_files.append(filepath)

# Stitch together into full scene
master_path = output_dir / "tillu_scene_master.wav"
print(f"\nCombining tracks into master scene: {master_path.name}...")

try:
    with wave.open(str(generated_files[0]), 'rb') as w_first:
        params = w_first.getparams()
        sample_rate = params.framerate
        n_channels = params.nchannels
        sampwidth = params.sampwidth

    # 0.4 second silence between lines
    silence_frames = int(sample_rate * 0.4)
    silence_bytes = b'\x00' * (silence_frames * n_channels * sampwidth)

    with wave.open(str(master_path), 'wb') as w_out:
        w_out.setparams(params)
        for i, fpath in enumerate(generated_files):
            with wave.open(str(fpath), 'rb') as w_in:
                w_out.writeframes(w_in.readframes(w_in.getnframes()))
            if i < len(generated_files) - 1:
                w_out.writeframes(silence_bytes)
                
    print(f" Master scene successfully created: {master_path.stat().st_size} bytes")
except Exception as e:
    print(f"Stitching note: {e}")

print("\nDone! All files ready in:", output_dir)

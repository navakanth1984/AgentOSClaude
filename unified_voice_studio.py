import os
import wave
import base64
import time
import struct
from pathlib import Path
from gradio_client import Client, handle_file
from sarvamai import SarvamAI

# 1. Environment & API Keys
env_path = Path(__file__).resolve().parent / ".env"
if not env_path.exists():
    env_path = Path("D:/navakanth001/.env")

if env_path.exists():
    with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

sarvam_api_key = os.getenv("SARVAM_API_KEY")
if not sarvam_api_key:
    raise ValueError("SARVAM_API_KEY not found in .env")

sarvam_client = SarvamAI(api_subscription_key=sarvam_api_key)

output_dir = Path(__file__).resolve().parent / "voice_samples" / "unified_studio_scene"
output_dir.mkdir(parents=True, exist_ok=True)

# 2. Resampling Helper (Linear Interpolation for 16-bit Mono PCM)
def resample_wave_mono_16bit(in_bytes, in_rate, out_rate):
    if in_rate == out_rate or not in_bytes:
        return in_bytes
    num_samples = len(in_bytes) // 2
    samples = struct.unpack(f"<{num_samples}h", in_bytes)
    out_len = int(num_samples * out_rate / in_rate)
    ratio = float(in_rate) / float(out_rate)
    out_samples = []
    for i in range(out_len):
        pos = i * ratio
        idx = int(pos)
        frac = pos - idx
        if idx >= num_samples - 1:
            out_samples.append(samples[-1])
        else:
            s0 = samples[idx]
            s1 = samples[idx + 1]
            interp = int(s0 + frac * (s1 - s0))
            out_samples.append(max(-32768, min(32767, interp)))
    return struct.pack(f"<{out_len}h", *out_samples)

# 3. Scene Script with Multi-Engine Routing
# Tillu: mani (bulbul:v3) calibrated for sarcastic/witty pacing (1.12x)
# Shiva: tarun_te_narration (bulbul:v4-flash)
# Savitri: kavitha_te_conversation (bulbul:v4-flash)
scene_manifest = [
    {
        "id": "01_tillu",
        "char": "TILLU",
        "engine": "sarvam_v3",
        "speaker": "mani",
        "model": "bulbul:v3",
        "text": "ఆ రాడ్ తీయి.",
        "pace": 1.12,
        "pause_after": 0.35,
    },
    {
        "id": "02_shiva",
        "char": "SHIVA",
        "engine": "sarvam_v4",
        "speaker": "tarun_te_narration",
        "model": "bulbul:v4-flash",
        "text": "రాడ్ కాదు. స్టాండ్.",
        "pace": 1.00,
        "pause_after": 0.30,
    },
    {
        "id": "03_tillu",
        "char": "TILLU",
        "engine": "sarvam_v3",
        "speaker": "mani",
        "model": "bulbul:v3",
        "text": "స్టాండ్ కి టవల్ ఎందుకు?",
        "pace": 1.15,
        "pause_after": 0.35,
    },
    {
        "id": "04_shiva",
        "char": "SHIVA",
        "engine": "sarvam_v4",
        "speaker": "tarun_te_narration",
        "model": "bulbul:v4-flash",
        "text": "స్టాండ్ కి డిగ్నిటీ కావాలి.",
        "pace": 0.98,
        "pause_after": 0.45,
    },
    {
        "id": "05_savitri",
        "char": "SAVITRI",
        "engine": "sarvam_v4",
        "speaker": "kavitha_te_conversation",
        "model": "bulbul:v4-flash",
        "text": "దీపం ఆరిపోకుండా చూసుకోవడం నా బాధ్యత.",
        "pace": 0.90,
        "pause_after": 0.40,
    },
    {
        "id": "06_tillu",
        "char": "TILLU",
        "engine": "sarvam_v3",
        "speaker": "mani",
        "model": "bulbul:v3",
        "text": "ఇది కోఇన్సిడెన్స్ లా లేదు. మేము ఇద్దరం ఒకే మనిషి కొడుకులం.",
        "pace": 1.08,
        "pause_after": 0.50,
    }
]

generated_lines = []

print(f"\n=== Running Multi-Engine Table Read Studio ({len(scene_manifest)} Lines) ===")

TARGET_RATE = 24000

for idx, item in enumerate(scene_manifest, start=1):
    fpath = output_dir / f"{item['id']}_{item['char'].lower()}.wav"
    print(f"\n[{idx}/{len(scene_manifest)}] {item['char']} via [{item['engine'].upper()} / {item['speaker']}] ... ", end="", flush=True)
    t0 = time.time()
    
    try:
        kwargs = {
            "text": item["text"],
            "language_code": "te-IN",
            "speaker": item["speaker"],
            "pace": item.get("pace", 1.0),
            "model": item["model"]
        }
        if item["model"] == "bulbul:v4-flash":
            kwargs["speech_sample_rate"] = TARGET_RATE
            
        res = sarvam_client.text_to_speech.convert(**kwargs)
        raw_wav = base64.b64decode(res.audios[0])
        
        # Save raw audio
        with open(fpath, "wb") as f:
            f.write(raw_wav)
            
        # Inspect and resample to TARGET_RATE if needed
        with wave.open(str(fpath), "rb") as w_check:
            native_rate = w_check.getframerate()
            channels = w_check.getnchannels()
            sampwidth = w_check.getsampwidth()
            pcm_frames = w_check.readframes(w_check.getnframes())
            
        if native_rate != TARGET_RATE:
            resampled_pcm = resample_wave_mono_16bit(pcm_frames, native_rate, TARGET_RATE)
            with wave.open(str(fpath), "wb") as w_resamp:
                w_resamp.setnchannels(channels)
                w_resamp.setsampwidth(sampwidth)
                w_resamp.setframerate(TARGET_RATE)
                w_resamp.writeframes(resampled_pcm)
                
        elapsed = time.time() - t0
        print(f"OK ({fpath.stat().st_size:,} B, 24kHz, {elapsed:.1f}s)")
        generated_lines.append({"file": fpath, "pause": item["pause_after"]})
    except Exception as e:
        print(f"Rendering Error: {e}")

# Master Stitching (24,000 Hz 16-bit PCM)
master_wav = output_dir / "unified_studio_master_scene.wav"
print(f"\nStitching Master Unified Scene: {master_wav.name}...")

rate = TARGET_RATE
channels = 1
width = 2

with wave.open(str(master_wav), "wb") as w_out:
    w_out.setnchannels(channels)
    w_out.setsampwidth(width)
    w_out.setframerate(rate)
    
    for i, item in enumerate(generated_lines):
        with wave.open(str(item["file"]), "rb") as w_in:
            w_out.writeframes(w_in.readframes(w_in.getnframes()))
        if i < len(generated_lines) - 1:
            pause_bytes = b"\x00" * int(rate * item["pause"] * channels * width)
            w_out.writeframes(pause_bytes)

print(f"\n Master Audio Drama Complete: {master_wav.stat().st_size:,} bytes")
print(f"All files saved to: {output_dir}")

import os
import wave
import base64
import time
import struct
import json
from pathlib import Path
from sarvamai import SarvamAI

# 1. Environment & API Setup
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

client = SarvamAI(api_subscription_key=sarvam_api_key)

output_base_dir = Path(__file__).resolve().parent / "voice_samples" / "mad_tillu_act2"
output_base_dir.mkdir(parents=True, exist_ok=True)

TARGET_RATE = 24000

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

# 3. Act Two Screenplay Manifest
act2_production = {
    "scene_19_20_interval_fallout": {
        "title": "Scene 19-20: Cold Clarity & The Decoy Ledger",
        "description": "Police station continuous: Lakshmi and Savitri compare postings. The phone unlocks 25 years of syndicate messages.",
        "lines": [
            {
                "id": "01_lakshmi",
                "char": "LAKSHMI",
                "speaker": "kavitha_te_conversation",
                "model": "bulbul:v4-flash",
                "pace": 0.95,
                "pause_after": 0.35,
                "text": "రెండు వేల ఒకటి... జూలై పదిహేను. ఎక్కడ ఉన్నారు మీ ఆయన?"
            },
            {
                "id": "02_savitri",
                "char": "SAVITRI",
                "speaker": "kavitha_te_narration",
                "model": "bulbul:v4-flash",
                "pace": 0.90,
                "pause_after": 0.35,
                "text": "విశాఖపట్నం జంక్షన్. డ్యూటీలో ఉన్నారు. నాకు మనీ ఆర్డర్ పంపించారు."
            },
            {
                "id": "03_lakshmi",
                "char": "LAKSHMI",
                "speaker": "kavitha_te_conversation",
                "model": "bulbul:v4-flash",
                "pace": 0.95,
                "pause_after": 0.40,
                "text": "ఇదిగో నా లెడ్జర్. ఆ రోజు రాత్రి సికింద్రాబాద్ లో నాకు పట్టుచీర కొనిచ్చారు."
            },
            {
                "id": "04_tillu",
                "char": "TILLU",
                "speaker": "mani",
                "model": "bulbul:v3",
                "pace": 1.12,
                "pause_after": 0.30,
                "text": "అమ్మా... కూల్ అవ్వమ్మా. రెండు వేల ఒకటి లో ట్రాఫిక్ చాలా ఎక్కువ ఉండేది, అటు ఇటు తిరిగారేమో."
            },
            {
                "id": "05_lakshmi",
                "char": "LAKSHMI",
                "speaker": "kavitha_te_conversation",
                "model": "bulbul:v4-flash",
                "pace": 0.95,
                "pause_after": 0.35,
                "text": "నువ్వు నోరు మూయ్ తిల్లూ. నీకన్నా పెద్ద అబద్ధాలకోరు మీ నాన్న."
            },
            {
                "id": "06_laddu",
                "char": "LADDU",
                "speaker": "tarun_te_narration",
                "model": "bulbul:v4-flash",
                "pace": 0.95,
                "pause_after": 0.35,
                "text": "అమ్మా... ఆ ఫోన్ లో మెసేజ్ లు వస్తున్నాయి చూడు."
            },
            {
                "id": "07_rao",
                "char": "INSPECTOR RAO",
                "speaker": "tarun_te_narration",
                "model": "bulbul:v4-flash",
                "pace": 1.00,
                "pause_after": 0.40,
                "text": "ఆగండి... పోలీస్ ప్రాపర్టీ అది. ఏముంది ఆ మెసేజ్ లో?"
            },
            {
                "id": "08_tillu",
                "char": "TILLU",
                "speaker": "mani",
                "model": "bulbul:v3",
                "pace": 1.10,
                "pause_after": 0.45,
                "text": "ఒకటే మెసేజ్ సర్... ఇరవై ఐదేళ్లుగా ఒకటే మెసేజ్. సేమ్ బాక్స్... సేమ్ వెయిట్... డోంట్ ఓపెన్."
            },
            {
                "id": "09_laddu",
                "char": "LADDU",
                "speaker": "tarun_te_narration",
                "model": "bulbul:v4-flash",
                "pace": 0.92,
                "pause_after": 0.40,
                "text": "అంటే... మా నాన్న రైల్వే ఎంప్లాయ్ కాదా? వీళ్ల మనిషా?"
            },
            {
                "id": "10_tillu",
                "char": "TILLU",
                "speaker": "mani",
                "model": "bulbul:v3",
                "pace": 1.14,
                "pause_after": 0.50,
                "text": "రైల్వే ఎంప్లాయ్ కాదు లడ్డూ... ఇరవై ఐదేళ్లుగా ఖాళీ బాక్స్ లు మోస్తున్న డెకాయ్."
            }
        ]
    },
    "scene_25_27_bangkok_midpoint": {
        "title": "Scene 25-27: Bangkok Muay Thai Gym & Anna's Midpoint",
        "description": "The brothers discover Bunty's shrine, the duplicate passport, and face Anna.",
        "lines": [
            {
                "id": "01_laddu",
                "char": "LADDU",
                "speaker": "tarun_te_narration",
                "model": "bulbul:v4-flash",
                "pace": 0.96,
                "pause_after": 0.35,
                "text": "అన్నా... ఈ పాస్ పోర్ట్ చూడు. నా పేరే ఉంది దీని మీద కూడా!"
            },
            {
                "id": "02_tillu",
                "char": "TILLU",
                "speaker": "mani",
                "model": "bulbul:v3",
                "pace": 1.12,
                "pause_after": 0.35,
                "text": "గణేష్ కుమార్ గౌడ్? ఒరేయ్... ఆయనకి పేర్లు గుర్తుపెట్టుకునే ఓపిక కూడా లేదన్నమాట. అందరికీ ఒకటే పేరా?"
            },
            {
                "id": "03_bunty",
                "char": "BUNTY",
                "speaker": "tarun_te_narration",
                "model": "bulbul:v4-flash",
                "pace": 1.05,
                "pause_after": 0.35,
                "text": "హేయ్! హూ ఆర్ యు? మా నాన్న రైల్వే ఆఫీసర్. మీరెవరు నా రూమ్ లో?"
            },
            {
                "id": "04_tillu",
                "char": "TILLU",
                "speaker": "mani",
                "model": "bulbul:v3",
                "pace": 1.12,
                "pause_after": 0.40,
                "text": "తమ్ముడూ... రైల్వే ఆఫీసర్ కాదు. మీ నాన్న మా నాన్న ఒక్కడే. వెల్కమ్ టు ది ఫ్యామిలీ."
            },
            {
                "id": "05_anna",
                "char": "ANNA",
                "speaker": "tarun_te_narration",
                "model": "bulbul:v4-flash",
                "pace": 0.90,
                "pause_after": 0.45,
                "text": "బాగుంది. ముగ్గురు కొడుకులు ఒకేసారి వచ్చారు. రండి... డిన్నర్ చేస్తూ మాట్లాడుకుందాం."
            },
            {
                "id": "06_tillu",
                "char": "TILLU",
                "speaker": "mani",
                "model": "bulbul:v3",
                "pace": 1.10,
                "pause_after": 0.35,
                "text": "డిన్నర్ వద్దు సార్... మా నాన్న ఎక్కడ ఉన్నాడు? బాక్స్ లో ఏమీ లేదు."
            },
            {
                "id": "07_anna",
                "char": "ANNA",
                "speaker": "tarun_te_narration",
                "model": "bulbul:v4-flash",
                "pace": 0.90,
                "pause_after": 0.50,
                "text": "నాకు తెలుసు తమ్ముడూ. నేను బాడీ కొన్నాను... బాక్స్ కాదు. అయిదు రోజుల్లో లెక్క తేల్చండి."
            }
        ]
    }
}

def render_scene(scene_key, scene_data):
    scene_dir = output_base_dir / scene_key
    scene_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n=======================================================")
    print(f"🎬 PRODUCING: {scene_data['title']}")
    print(f"📖 {scene_data['description']}")
    print(f"=======================================================")
    
    lines = scene_data["lines"]
    generated_lines = []
    
    for idx, item in enumerate(lines, start=1):
        fpath = scene_dir / f"{item['id']}_{item['char'].lower()}.wav"
        print(f"[{idx}/{len(lines)}] {item['char']} ({item['speaker']}) ... ", end="", flush=True)
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
                
            res = client.text_to_speech.convert(**kwargs)
            raw_wav = base64.b64decode(res.audios[0])
            
            with open(fpath, "wb") as f:
                f.write(raw_wav)
                
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
            print(f"Error: {e}")
            
    # Stitch Master Track
    master_file = scene_dir / f"{scene_key}_master.wav"
    print(f"\nStitching Master Track: {master_file.name}...")
    
    with wave.open(str(master_file), "wb") as w_out:
        w_out.setnchannels(1)
        w_out.setsampwidth(2)
        w_out.setframerate(TARGET_RATE)
        
        for i, entry in enumerate(generated_lines):
            with wave.open(str(entry["file"]), "rb") as w_in:
                w_out.writeframes(w_in.readframes(w_in.getnframes()))
            if i < len(generated_lines) - 1:
                pause_bytes = b"\x00" * int(TARGET_RATE * entry["pause"] * 1 * 2)
                w_out.writeframes(pause_bytes)
                
    print(f" Master Scene Complete: {master_file.stat().st_size:,} bytes")
    
    # Verify with STT on a key line
    try:
        sample_line = generated_lines[-1]["file"]
        with open(sample_line, "rb") as f_stt:
            stt_res = client.speech_to_text.transcribe(
                file=f_stt,
                model="saaras:v3",
                language_code="te-IN"
            )
            print(f"STT Verification ({sample_line.name}): {stt_res.transcript}\n")
    except Exception as e:
        print(f"STT Notice: {e}")
        
    return master_file

if __name__ == "__main__":
    for skey, sdata in act2_production.items():
        render_scene(skey, sdata)
    print("\n All Act Two Table Reads Rendered Successfully!")

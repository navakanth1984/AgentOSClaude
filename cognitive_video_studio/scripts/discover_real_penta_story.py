import os
import sys
import subprocess
import wave
import json
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = "C:/Users/navka/.gemini/antigravity/worktrees/navakanth001/integrate_reverse_engineer_anything/cognitive_video_studio/analysis_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Select takes across Day 1 (211212) and Day 2 (221212)
takes_to_analyze = [
    # Day 1: 211212
    ("211212", "E:/Nav/Work/Penta/211212/MVI_0999.MOV"),
    ("211212", "E:/Nav/Work/Penta/211212/MVI_1000.MOV"),
    ("211212", "E:/Nav/Work/Penta/211212/MVI_1005.MOV"),
    ("211212", "E:/Nav/Work/Penta/211212/MVI_1010.MOV"),
    ("211212", "E:/Nav/Work/Penta/211212/MVI_1013.MOV"),
    ("211212", "E:/Nav/Work/Penta/211212/MVI_1020.MOV"),
    ("211212", "E:/Nav/Work/Penta/211212/MVI_1035.MOV"),
    # Day 2: 221212
    ("221212", "E:/Nav/Work/Penta/221212/MVI_1162.MOV"),
    ("221212", "E:/Nav/Work/Penta/221212/MVI_1164.MOV"),
    ("221212", "E:/Nav/Work/Penta/221212/MVI_1167.MOV"),
]

takes = [(day, path) for day, path in takes_to_analyze if os.path.exists(path)]
print(f"Found {len(takes)} valid takes to analyze.", flush=True)

from faster_whisper import WhisperModel
print("Loading faster-whisper base model...", flush=True)
model = WhisperModel("base", device="cpu", compute_type="int8")

results = []

for day, mov_path in takes:
    base_name = os.path.splitext(os.path.basename(mov_path))[0]
    wav_path = os.path.join(OUTPUT_DIR, f"{day}_{base_name}.wav")
    frame_path = os.path.join(OUTPUT_DIR, f"{day}_{base_name}_frame.jpg")
    
    # Extract audio using ffmpeg
    if not os.path.exists(wav_path):
        cmd = f'ffmpeg -y -i "{mov_path}" -vn -ar 16000 -ac 1 -f wav "{wav_path}"'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    # Extract representative frame at 3s
    if not os.path.exists(frame_path):
        cmd_img = f'ffmpeg -y -ss 00:00:03 -i "{mov_path}" -vframes 1 -q:v 2 "{frame_path}"'
        subprocess.run(cmd_img, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    transcription = []
    translation = []
    detected_lang = "unknown"
    
    if os.path.exists(wav_path) and os.path.getsize(wav_path) > 1000:
        try:
            with wave.open(wav_path, 'rb') as wf:
                n_frames = wf.getnframes()
                raw_bytes = wf.readframes(n_frames)
                audio_np = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            # 1. Native transcription
            segs_native, info = model.transcribe(audio_np, beam_size=3)
            detected_lang = f"{info.language} ({info.language_probability:.2f})"
            for s in segs_native:
                text = s.text.strip()
                if text:
                    transcription.append(f"[{s.start:.1f}s - {s.end:.1f}s] {text}")

            # 2. English translation
            segs_en, _ = model.transcribe(audio_np, task="translate", beam_size=3)
            for s in segs_en:
                text = s.text.strip()
                if text:
                    translation.append(f"[{s.start:.1f}s - {s.end:.1f}s] {text}")
        except Exception as e:
            print(f"Error transcribing {base_name}: {e}", flush=True)

    item = {
        "take": f"{day}/{base_name}",
        "language": detected_lang,
        "native": transcription,
        "english": translation,
        "frame": frame_path
    }
    results.append(item)
    print(f"\n--- {day}/{base_name} ---", flush=True)
    print(f"Lang: {detected_lang}", flush=True)
    print(f"Native: {transcription}", flush=True)
    print(f"English: {translation}", flush=True)

output_json = os.path.join(OUTPUT_DIR, "penta_discovered_takes.json")
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\nSaved full analysis to:", output_json, flush=True)

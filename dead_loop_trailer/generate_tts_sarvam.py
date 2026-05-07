import requests
import os

API_KEY = os.getenv("SARVAM_API_KEY")
URL = "https://api.sarvam.ai/text-to-speech"

scripts = [
    ("How can I trust you?", "arjun_01.mp3", "en-IN"),
    ("I made mistakes. I am still learning.", "veda_01.mp3", "en-IN"),
    ("How can you learn while lives are lost?", "arjun_02.mp3", "en-IN"),
    ("I want to protect you. I will protect you.", "veda_02.mp3", "en-IN"),
    ("How will you protect me... when you can’t even protect yourself?", "arjun_03.mp3", "en-IN"),
    ("I might not be able to protect myself. But I will protect—", "veda_03.mp3", "en-IN"),
    ("He is here.", "veda_04.mp3", "en-IN")
]

# We'll use different speakers if possible, but let's start with 'meera' (female) for Veda 
# and find a male speaker for Arjun.
# Speakers for bulbul:v1 (common ones): 'meera', 'pavithra', 'mahesh', 'kumar'

import json
import base64

def generate_audio(text, output_file, lang, speaker):
    payload = {
        "inputs": [text],
        "target_language_code": lang,
        "speaker": speaker,
        "model": "bulbul:v2"
    }
    headers = {
        "api-subscription-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"Generating {output_file} ({speaker}): {text}")
    response = requests.post(URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        audio_base64 = data["audios"][0]
        audio_bytes = base64.b64decode(audio_base64)
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        print(f"Saved {output_file}")
    else:
        print(f"Error {response.status_code}: {response.text}")

scripts = [
    ("How can I trust you?", "arjun_01.wav", "en-IN"),
    ("I made mistakes. I am still learning.", "veda_01.wav", "en-IN"),
    ("How can you learn while lives are lost?", "arjun_02.wav", "en-IN"),
    ("I want to protect you. I will protect you.", "veda_02.wav", "en-IN"),
    ("How will you protect me... when you can’t even protect yourself?", "arjun_03.wav", "en-IN"),
    ("I might not be able to protect myself. But I will protect—", "veda_03.wav", "en-IN"),
    ("He is here.", "veda_04.wav", "en-IN")
]

for text, output_file, lang in scripts:
    speaker = "karun" if "arjun" in output_file else "arya"
    generate_audio(text, output_file, lang, speaker)

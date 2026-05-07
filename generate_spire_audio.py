import os
import requests

# Using Sarvam AI for TTS / Ambient Generation
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

def generate_ambient_audio(filename, text):
    print(f"Generating ambient audio: {filename}...")
    url = "https://api.sarvam.ai/text-to-speech"
    
    payload = {
        "text": text,
        "voice": "af_nova", # Atmospheric voice
        "language_code": "en-IN",
        "target_universe": "premium"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SARVAM_API_KEY}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            audio_content = response.json().get("audio_content")
            if audio_content:
                import base64
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(audio_content))
                print(f"Successfully saved {filename}")
            else:
                print("No audio content in response.")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error generating audio: {e}")

if __name__ == "__main__":
    # We use a descriptive atmospheric text to guide the TTS engine's prosody 
    # and then we can layer this or use it as a base ambient track.
    ambient_description = "The ancient bronze spire creaks under the weight of centuries. A low frequency hum vibrates through the weathered metal."
    os.makedirs("rust_minar_scene", exist_ok=True)
    generate_ambient_audio("rust_minar_scene/flow_ambient_soundscape.wav", ambient_description)

import os
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# 1. Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")

client = ElevenLabs(api_key=api_key)

output_dir = Path(__file__).resolve().parent / "voice_samples" / "elevenlabs_table_read"
output_dir.mkdir(parents=True, exist_ok=True)

# 2. Native Telugu Voice Mapping matched with Character Profiles
VOICE_MAP = {
    "TILLU": {
        "name": "Srinu - Energetic, Confident Telugu",
        "voice_id": "ge94MQm6fYaUCnxz1us6",
        "settings": VoiceSettings(stability=0.45, similarity_boost=0.85)
    },
    "LADDU": {
        "name": "Sagar - Telugu Natural & Realistic Male Voice",
        "voice_id": "2DRBj9T2XZ7Jmkcm6WCZ",
        "settings": VoiceSettings(stability=0.60, similarity_boost=0.80)
    },
    "ANNA": {
        "name": "Bharadwaj - Profound Telugu Mythology",
        "voice_id": "RoLT1qx7XJRXxWSIG5hS",
        "settings": VoiceSettings(stability=0.70, similarity_boost=0.90)
    },
    "SAVITRI": {
        "name": "Reddamma - Native Telugu",
        "voice_id": "vuiTjpjaJPYrzgnikx1u",
        "settings": VoiceSettings(stability=0.55, similarity_boost=0.85)
    },
    "LAKSHMI": {
        "name": "Vandana - Telugu Relatable Conversation",
        "voice_id": "eh5YJlyB5bmWfcmcEsLN",
        "settings": VoiceSettings(stability=0.65, similarity_boost=0.80)
    }
}

# 3. Scene Script (Cards 25-27: Bangkok Midpoint)
scene_lines = [
    {
        "id": "01_laddu",
        "char": "LADDU",
        "text": "అన్నా... ఈ పాస్ పోర్ట్ చూడు. నా పేరే ఉంది దీని మీద కూడా!"
    },
    {
        "id": "02_tillu",
        "char": "TILLU",
        "text": "గణేష్ కుమార్ గౌడ్? ఒరేయ్... ఆయనకి పేర్లు గుర్తుపెట్టుకునే ఓపిక కూడా లేదన్నమాట! అందరికీ ఒకటే పేరా?"
    },
    {
        "id": "03_tillu",
        "char": "TILLU",
        "text": "తమ్ముడూ... రైల్వే ఆఫీసర్ కాదు. మీ నాన్న మా నాన్న ఒక్కడే. వెల్కమ్ టు ది ఫ్యామిలీ."
    },
    {
        "id": "04_anna",
        "char": "ANNA",
        "text": "బాగుంది. ముగ్గురు కొడుకులు ఒకేసారి వచ్చారు. రండి... డిన్నర్ చేస్తూ మాట్లాడుకుందాం."
    },
    {
        "id": "05_tillu",
        "char": "TILLU",
        "text": "డిన్నర్ వద్దు సార్... మా నాన్న ఎక్కడ ఉన్నాడు? బాక్స్ లో ఏమీ లేదు."
    },
    {
        "id": "06_anna",
        "char": "ANNA",
        "text": "నాకు తెలుసు తమ్ముడూ. నేను బాడీ కొన్నాను... బాక్స్ కాదు. అయిదు రోజుల్లో లెక్క తేల్చండి."
    }
]

def generate_table_read():
    print(f"🎬 Synthesizing {len(scene_lines)} lines with ElevenLabs Native Telugu Cast...")
    audio_files = []
    
    for idx, item in enumerate(scene_lines, start=1):
        v_info = VOICE_MAP[item["char"]]
        fpath = output_dir / f"{item['id']}_{item['char'].lower()}.mp3"
        print(f"[{idx}/{len(scene_lines)}] {item['char']} via {v_info['name']} ... ", end="", flush=True)
        
        audio_stream = client.text_to_speech.convert(
            text=item["text"],
            voice_id=v_info["voice_id"],
            model_id="eleven_multilingual_v2",
            voice_settings=v_info["settings"]
        )
        
        with open(fpath, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)
                
        print(f"OK ({fpath.stat().st_size:,} bytes)")
        audio_files.append(fpath)
        
    print(f"\nAll lines generated in: {output_dir}")
    return audio_files

if __name__ == "__main__":
    generate_table_read()

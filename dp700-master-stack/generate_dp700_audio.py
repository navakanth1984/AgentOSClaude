import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from sarvamai import SarvamAI

def generate_audio():
    # Load .env
    env_path = Path("c:/Users/navka/navakanth001/.env")
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        print("[ERROR] SARVAM_API_KEY not found in .env")
        return

    client = SarvamAI(api_subscription_key=api_key)
    
    speech_text = """
Namaskaram andarki! Em sangathi? 

Ivala manam oka manchi vishayam gurinchi matladukundam. Ade Microsoft DP-700 exam! Idi 'Implementing Data Engineering Solutions Using Microsoft Fabric' gurinchi. 

Data Engineering ante emi anukuntunnaru? Mana data ni manchiga teesukuravadam, danni clean cheyadam, inka OneLake lo bhadranga pettadam. Ee exam lo moodu main parts untayi:
1. Analytics Solution ni setup cheyadam.
2. Data ni ingest inka transform cheyadam.
3. Mana solution ni monitor inka optimize cheyadam.

Kastapadi chadavandi anna! Microsoft Learn lo anni resources unnayi. SQL, PySpark, inka KQL paina baga focus cheyyali. Manchiga prepare ayite, certification mee chethilo untadi. 

Sarey mari, manchiga chadavandi, pasai tharvatha kaluddam! Jai Telangana!
""".strip()

    print(f"[INFO] Generating audio for: {speech_text[:50]}...")
    
    try:
        response = client.text_to_speech.convert(
            text=speech_text,
            target_language_code="te-IN",
            speaker="rohan",
            model="bulbul:v3",
            output_audio_codec="wav"
        )
        
        # The response.audios is a list of base64 strings
        if response.audios:
            audio_base64 = response.audios[0]
            audio_data = base64.b64decode(audio_base64)
            
            output_path = "dp700_speech.wav"
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            print(f"[SUCCESS] Audio saved to {output_path}")
        else:
            print("[ERROR] No audio data received.")
            
    except Exception as e:
        print(f"[ERROR] An error occurred: {str(e)}")

if __name__ == "__main__":
    generate_audio()

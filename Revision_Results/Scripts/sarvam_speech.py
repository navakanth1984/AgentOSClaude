from sarvamai import SarvamAI
import base64
import os

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

def test_tts():
    print("\n--- Testing Text-to-Speech (Hindi) ---")
    text = "नमस्ते, सर्वम एआई में आपका स्वागत है।"
    print(f"Input Text: {text}")
    
    response = client.text_to_speech.convert(
        text=text,
        target_language_code="hi-IN",
        speaker="aditya",
        model="bulbul:v3"
    )
    
    if hasattr(response, 'audios') and response.audios:
        audio_base64 = response.audios[0]
        audio_data = base64.b64decode(audio_base64)
        
        with open("output_audio.wav", "wb") as f:
            f.write(audio_data)
        print("Audio saved to output_audio.wav")
        return "output_audio.wav"
    else:
        print(f"Unexpected response format: {response}")
        return None

def test_stt(audio_path):
    if not audio_path or not os.path.exists(audio_path):
        print("No audio file to test STT.")
        return

    print("\n--- Testing Speech-to-Text ---")
    with open(audio_path, "rb") as f:
        response = client.speech_to_text.transcribe(
            file=f,
            model="saarika:v2.5"
        )
    
    print(f"Transcribed Text: {response.transcript}")

if __name__ == "__main__":
    try:
        audio_file = test_tts()
        if audio_file:
            test_stt(audio_file)
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

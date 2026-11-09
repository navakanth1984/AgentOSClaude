import os
from pathlib import Path
from gradio_client import Client, handle_file

print("Connecting to FunAudioLLM/Fun-CosyVoice3-0.5B on Hugging Face...")
client = Client("FunAudioLLM/Fun-CosyVoice3-0.5B")

# Use a test audio reference
prompt_audio_path = Path("voice_samples/tillu_sarcastic_witty_scene/01_tillu_intro.wav")

if not prompt_audio_path.exists():
    print("Prompt audio not found.")
    exit(1)

print(f"Using reference prompt: {prompt_audio_path.name}")

tts_text = "స్టాండ్ కి టవల్ ఎందుకు? స్టాండ్ కి డిగ్నిటీ కావాలి."
prompt_text = "Sir... First of all? Congratulations! Second of all... you have come to the right man."

print("Calling /generate_audio...")
result = client.predict(
    tts_text=tts_text,
    mode_value="zero_shot",
    prompt_text=prompt_text,
    prompt_wav_upload=handle_file(str(prompt_audio_path.resolve())),
    prompt_wav_record=handle_file(str(prompt_audio_path.resolve())),
    instruct_text="You are a helpful assistant. Please say a sentence as loudly as possible.<|endofprompt|>",
    seed=42.0,
    stream=False,
    ui_lang="En",
    api_name="/generate_audio"
)

print(f"CosyVoice Success! Generated audio at: {result}")

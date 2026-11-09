from gradio_client import Client
import sys

print("gradio_client successfully imported.")

# Let's inspect available CosyVoice 2 spaces on HF
spaces_to_check = [
    "FunAudioLLM/CosyVoice2-0.5B",
    "FunAudioLLM/CosyVoice-300M",
    "funaudiollm/CosyVoice2-0.5B"
]

for space in spaces_to_check:
    print(f"Checking space: {space} ... ", end="", flush=True)
    try:
        c = Client(space)
        print("ONLINE!")
        print("API Endpoints:")
        c.view_api()
        break
    except Exception as e:
        print(f"Unavailable ({e})")

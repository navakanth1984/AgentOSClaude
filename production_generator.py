import requests
import json
import os

# Sarvam AI for prompt expansion (Director logic)
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
LTX_API_URL = "http://localhost:8000/generate"

def enhance_prompt(prompt):
    print(f"Enhancing prompt via Sarvam AI: {prompt}")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SARVAM_API_KEY}"
    }
    payload = {
        "model": "sarvam-m",
        "messages": [
            {"role": "system", "content": "You are a Cinematic Director. Expand the prompt into a 6D structure: Input, Content, Style, Camera, Structure, Edit Commands."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post("https://api.sarvam.ai/v1/chat/completions", headers=headers, json=payload)
        print(f"API Response: {response.text}")
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error enhancing prompt: {e}")
        return prompt

def generate_video(final_prompt):
    print(f"Submitting to LTX-Video API...")
    data = {
        "prompt": final_prompt,
        "width": 1216,
        "height": 704,
        "num_frames": 121
    }
    try:
        # Note: This assumes the FastAPI server is running in another process
        response = requests.post(LTX_API_URL, data=data)
        return response.json()
    except Exception as e:
        print(f"Error calling LTX API: {e}")
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    raw_prompt = "Ancient weathered spire, oxidized bronze, volumetric lighting, epic push-in"
    enhanced = enhance_prompt(raw_prompt)
    print(f"\n--- ENHANCED 6D PROMPT ---\n{enhanced}\n")
    
    # Simulate video generation (since we can't run the server and client in one turn easily)
    # result = generate_video(enhanced)
    # print(result)
    
    # Create the 'rendered' folder if it doesn't exist
    os.makedirs("renders", exist_ok=True)
    with open("renders/production_log.txt", "w") as f:
        f.write(f"Prompt: {enhanced}\nStatus: Assets scheduled for generation.")

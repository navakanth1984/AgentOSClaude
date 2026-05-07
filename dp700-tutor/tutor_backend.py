import os
import json
import base64
import requests
import re
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from sarvamai import SarvamAI

# Load env from parent dir
load_dotenv(dotenv_path=Path("../.env"))

app = FastAPI()

# Configuration
NIM_API_KEY = os.getenv("NVIDIA_API_KEY")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

# Initialize Clients
nim_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NIM_API_KEY
)
sarvam_client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

# Load Curriculum
with open("curriculum.json", "r") as f:
    CURRICULUM = json.load(f)

class ChatRequest(BaseModel):
    message: str
    lang: str = "en"

class SpeakRequest(BaseModel):
    text: str
    lang: str = "en"

@app.post("/chat")
async def chat_stream(request: ChatRequest):
    # Prompt for Dual-Speaker Discussion
    system_prompt = (
        "You are the 'Fabric Guru' and your assistant 'Aura'. "
        "You must explain Microsoft Fabric (DP-700) concepts as a cinematic discussion between two speakers. "
        "Format your response strictly as follows:\n"
        "[GURU]: (The Master's technical/visionary explanation)\n"
        "[AURA]: (The Assistant's practical/follow-up question or summary)\n"
        "Use the DP-700 curriculum provided: " + json.dumps(CURRICULUM) + "\n"
        "Keep it high-energy, technical, and intuitive. Use analogies related to the 'N^th Dimension'."
    )
    
    def event_generator():
        try:
            stream = nim_client.chat.completions.create(
                model="meta/llama-3.1-8b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": request.message}
                ],
                temperature=0.8,
                max_tokens=1500,
                stream=True
            )
            for chunk in stream:
                if hasattr(chunk, 'choices') and chunk.choices:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield f"data: {json.dumps({'content': content})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/speak")
async def speak(request: SpeakRequest):
    # Split text by speaker tags
    # Pattern: [GURU]: ... [AURA]: ...
    parts = re.split(r'(\[GURU\]:|\[AURA\]:)', request.text)
    
    audio_segments = []
    current_speaker = "rohan" # Default
    
    lang_map = {"en": "en-IN", "te": "te-IN", "hi": "hi-IN", "ta": "ta-IN"}
    target_lang = lang_map.get(request.lang, "en-IN")

    try:
        for i in range(1, len(parts), 2):
            tag = parts[i]
            text = parts[i+1].strip()
            if not text: continue
            
            speaker = "rohan" if "[GURU]" in tag else "aditi"
            
            tts_res = sarvam_client.text_to_speech.convert(
                text=text,
                model="bulbul:v3",
                speaker=speaker,
                target_language_code=target_lang
            )
            audio_segments.append({"speaker": speaker, "audio": tts_res.audios[0]})
        
        # If no tags found, just speak the whole thing as Guru
        if not audio_segments:
            tts_res = sarvam_client.text_to_speech.convert(
                text=request.text,
                model="bulbul:v3",
                speaker="rohan",
                target_language_code=target_lang
            )
            audio_segments.append({"speaker": "rohan", "audio": tts_res.audios[0]})

        return {"segments": audio_segments}
    except Exception as e:
        return {"error": str(e)}

@app.post("/generate_visual")
async def generate_visual(request: dict):
    # NVIDIA SD3 visual generation logic
    invoke_url = "https://ai.api.nvidia.com/v1/genai/stabilityai/sd3-medium"
    headers = {"Authorization": f"Bearer {NIM_API_KEY}", "Accept": "application/json"}
    payload = {"prompt": request.get("prompt"), "cfg_scale": 7, "aspect_ratio": "16:9", "steps": 30}
    response = requests.post(invoke_url, headers=headers, json=payload)
    data = response.json()
    return {"image": data.get("image"), "error": data.get("detail") if not data.get("image") else None}

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)

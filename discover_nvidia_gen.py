import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

def check_gen_models():
    load_dotenv(Path(".env"))
    api_key = os.getenv("NVIDIA_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Try different endpoints
    endpoints = [
        "https://integrate.api.nvidia.com/v1/models",
        "https://ai.api.nvidia.com/v1/genai/models"
    ]
    
    all_models = []
    for url in endpoints:
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                ids = [m['id'] for m in data.get('data', [])]
                all_models.extend(ids)
        except:
            pass
            
    gen_models = [m for m in all_models if any(x in m.lower() for x in ['sdxl', 'diffusion', 'video', 'svd', 'image', 'flux'])]
    print(json.dumps(list(set(gen_models)), indent=2))

if __name__ == "__main__":
    check_gen_models()

import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

def get_models():
    load_dotenv(Path(".env"))
    api_key = os.getenv("NVIDIA_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get("https://integrate.api.nvidia.com/v1/models", headers=headers)
    models = [m['id'] for m in response.json()['data']]
    with open("nim_models.json", "w") as f:
        json.dump(models, f, indent=2)
    print(f"Found {len(models)} models.")

if __name__ == "__main__":
    get_models()

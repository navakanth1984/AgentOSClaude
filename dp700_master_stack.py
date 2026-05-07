import asyncio
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import requests

# NVIDIA NIM Endpoints
NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"

async def call_nim(session, model, prompt, role="user"):
    url = f"{NIM_BASE_URL}/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": role, "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 1024
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('NVIDIA_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    try:
        response = await asyncio.to_thread(requests.post, url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

async def run_master_stack():
    load_dotenv(dotenv_path=Path("c:/Users/navka/navakanth001/.env"))
    
    # 1. Strategy (Llama 3.3 70B)
    # 2. Execution (Qwen 2.5 Coder 32B)
    # 3. Analysis (VILA)
    
    tasks = [
        call_nim(None, "meta/llama-3.3-70b-instruct", "Provide a 5-step strategic roadmap for passing DP-700."),
        call_nim(None, "qwen/qwen2.5-coder-32b-instruct", "Write a PySpark script for Microsoft Fabric to ingest a CSV from OneLake."),
        call_nim(None, "nvidia/vila", "Analyze the architecture of a typical Microsoft Fabric environment.")
    ]
    
    print("Running Parallel NIM Inference...")
    results = await asyncio.gather(*tasks)
    
    print("\n--- STRATEGY (Llama 3.3) ---")
    print(results[0].get('choices', [{}])[0].get('message', {}).get('content', 'Error'))
    
    print("\n--- EXECUTION (Qwen 2.5) ---")
    print(results[1].get('choices', [{}])[0].get('message', {}).get('content', 'Error'))
    
    print("\n--- ANALYSIS (VILA) ---")
    print(results[2].get('choices', [{}])[0].get('message', {}).get('content', 'Error'))

if __name__ == "__main__":
    asyncio.run(run_master_stack())
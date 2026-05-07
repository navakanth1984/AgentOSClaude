import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict

def explore_nvidia_capabilities():
    env_path = Path("c:/Users/navka/navakanth001/.env")
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("[ERROR] NVIDIA_API_KEY not found.")
        return

    print("[INFO] Fetching NVIDIA NIM Catalog...")
    url = "https://integrate.api.nvidia.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"[ERROR] HTTP Error: {response.status_code}")
            return
            
        models = response.json().get("data", [])
        categories = defaultdict(list)
        
        for m in models:
            mid = m['id']
            if '/' in mid:
                vendor = mid.split('/')[0]
                categories[vendor].append(mid)
            else:
                categories['other'].append(mid)
        
        print(f"\n[SUMMARY] Total Models Available: {len(models)}")
        
        print("\n--- CAPABILITY BREAKDOWN ---")
        
        # 1. Image & Video
        vis_vendors = ['stabilityai', 'nvidia', 'black-forest-labs']
        print("\nIMAGE & VIDEO GENERATION")
        for v in vis_vendors:
            relevant = [m for m in categories[v] if any(x in m.lower() for x in ['stable', 'sdxl', 'svd', 'video', 'diffusion', 'flux'])]
            for m in relevant:
                print(f"  - {m}")

        # 2. Reasoning & Text (LLMs)
        text_vendors = ['meta', 'mistralai', 'deepseek', 'google', 'microsoft', 'nvidia']
        print("\nREASONING & TEXT (LLMs)")
        for v in text_vendors:
            relevant = [m for m in categories[v] if any(x in m.lower() for x in ['llama', 'mistral', 'deepseek', 'gemma', 'phi', 'nemotron'])]
            for m in relevant[:3]:
                print(f"  - {m}")
        
        # 3. Code Generation
        print("\nCODE GENERATION")
        code_keywords = ['coder', 'starcoder', 'codellama']
        for v, ms in categories.items():
            for m in ms:
                if any(k in m.lower() for k in m.lower().split('/')):
                    if any(kw in m.lower() for kw in code_keywords):
                        print(f"  - {m}")

        # 4. Multimodal (Vision-Language)
        print("\nMULTIMODAL (Vision-Language)")
        vlm_keywords = ['vila', 'nvlm', 'molmo', 'pixtral']
        for v, ms in categories.items():
            for m in ms:
                if any(k in m.lower() for k in vlm_keywords):
                    print(f"  - {m}")

    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    explore_nvidia_capabilities()

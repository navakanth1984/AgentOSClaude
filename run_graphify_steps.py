import sys, json, os
from pathlib import Path
from graphify.extract import collect_files, extract
from graphify.detect import detect
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json, to_html

def run():
    root = Path('c:/Users/navka/navakanth001')
    target = root / 'dp700-master-stack'
    out_dir = root / 'graphify-out'
    out_dir.mkdir(exist_ok=True)

    # 1. Detect
    print("Step 1: Detecting files...")
    det = detect(target)
    (out_dir / '.graphify_detect.json').write_text(json.dumps(det))

    # 2. AST Extraction
    print("Step 2: AST Extraction...")
    code_files = []
    for f in det.get('files', {}).get('code', []):
        p = root / f
        code_files.extend(collect_files(p) if p.is_dir() else [p])
    
    ast_result = extract(code_files, cache_root=root)
    (out_dir / '.graphify_ast.json').write_text(json.dumps(ast_result, indent=2))
    print(f"   - AST: {len(ast_result['nodes'])} nodes, {len(ast_result['edges'])} edges")

    # 3. Create a combined Master Stack script (Parallel Processing demonstration)
    print("Step 3: Creating Master Stack Implementation...")
    # This is where I'll write the actual master stack code
    create_master_stack_code(root)

def create_master_stack_code(root):
    code = """
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
    
    print("\\n--- STRATEGY (Llama 3.3) ---")
    print(results[0].get('choices', [{}])[0].get('message', {}).get('content', 'Error'))
    
    print("\\n--- EXECUTION (Qwen 2.5) ---")
    print(results[1].get('choices', [{}])[0].get('message', {}).get('content', 'Error'))
    
    print("\\n--- ANALYSIS (VILA) ---")
    print(results[2].get('choices', [{}])[0].get('message', {}).get('content', 'Error'))

if __name__ == "__main__":
    asyncio.run(run_master_stack())
"""
    (root / 'dp700_master_stack.py').write_text(code.strip())
    print(f"   - Created c:/Users/navka/navakanth001/dp700_master_stack.py")

if __name__ == "__main__":
    run()

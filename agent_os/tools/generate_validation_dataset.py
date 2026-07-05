import argparse
import json
import time
import urllib.request
import urllib.error
import os
from pathlib import Path

ENDPOINT = "http://localhost:8765/execute"
STATUS_ENDPOINT = "http://localhost:8765/execute/status"

# We map the requested categories to profiles available in `capabilities.py`.
# We'll use "Coding" for Coding, "Best Overall" for Architecture/Writing, "Research" for Research.
# We also want to hit Budget. So we'll rotate through profiles.
PROMPTS = [
    {
        "category": "Coding",
        "prompt": "Write a Python function to compute the 95th percentile of a list of numbers.",
        "profile": "Coding" # Represents Balanced
    },
    {
        "category": "Architecture",
        "prompt": "What are the tradeoffs of using a message queue versus an event bus in a microservices architecture?",
        "profile": "Best Overall" # Represents Premium
    },
    {
        "category": "Research",
        "prompt": "Summarize the key differences between Transformer and Mamba architectures.",
        "profile": "Research" # Contains Perplexity
    },
    {
        "category": "Writing",
        "prompt": "Write a short 2-paragraph introduction for a blog post about software craftsmanship.",
        "profile": "Budget" # Ensure we hit the Budget tier
    }
]

def run_job(prompt, mode, profile, aggregation):
    payload = {
        "prompt": prompt,
        "mode": mode,
        "profile": profile,
        "aggregation": aggregation
    }
    
    headers = {'Content-Type': 'application/json'}
    api_key = os.environ.get("AGENT_OS_API_KEY")
    if not api_key:
        # fallback for local testing without dotenv
        try:
            with open(Path(__file__).parent.parent / ".env") as f:
                for line in f:
                    if line.startswith("AGENT_OS_API_KEY="):
                        api_key = line.split("=")[1].strip()
                        break
        except Exception:
            pass
    if api_key:
        headers["X-API-Key"] = api_key

    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Error starting job: {e}")
        return False
        
    job_id = resp_data.get("job_id")
    if not job_id:
        print(f"No job_id returned: {resp_data}")
        return False
        
    print(f"Started job {job_id} for mode={mode} aggregation={aggregation} profile={profile}")
    
    # Poll for completion
    status_req = urllib.request.Request(STATUS_ENDPOINT, data=json.dumps({"job_id": job_id}).encode("utf-8"), headers=headers)
    
    while True:
        time.sleep(2)
        try:
            with urllib.request.urlopen(status_req) as response:
                status_data = json.loads(response.read().decode())
                
                status = status_data.get("status")
                if status == "completed":
                    print(f"Job {job_id} completed successfully.")
                    return True
                elif status == "failed":
                    print(f"Job {job_id} failed: {status_data.get('error')}")
                    return False
                
                print(f"  Job {job_id} status: {status}, stage: {status_data.get('stage')} - {status_data.get('per_model_status', {})}")
                
        except urllib.error.URLError as e:
            print(f"Error polling job {job_id}: {e}")
            return False

def run_stage_a():
    print("Starting Stage A: Smoke Validation...")
    runs = 0
    success = 0
    
    for p in PROMPTS:
        # 1. Single execution
        print(f"\n--- Running Single Execution for {p['category']} ---")
        if run_job(p["prompt"], "single", p["profile"], "fast"):
            success += 1
        runs += 1
        
        # 2. Mixture Fast execution
        print(f"\n--- Running Mixture Fast Execution for {p['category']} ---")
        if run_job(p["prompt"], "mixture", p["profile"], "fast"):
            success += 1
        runs += 1
        
        # 3. Mixture Standard execution
        print(f"\n--- Running Mixture Standard Execution for {p['category']} ---")
        if run_job(p["prompt"], "mixture", p["profile"], "standard"):
            success += 1
        runs += 1
        
    print(f"\nStage A completed: {success}/{runs} runs successful.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["a", "b"], required=True)
    args = parser.parse_args()
    
    if args.stage == "a":
        run_stage_a()
    elif args.stage == "b":
        print("Stage B is not yet implemented.")

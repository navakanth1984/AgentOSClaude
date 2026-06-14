"""Live integration test for Cloud Agent endpoint.
Triggers a cloud agent task via HTTP, waits for it, and verifies results.
"""
import os
import sys
import time
import urllib.request
import urllib.error
import json
from pathlib import Path

# Load env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ.get("AGENT_OS_API_KEY", "")
BASE = "http://localhost:8765"
ASSET_LIBRARY = Path(__file__).parent / "asset_library"
LOG_FILE = Path(__file__).parent / "agent_os.log"

def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"}
    )
    if API_KEY:
        req.add_header("X-API-Key", API_KEY)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def main():
    print("=== Testing Cloud Agent Endpoint ===")
    
    # Define a unique test asset name
    test_file_name = f"integration_test_{int(time.time())}.txt"
    test_file_path = ASSET_LIBRARY / test_file_name
    
    # Clean up if it somehow exists
    if test_file_path.exists():
        test_file_path.unlink()
        
    task_desc = (
        f"Create a file named '{test_file_name}' with the content 'Hello from Cloud Agent stress test!' "
        "and print 'Task completed successfully'"
    )
    
    print(f"Triggering task: {task_desc}")
    t0 = time.time()
    try:
        res = post("/cloud", {
            "task": task_desc,
            "model": "google/gemini-2.5-flash"
        })
        print(f"Response: {res}")
        if not res.get("started"):
            print("FAIL: started field is not True")
            sys.exit(1)
    except Exception as e:
        print(f"FAIL: Request failed: {e}")
        sys.exit(1)
        
    # Wait and poll for file creation in asset library (max 60 seconds)
    print("Polling asset library for generated file...")
    success = False
    for attempt in range(1, 31):
        time.sleep(2)
        if test_file_path.exists():
            print(f"PASS: File '{test_file_name}' was successfully created after {attempt * 2}s!")
            content = test_file_path.read_text(encoding="utf-8").strip()
            print(f"Content: '{content}'")
            if "Hello from Cloud Agent" in content:
                print("PASS: Content is correct.")
                success = True
            else:
                print(f"FAIL: Content mismatch. Got: {content}")
            break
        print(f"  Attempt {attempt}/30: file not yet present...")
        
    # Clean up test asset
    if test_file_path.exists():
        try:
            test_file_path.unlink()
            print("Cleaned up test file.")
        except Exception as e:
            print(f"Warning: Could not delete test file: {e}")
            
    if success:
        print("\n=== CLOUD AGENT INTEGRATION TEST PASSED ===")
        sys.exit(0)
    else:
        print("\n=== CLOUD AGENT INTEGRATION TEST FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    main()

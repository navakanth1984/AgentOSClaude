import httpx
import time
import sys

BASE_URL = "http://localhost:8000"

def check_backend():
    print(f"Checking backend at {BASE_URL}...")
    try:
        response = httpx.get(f"{BASE_URL}/configs")
        if response.status_code == 200:
            print("✓ Backend is UP")
            print(f"✓ Available configs: {len(response.json().get('configs', []))}")
            return True
    except Exception as e:
        print(f"✗ Backend is DOWN: {e}")
    return False

def test_generation():
    print("\nStarting generation test...")
    payload = {
        "prompt": "Test video: a cute robot waving",
        "seed": 42
    }
    
    try:
        # 1. Trigger generation
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{BASE_URL}/generate", data=payload)
            resp.raise_for_status()
            job_id = resp.json()["job_id"]
            print(f"✓ Job created: {job_id}")

            # 2. Poll for status
            status = "pending"
            for _ in range(30):
                time.sleep(2)
                status_resp = client.get(f"{BASE_URL}/status/{job_id}")
                data = status_resp.json()
                status = data["status"]
                print(f"  Current status: {status}")
                
                if status == "completed":
                    print(f"✓ Output URL: {data.get('output_url')}")
                    return True
                if status == "failed":
                    print(f"✗ Error: {data.get('error')}")
                    return False
        
        print(f"✓ Final status: {status}")
        return False
    except Exception as e:
        print(f"✗ Generation test failed: {e}")
    return False

if __name__ == "__main__":
    if check_backend():
        test_generation()
    else:
        print("\nPlease start the backend server before running the smoke test.")
        print("Command: cd ltx_video_api; py main.py")

"""Test a single OpenRouter call — check rate limit reset."""
import sys, time, urllib.request, json, os
sys.path.insert(0, ".")

_env_path = "C:/Users/navka/navakanth001/.env"
with open(_env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

api_key = os.environ.get("OPENROUTER_API_KEY", "")
print(f"Key present: {bool(api_key)}  (first 8 chars: {api_key[:8]})")

# Check available free models via OpenRouter models API
print("\nFetching available free models from OpenRouter...")
try:
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    free_models = [
        m["id"] for m in data.get("data", [])
        if m.get("pricing", {}).get("prompt") == "0"
    ]
    print(f"Free models available: {len(free_models)}")
    for m in free_models[:15]:
        print(f"  {m}")
except Exception as e:
    print(f"Models API error: {e}")

# Try a single call with a delay (account may have been rate-limited)
print("\nWaiting 10s for rate limit window to reset...")
time.sleep(10)
print("Making single test call...")
try:
    from openrouter_client import call_openrouter
    result = call_openrouter(
        "meta-llama/llama-3.3-70b-instruct:free",
        "You are a helpful assistant.",
        "In one sentence, what is Obsidian (the note-taking app)?",
    )
    print(f"SUCCESS: {result[:200]}")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")

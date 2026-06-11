"""Find which free models actually work on this account."""
import sys, json, time, urllib.request, os
sys.path.insert(0, ".")

_env_path = "C:/Users/navka/navakanth001/.env"
with open(_env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

api_key = os.environ.get("OPENROUTER_API_KEY", "")

FREE_MODELS_TO_TRY = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "moonshotai/kimi-k2.6:free",
    "poolside/laguna-xs.2:free",
    "openrouter/free",
]

print("Testing free models (1 call each, 3s apart):")

working = []
for model in FREE_MODELS_TO_TRY:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Say only: WORKS"}],
        "max_tokens": 10,
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read())
            reply = d["choices"][0]["message"]["content"].strip()[:40]
            print(f"  WORKS  {model}  reply={reply}")
            working.append(model)
    except Exception as e:
        print(f"  FAIL   {model}  {type(e).__name__}: {e}")
    time.sleep(3)

print(f"\nWorking models: {working}")

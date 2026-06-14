"""Layer 4: Live API calls — swarm, workflow (no browser), goal mode, logs, tune."""
import json
import sys
import time
import os
import urllib.request
import urllib.error
from pathlib import Path

# Load env variables from .env if present
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
PASS = 0
FAIL = 0

def get(path, timeout=30):
    req = urllib.request.Request(f"{BASE}{path}")
    if API_KEY:
        req.add_header("X-API-Key", API_KEY)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def post(path, body, timeout=120):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"}
    )
    if API_KEY:
        req.add_header("X-API-Key", API_KEY)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        print(f"  PASS  {name}")
        PASS += 1
    else:
        print(f"  FAIL  {name}  {detail}")
        FAIL += 1

def err(name, e):
    global FAIL
    print(f"  FAIL  {name}: {type(e).__name__}: {e}")
    FAIL += 1

print("=== Layer 4: Live API calls ===")

# --- POST /swarm (real 5-agent run)
print("\n[Test] POST /swarm  (launches 5 parallel agents — may take 30-60s)")
try:
    t0 = time.time()
    r = post("/swarm", {
        "topic": "Obsidian knowledge management workflow",
        "model": "google/gemini-2.5-flash",
    }, timeout=120)
    elapsed = round(time.time() - t0, 1)
    print(f"  Time: {elapsed}s")
    check("/swarm returns topic",          r.get("topic") == "Obsidian knowledge management workflow", r.get("topic"))
    check("/swarm agents=5",               r.get("agents") == 5, r.get("agents"))
    check("/swarm successful >= 1",        r.get("successful", 0) >= 1, r.get("successful"))
    check("/swarm note_path exists",       bool(r.get("note_path")), r.get("note_path"))
    check("/swarm notebooks_found is int", isinstance(r.get("notebooks_found"), int), r.get("notebooks_found"))
    check("/swarm results list",           isinstance(r.get("results"), list), type(r.get("results")))
    print(f"  agents ok={r.get('successful')}/5   notebooks={r.get('notebooks_found')}   note={r.get('note_path','')[-50:]}")
except Exception as e:
    err("/swarm live", e)

# --- POST /workflow (no browser, no build)
print("\n[Test] POST /workflow  (analyze + notebook search + save — no browser)")
try:
    t0 = time.time()
    r = post("/workflow", {
        "prompt": "summarize what context engineering is",
        "browser": False,
        "build": False,
    }, timeout=60)
    elapsed = round(time.time() - t0, 1)
    print(f"  Time: {elapsed}s")
    check("/workflow returns prompt",       "prompt" in r, r.keys())
    check("/workflow has stages",           isinstance(r.get("stages"), dict) and len(r["stages"]) > 0, type(r.get("stages")))
    check("/workflow has intent",           isinstance(r.get("intent"), dict), r.get("intent"))
    check("/workflow note_path set",        bool(r.get("note_path")), r.get("note_path"))
    check("/workflow suggestions list",     isinstance(r.get("suggestions"), list), r.get("suggestions"))
    print(f"  topic={r.get('intent',{}).get('topic','?')}   note={r.get('note_path','')[-50:]}")
except Exception as e:
    err("/workflow live", e)

# --- POST /goal (autonomous goal runner — quick plan-only run)
print("\n[Test] POST /goal  (autonomous goal: plan + execute + save — may take 60-120s)")
try:
    t0 = time.time()
    r = post("/goal", {
        "goal": "Research what PARA method is and save a summary note",
        "max_steps": 3,
        "model": "google/gemini-2.5-flash",
    }, timeout=180)
    elapsed = round(time.time() - t0, 1)
    print(f"  Time: {elapsed}s")
    check("/goal returns goal field",       "goal" in r, r.keys())
    check("/goal has status",               r.get("status") in ("achieved", "partial"), r.get("status"))
    check("/goal steps > 0",               r.get("steps", 0) > 0, r.get("steps"))
    check("/goal log_path set",             bool(r.get("log_path")), r.get("log_path"))
    check("/goal has verdict",              bool(r.get("verdict")), r.get("verdict"))
    print(f"  status={r.get('status')}  confidence={r.get('confidence')}%  steps={r.get('steps')}")
    print(f"  log={r.get('log_path','')[-60:]}")
except Exception as e:
    err("/goal live", e)

# --- GET /logs (CDLC Observe)
print("\n[Test] GET /logs  (workflow history — CDLC Observe phase)")
try:
    r = get("/logs?n=5")
    check("/logs has 'logs' key",           "logs" in r, r.keys())
    check("/logs total is int",             isinstance(r.get("total"), int), r.get("total"))
    check("/logs showing is int",           isinstance(r.get("showing"), int), r.get("showing"))
    check("/logs output_types is dict",     isinstance(r.get("output_types"), dict), r.get("output_types"))
    print(f"  total={r.get('total')}  showing={r.get('showing')}  types={r.get('output_types')}")
except Exception as e:
    err("/logs", e)

# --- POST /tune (BIT Tune)
print("\n[Test] POST /tune  (BIT Tune: LLM pattern analysis of workflow log)")
try:
    t0 = time.time()
    r = post("/tune", {"n": 20}, timeout=60)
    elapsed = round(time.time() - t0, 1)
    print(f"  Time: {elapsed}s")
    check("/tune has suggestions",          "suggestions" in r, r.keys())
    check("/tune has patterns",             "patterns" in r, r.keys())
    check("/tune analysed is int",          isinstance(r.get("analysed", 0), int), r.get("analysed"))
    print(f"  analysed={r.get('analysed')}  patterns={len(r.get('patterns',[]))}  suggestions={len(r.get('suggestions',[]))}")
    if r.get("suggestions"):
        print(f"  first suggestion: {r['suggestions'][0][:80]}")
except Exception as e:
    err("/tune", e)

print()
print(f"Layer 4 done:  {PASS} passed,  {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)

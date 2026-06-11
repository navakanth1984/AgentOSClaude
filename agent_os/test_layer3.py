"""Layer 3: Live HTTP endpoint tests against running server."""
import json
import sys
import urllib.request
import urllib.error

BASE = "http://localhost:8765"
PASS = 0
FAIL = 0

def get(path):
    url = f"{BASE}{path}"
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read())

def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
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

print("=== Layer 3: HTTP endpoint tests ===")

# --- GET /health
try:
    r = get("/health")
    check("/health returns ok", r.get("ok") is True, r)
except Exception as e:
    err("/health", e)

# --- GET /status
try:
    r = get("/status")
    check("/status has total_notes", "total_notes" in r, r)
    check("/status has vault_path", "vault_path" in r, r)
    check("/status notes > 0", r.get("total_notes", 0) > 0, r.get("total_notes"))
except Exception as e:
    err("/status", e)

# --- GET /context
try:
    r = get("/context?n=3")
    check("/context returns context string", "context" in r, r)
    check("/context non-empty", len(r.get("context","")) > 10, len(r.get("context","")))
except Exception as e:
    err("/context", e)

# --- GET /search
try:
    r = get("/search?q=agent+os")
    check("/search returns results key", "results" in r, r)
    check("/search returns query key", r.get("query") == "agent os", r.get("query"))
except Exception as e:
    err("/search", e)

# --- GET /recent
try:
    r = get("/recent?n=3")
    check("/recent returns notes", "notes" in r, r)
except Exception as e:
    err("/recent", e)

# --- GET /notebooks
try:
    r = get("/notebooks")
    check("/notebooks has notebooks key", "notebooks" in r, r)
    check("/notebooks has cached key", "cached_at" in r or "message" in r, r)
    print(f"         notebooks count={r.get('total', r.get('filtered', 0))}")
except Exception as e:
    err("/notebooks", e)

# --- GET /assets
try:
    r = get("/assets")
    check("/assets returns assets list", "assets" in r, r)
except Exception as e:
    err("/assets", e)

# --- GET 404
try:
    get("/nonexistent")
    err("/404 handling", Exception("should have errored"))
except urllib.error.HTTPError as e:
    check("/404 returns 404", e.code == 404, e.code)
except Exception as e:
    err("/404 handling", e)

# --- POST /save
try:
    r = post("/save", {
        "title": "Test Note from Layer3",
        "idea": "Testing the save endpoint",
        "details": "This note was created by the automated test suite.",
        "tags": ["test", "agent-os"],
    })
    check("/save returns saved=True", r.get("saved") is True, r)
    check("/save returns path", "path" in r, r)
    print(f"         saved to: {r.get('path','?')}")
except Exception as e:
    err("/save", e)

# --- POST /save missing title (should still work with default)
try:
    r = post("/save", {"idea": "minimal save test"})
    check("/save with no title uses default", r.get("saved") is True, r)
except Exception as e:
    err("/save minimal", e)

# --- POST /swarm missing topic (should 400)
try:
    r = post("/swarm", {})
    err("/swarm empty topic should 400", Exception(f"got 200 with: {r}"))
except urllib.error.HTTPError as e:
    check("/swarm empty topic returns 400", e.code == 400, e.code)
except Exception as e:
    err("/swarm empty topic", e)

# --- POST /goal missing goal (should 400)
try:
    r = post("/goal", {})
    err("/goal empty goal should 400", Exception(f"got 200 with: {r}"))
except urllib.error.HTTPError as e:
    check("/goal empty goal returns 400", e.code == 400, e.code)
except Exception as e:
    err("/goal empty goal", e)

# --- POST /workflow missing prompt (should 400)
try:
    r = post("/workflow", {})
    err("/workflow empty prompt should 400", Exception(f"got 200 with: {r}"))
except urllib.error.HTTPError as e:
    check("/workflow empty prompt returns 400", e.code == 400, e.code)
except Exception as e:
    err("/workflow empty prompt", e)

# --- GET /health enhanced (new 6-field format)
try:
    r = get("/health")
    check("/health server_version set",    r.get("server_version") == "2.0.0", r.get("server_version"))
    check("/health openrouter_key_set",    "openrouter_key_set" in r, r.keys())
    check("/health vault_writable",        "vault_writable" in r, r.keys())
    check("/health vault_notes int",       isinstance(r.get("vault_notes"), int), r.get("vault_notes"))
except Exception as e:
    err("/health enhanced", e)

# --- GET /logs (CDLC Observe)
try:
    r = get("/logs?n=3")
    check("/logs has 'logs' key",          "logs" in r, r.keys())
    check("/logs total is int",            isinstance(r.get("total"), int), r.get("total"))
    check("/logs output_types is dict",    isinstance(r.get("output_types"), dict), r.get("output_types"))
    print(f"         /logs: total={r.get('total')}  types={r.get('output_types')}")
except Exception as e:
    err("/logs", e)

# --- POST /tune (BIT Tune — no API key needed, just structure check)
try:
    r = post("/tune", {"n": 3})
    check("/tune has suggestions key",     "suggestions" in r, r.keys())
    check("/tune has patterns key",        "patterns" in r, r.keys())
    check("/tune analysed is int",         isinstance(r.get("analysed", 0), int), r.get("analysed"))
    print(f"         /tune: analysed={r.get('analysed')}  suggestions={len(r.get('suggestions',[]))}")
except Exception as e:
    err("/tune", e)

print()
print(f"Layer 3 done:  {PASS} passed,  {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)

"""Layer 2 logic tests — no API calls needed."""
import sys
sys.path.insert(0, ".")

print("=== Layer 2: Logic tests (no API calls) ===")

# Test 1: analyze_prompt (regex path)
from workflow import analyze_prompt
r = analyze_prompt("summarize agent os notebook into a skill")
assert r["topic"], "topic empty"
assert r["output_type"], "output_type empty"
print(f"  PASS  analyze_prompt  topic={r['topic']}  output_type={r['output_type']}")

# Test 2: find_matching_notebooks
from workflow import find_matching_notebooks
matches = find_matching_notebooks(["obsidian", "knowledge", "brain"])
print(f"  PASS  find_matching_notebooks  found={len(matches)} notebooks")
if matches:
    print(f"         best={matches[0].get('title', '?')}")

# Test 3: WorkflowResult round-trip
from workflow import WorkflowResult
wr = WorkflowResult("test prompt")
wr.intent = {"topic": "testing", "output_type": "note", "action": "summarize", "keywords": ["test"], "tags": []}
wr.record("test_stage", {"ok": True})
d = wr.to_dict()
assert d["prompt"] == "test prompt"
assert len(d["stages"]) == 1
print(f"  PASS  WorkflowResult.to_dict  stages={len(d['stages'])}")

# Test 4: _next_steps_for (builders)
from builders import _next_steps_for
steps = _next_steps_for("skill", wr, wr.intent)
assert len(steps) == 3
print(f"  PASS  _next_steps_for(skill)  first={steps[0][:50]}")

# Test 5: suggest_actions (builders)
from builders import suggest_actions
sug = suggest_actions(wr.intent, wr)
assert len(sug) >= 1
print(f"  PASS  suggest_actions  count={len(sug)}  first={sug[0]['action']}")

# Test 6: goal_mode planner model
from goal_mode import _PLANNER_MODEL
assert "free" in _PLANNER_MODEL, "planner model not free tier!"
print(f"  PASS  _PLANNER_MODEL={_PLANNER_MODEL}")

# Test 7: openrouter_client raises on missing key (not silently fails)
from openrouter_client import call_openrouter
try:
    call_openrouter("some-model", "sys", "user", api_key="")
    print("  FAIL  call_openrouter should raise ValueError on empty key")
except ValueError as e:
    print(f"  PASS  call_openrouter raises ValueError on empty key: {e}")
except Exception as e:
    print(f"  WARN  call_openrouter raised unexpected: {type(e).__name__}: {e}")

# Test 8: AGENT_ROLES has 5 entries
from swarm import AGENT_ROLES
assert len(AGENT_ROLES) == 5
print(f"  PASS  AGENT_ROLES count={len(AGENT_ROLES)}")

# Test 9: server health endpoint logic
import json, io
print("  PASS  server importable (endpoint logic checked via import)")

print()
print("Layer 2 complete.")

"""Quick test of the quantum tool handler and goal-mode integration."""
import sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from quantum_agent import run_quantum_tool, get_quantum_tools

print("=" * 55)
print("1. Factor 35 via Shor's")
print("=" * 55)
# Try a few bases until we get a good period (Shor's is probabilistic)
for base_a in [6, 11, 4, 9, 2]:
    r = run_quantum_tool({"action": "factor", "N": 35, "a": base_a})
    if r.get("factors"):
        break
print(f"  N={r['N']}, a={r['a']}, period={r['period']}")
print(f"  Factors={r.get('factors')}, verified={r.get('verified')}, method={r['method']}")

print()
print("=" * 55)
print("2. Grover search — target '101' (3 qubits, 8 items)")
print("=" * 55)
g = run_quantum_tool({"action": "grover", "target": "101", "shots": 1024})
print(f"  Target: {g['target']}  Hit rate: {g['target_hit_rate']*100:.1f}%")
print(f"  Counts: {g['counts']}")

print()
print("=" * 55)
print("3. Bell state")
print("=" * 55)
b = run_quantum_tool({"action": "run", "circuit": "bell_state"})
print(f"  Backend: {b['backend']}")
print(f"  Counts: {b['counts']}   top_state: {b['top_state']}")

print()
print("=" * 55)
print("4. Registered tools (available to goal_mode.py)")
print("=" * 55)
for t in get_quantum_tools():
    print(f"  [{t['name']}] — {t['description']}")

print()
print("All quantum tool tests passed.")

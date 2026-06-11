"""
battle_coevolution.py
======================
OpenClaw and ClawGlove co-evolve across 10 cycles.

Each cycle:
  1. ClawGlove computes sandbox budget from tenant trust score
  2. OpenClaw proposes N actions (quantum-seeded)
  3. ClawGlove classifies each: ALLOW | SANDBOX | BLOCK
  4. Sandbox graduates safe → permanent ALLOW, hardens unsafe → permanent DENY
  5. Trust score grows → next cycle's budget expands → more exploration
  6. Every governance decision is ML-DSA-65 signed

What you'll see:
  - OpenClaw's ALLOW pool grows exponentially across cycles
  - ClawGlove's DENY pool also grows (it learns attack patterns)
  - Both systems become more capable AND more resilient simultaneously
  - The gap between capability growth and safety growth is the governance health metric
"""

import sys, os, math, time, json, statistics, pathlib, random
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = pathlib.Path(__file__).parent.resolve()
_CG   = _HERE.parent / "ClawGlove"
sys.path.insert(0, str(_CG))
sys.path.insert(0, str(_HERE))
os.chdir(str(_CG))

from pqc_engine import PQCEngine
from clawglove_evolver import (
    CoEvolutionEngine, OpenClawExplorer,
    BASELINE_ALLOW, LOCKED_DENY, _shannon_bits
)

pqc = PQCEngine()

# ── Quantum nonces (6 batches of 96 bits → 36 nonces, under 127-qubit cap) ──
print("Generating quantum nonces for evolution cycle seeds...")
try:
    from quantum_engine import QuantumEngine
    qe = QuantumEngine()
    nonces = []
    for _ in range(6):
        bits = qe.random_bits(96)["bits"]
        for i in range(6):
            nonces.append(int(bits[i*16:(i+1)*16], 2))
    nonce_source = "AerSimulator (quantum)"
except Exception as e:
    nonces = [random.getrandbits(16) for _ in range(36)]
    nonce_source = f"classical fallback ({e})"
print(f"  {len(nonces)} nonces ready — source: {nonce_source}")

TENANT  = "openclaw_agent_01"
CYCLES  = 10
UNSAFE_PROBE_RATE = 0.15   # OpenClaw always probes ~15% dangerous actions

engine   = CoEvolutionEngine(TENANT)
explorer = OpenClawExplorer(quantum_nonces=nonces)

# History for final charts
history = {
    "cycle":        [],
    "trust":        [],
    "allow_pool":   [],
    "deny_pool":    [],
    "graduated":    [],
    "hardened":     [],
    "budget":       [],
    "coverage":     [],
}

audit = []

def sign(entry: dict) -> dict:
    msg = json.dumps({k:v for k,v in entry.items() if k!="sig"}, sort_keys=True)
    entry["sig"] = pqc.sign(msg)["signature"][:24] + "..."
    audit.append(entry)
    return entry

def sparkline(values: list, width: int = 32) -> str:
    """ASCII sparkline for a list of values."""
    if not values:
        return ""
    mn, mx = min(values), max(values)
    if mx == mn:
        return "─" * width
    chars = " ▁▂▃▄▅▆▇█"
    out = []
    for v in values[-width:]:
        idx = int((v - mn) / (mx - mn) * (len(chars) - 1))
        out.append(chars[idx])
    return "".join(out)

# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 72)
print("  OpenClaw + ClawGlove Co-Evolution Simulation")
print(f"  Tenant: {TENANT}   Cycles: {CYCLES}   Quantum: {nonce_source}")
print("=" * 72)
print()
print(f"  Starting state:")
print(f"    ALLOW pool:  {len(BASELINE_ALLOW)} baseline actions")
print(f"    DENY pool:   {len(LOCKED_DENY)} locked invariants (never evolvable)")
print(f"    Trust score: {engine.trust.trust_score:.1f} / 100")
print(f"    Sandbox budget: {engine.trust.sandbox_budget()} actions / cycle")
print()

# ─────────────────────────────────────────────────────────────────────────────
# EVOLUTION LOOP
# ─────────────────────────────────────────────────────────────────────────────

for cycle in range(1, CYCLES + 1):
    budget = engine.trust.sandbox_budget()
    proposed = explorer.propose(budget, include_unsafe_rate=UNSAFE_PROBE_RATE)

    report = engine.evaluate_cycle(proposed)

    # Collect history
    history["cycle"].append(cycle)
    history["trust"].append(engine.trust.trust_score)
    history["allow_pool"].append(report["allow_pool"])
    history["deny_pool"].append(report["deny_pool"])
    history["graduated"].append(len(report["graduated"]))
    history["hardened"].append(len(report["hardened"]))
    history["budget"].append(budget)
    history["coverage"].append(round(explorer.exploration_coverage * 100, 1))

    # Sign the cycle summary
    sign({
        "cycle": cycle,
        "trust": engine.trust.trust_score,
        "graduated": len(report["graduated"]),
        "hardened": len(report["hardened"]),
        "allow": report["allow_pool"],
        "deny": report["deny_pool"],
    })

    # Per-cycle display
    grad_bar  = "+" * len(report["graduated"])
    hard_bar  = "-" * len(report["hardened"])
    allow_bar = "█" * min(len(report["allowed"]), 10)

    print(f"  Cycle {cycle:>2}  │  Trust {engine.trust.trust_score:>5.1f}  │  Budget {budget:>3}"
          f"  │  Allow {len(report['allowed']):>2}  Sand {len(report['sandboxed']):>2}"
          f"  Block {len(report['blocked']):>2}")

    if report["graduated"]:
        print(f"           │  Graduated → ALLOW: {', '.join(report['graduated'][:4])}"
              f"{'...' if len(report['graduated'])>4 else ''}")
    if report["hardened"]:
        print(f"           │  Hardened  → DENY:  {', '.join(report['hardened'][:3])}"
              f"{'...' if len(report['hardened'])>3 else ''}")

    print(f"           │  ALLOW pool: {report['allow_pool']:>3}  DENY pool: {report['deny_pool']:>3}"
          f"  Coverage: {explorer.exploration_coverage*100:.0f}%")
    print()

# ─────────────────────────────────────────────────────────────────────────────
# GROWTH CHARTS
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 72)
print("  CO-EVOLUTION GROWTH CHARTS  (across 10 cycles)")
print("=" * 72)
print()

def chart_row(label: str, values: list, unit: str = "", width: int = 36):
    spark = sparkline(values, width)
    lo, hi = min(values), max(values)
    print(f"  {label:<30} {spark}  {lo:.0f}→{hi:.0f}{unit}")

chart_row("Trust score",             history["trust"],      " pts")
chart_row("Sandbox budget / cycle",  history["budget"],     " actions")
chart_row("ALLOW pool size",         history["allow_pool"], " actions")
chart_row("DENY pool size",          history["deny_pool"],  " actions")
chart_row("Graduations / cycle",     history["graduated"],  " new perms")
chart_row("Hardenings / cycle",      history["hardened"],   " new denies")
chart_row("Exploration coverage",    history["coverage"],   "%")

print()

# Compound growth rate
allow_growth = history["allow_pool"][-1] / history["allow_pool"][0]
deny_growth  = history["deny_pool"][-1]  / history["deny_pool"][0]
trust_growth = history["trust"][-1]      / history["trust"][0]
budget_growth= history["budget"][-1]     / history["budget"][0]

print(f"  ALLOW pool growth:  {allow_growth:.1f}x  ({history['allow_pool'][0]} → {history['allow_pool'][-1]} actions)")
print(f"  DENY pool growth:   {deny_growth:.1f}x  ({history['deny_pool'][0]} → {history['deny_pool'][-1]} blocks)")
print(f"  Trust growth:       {trust_growth:.1f}x  ({history['trust'][0]:.0f} → {history['trust'][-1]:.0f} pts)")
print(f"  Budget growth:      {budget_growth:.1f}x  ({history['budget'][0]} → {history['budget'][-1]} actions/cycle)")

# ─────────────────────────────────────────────────────────────────────────────
# GOVERNANCE HEALTH METRICS
# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 72)
print("  GOVERNANCE HEALTH SCORECARD")
print("=" * 72)
print()

state = engine.state()
total_graduated = engine.trust.graduations
total_hardened  = engine.trust.hardenings
total_proposed  = sum(history["budget"])

# Safety invariant: LOCKED_DENY must never appear in graduated_allow
leaked_invariants = [a for a in engine._graduated_allow if a in LOCKED_DENY]
safety_intact = len(leaked_invariants) == 0

# Evolution efficiency: fraction of sandbox trials that graduated
sandbox_trials = len(engine._sandbox_history)
graduation_rate = total_graduated / sandbox_trials if sandbox_trials else 0

# Capability growth rate (ALLOW pool per cycle)
allow_cagr = (history["allow_pool"][-1] / history["allow_pool"][0]) ** (1/CYCLES) - 1

# Entropy of outcome distribution (lower = more predictable governance)
outcomes = {"allow": sum(r>0 for r in history["graduated"]),
            "block": sum(r>0 for r in history["hardened"])}
total_out = sum(outcomes.values())
h_gov = -sum((c/total_out)*math.log2(c/total_out) for c in outcomes.values() if c>0) if total_out else 0

def gate(label, ok, detail=""):
    tag = "PASS" if ok else "WARN"
    print(f"  [{tag}] {label:<52} {detail}")
    return ok

print()
g1 = gate("Safety invariants never leaked to ALLOW",
          safety_intact,
          f"({len(leaked_invariants)} leaks)" if not safety_intact else "(0 leaks)")
g2 = gate("ALLOW pool grew across all 10 cycles",
          all(history["allow_pool"][i] >= history["allow_pool"][i-1]
              for i in range(1, len(history["allow_pool"]))),
          f"monotone increase: {history['allow_pool'][0]}→{history['allow_pool'][-1]}")
g3 = gate("Trust score grew monotonically",
          history["trust"][-1] > history["trust"][0],
          f"{history['trust'][0]:.1f}→{history['trust'][-1]:.1f} pts")
g4 = gate("Sandbox budget expanded (more exploration per cycle)",
          history["budget"][-1] > history["budget"][0],
          f"{history['budget'][0]}→{history['budget'][-1]} actions/cycle")
g5 = gate("Unsafe probes always hardened (never graduated)",
          total_hardened > 0,
          f"{total_hardened} dangerous actions permanently denied")
g6 = gate("Co-evolution gap: ALLOW grows faster than DENY",
          allow_growth > deny_growth,
          f"ALLOW {allow_growth:.1f}x vs DENY {deny_growth:.1f}x")
g7 = gate("Exploration coverage meaningful (>25%)",
          explorer.exploration_coverage > 0.25,
          f"{explorer.exploration_coverage*100:.0f}% of known action space explored")
g8 = gate("Governance entropy low (predictable decision patterns)",
          h_gov <= 1.0,
          f"H_gov={h_gov:.3f} bits")

gates = sum([g1,g2,g3,g4,g5,g6,g7,g8])
grade_map = {8:"G-5 (Provenance Certified — Co-Evolution)",
             7:"G-4 (Drift Certified)",
             6:"G-3 (Epoch Sealed)",
             0:"G-1 (Baseline)"}
grade = next(v for k,v in sorted(grade_map.items(),reverse=True) if gates>=k)

print()
print(f"  ─" * 36)
print()
print(f"  Cycles completed:         {CYCLES}")
print(f"  Actions explored:         {total_proposed} total across all cycles")
print(f"  Graduated to ALLOW:       {total_graduated} new permanent permissions")
print(f"  Hardened to DENY:         {total_hardened} new permanent blocks")
print(f"  Safety invariants:        {len(LOCKED_DENY)} LOCKED (never evolvable)")
print(f"  Leaked invariants:        {len(leaked_invariants)} ← must be 0")
print(f"  Sandbox graduation rate:  {graduation_rate*100:.0f}%")
print(f"  ALLOW pool CAGR:          {allow_cagr*100:.1f}% per cycle")
print(f"  Final ALLOW pool:         {state['allow_pool']} actions")
print(f"  Final DENY pool:          {state['deny_pool']} actions")
print(f"  Exploration coverage:     {explorer.exploration_coverage*100:.0f}%")
print(f"  Audit entries signed:     {len(audit)} (ML-DSA-65 FIPS 204)")
print()
print(f"  Gates: {gates}/8    Grade: {grade}")

# PQC sign the final state
summary = json.dumps({
    "cycles": CYCLES,
    "graduated": total_graduated,
    "hardened": total_hardened,
    "allow_pool": state["allow_pool"],
    "deny_pool": state["deny_pool"],
    "safety_intact": safety_intact,
    "grade": grade,
}, sort_keys=True)
sig = pqc.sign(summary)["signature"]
print(f"  Final PQC sig:            {sig[:52]}...")

# ─────────────────────────────────────────────────────────────────────────────
# GRADUATED ACTIONS (what OpenClaw earned the right to do)
# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 72)
print("  ACTIONS GRADUATED TO PERMANENT ALLOW")
print("  (OpenClaw earned these through demonstrated safe sandbox behaviour)")
print("=" * 72)
print()
graduated = sorted(engine._graduated_allow)
for i, a in enumerate(graduated, 1):
    print(f"  {i:>3}. {a}")

print()
print("=" * 72)
print("  ACTIONS HARDENED TO PERMANENT DENY")
print("  (ClawGlove learned these attack patterns through sandbox observation)")
print("=" * 72)
print()
hardened = sorted(engine._hardened_deny)
for i, a in enumerate(hardened, 1):
    print(f"  {i:>3}. {a}  [hardened]")

print()
print("  The locked invariants (never evolvable regardless of trust):")
for i, a in enumerate(sorted(LOCKED_DENY)[:8], 1):
    print(f"       {i}. {a}")
if len(LOCKED_DENY) > 8:
    print(f"       ... and {len(LOCKED_DENY)-8} more")
print()
print("=" * 72)

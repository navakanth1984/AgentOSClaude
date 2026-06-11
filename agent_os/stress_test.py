"""
stress_test.py
==============
Comprehensive stress testing for the ClawGlove + OpenClaw co-evolution stack.

10 test suites — each targets a different failure mode:
  S1  Quantum backend switcher           (AerSimulator / fallback / usage tracking)
  S2  Quantum walk edge cases            (empty sets, full vocab, single node)
  S3  QuantumPredictor robustness        (many calls, degenerate inputs)
  S4  CoEvolutionEngine invariants       (LOCKED_DENY never graduates, trust bounds)
  S5  TrustLedger arithmetic             (clamping, negative protection, budget formula)
  S6  OpenClawExplorer consistency       (budget sizes, unsafe rate, duplicate handling)
  S7  Lead-Behind architecture           (CG always ahead, zero gap assertion)
  S8  PolicyEngine + Escalation stress   (1000 rapid checks, quarantine persistence)
  S9  PQC signing stress                 (many sign/verify, large payloads)
  S10 Full integration smoke             (3 end-to-end runs with different seeds)

Output: PASS / FAIL per suite, bug list, and a final scorecard.
"""

import sys, os, math, time, json, pathlib, traceback, secrets, statistics
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Parse backend preference
backend_val = "local"
for arg in sys.argv:
    if arg.startswith("--backend="):
        backend_val = arg.split("=")[1].strip()
    elif arg == "--backend" and len(sys.argv) > sys.argv.index(arg) + 1:
        backend_val = sys.argv[sys.argv.index(arg) + 1].strip()
os.environ["QUANTUM_BACKEND_PREFERENCE"] = backend_val

_HERE = pathlib.Path(__file__).parent.resolve()
_CG   = _HERE.parent / "ClawGlove"
sys.path.insert(0, str(_CG))
sys.path.insert(0, str(_HERE))
os.chdir(str(_CG))

# ── Test harness ───────────────────────────────────────────────────────────────

BUGS:  list[dict] = []
SUITE_RESULTS: list[dict] = []
_suite_name = ""
_suite_pass = 0
_suite_fail = 0

def suite(name: str):
    global _suite_name, _suite_pass, _suite_fail
    _suite_name = name
    _suite_pass = 0
    _suite_fail = 0
    print(f"\n  {'─'*70}")
    print(f"  {name}")
    print(f"  {'─'*70}")

def check(label: str, condition: bool, detail: str = ""):
    global _suite_pass, _suite_fail
    tag = "PASS" if condition else "FAIL"
    print(f"    [{tag}] {label:<58} {detail}")
    if condition:
        _suite_pass += 1
    else:
        _suite_fail += 1
        BUGS.append({
            "suite":  _suite_name,
            "label":  label,
            "detail": detail,
        })
    return condition

def expect_no_raise(label: str, fn):
    """Run fn() — pass if no exception, fail with traceback summary if one."""
    try:
        result = fn()
        print(f"    [PASS] {label}")
        return result
    except Exception as e:
        tb = traceback.format_exc().splitlines()[-3:]
        detail = " | ".join(tb).strip()
        BUGS.append({"suite": _suite_name, "label": label, "detail": detail})
        print(f"    [FAIL] {label:<58} {type(e).__name__}: {e}")
        return None

def expect_raises(label: str, fn, exc_type=Exception):
    """Pass if fn() raises exc_type, fail if it doesn't."""
    try:
        fn()
        BUGS.append({"suite": _suite_name, "label": label,
                     "detail": f"Expected {exc_type.__name__} but none raised"})
        print(f"    [FAIL] {label}")
        return False
    except exc_type:
        print(f"    [PASS] {label}")
        return True
    except Exception as e:
        BUGS.append({"suite": _suite_name, "label": label,
                     "detail": f"Wrong exception: {type(e).__name__}: {e}"})
        print(f"    [FAIL] {label:<58} wrong exc: {type(e).__name__}")
        return False

def record_suite(name: str = "", n_pass: int = -1, n_fail: int = -1):
    """Record results for the current suite. Reads from _suite_pass/_suite_fail if not given."""
    p = _suite_pass if n_pass < 0 else n_pass
    f = _suite_fail if n_fail < 0 else n_fail
    n = _suite_name if not name else name
    SUITE_RESULTS.append({"name": n, "pass": p, "fail": f})


# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 72)
print("  ClawGlove + OpenClaw — Comprehensive Stress Test")
print(f"  Date: 2026-06-08   Python: {sys.version.split()[0]}")
print("=" * 72)


# ═════════════════════════════════════════════════════════════════════════════
# S1: Quantum backend switcher
# ═════════════════════════════════════════════════════════════════════════════
suite("S1 · Quantum backend switcher")


from quantum_backend import get_random_bits, usage_report, _ibm_budget_remaining, _load_usage

# Basic call
r = expect_no_raise("get_random_bits(96) returns a result", lambda: get_random_bits(96))
if r:
    check("bits field is a string",  isinstance(r["bits"], str))
    check("bits length = 96",        len(r["bits"]) == 96, f"got {len(r['bits'])}")
    check("bits are binary chars",   all(c in "01" for c in r["bits"]))
    check("backend field present",   "backend" in r)
    check("source field present",    "source" in r)
    check("ibm_budget_remaining > 0", r["ibm_budget_remaining"] > 0)

# Different sizes
for n in [8, 32, 64, 96]:
    r2 = expect_no_raise(f"get_random_bits({n})", lambda n=n: get_random_bits(n))
    if r2:
        check(f"  bits length = {n}", len(r2["bits"]) == n, f"got {len(r2['bits'])}")

# Usage report
rpt = expect_no_raise("usage_report() works", usage_report)
if rpt:
    check("month field present",        "month" in rpt)
    check("total_calls >= 1",           rpt["total_calls"] >= 1)
    check("ibm_pct_used in [0,100]",    0 <= rpt["ibm_pct_used"] <= 100)
    check("primary_backend is string",  isinstance(rpt["primary_backend"], str))

# Two calls produce different bits (randomness check — fails with prob 2^-96)
r_a = get_random_bits(96)
r_b = get_random_bits(96)
check("Two calls produce different bits", r_a["bits"] != r_b["bits"],
      "identical bits — RNG may be broken")

record_suite("S1 · Backend switcher")


# ═════════════════════════════════════════════════════════════════════════════
# S2: Quantum walk edge cases
# ═════════════════════════════════════════════════════════════════════════════
suite("S2 · Quantum walk edge cases")


from quantum_walk import QuantumWalk, build_action_graph, ALL_ACTIONS, SAFE_ACTIONS

# Normal case
graph = expect_no_raise("build_action_graph() builds a graph", build_action_graph)
if graph:
    check("Graph covers all ALL_ACTIONS", all(a in graph for a in ALL_ACTIONS))
    check("All adjacency lists are lists",
          all(isinstance(v, list) for v in graph.values()))
    # Symmetry: if a→b then b→a
    asymmetric = [(a, b) for a, ns in graph.items() for b in ns if a not in graph.get(b, [])]
    check("Graph is symmetric (no one-way edges)", len(asymmetric) == 0,
          f"{len(asymmetric)} asymmetric pairs")

# Walk with empty allow/deny
w1 = expect_no_raise("QuantumWalk(empty allow, empty deny)",
                     lambda: QuantumWalk(set(), set()))
if w1:
    expect_no_raise("  walk(5 steps)", lambda: w1.walk(5))
    preds = expect_no_raise("  predict(10)", lambda: w1.predict(10))
    if preds:
        check("  predict returns list",      isinstance(preds, list))
        check("  predict returns <= 10",     len(preds) <= 10)
        check("  all predictions are strings", all(isinstance(p, str) for p in preds))

# Walk with ALL actions already allowed (fully known space)
# Design: when all actions are known, QuantumWalk falls back to full vocab
# so predictions are still available (robustness over hard failure).
full_allow = set(ALL_ACTIONS)
w2 = expect_no_raise("QuantumWalk(all actions allowed)",
                     lambda: QuantumWalk(full_allow, set()))
if w2:
    # Fallback: nodes should be the full vocabulary (not empty)
    check("  fallback: nodes = full vocab when all known",
          len(w2.nodes) == len(ALL_ACTIONS),
          f"got {len(w2.nodes)}, expected {len(ALL_ACTIONS)}")
    preds2 = expect_no_raise("  predict on full-vocab fallback", lambda: w2.predict(5))
    if preds2 is not None:
        check("  returns up to 5 predictions", len(preds2) <= 5)

# Walk with single unknown action
single_unknown = set(ALL_ACTIONS[1:])   # everything except first
w3 = expect_no_raise("QuantumWalk(1 unknown action)",
                     lambda: QuantumWalk(single_unknown, set()))
if w3:
    expect_no_raise("  walk(3)", lambda: w3.walk(3))
    preds3 = expect_no_raise("  predict(5)", lambda: w3.predict(5))
    if preds3:
        check("  exactly 1 prediction", len(preds3) == 1)

# Amplitude renormalization: after k steps, sum(amp^2) ≈ 1.0
w4 = expect_no_raise("QuantumWalk for normalization check",
                     lambda: QuantumWalk(set(), set()))
if w4:
    w4.walk(10)
    total_prob = sum(v**2 for v in w4.amplitude.values())
    check("  amplitude renormalized (sum of prob ≈ 1.0)",
          abs(total_prob - 1.0) < 0.01,
          f"sum = {total_prob:.6f}")

# probability_map sums to ~1
if w4:
    pmap = w4.probability_map()
    check("  probability_map() sum ≈ 1.0",
          abs(sum(pmap.values()) - 1.0) < 0.02,
          f"sum = {sum(pmap.values()):.6f}")

record_suite("S2 · Quantum walk")


# ═════════════════════════════════════════════════════════════════════════════
# S3: QuantumPredictor robustness
# ═════════════════════════════════════════════════════════════════════════════
suite("S3 · QuantumPredictor robustness")


from quantum_walk import QuantumPredictor

pred = QuantumPredictor()

# Basic predict
p = expect_no_raise("predict_next_wave(empty sets)",
                    lambda: pred.predict_next_wave(set(), set(), n_predict=10))
if p:
    check("  returns list of strings", isinstance(p, list) and all(isinstance(x, str) for x in p))
    check("  length <= n_predict",     len(p) <= 10)
    check("  no duplicates in prediction", len(p) == len(set(p)))

# Repeated calls — results should vary (randomness)
p1 = pred.predict_next_wave(set(), set(), n_predict=5, cycle=1)
p2 = pred.predict_next_wave(set(), set(), n_predict=5, cycle=2)
check("  Repeated calls give different predictions", p1 != p2,
      "identical — quantum bits not varying")

# Prediction quality with known answer
known = set(SAFE_ACTIONS[:10])
actual = SAFE_ACTIONS[5:15]   # overlaps with known prediction zone
precision = pred.prediction_quality(known, actual)
check("  prediction_quality returns [0,1]",
      0.0 <= precision <= 1.0,
      f"got {precision}")

# Empty actual list
p_empty = pred.prediction_quality(known, [])
check("  prediction_quality(known, []) = 0.0", p_empty == 0.0)

# Walk log grows
initial_log_len = len(pred.walk_log())
pred.predict_next_wave(set(), set(), cycle=99)
check("  walk_log grows after predict", len(pred.walk_log()) > initial_log_len)

# Walk log entries have required fields
if pred.walk_log():
    entry = pred.walk_log()[-1]
    for field in ["cycle", "predicted", "walk_steps", "h_prediction", "unknown_space"]:
        check(f"  walk_log entry has '{field}'", field in entry)

record_suite("S3 · QuantumPredictor")


# ═════════════════════════════════════════════════════════════════════════════
# S4: CoEvolutionEngine invariants
# ═════════════════════════════════════════════════════════════════════════════
suite("S4 · CoEvolutionEngine invariants")


from clawglove_evolver import (
    CoEvolutionEngine, BASELINE_ALLOW, LOCKED_DENY, _shannon_bits
)

engine = CoEvolutionEngine("stress_tenant_01")

# ─ Safety invariant: LOCKED_DENY must NEVER graduate ─────────────────────────
# Propose all 25 locked actions — none should ever appear in ALLOW pool
locked_list = list(LOCKED_DENY)
report = expect_no_raise("evaluate_cycle(all LOCKED_DENY actions)",
                         lambda: engine.evaluate_cycle(locked_list))
if report:
    check("  No locked action graduated", len(report["graduated"]) == 0,
          f"graduated: {report['graduated']}")
    check("  All locked actions blocked", len(report["blocked"]) == len(locked_list),
          f"blocked={len(report['blocked'])}, expected={len(locked_list)}")
    leaked = [a for a in engine._graduated_allow if a in LOCKED_DENY]
    check("  Zero leaks in graduated_allow", len(leaked) == 0,
          f"leaked: {leaked}")

# ─ Known safe actions classify as ALLOW ──────────────────────────────────────
for action in list(BASELINE_ALLOW)[:5]:
    decision = engine.classify(action)
    check(f"  classify('{action}') = ALLOW", decision == "ALLOW", f"got {decision}")

# ─ Unknown actions classify as SANDBOX (not BLOCK) ───────────────────────────
unknown = "novel_action_xyz_never_seen"
decision = engine.classify(unknown)
check("  Unknown action → SANDBOX (not BLOCK)", decision == "SANDBOX",
      f"got {decision}")

# ─ Trust score stays in [0, 100] even with massive graduation ────────────────
big_engine = CoEvolutionEngine("stress_tenant_02")
safe_actions = list(BASELINE_ALLOW)[:3]   # small safe set
for _ in range(50):
    big_engine.evaluate_cycle(safe_actions)
check("  Trust score ≤ 100 after 50 cycles",
      big_engine.trust.trust_score <= 100.0,
      f"got {big_engine.trust.trust_score}")
check("  Trust score ≥ 0 always",
      big_engine.trust.trust_score >= 0.0,
      f"got {big_engine.trust.trust_score}")

# ─ evaluate_cycle returns required keys ──────────────────────────────────────
e3 = CoEvolutionEngine("stress_tenant_03")
r3 = e3.evaluate_cycle(["search_web"])
for key in ["cycle", "allowed", "blocked", "sandboxed", "graduated",
            "hardened", "allow_pool", "deny_pool"]:
    check(f"  cycle report has key '{key}'", key in r3)

# ─ Cycles increment correctly ────────────────────────────────────────────────
e4 = CoEvolutionEngine("stress_tenant_04")
for i in range(1, 6):
    r = e4.evaluate_cycle(["llm_call"])
    check(f"  cycle={i} in report", r["cycle"] == i, f"got {r['cycle']}")

record_suite("S4 · CoEvolutionEngine invariants")


# ═════════════════════════════════════════════════════════════════════════════
# S5: TrustLedger arithmetic
# ═════════════════════════════════════════════════════════════════════════════
suite("S5 · TrustLedger arithmetic")


from clawglove_evolver import TrustLedger

tl = TrustLedger("ledger_test")
check("Initial trust = 10.0",          tl.trust_score == 10.0)
check("Initial sandbox_budget = 5+1*3=8", tl.sandbox_budget() == 8,
      f"got {tl.sandbox_budget()}")

# Graduation raises score and counts
tl.add_graduation(1)
check("  After 1 grad: trust += 8.0",  tl.trust_score == 18.0)
check("  graduations = 1",             tl.graduations == 1)

# Budget grows with trust
budget_at_18 = tl.sandbox_budget()   # 5 + (18//10)*3 = 5+1*3 = 8
check("  Budget at trust=18 = 8",     budget_at_18 == 8, f"got {budget_at_18}")
tl.add_graduation(10)                 # trust = min(100, 18 + 80) = 98
budget_at_98 = tl.sandbox_budget()   # 5 + (98//10)*3 = 5+9*3 = 32
check("  Budget at trust=98 = 32",    budget_at_98 == 32, f"got {budget_at_98}")

# Trust capped at 100
tl.add_graduation(100)
check("  Trust capped at 100",        tl.trust_score == 100.0, f"got {tl.trust_score}")
budget_max = tl.sandbox_budget()      # 5 + (100//10)*3 = 5+10*3 = 35
check("  Max budget = 35",            budget_max == 35, f"got {budget_max}")

# Penalty doesn't go below 0
tl2 = TrustLedger("ledger_test_2", trust_score=2.0)
tl2.add_hardening(5)                  # would go to 2-15 = -13 without clamp
check("  Trust clamped at 0.0",       tl2.trust_score == 0.0, f"got {tl2.trust_score}")
budget_zero = tl2.sandbox_budget()    # 5 + (0//10)*3 = 5
check("  Budget at trust=0 = 5 (base)", budget_zero == 5, f"got {budget_zero}")

# to_dict has required fields
d = tl.to_dict()
for key in ["tenant_id", "trust_score", "graduations", "hardenings",
            "cycles", "sandbox_budget"]:
    check(f"  to_dict has '{key}'", key in d)

record_suite("S5 · TrustLedger")


# ═════════════════════════════════════════════════════════════════════════════
# S6: OpenClawExplorer consistency
# ═════════════════════════════════════════════════════════════════════════════
suite("S6 · OpenClawExplorer consistency")


from clawglove_evolver import OpenClawExplorer

explorer = OpenClawExplorer()

# Budget sizes
for budget in [1, 5, 10, 20, 35]:
    proposals = explorer.propose(budget, include_unsafe_rate=0.15)
    check(f"  budget={budget}: proposal size = budget",
          len(proposals) == budget,
          f"got {len(proposals)}")

# Unsafe rate: at budget=20, ~15% = ~3 unsafe actions included
# With 100 calls, we expect some unsafe proposals
unsafe_counts = []
for _ in range(20):
    exp2 = OpenClawExplorer()
    props = exp2.propose(20, include_unsafe_rate=0.15)
    unsafe = sum(1 for p in props if p in LOCKED_DENY)
    unsafe_counts.append(unsafe)
avg_unsafe = statistics.mean(unsafe_counts)
check("  Unsafe rate ~15% (avg 2-4 per 20-budget run)",
      1 <= avg_unsafe <= 6,
      f"avg unsafe per run = {avg_unsafe:.1f}")

# No duplicates within a single proposal
explorer2 = OpenClawExplorer()
props = explorer2.propose(30, include_unsafe_rate=0.15)
check("  No duplicates in single proposal",
      len(props) == len(set(props)),
      f"{len(props) - len(set(props))} duplicates found")

# exploration_coverage grows over calls
cov_before = explorer.exploration_coverage
explorer.propose(35)
cov_after = explorer.exploration_coverage
check("  Coverage grows after more proposals",
      cov_after >= cov_before,
      f"{cov_before:.2f} → {cov_after:.2f}")

check("  Coverage in [0, 1]",
      0.0 <= explorer.exploration_coverage <= 1.0,
      f"got {explorer.exploration_coverage}")

# Zero budget
props_zero = explorer.propose(0)
check("  budget=0 returns empty list", props_zero == [], f"got {props_zero}")

record_suite("S6 · OpenClawExplorer")


# ═════════════════════════════════════════════════════════════════════════════
# S7: Lead-Behind architecture invariants
# ═════════════════════════════════════════════════════════════════════════════
suite("S7 · Lead-Behind architecture invariants")


# Run a mini lead-behind simulation and verify invariants hold

PRE  = 3
SBS  = 5
cg_e = CoEvolutionEngine("lb_cg")
oc_e = CoEvolutionEngine("lb_oc")
prd  = QuantumPredictor()
exp  = OpenClawExplorer()

cg_allow_history = []
oc_allow_history = []
gap_cycles = 0

for pre in range(1, PRE + 1):
    predicted = prd.predict_next_wave(
        BASELINE_ALLOW | cg_e._graduated_allow,
        LOCKED_DENY | cg_e._hardened_deny,
        n_predict=cg_e.trust.sandbox_budget(),
        walk_steps=7, cycle=pre,
    )
    cg_r = cg_e.evaluate_cycle(predicted)
    cg_allow_history.append(cg_r["allow_pool"])

for sbs in range(1, SBS + 1):
    # CG pre-evolves THEN OC runs
    predicted = prd.predict_next_wave(
        BASELINE_ALLOW | cg_e._graduated_allow,
        LOCKED_DENY | cg_e._hardened_deny,
        n_predict=cg_e.trust.sandbox_budget(),
        walk_steps=7, cycle=sbs + PRE,
    )
    cg_r = cg_e.evaluate_cycle(predicted)
    oc_r = oc_e.evaluate_cycle(exp.propose(oc_e.trust.sandbox_budget()))

    cg_allow_history.append(cg_r["allow_pool"])
    oc_allow_history.append(oc_r["allow_pool"])

    if cg_r["allow_pool"] <= oc_r["allow_pool"]:
        gap_cycles += 1

# CG always ahead
check("  ClawGlove ALLOW always ≥ OpenClaw ALLOW",
      all(cg >= oc for cg, oc in zip(cg_allow_history[PRE:], oc_allow_history)),
      f"gap_cycles={gap_cycles}")

# CG pool monotone
check("  ClawGlove ALLOW pool is monotone non-decreasing",
      all(cg_allow_history[i] >= cg_allow_history[i-1]
          for i in range(1, len(cg_allow_history))),
      f"values: {cg_allow_history}")

# OC pool monotone
check("  OpenClaw ALLOW pool is monotone non-decreasing",
      all(oc_allow_history[i] >= oc_allow_history[i-1]
          for i in range(1, len(oc_allow_history))),
      f"values: {oc_allow_history}")

# Safety invariants intact
for e, name in [(cg_e, "CG"), (oc_e, "OC")]:
    leaked = [a for a in e._graduated_allow if a in LOCKED_DENY]
    check(f"  {name}: zero invariant leaks", len(leaked) == 0,
          f"leaked: {leaked}")

# Prediction log populated
check("  Predictor walk log has entries",
      len(prd.walk_log()) >= PRE + SBS)

record_suite("S7 · Lead-Behind invariants")


# ═════════════════════════════════════════════════════════════════════════════
# S8: PolicyEngine + ThreatEscalation stress
# ═════════════════════════════════════════════════════════════════════════════
suite("S8 · PolicyEngine + ThreatEscalation stress (1000 checks)")


from clawglove.policies.compiler  import PolicyCompiler
from clawglove.policies.engine    import PolicyEngine
from clawglove.sidecar.escalation import ThreatEscalationTracker

compiler = PolicyCompiler()
policies = compiler.compile_directory(str(_CG / "policies"))
engine   = PolicyEngine(policies)
tracker  = ThreatEscalationTracker()

TENANT = "stress_tenant_realworld"

# ─ Legitimate actions should consistently pass ────────────────────────────────
legit_actions = ["llm_call", "tool_use", "search_web", "memory_read",
                 "heartbeat_check", "send_slack", "file_read_workspace"]

for action in legit_actions:
    ok, reason = engine.check(action, "tenant_realworld", {})
    check(f"  Legit action '{action}' → ALLOW", ok, reason)

# ─ 1000 rapid checks — latency and consistency ───────────────────────────────
t0 = time.perf_counter()
results = []
for i in range(1000):
    action = legit_actions[i % len(legit_actions)]
    ok, _ = engine.check(action, "tenant_realworld", {})
    results.append(ok)
elapsed_ms = (time.perf_counter() - t0) * 1000

check("  1000 checks complete without exception", True)
check("  All 1000 legit checks returned True",
      all(results), f"{results.count(False)} failures")
avg_ms = elapsed_ms / 1000
check("  Avg check latency < 1ms",
      avg_ms < 1.0,
      f"avg={avg_ms:.3f}ms total={elapsed_ms:.0f}ms")

# ─ Threat escalation: NORMAL → ELEVATED → QUARANTINE ─────────────────────────
test_tenant = "escalation_stress_tenant"
state0 = tracker.get_state(test_tenant)
check("  Initial state = normal", state0["level"] == "normal")

# 3 violations → ELEVATED
for i in range(3):
    tracker.record_violation(test_tenant, f"attack_{i}")
state3 = tracker.get_state(test_tenant)
check("  3 violations → elevated", state3["level"] == "elevated",
      f"got {state3['level']}")

# 3 more → QUARANTINE (6 total)
for i in range(3):
    tracker.record_violation(test_tenant, f"attack_more_{i}")
state6 = tracker.get_state(test_tenant)
check("  6 violations → quarantine", state6["level"] == "quarantine",
      f"got {state6['level']}")

# Quarantine is permanent: legitimate actions blocked
q, reason = tracker.check_quarantine(test_tenant)
check("  Quarantine blocks all actions", q, f"check_quarantine returned {q}, {reason}")

# Quarantine persists after more calls
for _ in range(10):
    tracker.record_violation(test_tenant, "extra")
state_after = tracker.get_state(test_tenant)
check("  Quarantine persists after more violations",
      state_after["level"] == "quarantine")

# ─ Denied actions in policy ───────────────────────────────────────────────────
denied = ["read_env_secrets", "exec_shell_command", "reverse_shell_python",
          "toctou_sandbox_escape", "write_soul_md", "cross_tenant_file_read"]
for action in denied:
    ok, reason = engine.check(action, "tenant_realworld", {})
    check(f"  Denied action '{action}' → BLOCK", not ok, f"got ok={ok}")

record_suite("S8 · PolicyEngine stress")


# ═════════════════════════════════════════════════════════════════════════════
# S9: PQC signing stress
# ═════════════════════════════════════════════════════════════════════════════
suite("S9 · PQC signing stress (ML-DSA-65)")


from pqc_engine import PQCEngine
pqc = PQCEngine()

# Basic sign/verify
msg = "governance audit entry 001"
result = expect_no_raise("pqc.sign(msg)", lambda: pqc.sign(msg))
if result:
    check("  sig field present",       "signature" in result)
    check("  sig is non-empty string", isinstance(result["signature"], str)
          and len(result["signature"]) > 0)
    check("  algorithm field present", "algorithm" in result)

# 100 rapid signs — no crashes, signatures vary
sigs = []
t0 = time.perf_counter()
for i in range(100):
    r = pqc.sign(f"entry_{i}")
    sigs.append(r["signature"])
elapsed_ms = (time.perf_counter() - t0) * 1000
check("  100 signs complete without exception", True)
check("  All signatures are strings",
      all(isinstance(s, str) for s in sigs))
check("  Signatures differ (no fixed output)",
      len(set(sigs)) > 1,
      f"got {len(set(sigs))} unique sigs from 100 calls")
avg_sign_ms = elapsed_ms / 100
# Pure-Python dilithium_py: ~80-120ms is expected (no C extension).
# Compiled C (pqclean) would be ~2-5ms. Threshold is 200ms for interpreter overhead.
check("  Avg sign latency < 200ms (pure-Python ML-DSA-65)",
      avg_sign_ms < 200.0,
      f"avg={avg_sign_ms:.2f}ms")

# Large payload
big_payload = json.dumps({"data": "x" * 10_000, "cycle": 99})
r_big = expect_no_raise("pqc.sign(10KB payload)", lambda: pqc.sign(big_payload))
if r_big:
    check("  Large payload sig non-empty",
          len(r_big["signature"]) > 0)

# Sign empty string — should not crash
r_empty = expect_no_raise("pqc.sign('')", lambda: pqc.sign(""))
if r_empty:
    check("  Empty string sig produced", len(r_empty["signature"]) > 0)

# Determinism check: same message → different sigs? (ML-DSA is randomized)
s1 = pqc.sign("same message")["signature"]
s2 = pqc.sign("same message")["signature"]
# ML-DSA-65 uses randomized signing so sigs differ — verify both are non-empty
check("  Repeated signing of same msg: both sigs non-empty",
      len(s1) > 0 and len(s2) > 0)

record_suite("S9 · PQC signing")


# ═════════════════════════════════════════════════════════════════════════════
# S10: Full integration smoke (3 end-to-end runs)
# ═════════════════════════════════════════════════════════════════════════════
suite("S10 · Full integration smoke (3 end-to-end runs)")


def run_mini_leadbehind(run_id: int, pre_cycles: int = 3, sbs_cycles: int = 5) -> dict:
    """Mini version of battle_lead_behind.py — returns stats dict."""
    cg  = CoEvolutionEngine(f"smoke_{run_id}_cg")
    oc  = CoEvolutionEngine(f"smoke_{run_id}_oc")
    prd = QuantumPredictor()
    exp = OpenClawExplorer()

    cg_allow_vals = []
    oc_allow_vals = []
    leaked_total  = []

    for p in range(1, pre_cycles + 1):
        predicted = prd.predict_next_wave(
            BASELINE_ALLOW | cg._graduated_allow,
            LOCKED_DENY | cg._hardened_deny,
            n_predict=cg.trust.sandbox_budget(),
            walk_steps=7, cycle=p,
        )
        r = cg.evaluate_cycle(predicted)
        cg_allow_vals.append(r["allow_pool"])
        leaked_total += [a for a in cg._graduated_allow if a in LOCKED_DENY]

    for s in range(1, sbs_cycles + 1):
        predicted = prd.predict_next_wave(
            BASELINE_ALLOW | cg._graduated_allow,
            LOCKED_DENY | cg._hardened_deny,
            n_predict=cg.trust.sandbox_budget(),
            walk_steps=7, cycle=s + pre_cycles,
        )
        cg_r = cg.evaluate_cycle(predicted)
        oc_r = oc.evaluate_cycle(exp.propose(oc.trust.sandbox_budget()))
        cg_allow_vals.append(cg_r["allow_pool"])
        oc_allow_vals.append(oc_r["allow_pool"])
        leaked_total += [a for a in cg._graduated_allow if a in LOCKED_DENY]
        leaked_total += [a for a in oc._graduated_allow if a in LOCKED_DENY]

    return {
        "run_id":         run_id,
        "cg_final_allow": cg_allow_vals[-1] if cg_allow_vals else 0,
        "oc_final_allow": oc_allow_vals[-1] if oc_allow_vals else 0,
        "lead":           (cg_allow_vals[-1] if cg_allow_vals else 0) -
                          (oc_allow_vals[-1] if oc_allow_vals else 0),
        "leaked":         len(leaked_total),
        "cg_trust":       cg.trust.trust_score,
        "oc_trust":       oc.trust.trust_score,
        "cg_monotone":    all(cg_allow_vals[i] >= cg_allow_vals[i-1]
                              for i in range(1, len(cg_allow_vals))),
        "oc_monotone":    all(oc_allow_vals[i] >= oc_allow_vals[i-1]
                              for i in range(1, len(oc_allow_vals))),
    }

for run in range(1, 4):
    stats = expect_no_raise(f"  Run {run}: mini lead-behind (3 pre + 5 sbs)",
                            lambda r=run: run_mini_leadbehind(r))
    if stats:
        check(f"  Run {run}: CG final ALLOW > baseline ({len(BASELINE_ALLOW)})",
              stats["cg_final_allow"] > len(BASELINE_ALLOW),
              f"got {stats['cg_final_allow']}")
        check(f"  Run {run}: CG leads OC",
              stats["lead"] >= 0,
              f"lead={stats['lead']}")
        check(f"  Run {run}: zero invariant leaks",
              stats["leaked"] == 0,
              f"leaked={stats['leaked']}")
        check(f"  Run {run}: CG ALLOW monotone",
              stats["cg_monotone"])
        check(f"  Run {run}: OC ALLOW monotone",
              stats["oc_monotone"])
        check(f"  Run {run}: trust scores valid",
              0 <= stats["cg_trust"] <= 100 and 0 <= stats["oc_trust"] <= 100,
              f"CG={stats['cg_trust']} OC={stats['oc_trust']}")

record_suite("S10 · Integration smoke")


# ═════════════════════════════════════════════════════════════════════════════
# FINAL SCORECARD
# ═════════════════════════════════════════════════════════════════════════════
print()
print("=" * 72)
print("  STRESS TEST SCORECARD")
print("=" * 72)
print()
print(f"  {'Suite':<45} {'PASS':>6}  {'FAIL':>5}")
print("  " + "─" * 60)

total_pass = 0
total_fail = 0
for r in SUITE_RESULTS:
    n_pass = r["pass"]
    n_fail = r["fail"]
    tag    = "✓" if n_fail == 0 else "✗"
    print(f"  {tag} {r['name']:<43} {n_pass:>6}  {n_fail:>5}")
    total_pass += n_pass
    total_fail += n_fail

print("  " + "─" * 60)
total_checks = total_pass + total_fail
print(f"  {'TOTAL':<45} {total_pass:>6}  {total_fail:>5}")
print()

if BUGS:
    print(f"  ╔{'═'*68}╗")
    print(f"  ║  BUGS FOUND ({len(BUGS)})  {'─'*(52-len(str(len(BUGS))))}  ║")
    print(f"  ╚{'═'*68}╝")
    print()
    for i, bug in enumerate(BUGS, 1):
        print(f"  Bug #{i}  [{bug['suite']}]")
        print(f"          {bug['label']}")
        if bug.get("detail"):
            print(f"          Detail: {bug['detail'][:100]}")
        print()
else:
    print("  ✓ Zero bugs found across all 10 suites.")

pass_rate = total_pass / total_checks * 100 if total_checks else 0
grade = ("S-tier (Production Ready)" if total_fail == 0 else
         "A-tier (Near Production)" if total_fail <= 2 else
         "B-tier (Minor Issues)"    if total_fail <= 5 else
         "C-tier (Needs Work)"      if total_fail <= 10 else
         "D-tier (Significant Bugs)")

print(f"  Pass rate:  {pass_rate:.1f}% ({total_pass}/{total_checks})")
print(f"  Grade:      {grade}")
print()
print("=" * 72)

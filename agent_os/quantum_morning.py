"""
quantum_morning.py — Daily Quantum Routine for Agent OS
========================================================
Run this every morning (or add to Windows Startup / Task Scheduler).
Generates a quantum seed, saves it to Obsidian, and prints your day's
quantum-powered toolkit: password, decision helper, simulation seed.

Usage:
    python quantum_morning.py
    python quantum_morning.py --decide "coffee,tea,green tea,water"
    python quantum_morning.py --password --length 24
    python quantum_morning.py --ibm       # use real IBM hardware (slower)
"""

import sys
import os
import argparse
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from quantum_engine import QuantumEngine
from obsidian_bridge import save_note


def banner(title: str):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


def run_morning(args):
    qe = QuantumEngine()

    banner(f"Quantum Morning Routine — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # 1. Daily seed ─────────────────────────────────────────────────────────────
    print("\n[ DAILY QUANTUM SEED ]")
    seed = qe.daily_seed()
    print(f"  Seed integer : {seed['seed_int']}")
    print(f"  Seed float   : {seed['seed_float']}")
    print(f"  A/B group    : {seed['uses']['ab_test_group']}")
    print(f"  Python use   : {seed['uses']['python_random']}")
    print(f"  NumPy use    : {seed['uses']['numpy']}")
    print(f"  API nonce    : {seed['uses']['api_nonce']}")

    # 2. Quantum password — always generate for vault; optionally display ───────
    length = args.length or 20
    pw = qe.random_password(length=length)
    if args.password or not args.decide:
        print("\n[ QUANTUM PASSWORD ]")
        print(f"  Password     : {pw['password']}")
        print(f"  Entropy      : {pw['entropy_bits']} bits  ({pw['strength']})")
        print(f"  Charset      : {pw['charset']} ({pw['charset_size']} chars)")

    # 3. Decision ────────────────────────────────────────────────────────────────
    if args.decide:
        options = [o.strip() for o in args.decide.split(",")]
        print(f"\n[ QUANTUM DECISION: {options} ]")
        d = qe.decide(options)
        print(f"  >>> Quantum chose: {d['chosen']} <<<")
        print(f"  From {d['n_options']} options, fair={d['fair']}")

    # 4. Quantum coin flip ───────────────────────────────────────────────────────
    print("\n[ QUANTUM COIN FLIP ]")
    coin = qe.decide(["Heads", "Tails"])
    print(f"  Result: {coin['chosen']}")

    # 5. Quantum dice ────────────────────────────────────────────────────────────
    print("\n[ QUANTUM DICE — 2d6 ]")
    dice = qe.dice(sides=6, n_dice=2)
    print(f"  Rolls: {dice['rolls']}  Total: {dice['total']}")

    # 6. Quick circuit health check ──────────────────────────────────────────────
    print("\n[ QUANTUM HEALTH CHECK ]")
    result = qe.run("bell_state", shots=256)
    counts = result["counts"]
    total  = sum(counts.values())
    ideal  = counts.get("00", 0) + counts.get("11", 0)
    fidelity_proxy = ideal / total
    print(f"  Bell state (256 shots): {counts}")
    print(f"  Fidelity proxy: {fidelity_proxy*100:.1f}%  ", end="")
    print("OK" if fidelity_proxy > 0.95 else "DEGRADED")

    # 7. Save to Obsidian ────────────────────────────────────────────────────────
    date_str = datetime.now().strftime("%Y-%m-%d")
    note_details = f"""## Daily Quantum Seed
- **Seed integer**: `{seed['seed_int']}`
- **Seed float**: `{seed['seed_float']}`
- **A/B group today**: `{seed['uses']['ab_test_group']}`
- **Python**: `{seed['uses']['python_random']}`
- **NumPy**: `{seed['uses']['numpy']}`
- **API nonce**: `{seed['uses']['api_nonce']}`

## Quantum-Generated Password
`{pw['password']}`
*(entropy: {pw['entropy_bits']} bits — {pw['strength']})*

## Quick Decisions
- **Coin flip**: {coin['chosen']}
- **Dice 2d6**: {dice['rolls']} = {dice['total']}

## Health Check
Bell state fidelity: {fidelity_proxy*100:.1f}% {'✓' if fidelity_proxy > 0.95 else '⚠️'}"""

    try:
        path = save_note(
            title=f"Quantum Daily — {date_str}",
            key_idea="Daily quantum random seed, password, and decisions",
            details=note_details,
            next_steps=[
                "Use seed in today's simulations or A/B tests",
                "Rotate password for any new account today",
            ],
            tags=["quantum", "daily", "random", "seed"],
            folder="inbox",
        )
        print(f"\n[ VAULT ] Saved to {path}")
    except Exception as e:
        print(f"\n[ VAULT ] Save failed: {e}")

    banner("Morning routine complete")
    return seed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quantum morning routine")
    parser.add_argument("--decide",   type=str, help="Comma-separated options to choose from")
    parser.add_argument("--password", action="store_true", help="Generate a quantum password")
    parser.add_argument("--length",   type=int, default=20, help="Password length")
    parser.add_argument("--ibm",      action="store_true", help="Use IBM hardware (slower)")
    args = parser.parse_args()
    run_morning(args)

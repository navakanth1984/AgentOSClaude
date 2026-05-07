"""
loop.py — AutoResearch orchestrator for vault capture prompt optimization.

Run this once and walk away. It will:
  1. Record a baseline score
  2. Ask Claude Sonnet to propose a prompt improvement
  3. Test it with Claude Haiku (fast + cheap)
  4. Commit improvements, revert regressions
  5. Repeat up to MAX_EXPERIMENTS times

Usage:
    python loop.py
    python loop.py --experiments 20  # run fewer experiments
    python loop.py --dry-run         # run baseline only, no modifications
"""

import argparse
import subprocess
import sys
import re
import anthropic
from evaluate import run_evaluation

MAX_EXPERIMENTS = 50
client = anthropic.Anthropic()


# ── Git helpers ────────────────────────────────────────────────────────────────

def git_init_if_needed():
    result = subprocess.run(["git", "status"], capture_output=True)
    if result.returncode != 0:
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", "program.md", "train.py", "evaluate.py",
                        "test_inputs.json", "loop.py"], check=True)
        subprocess.run(["git", "commit", "-m", "baseline: initial prompt"], check=True)
        print("Git repo initialized with baseline commit.")


import sys
PYTHON = sys.executable  # use same interpreter that launched this script


def git_commit(score: float, experiment_num: int):
    subprocess.run(["git", "add", "train.py"], check=True)
    subprocess.run([
        "git", "commit", "-m",
        f"autoresearch exp-{experiment_num:03d}: score {score:.1f}"
    ], check=True)


def git_revert():
    subprocess.run(["git", "checkout", "train.py"], check=True)


def git_log_summary() -> str:
    result = subprocess.run(
        ["git", "log", "--oneline", "-10"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


# ── Prompt proposal ────────────────────────────────────────────────────────────

def read_current_prompt() -> str:
    with open("train.py") as f:
        return f.read()


def read_program_md() -> str:
    with open("program.md") as f:
        return f.read()


def propose_modification(current_code: str, history: list[dict]) -> str:
    """Ask Claude Sonnet to propose ONE specific improvement to train.py."""

    history_lines = "\n".join([
        f"  exp-{h['n']:03d}: score {h['score']:.1f} — {h['action']} ({h['note']})"
        for h in history[-8:]
    ]) or "  (no history yet)"

    program = read_program_md()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        system="""You are an expert prompt engineer running an AutoResearch optimization loop.
Your job: propose ONE specific, targeted change to improve the system prompt in train.py.
Read the goal in program.md, review the experiment history, and make a deliberate hypothesis.

Rules:
- Return ONLY the complete modified train.py file — no explanation, no markdown fences
- Make exactly ONE change per experiment (don't rewrite everything at once)
- Use the history to avoid repeating failed approaches
- Try: different personas, few-shot examples, explicit format reminders, chain-of-thought, word count instructions
- The get_prompt(today) function signature must remain unchanged""",
        messages=[{
            "role": "user",
            "content": f"""## Goal (program.md)
{program}

## Current train.py
{current_code}

## Experiment History
{history_lines}

Propose your next experiment. Return only the complete train.py file."""
        }]
    )

    return response.content[0].text.strip()


def write_proposed_code(code: str):
    # Strip markdown fences if the model accidentally included them
    code = re.sub(r"^```python\n?", "", code)
    code = re.sub(r"\n?```$", "", code)
    with open("train.py", "w") as f:
        f.write(code)


# ── Main loop ──────────────────────────────────────────────────────────────────

def run_loop(max_experiments: int = MAX_EXPERIMENTS, dry_run: bool = False):
    git_init_if_needed()

    print("=" * 60)
    print("AutoResearch — Vault Capture Prompt Optimizer")
    print("=" * 60)
    print("\nRunning baseline evaluation...")

    baseline = run_evaluation(verbose=True)
    best_score = baseline
    history = []

    if dry_run:
        print("\n[dry-run] Baseline only. Exiting.")
        return

    print(f"\nBaseline: {baseline:.1f}/100")
    print(f"Starting {max_experiments} experiments...\n")

    for i in range(1, max_experiments + 1):
        print(f"\n{'─' * 50}")
        print(f"Experiment {i}/{max_experiments}  |  Best so far: {best_score:.1f}")

        current_code = read_current_prompt()

        try:
            proposed_code = propose_modification(current_code, history)
            write_proposed_code(proposed_code)
        except Exception as e:
            print(f"  Proposal failed: {e} — skipping")
            git_revert()
            continue

        try:
            score = run_evaluation(verbose=False)
        except Exception as e:
            print(f"  Evaluation failed: {e} — reverting")
            git_revert()
            continue

        if score > best_score:
            delta = score - best_score
            best_score = score
            git_commit(score, i)
            action = "COMMIT"
            note = f"+{delta:.1f} improvement"
            print(f"  {action}: {score:.1f}  ({note})")
        else:
            delta = score - best_score
            git_revert()
            action = "REVERT"
            note = f"{delta:.1f} vs best"
            print(f"  {action}: {score:.1f}  ({note})")

        history.append({"n": i, "score": score, "action": action, "note": note})

    print("\n" + "=" * 60)
    print(f"Done. Baseline: {baseline:.1f}  →  Best: {best_score:.1f}")
    print(f"Improvement: +{best_score - baseline:.1f} points")
    print("\nGit history of winning experiments:")
    print(git_log_summary())
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoResearch vault prompt optimizer")
    parser.add_argument("--experiments", type=int, default=MAX_EXPERIMENTS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run_loop(max_experiments=args.experiments, dry_run=args.dry_run)

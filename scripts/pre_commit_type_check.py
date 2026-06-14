import subprocess
import sys

# Sub-projects with their own venvs/deps cause missing-import noise.
# Only check syntax/logic errors in staged .py files instead.
SKIP_PROJECTS = {
    "AutoGrade_Backend", "dead_loop_trailer", "AutoGrade_Flutter",
    "capcut_pipeline", "clawglove_final",
}


def get_staged_py_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True,
    )
    files = [
        f for f in result.stdout.splitlines()
        if f.endswith(".py") and f.split("/")[0] not in SKIP_PROJECTS
    ]
    return files


def run_check():
    print(">>> Starting Pyrefly Type-Safety Pre-Commit Check...")

    staged = get_staged_py_files()
    if not staged:
        print("[PASS] No staged Python files to check.")
        return True

    print(f"Checking {len(staged)} staged file(s)...")
    cmd = ["pyrefly", "check"] + staged

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("[PASS] Type check passed!")
            return True
        else:
            print("[FAIL] Type check failed. Please fix the following errors before committing:")
            print("-" * 50)
            print(result.stdout)
            print("-" * 50)
            return False

    except FileNotFoundError:
        print("pyrefly not found — skipping type check. Install with: pip install pyrefly")
        return True


if __name__ == "__main__":
    if not run_check():
        sys.exit(1)

"""
adlc_pipeline.py — BLEUUBOARD Agentic Development Life Cycle Pipeline
Mirrors the pattern from agent_os/adlc_pipeline.py, scoped to whiteboard-4d.

Environments:
  non-prod (staging)  -> bleuboard-dev.vercel.app   (permanent alias, updated on every stage)
  prod                -> bleuboard.vercel.app        (only promoted after smoke test passes)

Branches:
  bleuuboard-dev  -> work-in-progress, maps to staging
  master          -> production-ready, maps to prod

Usage:
  python adlc_pipeline.py stage          # deploy to staging + pin bleuboard-dev.vercel.app
  python adlc_pipeline.py promote        # run smoke test -> if pass, deploy to prod
  python adlc_pipeline.py status         # show last CI run
  python adlc_pipeline.py deploy         # stage + smoke + promote in one shot
"""

import sys
import os
import re
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

WORK_DIR = Path(__file__).parent
CI_LOG = WORK_DIR / "adlc_ci.json"
HTML_FILE = WORK_DIR / "index.html"

# On Windows, npm scripts are .cmd wrappers — use vercel.cmd directly
VERCEL_CMD = "vercel.cmd" if sys.platform == "win32" else "vercel"

STAGING_ALIAS = "bleuboard-dev.vercel.app"
PROD_ALIAS    = "bleuboard.vercel.app"


# ── Helpers ──────────────────────────────────────────────────────────────────

def run(args: list[str], timeout: int = 120) -> tuple[int, str, str]:
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=WORK_DIR, shell=(sys.platform == "win32"))
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Timed out after {timeout}s"
    except Exception as e:
        return -2, "", str(e)


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[ADLC {ts}] {msg}")


def write_ci_log(entry: dict):
    history = []
    if CI_LOG.exists():
        try:
            history = json.loads(CI_LOG.read_text())
        except Exception:
            history = []
    history.insert(0, entry)
    CI_LOG.write_text(json.dumps(history[:20], indent=2))  # keep last 20 runs


# ── Smoke Test ───────────────────────────────────────────────────────────────

def smoke_test() -> tuple[bool, str]:
    """
    Quick local smoke test on index.html before promoting to prod.
    Checks:
      1. File exists and is non-empty
      2. No obvious syntax errors (unclosed script tags, missing </html>)
      3. Key BLEUUBOARD identifiers are present
      4. WebGL renderer is wrapped in try-catch (the bug we fixed)
    """
    log("Running smoke test on index.html...")

    if not HTML_FILE.exists():
        return False, "index.html not found"

    html = HTML_FILE.read_text(encoding="utf-8")

    checks = [
        ("File non-empty", len(html) > 10_000),
        ("Closing </html> tag", "</html>" in html.lower()),
        ("BLEUUBOARD title present", "BLEUUBOARD" in html),
        ("WebGL try-catch guard", "try {" in html and "WebGLRenderer" in html),
        ("Guide Next button exists", "guide-next" in html),
        ("Draw suggest popup exists", "draw-suggest" in html),
        ("showSuggest uses offsetWidth", "offsetWidth" in html),
        ("No unclosed <script>", html.count("<script") == html.count("</script>")),
    ]

    failures = [name for name, passed in checks if not passed]

    if failures:
        return False, f"Smoke test FAILED — checks failed: {', '.join(failures)}"

    passed_count = len(checks)
    return True, f"Smoke test PASSED — {passed_count}/{passed_count} checks"


# ── Vercel Deploy ─────────────────────────────────────────────────────────────

def deploy_staging() -> tuple[bool, str]:
    log("Deploying to staging (Vercel preview)...")
    code, stdout, stderr = run([VERCEL_CMD, "--yes"], timeout=120)
    combined = stdout + stderr
    url_match = re.search(r"https://\S+\.vercel\.app", combined)
    url = url_match.group(0) if url_match else "(no URL found)"
    if code == 0:
        log(f"Staging deployed -> {url}")
        # Pin the permanent non-prod alias to this deploy
        a_code, a_out, a_err = run([VERCEL_CMD, "alias", "set", url, STAGING_ALIAS], timeout=30)
        if a_code == 0:
            log(f"Staging alias updated -> https://{STAGING_ALIAS}")
        else:
            log(f"Warning: alias update failed: {(a_out+a_err)[:120]}")
        return True, url
    else:
        log(f"Staging deploy FAILED: {combined[:300]}")
        return False, combined[:300]


def deploy_prod() -> tuple[bool, str]:
    log("Deploying to PRODUCTION (vercel --prod)...")
    code, stdout, stderr = run([VERCEL_CMD, "--prod", "--yes"], timeout=120)
    combined = stdout + stderr
    url_match = re.search(r"https://\S+\.vercel\.app", combined)
    url = url_match.group(0) if url_match else "(no URL found)"
    if code == 0:
        log(f"Production deployed -> {url}")
        return True, url
    else:
        log(f"Prod deploy FAILED: {combined[:300]}")
        return False, combined[:300]


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_stage():
    ok, result = deploy_staging()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": "stage",
        "status": "PASS" if ok else "FAIL",
        "detail": result,
    }
    write_ci_log(entry)
    return 0 if ok else 1


def cmd_promote():
    smoke_ok, smoke_msg = smoke_test()
    log(smoke_msg)
    if not smoke_ok:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "promote",
            "status": "FAIL",
            "detail": smoke_msg,
        }
        write_ci_log(entry)
        return 1

    prod_ok, prod_url = deploy_prod()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": "promote",
        "status": "PASS" if prod_ok else "FAIL",
        "detail": prod_url,
    }
    write_ci_log(entry)
    return 0 if prod_ok else 1


def cmd_deploy():
    """Full ADLC loop: stage -> smoke -> promote."""
    log("=== BLEUUBOARD ADLC FULL DEPLOY ===")

    # Stage
    stage_ok, stage_url = deploy_staging()
    if not stage_ok:
        log("Aborting — staging deploy failed.")
        return 1
    log(f"Staging OK: {stage_url}")
    time.sleep(2)

    # Smoke test
    smoke_ok, smoke_msg = smoke_test()
    log(smoke_msg)
    if not smoke_ok:
        log("Aborting — smoke test failed. Prod NOT updated.")
        return 1

    # Promote to prod
    prod_ok, prod_url = deploy_prod()
    status = "PASS" if prod_ok else "FAIL"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": "deploy",
        "status": status,
        "staging_url": stage_url,
        "prod_url": prod_url,
        "smoke": smoke_msg,
    }
    write_ci_log(entry)
    log(f"=== ADLC COMPLETE — {status} ===")
    if prod_ok:
        log(f"Live at: {prod_url}")
    return 0 if prod_ok else 1


def cmd_status():
    if not CI_LOG.exists():
        print("No CI runs yet. Run: python adlc_pipeline.py deploy")
        return 0
    history = json.loads(CI_LOG.read_text())
    print(f"\n{'─'*60}")
    print(f"  BLEUUBOARD ADLC — Last {min(5, len(history))} runs")
    print(f"{'─'*60}")
    for r in history[:5]:
        status_icon = "✓" if r["status"] == "PASS" else "✗"
        ts = r["timestamp"][:16].replace("T", " ")
        print(f"  {status_icon} [{ts}] {r['action']:10}  {r['status']:4}  {r.get('prod_url', r.get('detail', ''))[:50]}")
    print(f"{'─'*60}\n")
    return 0


# ── Entry ─────────────────────────────────────────────────────────────────────

COMMANDS = {
    "stage": cmd_stage,
    "promote": cmd_promote,
    "deploy": cmd_deploy,
    "status": cmd_status,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "deploy"
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Usage: python adlc_pipeline.py [{' | '.join(COMMANDS)}]")
        sys.exit(1)
    sys.exit(COMMANDS[cmd]())

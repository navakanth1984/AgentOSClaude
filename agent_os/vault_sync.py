"""
vault_sync.py — Git-based Vault Synchronization for Cloud Deployment

When Agent OS runs in Cloud Run (or any remote environment), this module
syncs the Obsidian vault via Git instead of relying on an ngrok tunnel.

Flow:
  1. On startup: git clone the vault repo (shallow, sparse)
  2. Before reads: git pull (with rate-limiting to avoid hammering GitHub)
  3. After writes: git add + commit + push

Environment variables:
  VAULT_REPO_URL   — e.g. https://token@github.com/user/repo.git
  VAULT_REPO_PATH  — local clone path (default: /app/vault_clone)
  VAULT_SUBDIR     — subdirectory within the repo containing the vault
                     (default: obsidian-vault/Obsidian Vault)
  VAULT_SYNC_INTERVAL — minimum seconds between git pulls (default: 60)
"""

import os
import subprocess
import time
import threading
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────
VAULT_REPO_URL = os.environ.get("VAULT_REPO_URL", "")
VAULT_REPO_PATH = Path(os.environ.get("VAULT_REPO_PATH", "/app/vault_clone"))
VAULT_SUBDIR = os.environ.get("VAULT_SUBDIR", "obsidian-vault/Obsidian Vault")
SYNC_INTERVAL = int(os.environ.get("VAULT_SYNC_INTERVAL", "60"))

_last_pull_time = 0
_sync_lock = threading.Lock()


def is_cloud_mode() -> bool:
    """Returns True if running in cloud mode (VAULT_REPO_URL is set)."""
    return bool(VAULT_REPO_URL)


def get_vault_path() -> Path:
    """Returns the effective vault path — cloud clone or local Windows path."""
    if is_cloud_mode():
        return VAULT_REPO_PATH / VAULT_SUBDIR
    # Local mode: return the hardcoded Windows path
    return Path(r"C:\Users\navka\navakanth001\obsidian-vault\Obsidian Vault")


def _run_git(*args, cwd=None) -> subprocess.CompletedProcess:
    """Run a git command and return the result."""
    cmd = ["git"] + list(args)
    return subprocess.run(
        cmd,
        cwd=str(cwd or VAULT_REPO_PATH),
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )


def initial_clone():
    """
    Clone the vault repo on first startup.
    Uses shallow clone + sparse checkout to minimize bandwidth.
    """
    if not is_cloud_mode():
        return

    if (VAULT_REPO_PATH / ".git").exists():
        print("[VaultSync] Repo already cloned, pulling latest...")
        pull()
        return

    print(f"[VaultSync] Cloning vault repo to {VAULT_REPO_PATH}...")
    VAULT_REPO_PATH.mkdir(parents=True, exist_ok=True)

    # Shallow clone with depth 1
    result = _run_git(
        "clone",
        "--depth", "1",
        "--filter=blob:none",
        "--sparse",
        VAULT_REPO_URL,
        str(VAULT_REPO_PATH),
        cwd="/app",
    )

    if result.returncode != 0:
        print(f"[VaultSync] Clone failed: {result.stderr}")
        # Fallback: full shallow clone
        result = _run_git(
            "clone", "--depth", "1",
            VAULT_REPO_URL, str(VAULT_REPO_PATH),
            cwd="/app",
        )
        if result.returncode != 0:
            print(f"[VaultSync] FATAL: Clone failed: {result.stderr}")
            return

    # Set sparse checkout to only pull vault + agent_os directories
    _run_git("sparse-checkout", "set", "obsidian-vault", "agent_os")

    # Configure git for commits from cloud
    _run_git("config", "user.email", "agent-os@cloud.run")
    _run_git("config", "user.name", "Agent OS Cloud")

    vault_path = get_vault_path()
    if vault_path.exists():
        note_count = len(list(vault_path.rglob("*.md")))
        print(f"[VaultSync] Clone complete. Vault has {note_count} notes.")
    else:
        print(f"[VaultSync] WARNING: Vault subdir not found at {vault_path}")


def pull():
    """
    Pull latest changes from the remote repo.
    Rate-limited to SYNC_INTERVAL seconds between pulls.
    """
    global _last_pull_time

    if not is_cloud_mode():
        return

    now = time.time()
    if now - _last_pull_time < SYNC_INTERVAL:
        return  # Too soon, skip

    with _sync_lock:
        # Double-check after acquiring lock
        if time.time() - _last_pull_time < SYNC_INTERVAL:
            return

        result = _run_git("pull", "--rebase", "--autostash")
        _last_pull_time = time.time()

        if result.returncode != 0:
            print(f"[VaultSync] Pull failed: {result.stderr}")
        else:
            if "Already up to date" not in result.stdout:
                print(f"[VaultSync] Pulled new changes: {result.stdout.strip()}")


def commit_and_push(file_path: str, message: str = "Agent OS: auto-save note"):
    """
    Stage a file, commit, and push to remote.
    Called after saving a note from the cloud server.
    """
    if not is_cloud_mode():
        return

    with _sync_lock:
        try:
            # Make path relative to repo root
            rel_path = os.path.relpath(file_path, VAULT_REPO_PATH)

            _run_git("add", rel_path)

            result = _run_git("commit", "-m", message)
            if result.returncode != 0:
                if "nothing to commit" in result.stdout:
                    return  # No changes
                print(f"[VaultSync] Commit failed: {result.stderr}")
                return

            result = _run_git("push")
            if result.returncode != 0:
                print(f"[VaultSync] Push failed: {result.stderr}")
                # Try pull-rebase then push
                _run_git("pull", "--rebase", "--autostash")
                _run_git("push")

            print(f"[VaultSync] Pushed: {rel_path}")
        except Exception as e:
            print(f"[VaultSync] Error: {e}")


def start_background_sync(interval: int = 300):
    """
    Start a background thread that periodically pulls changes.
    Default: every 5 minutes.
    """
    if not is_cloud_mode():
        return

    def _sync_loop():
        while True:
            time.sleep(interval)
            try:
                pull()
            except Exception as e:
                print(f"[VaultSync] Background sync error: {e}")

    t = threading.Thread(target=_sync_loop, daemon=True)
    t.start()
    print(f"[VaultSync] Background sync started (every {interval}s)")

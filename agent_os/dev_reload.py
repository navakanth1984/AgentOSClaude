"""
dev_reload.py — Auto-reloading supervisor for the Agent OS server.

Watches every *.py file under agent_os/ and restarts server.py automatically
whenever one changes, so backend edits (like the creative_pipeline long-form
fixes) take effect without a manual restart.

Zero dependencies — pure stdlib mtime polling. Run it INSTEAD of `python server.py`:

    python dev_reload.py

Stop with Ctrl+C. The child server is terminated cleanly on exit and on reload.
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

HERE = Path(__file__).parent.resolve()
SERVER = HERE / "server.py"
POLL_SECONDS = 1.0
DEBOUNCE_SECONDS = 0.4  # wait for a burst of saves to settle before restarting

# Directories under agent_os/ we don't care about (noise / generated files).
_IGNORE_DIRS = {"__pycache__", ".git", "scratch", "worktrees", ".graphify"}


def _snapshot() -> dict[str, float]:
    """Map every watched .py file → its last-modified time."""
    snap: dict[str, float] = {}
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in _IGNORE_DIRS]
        for f in files:
            if f.endswith(".py"):
                p = os.path.join(root, f)
                try:
                    snap[p] = os.path.getmtime(p)
                except OSError:
                    pass
    return snap


def _start() -> subprocess.Popen:
    print(f"[dev-reload] starting: {sys.executable} server.py", flush=True)
    # On Windows a fresh process group lets us signal the child without hitting
    # this supervisor. CREATE_NEW_PROCESS_GROUP is Windows-only (0 elsewhere).
    creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    return subprocess.Popen(
        [sys.executable, str(SERVER)], cwd=str(HERE), creationflags=creationflags
    )


def _stop(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def _changed(old: dict[str, float], new: dict[str, float]) -> list[str]:
    changed = []
    for p, m in new.items():
        if old.get(p) != m:
            changed.append(p)
    for p in old:
        if p not in new:
            changed.append(p)
    return changed


def main() -> None:
    print("[dev-reload] watching agent_os/**/*.py — edit & save to auto-restart. Ctrl+C to quit.", flush=True)
    proc = _start()
    watched = _snapshot()

    def _shutdown(*_):
        print("\n[dev-reload] shutting down…", flush=True)
        _stop(proc)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        while True:
            time.sleep(POLL_SECONDS)

            # If the server died on its own (crash / syntax error), relaunch it.
            if proc.poll() is not None:
                print(f"[dev-reload] server exited (code {proc.returncode}) — relaunching…", flush=True)
                proc = _start()
                watched = _snapshot()
                continue

            current = _snapshot()
            hits = _changed(watched, current)
            if hits:
                # Debounce: let a save-burst settle, then take a final snapshot.
                time.sleep(DEBOUNCE_SECONDS)
                current = _snapshot()
                names = ", ".join(Path(h).name for h in hits[:5])
                extra = f" (+{len(hits) - 5} more)" if len(hits) > 5 else ""
                print(f"[dev-reload] change detected: {names}{extra} — restarting server.", flush=True)
                _stop(proc)
                proc = _start()
                watched = current
    except KeyboardInterrupt:
        _shutdown()


if __name__ == "__main__":
    main()

"""Central tunables. Imported by the Auditor wiring (runner.py, loop.py)."""
import os

from policy import STRICT, GatePolicy

DEFAULT_POLICY: GatePolicy = STRICT  # threshold is an experimental variable; STRICT is the safe default
MODEL_NAME = "gemini-2.5-flash"      # Tier 1/2 per model-economics rule


def gate_key() -> bytes:
    # Stable per-machine dev key; override via env for real runs.
    return os.environ.get("MVCT_GATE_KEY", "dev-only-gate-key").encode()

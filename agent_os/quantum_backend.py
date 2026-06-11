"""
quantum_backend.py
==================
Smart quantum backend switcher — stays on free tiers, never pays.

Priority order (tried in sequence, first available wins):
  1. AerSimulator  — local Qiskit simulator, always free, always available
  2. IBM Quantum   — real QPU, free Open Plan: 10 min/month
  3. Classical     — secrets.token_bytes() CSPRNG, zero quantum advantage but safe fallback

Usage tracking:
  - IBM QPU time is logged to agent_os/quantum_usage.json
  - Monthly counter resets automatically on the 1st of each month
  - When IBM budget < SAFETY_MARGIN seconds remaining → skip IBM, use classical

IBM token source (in priority order):
  1. Environment variable: IBM_QUANTUM_TOKEN
  2. .env file in agent_os/
  3. Not available → skip IBM entirely

This module replaces direct QuantumEngine calls in quantum_walk.py.
All other code should import get_random_bits() from here.
"""

import json
import os
import secrets
import time
import pathlib
from datetime import datetime, timezone

# ── Constants ─────────────────────────────────────────────────────────────────
_HERE          = pathlib.Path(__file__).parent.resolve()
_USAGE_FILE    = _HERE / "quantum_usage.json"

IBM_FREE_SECONDS_PER_MONTH = 600      # 10 minutes
SAFETY_MARGIN_SECONDS      = 30       # keep this buffer unused (queue overhead)
AERSIM_QUBIT_CAP           = 127      # AerSimulator hard limit

# ── Usage ledger ──────────────────────────────────────────────────────────────

def _load_usage() -> dict:
    """Load usage ledger from disk. Returns fresh ledger if missing or corrupt."""
    if _USAGE_FILE.exists():
        try:
            data = json.loads(_USAGE_FILE.read_text(encoding="utf-8"))
            # Reset if it's a new month
            now = datetime.now(timezone.utc)
            if data.get("month") != now.strftime("%Y-%m"):
                return _fresh_ledger()
            return data
        except Exception:
            pass
    return _fresh_ledger()


def _fresh_ledger() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "month":              now.strftime("%Y-%m"),
        "ibm_seconds_used":   0.0,
        "ibm_calls":          0,
        "aer_calls":          0,
        "classical_calls":    0,
        "last_updated":       now.isoformat(),
        "log":                [],
    }


def _save_usage(ledger: dict):
    ledger["last_updated"] = datetime.now(timezone.utc).isoformat()
    try:
        _USAGE_FILE.write_text(
            json.dumps(ledger, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except Exception:
        pass


def _ibm_budget_remaining(ledger: dict) -> float:
    """Seconds of IBM free tier remaining this month."""
    return IBM_FREE_SECONDS_PER_MONTH - ledger.get("ibm_seconds_used", 0.0)


# ── IBM token discovery ────────────────────────────────────────────────────────

def _find_ibm_token() -> str | None:
    """
    Find IBM Quantum token from environment or .env file.
    Never hardcoded — credentials stay out of source code.
    """
    # 1. Environment variable
    tok = os.environ.get("IBM_QUANTUM_TOKEN", "").strip()
    if tok:
        return tok

    # 2. Check .env in agent_os/ and project root
    for folder in [_HERE, _HERE.parent]:
        env_file = folder / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("IBM_QUANTUM_TOKEN="):
                    tok = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if tok:
                        return tok

    return None


# ── AerSimulator backend ───────────────────────────────────────────────────────

def _aer_random_bits(n_bits: int) -> tuple[str, str]:
    """
    Generate n_bits random bits via AerSimulator.
    Returns (bitstring, backend_name).
    Caps at AERSIM_QUBIT_CAP per call — caller handles chunking.
    """
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    n = min(n_bits, AERSIM_QUBIT_CAP)
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))

    sim = AerSimulator()
    counts = sim.run(qc, shots=1).result().get_counts()
    bitstr = list(counts.keys())[0].replace(" ", "")
    return bitstr, "AerSimulator"


# ── IBM Quantum backend ────────────────────────────────────────────────────────

def _ibm_random_bits(n_bits: int, token: str | None) -> tuple[str, str, float]:
    """
    Generate n_bits random bits via IBM Quantum QPU.
    If no token is provided, simulates a noisy IBM backend locally.
    Returns (bitstring, backend_name, elapsed_seconds).
    """
    from qiskit import QuantumCircuit
    n = min(n_bits, 127)
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))

    if token:
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
        backend = service.least_busy(operational=True, simulator=False,
                                     min_num_qubits=n)
        pm      = generate_preset_pass_manager(backend=backend, optimization_level=1)
        isa_qc  = pm.run(qc)
        sampler = Sampler(mode=backend)

        t0  = time.perf_counter()
        job = sampler.run([isa_qc], shots=1)
        res = job.result()
        elapsed = time.perf_counter() - t0

        counts = res[0].data.c.get_counts()
        bitstr = list(counts.keys())[0].replace(" ", "")
        return bitstr, backend.name, elapsed
    else:
        # Noisy fake IBM simulator fallback - chunked to max 5 qubits to prevent memory explosion
        import math
        import random as _rand
        from qiskit.providers.fake_provider import GenericBackendV2
        
        sim_qubits = min(5, n_bits) if n_bits > 0 else 1
        qc_sim = QuantumCircuit(sim_qubits, sim_qubits)
        qc_sim.h(range(sim_qubits))
        qc_sim.measure(range(sim_qubits), range(sim_qubits))
        
        fake_backend = GenericBackendV2(num_qubits=max(2, sim_qubits))
        t0 = time.perf_counter()
        
        needed_shots = max(1, math.ceil(n_bits / sim_qubits))
        job = fake_backend.run(qc_sim, shots=needed_shots)
        res = job.result()
        elapsed = time.perf_counter() - t0
        
        counts = res.get_counts()
        bitstrings = []
        for bitstr, count in counts.items():
            bitstrings.extend([bitstr.replace(" ", "")] * count)
        
        _rand.shuffle(bitstrings)
        combined_bits = "".join(bitstrings)[:n_bits]
        combined_bits = combined_bits.ljust(n_bits, "0")
        
        return combined_bits, f"fake_{fake_backend.name}", elapsed


# ── Classical CSPRNG fallback ──────────────────────────────────────────────────

def _classical_random_bits(n_bits: int) -> tuple[str, str]:
    """
    Generate n_bits from OS CSPRNG (secrets module).
    No quantum advantage — but cryptographically secure and always available.
    """
    n_bytes = (n_bits + 7) // 8
    raw     = secrets.token_bytes(n_bytes)
    bitstr  = bin(int.from_bytes(raw, "big"))[2:].zfill(n_bytes * 8)[:n_bits]
    return bitstr, "classical_CSPRNG"


# ── Public API ─────────────────────────────────────────────────────────────────

def get_random_bits(n_bits: int = 96) -> dict:
    """
    Get n_bits random bits from the best available free-tier backend.

    Returns:
        {
          "bits":     "01101...",
          "n_bits":   96,
          "backend":  "AerSimulator" | "IBM:<device>" | "classical_CSPRNG",
          "source":   "quantum" | "quantum_hardware" | "classical",
          "ibm_seconds_used_this_month": 42.3,
          "ibm_budget_remaining":        557.7,
        }
    """
    ledger = _load_usage()
    reason = ""
    pref = os.environ.get("QUANTUM_BACKEND_PREFERENCE", "").lower()

    # If IBM is preferred, try it first (real QPU if token exists, otherwise fake noisy IBM simulator)
    if pref == "ibm" or pref == "fake_ibm":
        token = _find_ibm_token()
        remaining = _ibm_budget_remaining(ledger)
        if token and remaining <= SAFETY_MARGIN_SECONDS:
            reason += f"IBM budget exhausted ({remaining:.1f}s remaining < {SAFETY_MARGIN_SECONDS}s margin) | "
        else:
            try:
                bits, backend_name, elapsed = _ibm_random_bits(n_bits, token)
                if token:
                    ledger["ibm_seconds_used"] += elapsed
                    ledger["ibm_calls"]        += 1
                else:
                    ledger["aer_calls"]        += 1  # count under Aer/simulation calls
                ledger["log"].append({
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "backend": backend_name, "n_bits": n_bits,
                    "elapsed_s": round(elapsed, 3) if token else 0.0,
                })
                _save_usage(ledger)
                return {
                    "bits":    bits,
                    "n_bits":  n_bits,
                    "backend": f"IBM:{backend_name}" if token else f"fake_ibm:{backend_name}",
                    "source":  "quantum_hardware" if token else "quantum_simulation",
                    "ibm_seconds_used_this_month": ledger["ibm_seconds_used"],
                    "ibm_budget_remaining":        _ibm_budget_remaining(ledger),
                }
            except Exception as e:
                reason += f"IBM preferred but failed: {e} | "

    # ── Backend 1: AerSimulator ────────────────────────────────────────────────
    try:
        bits, backend_name = _aer_random_bits(n_bits)
        ledger["aer_calls"] += 1
        ledger["log"].append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "backend": "AerSimulator", "n_bits": n_bits,
        })
        _save_usage(ledger)
        return {
            "bits":    bits,
            "n_bits":  n_bits,
            "backend": "AerSimulator",
            "source":  "quantum",
            "ibm_seconds_used_this_month": ledger["ibm_seconds_used"],
            "ibm_budget_remaining":        _ibm_budget_remaining(ledger),
        }
    except Exception as e:
        reason += f"AerSimulator failed: {e} | "

    # ── Backend 2: IBM Quantum free tier (if not already tried) ────────────────
    if pref != "ibm" and pref != "fake_ibm":
        token = _find_ibm_token()
        remaining = _ibm_budget_remaining(ledger)

        if token and remaining > SAFETY_MARGIN_SECONDS:
            try:
                bits, backend_name, elapsed = _ibm_random_bits(n_bits, token)
                ledger["ibm_seconds_used"] += elapsed
                ledger["ibm_calls"]        += 1
                ledger["log"].append({
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "backend": backend_name, "n_bits": n_bits,
                    "elapsed_s": round(elapsed, 3),
                })
                _save_usage(ledger)
                return {
                    "bits":    bits,
                    "n_bits":  n_bits,
                    "backend": f"IBM:{backend_name}",
                    "source":  "quantum_hardware",
                    "ibm_seconds_used_this_month": ledger["ibm_seconds_used"],
                    "ibm_budget_remaining":        _ibm_budget_remaining(ledger),
                }
            except Exception as e:
                reason += f"IBM failed: {e} | "
        elif not token:
            reason += "IBM token not set | "
        else:
            reason += f"IBM budget exhausted ({remaining:.1f}s remaining < {SAFETY_MARGIN_SECONDS}s margin) | "

    # ── Backend 3: Classical CSPRNG fallback ───────────────────────────────────
    bits, backend_name = _classical_random_bits(n_bits)
    ledger["classical_calls"] += 1
    ledger["log"].append({
        "ts": datetime.now(timezone.utc).isoformat(),
        "backend": "classical_CSPRNG", "n_bits": n_bits,
        "reason": reason,
    })
    _save_usage(ledger)
    return {
        "bits":    bits,
        "n_bits":  n_bits,
        "backend": "classical_CSPRNG",
        "source":  "classical",
        "fallback_reason": reason,
        "ibm_seconds_used_this_month": ledger["ibm_seconds_used"],
        "ibm_budget_remaining":        _ibm_budget_remaining(ledger),
    }


def usage_report() -> dict:
    """Return current month's usage stats across all backends."""
    ledger = _load_usage()
    ibm_remaining = _ibm_budget_remaining(ledger)
    total_calls = (ledger["aer_calls"] +
                   ledger["ibm_calls"] +
                   ledger["classical_calls"])
    return {
        "month":                   ledger["month"],
        "total_calls":             total_calls,
        "aer_calls":               ledger["aer_calls"],
        "ibm_calls":               ledger["ibm_calls"],
        "classical_calls":         ledger["classical_calls"],
        "ibm_seconds_used":        round(ledger["ibm_seconds_used"], 2),
        "ibm_seconds_remaining":   round(ibm_remaining, 2),
        "ibm_pct_used":            round(
            ledger["ibm_seconds_used"] / IBM_FREE_SECONDS_PER_MONTH * 100, 1
        ),
        "primary_backend":         (
            "AerSimulator" if ledger["aer_calls"] >= ledger["ibm_calls"]
            else "IBM Quantum"
        ),
        "last_updated":            ledger.get("last_updated", "never"),
    }

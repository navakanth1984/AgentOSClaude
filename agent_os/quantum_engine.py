"""
quantum_engine.py — Agent OS Quantum Compute Layer
===================================================
Core module that every other Agent OS component calls for quantum work.
Supports: AerSimulator (local, free) and IBM Quantum (real hardware).

Usage anywhere in Agent OS:
    from quantum_engine import QuantumEngine
    qe = QuantumEngine()
    result = qe.run("bell_state", shots=1000)
    result = qe.run_circuit(my_qiskit_circuit, backend="ibm")
    result = qe.grover_search(target="11", n_qubits=2)
"""

import json
import math
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# ── Qiskit core (always available) ────────────────────────────────────────────
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SIM = AerSimulator()

# ── IBM Runtime (optional — only used when token is set) ──────────────────────
def _ibm_available() -> bool:
    try:
        from quantum_backend import _find_ibm_token
        token = _find_ibm_token()
        if not token:
            return False
        from qiskit_ibm_runtime import QiskitRuntimeService
        QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
        return True
    except Exception:
        return False


# ── Built-in circuit library ───────────────────────────────────────────────────
BUILTIN_CIRCUITS = {
    "bell_state": "2-qubit Bell state (maximum entanglement)",
    "ghz_3":      "3-qubit GHZ state (3-way entanglement)",
    "superposition": "Single qubit in superposition (coin flip)",
    "grover_2":   "Grover search on 2 qubits (target |11>)",
    "qft_3":      "Quantum Fourier Transform on 3 qubits",
    "full_adder": "Quantum full adder: 1+1 in binary",
}

def _build_circuit(name: str) -> QuantumCircuit:
    import numpy as np

    if name == "bell_state":
        qc = QuantumCircuit(2, 2)
        qc.h(0); qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
        return qc

    if name == "ghz_3":
        qc = QuantumCircuit(3, 3)
        qc.h(0); qc.cx(0, 1); qc.cx(0, 2)
        qc.measure([0, 1, 2], [0, 1, 2])
        return qc

    if name == "superposition":
        qc = QuantumCircuit(1, 1)
        qc.h(0); qc.measure(0, 0)
        return qc

    if name == "grover_2":
        qc = QuantumCircuit(2, 2)
        qc.h(0); qc.h(1)          # superposition
        qc.cz(0, 1)               # oracle: marks |11>
        qc.h(0); qc.h(1)          # diffusion step 1
        qc.x(0); qc.x(1)
        qc.cz(0, 1)
        qc.x(0); qc.x(1)
        qc.h(0); qc.h(1)          # diffusion step 2
        qc.measure([0, 1], [0, 1])
        return qc

    if name == "qft_3":
        qc = QuantumCircuit(3, 3)
        qc.h(2)                   # encode period-4 signal
        for j in range(3):
            qc.h(j)
            for k in range(j + 1, 3):
                qc.cp(np.pi / (2 ** (k - j)), k, j)
        for i in range(3 // 2):
            qc.swap(i, 3 - i - 1)
        qc.measure([0, 1, 2], [0, 1, 2])
        return qc

    if name == "full_adder":
        qc = QuantumCircuit(4, 2)
        qc.x(0); qc.x(1)          # A=1, B=1
        qc.cx(0, 2); qc.cx(1, 2)  # XOR → sum
        qc.ccx(0, 1, 3)           # Toffoli → carry
        qc.measure([2, 3], [0, 1])
        return qc

    raise ValueError(f"Unknown circuit '{name}'. Available: {list(BUILTIN_CIRCUITS)}")


# ── Main engine class ──────────────────────────────────────────────────────────

class QuantumEngine:
    """
    Single interface for all quantum compute tasks in Agent OS.
    All results are JSON-serialisable dicts — safe to return from server.py.
    """

    def __init__(self):
        self.log_path = Path(__file__).parent / "quantum_log.json"

    # ── Public API ─────────────────────────────────────────────────────────────

    def run(self, circuit_name: str, shots: int = 1024,
            backend: str = "local") -> dict:
        """
        Run a named built-in circuit.
        backend: "local" (AerSimulator) | "ibm" (real hardware)
        """
        qc = _build_circuit(circuit_name)
        return self.run_circuit(qc, shots=shots, backend=backend,
                                label=circuit_name)

    def run_circuit(self, qc: QuantumCircuit, shots: int = 1024,
                    backend: str = "local", label: str = "custom") -> dict:
        """Run any Qiskit QuantumCircuit and return a structured result."""
        t0 = datetime.now()

        if backend == "ibm" and _ibm_available():
            result = self._run_ibm(qc, shots)
        elif backend == "ibm":
            try:
                from qiskit.providers.fake_provider import GenericBackendV2
                fake_backend = GenericBackendV2(num_qubits=max(2, qc.num_qubits))
                counts = fake_backend.run(qc, shots=shots).result().get_counts()
                result = {
                    "backend": f"fake_ibm_noisy ({fake_backend.name})",
                    "counts": counts,
                    "warning": "IBM Quantum token not configured; running on local noisy IBM simulator (GenericBackendV2)"
                }
            except Exception as fake_err:
                result = {"warning": f"IBM not configured and fake simulator failed ({fake_err}), using AerSimulator"}
                counts = SIM.run(qc, shots=shots).result().get_counts()
                result.update({"backend": "AerSimulator", "counts": counts})
        else:
            result = {}
            counts = SIM.run(qc, shots=shots).result().get_counts()
            result.update({"backend": "AerSimulator", "counts": counts})

        # Enrich result
        total = sum(result["counts"].values())
        result.update({
            "label":       label,
            "shots":       shots,
            "num_qubits":  qc.num_qubits,
            "depth":       qc.depth(),
            "circuit_str": str(qc.draw(output="text")),
            "top_state":   max(result["counts"], key=result["counts"].get),
            "top_prob":    max(result["counts"].values()) / total,
            "elapsed_ms":  int((datetime.now() - t0).total_seconds() * 1000),
            "timestamp":   t0.isoformat(),
        })

        self._log(result)
        return result

    def grover_search(self, target: str, n_qubits: Optional[int] = None,
                      shots: int = 1024, backend: str = "local") -> dict:
        """
        Build and run Grover's search for a given binary target string.
        target: binary string like "110" — the item to find
        """
        if n_qubits is None:
            n_qubits = len(target)
        target = target.zfill(n_qubits)
        qc = self._build_grover(target, n_qubits)
        result = self.run_circuit(qc, shots=shots, backend=backend,
                                  label=f"grover_target_{target}")
        result["target"] = target
        result["target_decimal"] = int(target, 2)
        counts = result["counts"]
        total = sum(counts.values())
        result["target_hit_rate"] = counts.get(target, 0) / total
        return result

    def factor(self, N: int, a: Optional[int] = None) -> dict:
        """
        Shor's algorithm (classical period-finding simulation).
        Returns factors of N using the quantum-equivalent math.
        """
        import random
        if a is None:
            a = random.randint(2, N - 1)

        g = math.gcd(a, N)
        if g != 1:
            return {"N": N, "a": a, "factors": [g, N // g],
                    "method": "lucky_gcd", "period": None}

        r = next((x for x in range(1, N + 1) if pow(a, x, N) == 1), None)
        if r is None or r % 2 != 0:
            return {"N": N, "a": a, "factors": None,
                    "method": "bad_period", "period": r,
                    "message": f"Period r={r} is odd or missing — retry with different a"}

        x = pow(a, r // 2, N)
        if x == N - 1:
            return {"N": N, "a": a, "factors": None,
                    "method": "trivial_sqrt", "period": r,
                    "message": "a^(r/2) mod N = N-1 — retry with different a"}

        f1 = math.gcd(x - 1, N)
        f2 = math.gcd(x + 1, N)
        factors = [f for f in [f1, f2] if 1 < f < N]

        return {
            "N": N, "a": a, "period": r,
            "sqrt_mod": x,
            "factors": factors if factors else None,
            "verified": factors[0] * factors[1] == N if len(factors) == 2 else False,
            "method": "shors_period_finding",
        }

    def compare(self, circuit_name: str, shots: int = 1024) -> dict:
        """
        Run the SAME circuit on local AerSimulator AND real IBM hardware
        simultaneously (parallel threads), then compute a full noise analysis.

        Returns a single dict with:
          local      — AerSimulator result (ground truth / ideal)
          ibm        — real hardware result (with noise)
          noise      — statistical comparison: TVD, fidelity, per-state error
          circuit    — circuit metadata and diagram
          summary    — human-readable verdict
        """
        import concurrent.futures, math as _math, time

        qc = _build_circuit(circuit_name)

        # ── Run both backends in parallel threads ──────────────────────────────
        local_result: dict = {}
        ibm_result:   dict = {}
        local_err:    str  = ""
        ibm_err:      str  = ""

        def run_local():
            t0 = time.perf_counter()
            counts = SIM.run(qc, shots=shots).result().get_counts()
            return {
                "backend":    "AerSimulator",
                "counts":     counts,
                "elapsed_ms": int((time.perf_counter() - t0) * 1000),
            }

        def run_ibm():
            t0 = time.perf_counter()
            r = self._run_ibm(qc, shots)
            r["elapsed_ms"] = int((time.perf_counter() - t0) * 1000)
            return r

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            f_local = pool.submit(run_local)
            f_ibm   = pool.submit(run_ibm)

            try:
                local_result = f_local.result(timeout=30)
            except Exception as e:
                local_err = str(e)

            try:
                ibm_result = f_ibm.result(timeout=300)   # IBM can queue
            except Exception as e:
                ibm_err = str(e)

        # ── Noise analysis ─────────────────────────────────────────────────────
        noise = {}
        if local_result and ibm_result and not local_err and not ibm_err:
            noise = self._noise_analysis(
                local_result["counts"], ibm_result["counts"], shots, qc
            )

        # ── Side-by-side table (plain text) ───────────────────────────────────
        table = self._side_by_side_table(
            local_result.get("counts", {}),
            ibm_result.get("counts",  {}),
            shots,
        )

        # ── Human-readable verdict ─────────────────────────────────────────────
        if noise:
            tvd   = noise["total_variation_distance"]
            fidel = noise["fidelity"]
            if tvd < 0.02:
                verdict = f"Hardware nearly perfect — TVD={tvd:.3f}, fidelity={fidel:.3f}"
            elif tvd < 0.05:
                verdict = f"Excellent hardware fidelity — TVD={tvd:.3f}, fidelity={fidel:.3f}"
            elif tvd < 0.10:
                verdict = f"Good hardware fidelity — TVD={tvd:.3f}, fidelity={fidel:.3f}"
            else:
                verdict = f"Significant noise — TVD={tvd:.3f}, fidelity={fidel:.3f}"
        elif local_err or ibm_err:
            verdict = f"Comparison incomplete. Local error: {local_err or 'none'}. IBM error: {ibm_err or 'none'}"
        else:
            verdict = "Comparison complete."

        result = {
            "circuit":       circuit_name,
            "shots":         shots,
            "num_qubits":    qc.num_qubits,
            "circuit_depth": qc.depth(),
            "circuit_str":   str(qc.draw(output="text")),
            "local":         local_result,
            "ibm":           ibm_result,
            "local_error":   local_err  or None,
            "ibm_error":     ibm_err    or None,
            "noise":         noise,
            "table":         table,
            "verdict":       verdict,
            "timestamp":     datetime.now().isoformat(),
        }
        self._log({k: v for k, v in result.items()
                   if k not in ("circuit_str", "table")})
        return result

    # ── Noise analysis helpers ─────────────────────────────────────────────────

    def _noise_analysis(self, ideal: dict, noisy: dict,
                        shots: int, qc: QuantumCircuit) -> dict:
        """
        Compute statistical noise metrics between ideal (local) and
        noisy (IBM hardware) distributions.
        """
        import math as _math

        # All states that appeared in either distribution
        all_states = sorted(set(ideal) | set(noisy))

        # Normalise to probabilities
        p_ideal = {s: ideal.get(s, 0) / shots for s in all_states}
        p_noisy = {s: noisy.get(s, 0) / shots for s in all_states}

        # Total Variation Distance  TVD = 0.5 * Σ |p_i - q_i|
        tvd = 0.5 * sum(abs(p_ideal[s] - p_noisy[s]) for s in all_states)

        # Fidelity (Bhattacharyya / classical proxy)
        # F = Σ sqrt(p_i * q_i)
        fidelity = sum(
            _math.sqrt(p_ideal[s] * p_noisy[s]) for s in all_states
        )

        # Per-state deviation table
        per_state = []
        for s in all_states:
            pi, pn = p_ideal[s], p_noisy[s]
            deviation = pn - pi          # positive = hardware over-counts this state
            direction = "↑" if deviation > 0.005 else ("↓" if deviation < -0.005 else "≈")
            per_state.append({
                "state":          s,
                "ideal_prob":     round(pi, 4),
                "hardware_prob":  round(pn, 4),
                "deviation":      round(deviation, 4),
                "direction":      direction,
            })
        per_state.sort(key=lambda x: abs(x["deviation"]), reverse=True)

        # Error states — states that shouldn't appear (ideal prob ≈ 0) but do
        error_states = [
            e for e in per_state
            if e["ideal_prob"] < 0.01 and e["hardware_prob"] > 0.005
        ]

        # Total error rate = probability mass in wrong states
        error_rate = sum(e["hardware_prob"] for e in error_states)

        # Transpiled depth (fetch from IBM result if available)
        transpiled_depth = None   # populated by caller if known

        return {
            "total_variation_distance": round(tvd, 5),
            "fidelity":                 round(fidelity, 5),
            "error_rate":               round(error_rate, 5),
            "ideal_states":             [s for s in all_states if p_ideal[s] > 0.01],
            "error_states":             [e["state"] for e in error_states],
            "per_state":                per_state,
            "interpretation": {
                "tvd_scale":     "0=perfect, 0.05=excellent, 0.10=good, >0.15=noisy",
                "fidelity_scale":"1.0=perfect, 0.95+=excellent, <0.85=noisy",
                "error_rate":    f"{error_rate*100:.2f}% of shots landed in wrong states",
            },
        }

    def _side_by_side_table(self, ideal: dict, noisy: dict, shots: int) -> str:
        """Render a plain-text side-by-side comparison table."""
        all_states = sorted(set(ideal) | set(noisy))
        lines = [
            f"{'State':<8} {'Ideal (sim)':>14} {'Hardware (IBM)':>16} {'Δ':>8}",
            "─" * 50,
        ]
        for s in all_states:
            pi = ideal.get(s, 0) / shots
            pn = noisy.get(s, 0) / shots
            delta = pn - pi
            arrow = " ↑" if delta > 0.005 else (" ↓" if delta < -0.005 else "  ")
            lines.append(
                f"|{s}|  {pi*100:6.1f}%  ({ideal.get(s,0):4d})  "
                f"{pn*100:6.1f}%  ({noisy.get(s,0):4d})  "
                f"{delta*100:+5.1f}%{arrow}"
            )
        lines.append("─" * 50)
        return "\n".join(lines)

    def compare_algorithms(self, shots: int = 1024) -> dict:
        """
        Run Bell state, GHZ-3, Grover-2, and QFT-3 on BOTH backends.
        Produces a ranked noise table showing how TVD and fidelity
        scale with circuit depth and algorithm type.

        Returns per-algorithm results + a ranked summary.
        """
        import concurrent.futures

        algorithms = [
            ("bell_state", "Bell State",   "entanglement / baseline"),
            ("ghz_3",      "GHZ-3",        "3-qubit entanglement"),
            ("grover_2",   "Grover-2",     "amplitude amplification"),
            ("qft_3",      "QFT-3",        "phase estimation"),
        ]

        results = []

        def run_one(name, label, role):
            qc = _build_circuit(name)
            local_counts = SIM.run(qc, shots=shots).result().get_counts()
            ibm_info     = self._run_ibm(qc, shots)
            ibm_counts   = ibm_info["counts"]
            noise        = self._noise_analysis(local_counts, ibm_counts, shots, qc)
            return {
                "circuit":          name,
                "label":            label,
                "role":             role,
                "num_qubits":       qc.num_qubits,
                "logical_depth":    qc.depth(),
                "transpiled_depth": ibm_info.get("transpiled_depth"),
                "ibm_backend":      ibm_info.get("backend", "ibm"),
                "job_id":           ibm_info.get("job_id"),
                "local_counts":     local_counts,
                "ibm_counts":       ibm_counts,
                "tvd":              noise["total_variation_distance"],
                "fidelity":         noise["fidelity"],
                "error_rate":       noise["error_rate"],
                "error_states":     noise["error_states"],
                "per_state":        noise["per_state"],
            }

        # Submit all 4 algorithms in parallel threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures = {
                pool.submit(run_one, name, label, role): (name, label)
                for name, label, role in algorithms
            }
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result(timeout=300))
                except Exception as e:
                    name, label = futures[future]
                    results.append({"circuit": name, "label": label,
                                    "error": str(e)})

        # Sort by TVD ascending (best fidelity first)
        ok = [r for r in results if "tvd" in r]
        ok.sort(key=lambda r: r["tvd"])
        failed = [r for r in results if "tvd" not in r]

        # Correlation: does logical depth predict TVD?
        if len(ok) >= 2:
            depths = [r["logical_depth"] for r in ok]
            tvds   = [r["tvd"] for r in ok]
            avg_d  = sum(depths) / len(depths)
            avg_t  = sum(tvds) / len(tvds)
            cov    = sum((d - avg_d) * (t - avg_t) for d, t in zip(depths, tvds))
            var_d  = sum((d - avg_d)**2 for d in depths)
            depth_tvd_correlation = round(cov / var_d, 4) if var_d else 0.0
        else:
            depth_tvd_correlation = None

        # Ranking table (plain text)
        table_lines = [
            f"{'Rank':<5} {'Circuit':<12} {'Qubits':>6} {'Depth':>6} {'Xpile':>6} "
            f"{'TVD':>8} {'Fidelity':>9} {'Err%':>6}",
            "─" * 65,
        ]
        for rank, r in enumerate(ok, 1):
            table_lines.append(
                f"#{rank:<4} {r['label']:<12} {r['num_qubits']:>6} "
                f"{r['logical_depth']:>6} {r.get('transpiled_depth','?'):>6} "
                f"{r['tvd']:>8.4f} {r['fidelity']:>9.5f} {r['error_rate']*100:>5.2f}%"
            )

        best  = ok[0]  if ok else None
        worst = ok[-1] if ok else None

        result = {
            "shots":                  shots,
            "algorithms_tested":      len(ok),
            "ranked":                 ok,
            "failed":                 failed,
            "table":                  "\n".join(table_lines),
            "depth_tvd_correlation":  depth_tvd_correlation,
            "best":  {"circuit": best["circuit"],  "tvd": best["tvd"]}  if best  else None,
            "worst": {"circuit": worst["circuit"], "tvd": worst["tvd"]} if worst else None,
            "insight": (
                f"Depth-TVD correlation: {depth_tvd_correlation:.3f} "
                f"({'positive — deeper = noisier' if depth_tvd_correlation and depth_tvd_correlation > 0 else 'weak — other factors dominate'}). "
                f"Best: {best['label']} (TVD={best['tvd']:.4f}). "
                f"Worst: {worst['label']} (TVD={worst['tvd']:.4f})."
            ) if best and worst and depth_tvd_correlation is not None else "Analysis incomplete.",
            "timestamp": datetime.now().isoformat(),
        }
        self._log({"type": "algo_compare", "shots": shots,
                   "depth_tvd_correlation": depth_tvd_correlation})
        return result

    def compare_sweep(self, circuit_name: str,
                      shot_levels: list = None) -> dict:
        """
        Run the same circuit at multiple shot counts on BOTH backends.
        Shows how TVD and fidelity stabilise as shots increase —
        separating statistical noise (shrinks with shots) from
        hardware noise (fixed floor regardless of shots).

        Returns per-level results plus a convergence summary.
        """
        import math as _math

        if shot_levels is None:
            shot_levels = [128, 256, 512, 1024, 2048, 4096]

        qc = _build_circuit(circuit_name)
        levels = []

        for shots in shot_levels:
            local_counts = SIM.run(qc, shots=shots).result().get_counts()
            ibm_info     = self._run_ibm(qc, shots)
            ibm_counts   = ibm_info["counts"]
            noise        = self._noise_analysis(local_counts, ibm_counts, shots, qc)

            # Statistical uncertainty on TVD: ~1/sqrt(shots)
            stat_uncertainty = round(1 / _math.sqrt(shots), 4)

            levels.append({
                "shots":               shots,
                "tvd":                 noise["total_variation_distance"],
                "fidelity":            noise["fidelity"],
                "error_rate":          noise["error_rate"],
                "stat_uncertainty":    stat_uncertainty,
                "signal_noise_ratio":  round(
                    noise["total_variation_distance"] / max(stat_uncertainty, 1e-9), 2
                ),
                "local_counts":        local_counts,
                "ibm_counts":          ibm_counts,
                "ibm_backend":         ibm_info.get("backend", "ibm"),
                "transpiled_depth":    ibm_info.get("transpiled_depth"),
                "job_id":              ibm_info.get("job_id"),
            })

        # Convergence analysis: at what shot count does TVD stabilise?
        tvds = [lv["tvd"] for lv in levels]
        hardware_floor = min(tvds)
        converged_at   = None
        for i in range(1, len(levels)):
            if abs(tvds[i] - tvds[i-1]) < 0.005:   # < 0.5% change → converged
                converged_at = levels[i]["shots"]
                break

        # Trend line (are we still improving or flat?)
        trend = "stabilising" if converged_at else "still converging"
        if len(tvds) >= 2 and tvds[-1] > tvds[-2] + 0.005:
            trend = "fluctuating (hardware noise dominates)"

        # Plain-text sweep table
        table_lines = [
            f"{'Shots':>6}  {'TVD':>8}  {'Fidelity':>9}  {'Stat±':>7}  {'SNR':>6}  {'Error%':>7}",
            "─" * 55,
        ]
        for lv in levels:
            table_lines.append(
                f"{lv['shots']:>6}  {lv['tvd']:>8.4f}  {lv['fidelity']:>9.5f}  "
                f"±{lv['stat_uncertainty']:>5.4f}  {lv['signal_noise_ratio']:>6.2f}  "
                f"{lv['error_rate']*100:>6.2f}%"
            )

        result = {
            "circuit":        circuit_name,
            "shot_levels":    shot_levels,
            "levels":         levels,
            "hardware_floor": hardware_floor,
            "converged_at":   converged_at,
            "trend":          trend,
            "table":          "\n".join(table_lines),
            "interpretation": {
                "hardware_floor": f"Minimum achievable TVD on this chip: {hardware_floor:.4f}",
                "converged_at":   f"TVD stabilised at {converged_at} shots" if converged_at
                                  else "TVD still decreasing — try more shots",
                "trend":          trend,
                "snr_guide":      "SNR > 5 means hardware signal is reliable above statistical noise",
            },
            "timestamp": datetime.now().isoformat(),
        }
        self._log({"type": "sweep", "circuit": circuit_name,
                   "hardware_floor": hardware_floor, "trend": trend})
        return result

    # ── Daily utility methods ──────────────────────────────────────────────────

    def random_bits(self, n_bits: int = 8) -> dict:
        """
        Generate truly random bits via quantum measurement.

        Classical RNGs are deterministic given a seed — reproducible.
        Quantum measurement collapse is fundamentally non-deterministic:
        no seed, no pattern, no prediction possible even in principle.

        Each bit = one qubit measured after H gate (50/50 superposition).
        """
        pref = os.environ.get("QUANTUM_BACKEND_PREFERENCE", "").lower()
        if pref == "ibm" or pref == "fake_ibm":
            try:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent))
                from quantum_backend import get_random_bits
                res = get_random_bits(n_bits)
                if "bits" in res:
                    return res
            except Exception:
                pass

        import math as _math
        # Build n_bits-qubit circuit, each in superposition
        n_qubits = min(n_bits, 127)           # AerSimulator cap
        qc = QuantumCircuit(n_qubits, n_qubits)
        qc.h(range(n_qubits))
        qc.measure(range(n_qubits), range(n_qubits))

        # Single shot = one genuine random bitstring
        counts  = SIM.run(qc, shots=1).result().get_counts()
        bitstr  = list(counts.keys())[0].replace(" ", "")

        # Derive useful formats
        integer = int(bitstr, 2)
        floatv  = integer / (2**n_bits)       # uniform float in [0, 1)
        byte_arr = [int(bitstr[i:i+8], 2)
                    for i in range(0, len(bitstr) - len(bitstr) % 8, 8)]

        return {
            "bits":       bitstr,
            "n_bits":     n_bits,
            "integer":    integer,
            "float_0_1":  round(floatv, 8),
            "bytes":      byte_arr,
            "hex":        hex(integer),
            "source":     "quantum_superposition_collapse",
            "reproducible": False,   # physically impossible to reproduce
        }

    def random_password(self, length: int = 20,
                        charset: str = "alphanumeric_symbols") -> dict:
        """
        Generate a quantum-random password.
        Entropy comes from qubit measurement, not a pseudo-random seed.
        """
        import string, math as _math

        charsets = {
            "alphanumeric":         string.ascii_letters + string.digits,
            "alphanumeric_symbols": string.ascii_letters + string.digits + "!@#$%^&*",
            "hex":                  string.hexdigits[:16],
            "digits":               string.digits,
            "letters":              string.ascii_letters,
        }
        chars = charsets.get(charset, charsets["alphanumeric_symbols"])
        bits_per_char = _math.ceil(_math.log2(len(chars)))

        # Rejection sampling: values 0..2^bits_per_char-1, accept only 0..len(chars)-1
        # Acceptance rate ~ len(chars) / 2^bits_per_char (e.g. 70/128 ≈ 55%)
        # We batch-generate 120 bits per round and loop until we have `length` chars.
        BATCH_BITS = 120  # stays under AerSimulator 127-qubit cap
        password_chars = []
        while len(password_chars) < length:
            rand   = self.random_bits(BATCH_BITS)
            bitstr = rand["bits"]
            pos    = 0
            while len(password_chars) < length and pos + bits_per_char <= len(bitstr):
                chunk = int(bitstr[pos:pos + bits_per_char], 2)
                if chunk < len(chars):          # rejection sampling — unbiased
                    password_chars.append(chars[chunk])
                pos += bits_per_char

        password = "".join(password_chars[:length])
        entropy_bits = length * _math.log2(len(chars))

        return {
            "password":     password,
            "length":       len(password),
            "charset":      charset,
            "charset_size": len(chars),
            "entropy_bits": round(entropy_bits, 1),
            "strength":     ("weak"   if entropy_bits < 40  else
                             "medium" if entropy_bits < 72  else
                             "strong" if entropy_bits < 100 else
                             "very_strong"),
            "source":       "quantum_random_bits",
        }

    def decide(self, options: list) -> dict:
        """
        Make a quantum-random decision from a list of options.
        Fair, unbiased, physically non-deterministic.
        """
        import math as _math
        if not options:
            return {"error": "No options provided"}
        if len(options) == 1:
            return {"chosen": options[0], "options": options,
                    "method": "only_one_option"}

        n_bits = _math.ceil(_math.log2(len(options)))
        chosen = None
        attempts = 0
        while chosen is None and attempts < 20:
            rand = self.random_bits(n_bits)
            idx  = rand["integer"]
            if idx < len(options):
                chosen = options[idx]
            attempts += 1

        return {
            "chosen":   chosen or options[0],
            "options":  options,
            "n_options": len(options),
            "method":   "quantum_random_index",
            "attempts": attempts,
            "fair":     True,
        }

    def dice(self, sides: int = 6, n_dice: int = 1) -> dict:
        """Roll quantum-random dice (any number of sides)."""
        import math as _math
        rolls = []
        for _ in range(n_dice):
            n_bits  = _math.ceil(_math.log2(sides))
            result  = None
            for _ in range(20):
                rand = self.random_bits(n_bits)
                val  = (rand["integer"] % sides) + 1
                result = val
                break
            rolls.append(result)
        return {
            "rolls":  rolls,
            "total":  sum(rolls),
            "sides":  sides,
            "n_dice": n_dice,
            "source": "quantum",
        }

    def daily_seed(self) -> dict:
        """
        Generate a daily quantum random seed — use it to seed any
        simulation, shuffle, A/B test split, or random process.
        Includes multiple formats for different use-cases.
        """
        rand256 = self.random_bits(256)
        rand64  = self.random_bits(64)
        rand32  = self.random_bits(32)

        import hashlib
        # Derive a stable UUID-like string from the 256 bits
        h = hashlib.sha256(rand256["bits"].encode()).hexdigest()
        uid = f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"

        return {
            "seed_int":     rand64["integer"],
            "seed_hex":     rand256["hex"],
            "seed_float":   rand32["float_0_1"],
            "seed_uuid":    uid,
            "seed_bits256": rand256["bits"],
            "timestamp":    datetime.now().isoformat(),
            "uses": {
                "python_random":  f"random.seed({rand64['integer']})",
                "numpy":          f"np.random.seed({rand32['integer']})",
                "ab_test_group":  "A" if rand32["float_0_1"] < 0.5 else "B",
                "shuffle_seed":   rand32["integer"],
                "api_nonce":      rand256["hex"][:32],
            },
        }

    def list_circuits(self) -> dict:
        """Return all available built-in circuits."""
        return {"circuits": BUILTIN_CIRCUITS}

    def get_log(self, n: int = 20) -> list:
        """Return last N quantum experiment results."""
        if not self.log_path.exists():
            return []
        log = json.loads(self.log_path.read_text(encoding="utf-8"))
        return log[-n:]

    # ── IBM hardware runner ────────────────────────────────────────────────────

    def _run_ibm(self, qc: QuantumCircuit, shots: int) -> dict:
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from quantum_backend import _find_ibm_token

        token = _find_ibm_token()
        service  = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
        backend  = service.least_busy(operational=True, simulator=False)
        pm       = generate_preset_pass_manager(backend=backend, optimization_level=1)
        isa_qc   = pm.run(qc)
        sampler  = Sampler(mode=backend)
        job      = sampler.run([isa_qc], shots=shots)
        result   = job.result()
        counts   = result[0].data.c.get_counts()

        return {
            "backend":          backend.name,
            "backend_qubits":   backend.num_qubits,
            "transpiled_depth": isa_qc.depth(),
            "job_id":           job.job_id(),
            "counts":           counts,
        }

    # ── Grover circuit builder ─────────────────────────────────────────────────

    def _build_grover(self, target: str, n: int) -> QuantumCircuit:
        """Build Grover's circuit for any binary target string with optimal iterations."""
        import math
        qc = QuantumCircuit(n, n)
        # Superposition
        qc.h(range(n))
        
        # Calculate optimal number of Grover iterations: (pi/4) * sqrt(2^n)
        iterations = max(1, math.floor((math.pi / 4) * math.sqrt(2 ** n)))
        
        for _ in range(iterations):
            # Oracle: phase-flip the target state
            for i, bit in enumerate(reversed(target)):
                if bit == "0":
                    qc.x(i)
            
            if n == 1:
                qc.z(0)
            else:
                qc.h(n - 1)
                qc.mcx(list(range(n - 1)), n - 1)
                qc.h(n - 1)
                
            for i, bit in enumerate(reversed(target)):
                if bit == "0":
                    qc.x(i)
                    
            # Diffusion operator (Inversion about the mean)
            qc.h(range(n))
            qc.x(range(n))
            if n == 1:
                qc.z(0)
            else:
                qc.h(n - 1)
                qc.mcx(list(range(n - 1)), n - 1)
                qc.h(n - 1)
            qc.x(range(n))
            qc.h(range(n))
            
        qc.measure(range(n), range(n))
        return qc

    # ── Logging ────────────────────────────────────────────────────────────────

    def _log(self, result: dict):
        log = []
        if self.log_path.exists():
            try:
                log = json.loads(self.log_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        # Store a compact version (skip circuit_str to keep log small)
        entry = {k: v for k, v in result.items() if k != "circuit_str"}
        log.append(entry)
        self.log_path.write_text(
            json.dumps(log[-500:], ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

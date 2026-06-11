---
date: 2026-06-07
tags: [quantum-computing, qiskit, python, learning, AI-automation]
project: "AI Tools & Automation"
source: "Live coding session with Claude Code — foundation to progress curriculum"
---

# Quantum Computing: Foundation to Progress

## Key Idea
Build real intuition for quantum computing by writing and running working Qiskit code at each stage — from a single qubit all the way to Grover's search algorithm and IBM real hardware.

---

## Environment Setup

```bash
pip install qiskit qiskit-aer
# Versions confirmed working: qiskit 2.4.1, qiskit-aer 0.17.2
```

```python
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
sim = AerSimulator()   # local simulator — no IBM account needed for stages 1-5
```

---

## Stage 1 — Classical vs Quantum Bits (Superposition)

**The concept:** A classical bit is 0 or 1. A qubit in superposition is both simultaneously — until you measure it, then it collapses to one value.

```python
qc = QuantumCircuit(1, 1)
qc.h(0)          # Hadamard gate: puts qubit into superposition
qc.measure(0, 0)

counts = sim.run(qc, shots=1000).result().get_counts()
# Result: {'1': 467, '0': 533}  ← ~50/50 randomness confirmed
```

**Why it matters:** This is NOT random in the classical sense. The qubit simultaneously explores both outcomes until observation forces a choice. This is what enables quantum parallelism.

---

## Stage 2 — Quantum Gates

**The concept:** Gates are operations on qubits — like logic gates in classical computing, but reversible.

```python
# X gate — quantum NOT: flips |0> to |1>
qc = QuantumCircuit(1, 1)
qc.x(0)
qc.measure(0, 0)
# Result: {'1': 100}  — always 1, 100% deterministic

# H gate — superposition (as above)
# Z gate — phase flip: |0>→|0>, |1>→-|1>  (no visible effect alone, matters in interference)
```

**Gates palette:**
| Gate | Symbol | Effect |
|------|--------|--------|
| NOT | X | Flips 0↔1 |
| Hadamard | H | Creates superposition |
| Phase flip | Z | Flips phase of \|1⟩ |
| CNOT | CX | Flips target if control=\|1⟩ |
| Toffoli | CCX | Flips target if BOTH controls=\|1⟩ |

---

## Stage 3 — Entanglement (Bell State)

**The concept:** Two qubits become linked — measuring one instantly determines the other, regardless of distance. Einstein called this "spooky action at a distance."

```python
qc = QuantumCircuit(2, 2)
qc.h(0)          # superposition on qubit 0
qc.cx(0, 1)      # CNOT: entangle qubit 1 with qubit 0
qc.measure([0, 1], [0, 1])

counts = sim.run(qc, shots=1000).result().get_counts()
# Result: {'00': 518, '11': 482}  ← NEVER 01 or 10
```

**Why it matters:** This is a Bell state — the simplest form of entanglement. The two qubits share a single quantum state. Used in quantum cryptography (BB84 protocol) and quantum teleportation.

---

## Stage 4 — Quantum Circuits (Putting It Together)

### 4a: GHZ State (3-qubit entanglement)

```python
qc = QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, 1)    # entangle qubit 1 with qubit 0
qc.cx(0, 2)    # entangle qubit 2 with qubit 0
qc.measure([0, 1, 2], [0, 1, 2])

# Result: {'000': 504, '111': 496}  ← all three always agree
```

**Used in:** Quantum error correction, quantum networks, quantum key distribution.

### 4b: Quantum Full Adder (1-bit arithmetic)

```python
qc = QuantumCircuit(4, 2)
qc.x(0)         # A = 1
qc.x(1)         # B = 1

qc.cx(0, 2)     # XOR step 1
qc.cx(1, 2)     # XOR step 2  → sum bit = A XOR B

qc.ccx(0, 1, 3) # Toffoli: carry = 1 only if A=1 AND B=1

qc.measure([2, 3], [0, 1])
# Result: {'10': 100}  →  carry=1, sum=0  →  1+1=10 in binary ✓
```

**Circuit diagram reading:**
- Lines = qubits (top to bottom)
- Gates appear left-to-right in time order
- `■` with `─┤X├─` below = CNOT (control → target)
- `─┤M├─` = measurement

---

## Stage 5 — Grover's Algorithm (Quantum Search)

**The concept:** Searching N unsorted items.
- Classical: O(N) — check each one  
- Grover's: O(√N) — **quadratic speedup**

For 1 million items: classical = 1,000,000 steps, Grover's = ~1,000 steps.

**How it works:**
1. **Superposition** — H gates put all N items in parallel exploration
2. **Oracle** — marks the target by flipping its phase (negative amplitude)
3. **Diffusion** — amplifies the marked item, suppresses all others
4. **Repeat** oracle+diffusion √N times
5. **Measure** — target emerges with high probability

```python
# 2-qubit Grover's: searching 4 items (00, 01, 10, 11) for target |11>
qc = QuantumCircuit(2, 2)

# Step 1: Superposition
qc.h(0)
qc.h(1)

# Step 2: Oracle for |11> — CZ flips phase of |11> only
qc.cz(0, 1)

# Step 3: Diffusion operator (amplitude amplification)
qc.h(0); qc.h(1)
qc.x(0); qc.x(1)
qc.cz(0, 1)
qc.x(0); qc.x(1)
qc.h(0); qc.h(1)

qc.measure([0, 1], [0, 1])

counts = sim.run(qc, shots=1000).result().get_counts()
# Result: {'11': 1000}  ← 100% hit rate for N=4 with 1 iteration
```

**Key insight:** The oracle doesn't tell you WHERE the target is — it just marks it with a phase flip. The diffusion operator amplifies anything marked. This is "amplitude amplification" — quantum waves constructively interfere at the target, destructively elsewhere.

---

## Stage 6 — Real IBM Quantum Hardware

### Setup

```bash
pip install qiskit-ibm-runtime
```

```python
from qiskit_ibm_runtime import QiskitRuntimeService

# First time: save your IBM Quantum token
QiskitRuntimeService.save_account(
    channel="ibm_quantum",
    token="YOUR_IBM_TOKEN_HERE",   # get from: quantum.ibm.com
    set_as_default=True
)
```

### Running on Real Hardware

```python
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)
print(f"Running on: {backend.name}")

# Transpile circuit for real hardware (handles gate decomposition + qubit mapping)
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
isa_circuit = pm.run(qc)   # qc = any circuit from stages above

sampler = Sampler(mode=backend)
job = sampler.run([isa_circuit], shots=1000)
result = job.result()
counts = result[0].data.c.get_counts()
print(f"Real hardware result: {counts}")
```

### Key Differences: Simulator vs Real Hardware

| Aspect | AerSimulator | IBM Real Hardware |
|--------|-------------|-------------------|
| Noise | None — perfect | Yes — gate errors, decoherence |
| Speed | Instant | Queue wait (minutes to hours) |
| Qubits | Unlimited | 127–1000+ (Eagle, Heron chips) |
| Cost | Free | Free tier available |
| Results | Exact quantum math | Real quantum physics |

### What Noise Looks Like

Real hardware gives results like `{'11': 891, '00': 84, '01': 14, '10': 11}` instead of perfect `{'11': 1000}`. The "wrong" answers (01, 10) are **quantum errors** from:
- **Gate fidelity** — imperfect control pulses
- **Decoherence** — qubit losing its quantum state over time  
- **Crosstalk** — neighboring qubits interfering

This is why quantum error correction (like the GHZ state from Stage 4) matters.

---

## Learning Path Summary

```
Stage 1: Superposition         → H gate, 50/50 randomness
Stage 2: Quantum gates         → X, H, Z — the building blocks
Stage 3: Entanglement          → CNOT, Bell states, spooky action
Stage 4: Quantum circuits      → GHZ state, full adder, circuit diagrams
Stage 5: Grover's algorithm    → O(√N) search, amplitude amplification
Stage 6: Real hardware         → IBM Quantum, noise, transpilation
```

## Resources

- **IBM Quantum account (free):** https://quantum.ibm.com
- **Qiskit docs:** https://docs.quantum.ibm.com
- **Qiskit textbook (free):** https://learning.quantum.ibm.com
- **IBM Quantum Learning:** courses from beginner to advanced

## Action / Next Steps

- [ ] Create free IBM Quantum account at quantum.ibm.com
- [ ] Get API token and run Stage 6 on real hardware
- [ ] Try Grover's on 3 qubits (8 items) — needs 2 oracle+diffusion iterations
- [ ] Explore Shor's algorithm (factoring) — the algorithm that breaks RSA encryption
- [ ] Look into Variational Quantum Eigensolvers (VQE) — chemistry applications

---
date: 2026-06-11
tags: [webgl, 3d-graphics, quantum-computing, agent-os, clawglove]
project: "AI Tools & Automation"
source: "Agent OS Workspace Dashboard Implementation"
---

# 3D WebGL Neural Graph & Simulation Dashboard Upgrade

## Key Idea
Implementation of an interactive WebGL-based 3D Neural Graph and Quantum Simulation Dashboard, mapping notes, notebooks, and security engines as physical geometric nodes with real-time particle-flow synapses, alongside custom viewports for active quantum algorithm visualizations.

## Details

### 1. Architectural Integration & Routing
The dashboard serves as the central visual interface for Agent OS, combining obsidian notes, NotebookLM libraries, and active governance simulators.
- **`/neural` (Primary Route):** Serves the new WebGL-enabled `neural3d.html` dashboard, rendering nodes in three dimensions.
- **`/neural2d` (Legacy Route):** Preserves the original 2D D3.js force-directed graph layout (`neural.html`) as a lightweight fallback for lower-end compute environments.

---

### 2. WebGL 3D Graph Visualization
Built using the `3d-force-graph` and `three.js` libraries, the graph constructs a spatial web of the agent's knowledge and policy boundaries:
- **Node Classification:** Represents knowledge and systems as distinct geometric shapes:
  - *Vault Notes:* Standard file nodes representing Obsidian Markdown files.
  - *NotebookLM Notebooks:* Purple spheres indicating active Google NotebookLM workspaces.
  - *Engine Systems:* High-value endpoints for ClawGlove (governance) and OpenClaw (explorer).
- **Particle Synapses:** Nodes are connected by glowing links that utilize Three.js particle systems. The flow density (directional particles) and speed are proportional to connection weight, representing active knowledge pathways and communication speeds.

---

### 3. Interactive Simulation Viewports
The dashboard embeds specialized 3D canvas containers to visualize active quantum computations and defenses:

#### A. Bell State Entanglement Check (TOCTOU Defense)
- **Visuals:** Renders two spheres (Qubit 0 in cyan, Qubit 1 in purple) connected by a solid, pulsing laser beam representing quantum entanglement.
- **Behavior:** Upon context tampering injection (simulating a Time-of-Check to Time-of-Use attack), the laser line shatters into faint, red segments (`#f85149`).
- **Data Feedback:** Displays a status indicator (`BROKEN! TAMPER DETECTED`) and a correlation ratio drop to `0%` to visually verify the deterministic blocking of tampered actions.

#### B. Grover's Amplitude Amplification
- **Visuals:** An animated column chart mapping the probability distribution of 3-qubit states ($|000\rangle$ through $|111\rangle$).
- **Behavior:** Stepping the algorithm triggers amplitude amplification. The target state $|101\rangle$ grows in probability from $0.35$ (uniform superposition) to $0.85$ on step 1, and reaches $0.98$ on step 2, while other states are suppressed.
- **Formula Overlay:** Displays $k = \lfloor \frac{\pi}{4}\sqrt{2^n} \rfloor$ to show the math behind optimal iteration calculation.

#### C. Quantum Walk Predictor
- **Visuals:** Visualizes particle diffusion over the active 3D action graph network.
- **Behavior:** Temporarily boosts link particle flow density (from 2 to 6 particles) and speed (to `0.025`) to simulate linear quantum walk diffusion.
- **Data Feedback:** Highlights affected nodes with a purple prediction wave glow and alerts the user of a completed lookahead prediction wave (averaging `54.3%` precision).

---

### 4. NotebookLM Source Access
The dashboard integrates directly with the `/notebooks` API endpoint to display workspace resources:
- **Right Inspector Panel:** Clicking any notebook node populates a sidebar containing:
  - Notebook Title, Cluster topic, and modification timestamps.
  - Quick-launch URL to open the workspace directly in NotebookLM.
  - Connections list detailing all related notes and clusters based on shared keywords.

## Action / Next Steps
- [ ] Connect the active /neural endpoint to the server launch script.
- [ ] Implement dynamic GPU capability detection to auto-fallback to `/neural2d` on low-power devices.
- [ ] Add direct markdown editor popups within the inspector panel for Vault notes.

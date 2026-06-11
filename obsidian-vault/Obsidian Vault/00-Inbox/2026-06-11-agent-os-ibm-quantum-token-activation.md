---
date: 2026-06-11
tags: [agent-os, qiskit, ibm-quantum, env-configuration]
project: "AI Tools & Automation"
source: "Agent OS Workspace Upgrades"
---

# IBM Quantum QPU Token Activation

## Key Idea
Configured the backend server environment to load the active `IBM_QUANTUM_TOKEN` credentials from the parent `.env` file, enabling real physical QPU execution for simulation checks.

## Details
1. **Server Restart**: Recycling the background HTTP process was required since environment variables are loaded once at server startup. Stopped the stale process on port `8765` and spun up a new instance in the background.
2. **Dynamic Credential Routing**: Verified that the Qiskit quantum backend switcher (`quantum_backend.py`) successfully loads `os.environ["IBM_QUANTUM_TOKEN"]`.
3. **QPU Execution & Budgeting**: The system is now ready to route quantum walks and Bell state validation checks to the real IBM physical hardware. When the monthly budget limit (10 minutes/month) is exhausted, it will automatically degrade gracefully to local noisy simulations.

## Action / Next Steps
- [ ] Monitor the **Quantum** tab on the main dashboard to check active IBM QPU call usage and remaining seconds.
- [ ] Run a simulation cycle to verify the connection.

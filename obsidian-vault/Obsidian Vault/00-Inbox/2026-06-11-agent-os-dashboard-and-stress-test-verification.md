---
date: 2026-06-11
tags: [agent-os, dashboard, webgl, chrome-devtools, stress-test, quantum-computing]
project: "AI Tools & Automation"
source: "Agent OS Workspace Testing & Verification"
---

# Agent OS Dashboard & Stress Test Verification

## Key Idea
Verified dashboard links and 3D Neural Map loading using Chrome DevTools browser automation, successfully resolving library loading conflicts. Executed the co-evolution stress test suite, achieving a 100% pass rate.

## Details
1. **Dashboard & Neural Map Verification**:
   - Navigated browser to `http://localhost:8765/dashboard` and `http://localhost:8765/neural`.
   - Encountered initial console error `Uncaught ReferenceError: THREE is not defined` and `Uncaught TypeError: Ak.Timer is not a constructor` on the 3D map.
   - Identified that `3d-force-graph` has a bundled version of Three.js in its package that conflicts with standalone loaded UMD versions, and newer versions (r150+) have deprecated global builds.
   - **Fix:** Switched script tags to matching compatible UMD versions: Three.js `0.146.0` and 3D Force Graph `1.70.5` loaded from jsDelivr (avoiding MIME-type CORB/ORB blocking).
   - Reloaded `/neural` and confirmed that all ReferenceErrors and TypeErrors were completely resolved, with the WebGL scene compiling and executing cleanly.
   - Captured and stored viewports as visual proof:
     - 3D Neural Map Viewport: [neural_3d_screenshot.png](file:///C:/Users/navka/navakanth001/agent_os/neural_3d_screenshot.png)
     - Dashboard Viewport: [dashboard_screenshot.png](file:///C:/Users/navka/navakanth001/agent_os/dashboard_screenshot.png)
2. **ClawGlove + OpenClaw Co-Evolution Stress Test**:
   - Executed `python stress_test.py --backend=local` to run all 10 validation suites.
   - Verified backend switcher (S1), quantum walks (S2), prediction (S3), co-evolution invariants (S4), ledger rules (S5), explorer (S6), lead-behind architecture (S7), policy engines (S8), ML-DSA-65 PQC signing (S9), and integration runs (S10).
   - **Outcome:** 143/143 tests passed successfully (0 failures, 100% pass rate).
   - **Grade:** S-tier (Production Ready).

## Action / Next Steps
- [ ] View the saved screenshot artifacts: [neural_3d_screenshot.png](file:///C:/Users/navka/navakanth001/agent_os/neural_3d_screenshot.png) and [dashboard_screenshot.png](file:///C:/Users/navka/navakanth001/agent_os/dashboard_screenshot.png).
- [ ] Verify that the 3D graph renders nodes for notebooks, vault notes, and governance systems with active glowing particle flow synapses.

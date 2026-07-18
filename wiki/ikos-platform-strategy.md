# IKOS Platform Strategy — Canonical Directive

**Status:** Adopted 2026-07-18 (v3 — includes Innovation Pipeline, Innovation Gate, Flight Status Dashboard)
**Supersedes:** the "Interactor vs. Whiteboard 4D" migration framing.
**One-line summary:** *Applications are experiments. Platform packages are products.*

---

## Vision

Interactor evolves into the **Interactive Knowledge Operating System (IKOS)**.
Bleuuboard, Whiteboard 4D, and future apps (Simulation Studio, Story Builder, education apps, community apps) are **platform clients**, not isolated products. Every application both consumes and contributes platform capabilities.

```
                    IKOS Platform
┌──────────────────────────────────────────────────────┐
│ Interaction Runtime      Recording Runtime           │
│ Selection Runtime        Object Runtime              │
│ Timeline Runtime         Collaboration Runtime       │
│ AI Runtime               Publishing Runtime          │
│ Knowledge Runtime                                    │
└──────────────────────────────────────────────────────┘
          ▲          ▲          ▲
      Bleuuboard  Interactor  Future Apps
```

No application owns interaction. The platform owns interaction. Applications compose platform capabilities.

## Roles

| App | Role | Leads on |
|---|---|---|
| **Bleuuboard** | Interaction laboratory — free to experiment rapidly | Fluid pointer interactions, workspace manipulation, smart navigation, hover reveal, compass interaction, gesture editing, spatial workflows |
| **Interactor** | Flagship platform application — prioritizes stability | Event sourcing, telemetry, knowledge capture, publishing, experiment infra, learning workflows, backend sync |

Not every Bleuuboard experiment becomes part of IKOS. Successful experiments graduate. Interactor adopts interaction capabilities only when mature.

| Component | Primary role | Success metric |
|---|---|---|
| Bleuuboard | Interaction laboratory | New interaction patterns validated |
| Interactor | Flagship IKOS application | Complete creator and learner workflows |
| `packages/` | Shared platform | Reduced duplication across applications |
| IKOS | Platform governance | Stable reusable capabilities |

**North Star:** Applications prove ideas. The platform preserves successful ideas. The ecosystem multiplies successful ideas.

## Build While Flying (aviation analogy)

Interactor and Bleuuboard are operational aircraft; the platform is the engine. We never ground the fleet for a rewrite. Every sprint leaves the apps more capable, more stable, more enjoyable — while better engines are proven in one aircraft, installed in a second, and only then promoted to the shared platform.

This is **not** a phased rewrite or framework-first initiative. The platform is not built first — it **emerges**. Applications lead; the platform follows. The framework is crystallized knowledge extracted from excellent applications.

## The Innovation Pipeline (one-directional flow)

```
Research → Bleuuboard experiment → User validation → Telemetry & performance
  → Second application needs it → Extract into packages/ → Interactor adopts
  → Future applications reuse → Eventually open source
```

**Progression:** Bleuuboard explores → Interactor operationalizes → IKOS standardizes → the open-source ecosystem amplifies.

## The Innovation Gate

Before extracting anything into `packages/`, a capability must satisfy **all five**:

1. **Works** — implemented and shipped in one application.
2. **Wanted** — a second application genuinely benefits from it.
3. **Reusable** — no hidden assumptions tied to the original app.
4. **Measured** — telemetry or user testing shows it improves the experience.
5. **Stable** — the API is unlikely to change significantly in the next few sprints.

If any criterion fails, keep iterating inside the application.

## Flight Status Dashboard (sprint-end ritual)

Every sprint ends with a short status report:

```
✈ Flight Status
Bleuuboard   ✅ Flying — new capabilities validated: N
Interactor   ✅ Flying — capabilities adopted: N
packages/    📦 New shared modules: N
Architecture debt: P0/P1 counts
Next extraction candidate: <name>
```

This keeps the focus on delivering software, not producing plans.

## Monorepo First

Shared capabilities start in a common `packages/` workspace. Publish standalone `@ikos/*` packages (interaction-runtime, object-registry, selection-system, gesture-engine, recording-runtime, timeline-engine, collaboration-runtime, knowledge-runtime, ai-runtime, ivp) only when multiple internal apps depend on them, APIs have stabilized, and maintenance cost is justified. **Internal reuse precedes open-source distribution.**

## Sprint Evaluation — three levels

1. **Application** — does this improve Bleuuboard or Interactor today?
2. **Platform** — can this become a reusable runtime?
3. **Ecosystem** — could other apps / the open-source community benefit?

Capabilities need at least Levels 1 and 2 to become platform assets.

## Success Metrics — every sprint delivers all three

- **Product:** a visible improvement users experience today.
- **Platform:** a reusable capability closer to extraction.
- **Evidence:** telemetry, testing, or adoption proving it deserves to enter IKOS. Without evidence, architecture is a hypothesis.

## Principles

1. Users always receive working software.
2. Architecture evolves from implementation.
3. Working code outweighs speculative design.
4. Platform capabilities are extracted, not invented.
5. Every extraction reduces future duplication.
6. Every sprint improves both product and platform.

## Immediate implications (current sprint)

- Finish the 3 open Bleuuboard P0s (draggable compass pane, utils hover-reveal, Nav+Move merge) **inside Bleuuboard**, written extraction-friendly: pointer/drag/gesture logic in plain modules with no Bleuuboard globals, so they become first candidates for `@ikos/interaction-runtime`.
- First real extraction happens when Interactor needs one of these capabilities — not before.
- `packages/` workspace before any npm publishing.

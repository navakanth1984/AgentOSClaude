# MVCT MRP — Minimum Research Product

> Event-sourced AI tutor architecture built to test H1: "Does persistent learner state improve 14-day retention on Boolean Logic over a stateless LLM chatbot?"

## Location
`mvct-mrp-core/` in the workspace root (`c:\Users\navka\navakanth001\mvct-mrp-core`).

## The Hypothesis

**H1:** Persistent learner state (BKT mastery tracking + retrieval scheduling) improves 14-day retention on Boolean Logic assessments compared with a stateless LLM chatbot control.

## Core Architectural Invariants
1. **Facts are immutable** — `UniversalLearningEvent` is append-only (no UPDATE/DELETE).
2. **State is a projection** — `StudentMasteryProjection` is derived via BKT replay, never directly mutated.
3. **No feature creep** — No dashboards, auth, or multi-tenant until H1 is answered.

## Milestone Map

| Milestone | Deliverable / Focus | Status |
| :--- | :--- | :--- |
| **M0** | Azure infrastructure, deterministic BKT oracle, live DB migration | ✅ Complete |
| **M1** | Ingestion API (`POST /session`, `POST /attempt`), event sourcing, Serializable transactions | ✅ Complete |
| **M2** | API robustness (Zod, jitter retries, idempotency), `/experience` feed, React Vite UI | ✅ Complete |
| **M3** | Event-driven ingestion (202 Accepted), EventBus, optimistic projection, recommendation policy, pluggable CardRenderer, Telemetry Dashboard | ✅ Complete |
| **M4** | EventBus memory audit, CardRenderer staging, telemetry visualizations, 50k-event stress test | ✅ Complete |
| **M5** | H1 Experiment Harness (outcome logger, assignment, validator scripts) | ✅ Complete |
| **M6** | Controlled Pilot & Nightly Watch Runner (DB-backed IOS runtime) | ✅ Complete |
| **M7** | Experience Intelligence (UX redesign, onboarding, design telemetry, visual snapshots) | ✅ Complete |
| **M8** | Platform (SDK → Native ladder); **Governance Layer review** | ⏳ Planned |
| **M9** | Engineering Projector (fitness scoring telemetry, backlog tracking) | ✅ Complete |
| **M10** | Product Intelligence (behavioral analytics, friction detection, auto-issue gen) | ⏳ Planned |

> Milestone themes revised 2026-07-11 per `CONTEXT.md` v3.1. Full governance
> stack (constitution, canonical context, ADR-007–010) landed this session —
> see [mvct-mrp-core-governance-platform-next-steps.md](mvct-mrp-core-governance-platform-next-steps.md).

## The Three Parallel Streams

* **Stream A — Research (Scientific Validity)**: Multi-participant synthetic simulations (`simulate_1000_participants.ts`), strict byte-for-byte event replay validation, and statistical validation against false positives/negatives.
* **Stream B — Product UX & Delight (Adoption)**: Transitioning MVCT to "Duolingo for reasoning" via animated learning feeds, streaks, achievements, review systems, and offline PWA capability.
* **Stream C — Platform Engineering (Scalability)**: CI/CD automation and autonomous specialized QA agents (QA, UI, Performance, Research, Security, Deployment) ensuring zero-human-intervention PR gatekeeping.

## Architecture Evolution

| Milestone | Architectural Shift | Key Decision | ADR |
| :--- | :--- | :--- | :--- |
| M0 | Infrastructure & deterministic validation | Prisma 7 adapter, Azure Flexible Server, locked `eval_bkt.ts` oracle | ADR-000 |
| M1 | Event-sourced ingestion | `LearningEvent` append-only ledger; `StudentProjection` rebuilt via BKT replay | ADR-001 |
| M2 | Robust synchronous API | Jitter-backoff Serializable retries; Zod validation; idempotency via P2002 catch | ADR-002 |
| M3 | Asynchronous event-driven write path | Per-learner promise queue (EventBus) replaces SERIALIZABLE locks; HTTP 202 Accepted | ADR-003 |
| M4 | Runtime hardening | Memory lifecycle audit; long-duration stability proof; dashboard observability | ADR-004 |
| M5 | Experiment Harness | Frozen experiment.json, append-only outcomes, validation scripts | ADR-005 |
| M6 | Engineering Quality Platform | Preflight, Zod API contracts, multi-metric performance checks, synthetic profiles, visual viewports matrix, accessibility, and security validation | ADR-006 |
| M6 | Engineering Cognition Layer | Mirrors student pipeline (events → projection → proposals → simulation → PR) | ADR-007 |
| M6 | Maximum Pressure Benchmark | Tiered agent organization & multi-model adversarial pressure loop | ADR-008 |
| M6 | Adaptive Agent Ecology | Agent mutation, cloning, and statistical retirement criteria | ADR-009 |
| M6 | Product Intelligence Layer | InteractionEvent stream, Product Genome, and 7-level Evidence Hierarchy | ADR-010 |

> Full ADR rationale for M3 decisions in [mvct-mrp-core-sprint4.md](mvct-mrp-core-sprint4.md).

## Key Files
| File | Purpose |
|------|---------|
| `program.md` | Master contract — read first |
| `README_FIRST.md` | Project north star — governance rules |
| `prisma/schema.prisma` | Event Kernel + Projection Layer schema |
| `eval_bkt.ts` | 🔒 Locked oracle — DO NOT MODIFY |
| `src/bkt.ts` | Pure BKT math engine (green ✅) |
| `src/index.ts` | Express server — ingestion, experience, health endpoints |
| `src/eventBus.ts` | Per-learner sequential promise queue + DLQ |
| `src/projectors/masteryProjectionProjector.ts` | Atomic optimistic-concurrency projection updates |
| `src/recommendation/engine.ts` | Candidate → Feature → Score → Rank pipeline |
| `apps/web/src/` | Vite React UI — Feed, CardRenderer registry, TelemetryDashboard |
| `scripts/calibrate_instrument.ts` | Calibration suite (202 acceptance, replay invariant, idempotency) |
| `tests/projection_determinism.test.ts` | Deterministic projection rebuild proofs |

## Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Platform** | Node.js v24, TypeScript, Express |
| **Research** | BKT math engine (`src/bkt.ts`), locked oracle (`eval_bkt.ts`) |
| **Persistence** | Azure PostgreSQL Flexible Server (B1ms), Prisma 7 (pg driver adapter) |
| **Queue** | In-process EventBus — per-learner sequential promise queue; Redis/BullMQ deferred to M5+ |
| **Frontend** | Vite + React 18, served as static assets from Express |
| **Infrastructure** | Azure (DB only); local Express server; no auth, no multi-tenant until H1 answered |
| **Budget** | ₹12,000/month hard cap |

## BKT Engine
The `updateMastery` function implements a product-form BKT update:

```
isCorrect  → pNew = 1 - (1-pL) * (1-pT) * (1-pG)
isIncorrect → pNew = pL * (1-pT) * (1-pS)
```

Passes all three locked eval assertions (moderate first-correct increase, convergence after 3 corrects, strict decrease on incorrect).

## Relationship to mvct-v1
`mvct-v1` (the Microscope) was the v1 capability-detection gate — a separate, older design. The MRP (`mvct-mrp-core`) is the new event-sourced research architecture, built to test H1 scientifically. The two coexist in the monorepo.

## Future Research & Feature Proposals
- **[DMP-GMS Concept Specification](file:///C:/Users/navka/.gemini/antigravity/brain/e8b0e72e-ddc1-4fbf-8052-e42023288504/concept_specification_dmp_gms.md):** Dynamic Misconception Projections & Generative Micro-Scaffolding. Designed by the Innovation Lab (2026-07-15) to track micro-telemetry (hesitation, wrong paths) and serve real-time visual learning feedback.

## Governance Rule
> **No architectural change without evidence.**
> 1. Observe → 2. Analyze → 3. Change. Never the reverse.

## Sources
- Research design conversation: this session (2026-07-09), architect-level design process.
- [program.md](../mvct-mrp-core/program.md) — master contract
- [README_FIRST.md](../mvct-mrp-core/README_FIRST.md) — north star doc

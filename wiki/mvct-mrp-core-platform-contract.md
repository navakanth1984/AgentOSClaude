# MVCT Core — Platform Execution Contract (Post PR #35)

## Execution Mode

**Architecture, Governance, ADRs, and Platform decisions are FROZEN.**
No redesigns. No roadmap debates. No milestone renaming. Current phase is **Platform Development**. Infrastructure stabilization is complete.

---

## Current Verified State

### Repository
*   **Branch**: `master` (clean)
*   **SDK implementation**: `COMPLETE`
*   **SDK PR**: **PR #35 (MERGED)** — Merged and verified on 2026-07-13.

### Azure Dev
*   **Deployment Pipeline**: Deploy Azure Dev (Run 29207266443) is `GREEN`.
*   **Live Endpoint**: `https://app-mvct-dev-api.azurewebsites.net`
*   **Health**: `Healthy` (Database reachable, Migration complete, Seed complete, Projection healthy, Event dictionary healthy).
*   **Only remaining warning**: `checksums.schema.valid = false` (Informational only, not an infrastructure issue).

---

## Completed Platform Work (Azure)
*   Completed Azure App Service, Azure PostgreSQL, firewall configuration, automated deployment, automated Prisma migration, automated database seed, health gate, Application Insights, and deployment optimization.
*   Merged PR #32 (Application Insights), PR #33 (Deployment optimization), and PR #35 (SDK integration).
*   Deployment pipeline now automatically builds, deploys, migrates, seeds, and performs health verification.

---

## SDK Foundation (`packages/sdk`)
*   Created workspace package with files: `client.ts`, `types.ts`, `session.ts`, `learning.ts`, `telemetry.ts`, `health.ts`, `index.ts`, `README.md`, `package.json`, `tsconfig.json`.
*   **MvctHttpClient**: Implements configurable base URL, timeout, retry, exponential backoff, and typed errors.
*   **TelemetryClient**: Implements `trackInteraction()`, `trackDesignEvent()`, `flush()`, `retryFailed()`, offline queueing with browser `localStorage` and memory fallback for Node.
*   **Frontend Migration**: All direct `fetch()` calls removed and replaced with `@mvct/sdk` client APIs in `SessionContext`, `Feed`, `ChallengeCard`, `FeedbackOverlay`, `ComicCard`, `ExplanationCard`, `VideoCard`, `TelemetryDashboard`, `interactionClient`, and `designEventClient`.

---

## Immediate Priorities & Roadmap

### P0 — Review & Merge PR #35 (COMPLETE)
*   **Status**: COMPLETE. Merged on 2026-07-13.
*   **Validation**: Independent SDK compile-check (`PASS`), Web client production build (`PASS`), eslint rules check (`PASS`), unit/replay tests (`PASS`), local browser ESM interop and rendering verified.

### P1 (Current) — Power BI Integration
Transform telemetry into operational dashboards.
*   **Deliverables** (`src/intelligence/powerbi/`): `dashboardExporter.ts`, `datasetBuilder.ts`, `schema.ts`, `mapping.ts`.
*   Create export pipelines and generate datasets for Engineering, Product, Learning, and Deployment dashboards using Engineering, Interaction, and Learning telemetry alongside Azure Monitor metrics and Application Insights.
*   **Acceptance**: Dashboard JSON validates and Power BI imports without modification.

### P2 — Product Intelligence
Aggregate existing telemetry:
```text
InteractionEvents → JourneyGraph → ScreenTransitions → DropoffDetection → FrictionIndex
```
*   **Deliverables**: `interactionAggregator.ts`, `journeyProjector.ts`, `frictionCalculator.ts`, `screenGraph.ts`.
*   **Acceptance**: Replay is deterministic and produces an identical graph.

### P3 — Component Fitness
Calculate views, completion, hesitation, abandonment, engagement, and retries per component.
*   **Deliverables**: `ComponentFitness`, `ComponentTrend`, `RegressionWarning`.
*   **Acceptance**: Ranking and replay are deterministic.

### P4 — Recommendation Engine
Consume Journey Graph, Component Fitness, Learning state, and Engineering health to generate `LivingBacklogItem` priorities (P0, P1, P2).
*   **Acceptance**: Backlog is generated automatically.

### P5 — Checksum Cleanup
Resolve `checksums.schema.valid = false` using canonical schema hashing that ignores line endings, whitespace, and comments. Only semantic schema changes should alter checksum. Handle in a separate PR.

---

## Engineering Rules
*   **PR Isolation**: One capability per PR. No mega PRs.
*   **Lifecycle**: `Feature Branch` → `Small PR` → `CI` → `Review` → `Merge` → `Azure Deploy`.
*   **Verification**: Every PR must include builds, unit tests, replay tests (where applicable), smoke tests, Azure deployment, and health endpoint validations.
*   **Explicitly Deferred**: Do NOT implement Authentication, React Native, Offline DB, Plugin Runtime, Marketplace, Mobile SDK, LLM orchestration, or version negotiation beyond SDK abstraction.

---

## Definition of Done
*   PR #35 merged.
*   CI and deployment green.
*   Frontend contains zero direct `fetch()` calls.
*   SDK builds independently.
*   Browser and Node support verified.
*   Telemetry exclusively flows through SDK.
*   Public API documented.

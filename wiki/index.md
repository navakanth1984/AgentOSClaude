# Knowledge Map Index

> [!NOTE]
> **ARCHIVED KNOWLEDGE BASE (READ-ONLY)**
> This wiki is a read-only historical archive. Canonical living documentation has migrated to the root folders:
> * **[`research/`](file:///c:/Users/navka/navakanth001/mvct-mrp-core/research/README.md)** (Experimental protocols, datasets, analysis)
> * **[`product/`](file:///c:/Users/navka/navakanth001/mvct-mrp-core/product/README.md)** (Roadmap, capabilities, user backlog)
> * **[`platform/`](file:///c:/Users/navka/navakanth001/mvct-mrp-core/platform/README.md)** (API versioning, SDK, integrations)
> * **[`docs/`](file:///c:/Users/navka/navakanth001/mvct-mrp-core/docs/README.md)** (ADRs, technical architecture blueprints)

> Front door of the self-improving knowledge base. One synthesized page per topic; sources live in `sources/`. See [CLAUDE.md](CLAUDE.md) for how this folder operates.

## Creative Portfolio
- [Love Lasts for Seven Seconds](love-lasts-seven-seconds.md) — Romantic novel and screenplay project.
- [DAAVA](daava.md) — Action thriller novel and screenplays.
- [KAALIKA](kaalika.md) — Screenplay and media prompting pipeline.
- [Vaayuthram Vaalagaathram](vaayuthram-vaalagaathram.md) — Retelling Ramayana's Sundarakanda from the tail's POV.

## Technical & AI Engineering
- [Agent OS](agent-os.md) — The central operating system for orchestrating AI agents, workflows, and creative pipelines.
- [Agent OS Speech Pipeline](agent-os-speech-pipeline.md) — Artifact-driven DAG executor for semantic-to-audio TTS (Kokoro ONNX backend).
- [Agentic Loops Architecture](agentic-loops-architecture.md) — Umbrella: self-updating agents, memory loops, RAG.
- [Cognitive Runtime Platform (CRP)](cognitive-runtime-platform.md) — Measurement-first adaptive runtime with telemetry, replay, and representation selection.
- [Nth Dimension Academy](nth-dimension-academy.md) — Conversational AI teaching assistant on Google Cloud RAG.
- [MVCT MRP](mvct-mrp.md) — Minimum Research Product: event-sourced BKT tutor testing H1 (persistent state vs. stateless chatbot, 14-day Boolean Logic retention).
  - ├── [Implementation Charter](mvct-mrp-core-implementation-charter.md) — Operational targets for shipping, telemetry, and product evolution.
  - ├── [Release Readiness Report](mvct-mrp-core-readiness-report.md) — Grounded codebase audit: documented vs implemented, CI, debt, and capabilities.
  - ├── [M0 Infrastructure](mvct-mrp-core-m0-next-steps.md) — Azure deployment, BKT oracle, live DB migration. ✅
  - ├── M1 Event Ingestion — Ingestion API, event sourcing, Serializable transactions. ✅
  - ├── [M2 Robust Experience Platform](mvct-mrp-sprint3-next-steps.md) — API robustness, idempotency, React feed UI. ✅
  - ├── [M3 Event-Driven Cognitive Infrastructure](mvct-mrp-core-sprint4.md) — Non-blocking EventBus, recommendation pipeline, pluggable cards, telemetry. ✅
  - ├── [M4 Runtime Hardening](mvct-mrp-core-sprint5-next-steps.md) — EventBus ++/-- fix, CardRenderer ErrorBoundary, /telemetry/dlq + dashboard. ✅
  - ├── [M5 H1 Experiment Harness](mvct-mrp-core-h1-next-steps.md) — Outcome logger, arm assignment, stopping rules. ✅
  - ├── [M6 Controlled Pilot + Engineering Intelligence E0/E1](mvct-mrp-core-governance-platform-next-steps.md) — Constitution, canonical context, ADRs-007-010, EngineeringEvents (E0), nightly Watch Runner (E1). ✅
  - ├── [M7 Experience Intelligence](mvct-mrp-core-governance-platform-next-steps.md) — UX redesign, motion, streaks, PWA support, telemetry-driven UX. 🔜 **Active**
  - ├── [M8 Auto Engineering](mvct-mrp-core-h1-next-steps.md) — Agentic CI/CD, auto-QA, performance/security agents. ⏳ Planned
  - ├── [M9 Platform SDK & API](mvct-mrp-core-h1-next-steps.md) — TypeScript SDK, public API, webhooks, multi-tenant. ⏳ Planned
  - └── [M10 Multi-Platform](mvct-mrp-core-h1-next-steps.md) — React Native, iOS, Android, offline-first sync. ⏳ Planned
- [Nth Absolute Cinema](nth-absolute-cinema.md) — AI filmmaking Creative OS; five-graph compiler architecture; lives at `E:\nth-absolute-cinema\`, portable/hardware-adaptive by design.
- [OKF Bundle Generator](okf-bundle-generator.md) — Completed tool: DB schema → linked Markdown knowledge bundle.
- [Design Extraction Workflow](design-extraction-workflow.md) — Standard practice: extract a design blueprint from a reference site (evidence-gated, anti-hallucination) and apply it to a new design; mirrored across all AI tools.
- [BLEUUBOARD](bleuboard.md) — 4D creative whiteboard (3D strokes, extruded text, images, live video, 4th-dimension animation). Deployed at bleuboard.vercel.app. Single-file Vercel static deployment.
- [NotebookLM Bridge](notebooklm-bridge.md) — Direct-API integration with NotebookLM (no browser automation).
- [Karpathy Mandates](karpathy-mandates.md) — Four execution principles governing all AI work here.
- [Production Stack Strategy](production-stack-strategy.md) — Technical co-founder brief: credit allocation (₹1.5L+ Google AI), tool roles (Claude=engineer, Gemini=product), FastAPI+Flutter+Postgres production architecture, and 30-day product focus.
- [Workspace Productivity Upgrades](antigravity-upgrades.md) — Integration of four productivity upgrades (Roast, Verification, Handoff, Goals) into the self-improving KB.
- [Google Anti-Gravity](google-antigravity.md) — Rebuilt five-piece architecture and sub-agent engine powered by Gemini 3.5 Flash.
- [Agentic Development Lifecycle](agentic-dev-lifecycle.md) — **Full 8-stage lifecycle: work tree → develop → verify → PR → staging → production → KB handoff.** Every agent must follow this end-to-end.
- [Code Development Lifecycle](development-lifecycle.md) — Standard branch→verify→commit→push→PR→merge flow + deprecate-before-delete rule for code.
- [Storage Management](storage-management.md) — C: ↔ E: strategy: delete regeneratable deps (node_modules, venvs, pycache) + mirror heavy folders to E:\navakanth001\ via symlinks.
- [Generative Production Workflows](production-workflows.md) — Best practices and identified pitfalls for creating generative media.
- [Agent OS Speech — Next Steps](agent-os-speech-next-steps.md)
- [Usage Efficiency — Next Steps](usage-efficiency-next-steps.md) — Roadmap for minimizing token context drift under the ULCOP v2.1 standard.
- [Agent OS Execution Framework — Next Steps](agent-os-execution-next-steps.md) — Mixture-of-Agents Phase 1 handoff (PR #29, cold-start for Antigravity).
- [Validator Research — Next Steps](20260702-next-steps.md) — Cold-start handoff (P0–P7) for the next agent continuing the speech pipeline.
- [CRP Next Steps](crp-next-steps.md) — Cold-start handoff for CRP Plan 3/3 after M3-M4 shipped.
- [MVCT Core Consolidation — Next Steps](mvct-mrp-core-consolidation-next-steps.md) — Cold-start merge consolidation handoff for Claude Code.
- [NAC Current State](CURRENT.md) — live operating manual: Production Readiness Gate, Stop Line, Definition of Done, Milestone Lifecycle. Start here for NAC status.
- [NAC Roadmap](ROADMAP.md) — what comes after the Gate passes (UX Pass 2 → Restore Manager → Character Department → ...).
- [NAC Decisions](DECISIONS.md) — architecture decision log (Departments replace Compilers, Genome composition, local-first, etc.).
- [NAC Changelog](CHANGELOG.md) — one line per dated milestone.
- [NAC Next Steps](nac-next-steps.md) — historical session-by-session handoffs (journal, not live status — see CURRENT.md instead).
- [Microsoft Fabric (DP-700)](fabric-dp700.md) — Fabric data-engineering study stack.
- [KB Sync Test](sync-test.md) — Canary verification page for Claude & Antigravity.


## Academic
- [Science FA2 Revision](science-fa2-revision.md) — Bilingual Science FA2 revision material.

## Knowledge Base System
- [Memory OS](memory-os.md) — The persistent memory, governance, and preference layer for all agents.
- [Knowledge Base Protocol](knowledge-base-protocol.md) — Shared AI-tool contract: graph + wiki layers, extract/feed order.
- [Knowledge Base Map](knowledge-base-map.md) — Front door across all repos: which has a graph / wiki.
- [AI Tool Sync](ai-tool-sync.md) — Markdown bridge inventory for Claude Code, Antigravity, Gemini, Codex, and shared agent folders.

## Administration
- [Operating Brief](CLAUDE.md) — How ingest / answer / tidy and the nightly loop work.
- [Log](log.md) — Activity history.

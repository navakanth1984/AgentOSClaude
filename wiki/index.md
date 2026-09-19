# Knowledge Map Index

> [!NOTE]
> **ARCHIVED KNOWLEDGE BASE (READ-ONLY)**
> This wiki is a read-only historical archive. Canonical living documentation has migrated to the root folders:
> * **[`research/`](file:///c:/Users/navka/navakanth001/mvct-mrp-core/research/README.md)** (Experimental protocols, datasets, analysis)
> * **[`product/`](file:///c:/Users/navka/navakanth001/mvct-mrp-core/product/README.md)** (Roadmap, capabilities, user backlog)
> * **[`platform/`](file:///c:/Users/navka/navakanth001/mvct-mrp-core/platform/README.md)** (API versioning, SDK, integrations)
> * **[`docs/`](file:///c:/Users/navka/navakanth001/mvct-mrp-core/docs/README.md)** (ADRs, technical architecture blueprints)

> Front door of the self-improving knowledge base. One synthesized page per topic; sources live in `sources/`. See [CLAUDE.md](CLAUDE.md) for how this folder operates.

- [Indic Graphic Novel Engine & Sarvam AI Showcase](indic-graphic-novel-and-sarvam-showcase.md) — 7-chapter retro-comic reader, 2-host podcasts, LiveKit WebRTC agent, and 1947 historical ephemera.

## Creative Portfolio
- [Love Lasts for Seven Seconds](love-lasts-seven-seconds.md) — Romantic novel and screenplay project.
- [DAAVA](daava.md) — Action thriller novel and screenplays.
- [KAALIKA](kaalika.md) — Screenplay and media prompting pipeline.
- [Vaayuthram Vaalagaathram](vaayuthram-vaalagaathram.md) — Retelling Ramayana's Sundarakanda from the tail's POV.

## Technical & AI Engineering
- [Master Architecture Registry](file:///c:/Users/navka/navakanth001/docs/architecture/ARCHITECTURE_REGISTRY.md) — Primary index listing all ratified architectural concepts, statuses, and canonical specs.
- [Harness Engineering Platform](harness_engineering_gbrain.md) — The 2026 Thoughtworks/OpenAI paradigm ($\text{Agent} = \text{Model} + \text{Harness}$): 4-quadrant control, shift-left feedback sensors, positive prompt injection, Stryker/mutmut mutation testing, and the Cybernetic Steering Law.
- [Agent OS](agent-os.md) — The central operating system for orchestrating AI agents, workflows, and creative pipelines.
- [Agent OS Speech Pipeline](agent-os-speech-pipeline.md) — Artifact-driven DAG executor for semantic-to-audio TTS (Kokoro ONNX backend).
- [Agentic Loops Architecture](agentic-loops-architecture.md) — Umbrella: self-updating agents, memory loops, RAG.
- [Cognitive Runtime Platform (CRP)](cognitive-runtime-platform.md) — Measurement-first adaptive runtime with telemetry, replay, and representation selection.
- [Capability OS](capability-os.md) — Hardened systems kernel with stable provider contracts, dynamic telemetry, and event ingestion.
- [Global Skills Synchronization & AI Tools Engine](global-skills-synchronization-and-tools.md) — 4-way real-time skill mesh (`~/.claude/skills`, `~/.gemini/config/skills`, `~/.agents/skills`, `.agents/skills`), auto-sync daemon with 1.5s debounce, Needle 2.0 SLM integration, MoneyPrinterTurbo video automation, and Minto Pyramid skill.
- [Video Production Workflow](video-production-workflow.md) — Screen recording (OBS) to edited shorts/reels/carousel/long-form output for commercial use; self-hosted live streaming (MediaMTX + cloudflared) as a YouTube/social-platform alternative. Tool-neutral skill, DaVinci Resolve deferred pending RAM upgrade.
- [ACDC Framework (Guide/Verify/Solve)](acdc-framework.md) — Solve loop implemented and running inside `opendatalifecycleintelligence/substrate`; Guide/Verify still contract-only. On-demand trigger centralized at `C:\Users\navka\.claude\skills\acdc-maintenance\`.
  - └── [Skill Promotion Pipeline](skill-promotion-pipeline.md) — 5-phase governance pipeline converting failure patterns into permanent capabilities.
- [Open Cognitive Operating System (OCOS)](ocos.md) — Unified cross-project governance index and standard adapters.
- [Nth Dimension Academy](nth-dimension-academy.md) — Production digital academy: OpenSEO & GEO engine, Edge markdown negotiation, Schema.org course graphs, and 2-minute interactive certification lead capture on React 19 / Vite 8.
- [Repository Intelligence Platform](repository-intelligence-platform.md) — Architectural static analysis overlays, rule checking engine, and natural-language citations Q&A.
- [Azure Quantum Platform](azure-quantum.md) — Cloud-native continuous quantum execution platform, job replay engine, and calibration scheduler on Azure Quantum (`wsnamequantum001`).
- [MVCT MRP](mvct-mrp.md) — Minimum Research Product: event-sourced BKT tutor testing H1 (persistent state vs. stateless chatbot, 14-day Boolean Logic retention).
- [FinAura & FinDFunDme Architecture](finaura-findfundme-architecture.md) — High-velocity vibe coding, viral milestone cards, OpenSEO static head pre-rendering, and Vercel edge deployment for financial intelligence platforms.
- [Signal](signal-app.md) — Local research web app wrapping the `last30days` skill engine; `E:\navakanth001\signal-app\`, not under git.

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
  - ├── [AGENT_BOOT — Engineering Operating Manual](mvct-agent-boot.md) — Canonical cold-start doc for all agents: Product North Star, Engineering Flywheel, Orchestrator model, Browser-First development, Whiteboard 4D subsystem, capability registry. (2026-07-15, commits 5001757–6e40528)
  - ├── [M8 Auto Engineering](mvct-mrp-core-h1-next-steps.md) — Agentic CI/CD, auto-QA, performance/security agents. ⏳ Planned
  - ├── [M9 Platform SDK & API](mvct-mrp-core-h1-next-steps.md) — TypeScript SDK, public API, webhooks, multi-tenant. ⏳ Planned
  - └── [M10 Multi-Platform](mvct-mrp-core-h1-next-steps.md) — React Native, iOS, Android, offline-first sync. ⏳ Planned
- [Nth Absolute Cinema](nth-absolute-cinema.md) — AI filmmaking Creative OS; five-graph compiler architecture; lives at `E:\nth-absolute-cinema\`, portable/hardware-adaptive by design.
- [OKF Bundle Generator](okf-bundle-generator.md) — Completed tool: DB schema → linked Markdown knowledge bundle.
- [Design Extraction Workflow](design-extraction-workflow.md) — Standard practice: extract a design blueprint from a reference site (evidence-gated, anti-hallucination) and apply it to a new design; mirrored across all AI tools.
- [BLEUUBOARD](bleuboard.md) — 4D creative whiteboard (3D strokes, extruded text, images, live video, 4th-dimension animation). Deployed at bleuboard.vercel.app. Single-file Vercel static deployment. Includes the **Spatial Awareness System (SAS)** — intent-based dragging where the HUD explains the user's intention, never the engine (Phase 1 live 2026-07-18) — and the ADLC deploy/verify/rollback contract.
- [IKOS Platform Strategy](ikos-platform-strategy.md) — "Applications are experiments, platform packages are products." Innovation Gate (Works · Wanted · Reusable · Measured · Stable) and the 2-consumer extraction threshold.
- [Workspace OS — Sprint 7 Plan](ikos-sprint-7-workspace-os.md) — Plan for the Spatial Operating System infrastructure, Layered Workspace Architecture, Capability Bus, and IKOS Plugin API.
- [IKOS Capability Candidate Registry](ikos-capability-candidates.md) — Capabilities proven in one app awaiting a second consumer before extraction to `packages/` (5 registered: InteractionDispatcher, DraggablePanel, HoverRevealPanel, SpatialHUD, SAS).
- [NotebookLM Bridge](notebooklm-bridge.md) — Direct-API integration with NotebookLM (no browser automation).
- [Karpathy Mandates](karpathy-mandates.md) — Four execution principles governing all AI work here.
- [Production Stack Strategy](production-stack-strategy.md) — Technical co-founder brief: credit allocation (₹1.5L+ Google AI), tool roles (Claude=engineer, Gemini=product), FastAPI+Flutter+Postgres production architecture, and 30-day product focus.
- [ShoonyaAI](shoonyaai.md) — Current verified status, production gaps, and links to the AI-native ETL/analytics repository.
- [ShoonyaAI Antigravity Handoff](shoonyaai-antigravity-handoff-2026-09-15.md) — Cold-start execution sequence for staging, Vercel recovery, Azure gates, and production evidence.
- [Workspace Productivity Upgrades](antigravity-upgrades.md) — Integration of four productivity upgrades (Roast, Verification, Handoff, Goals) into the self-improving KB.
- [Google Anti-Gravity](google-antigravity.md) — Rebuilt five-piece architecture and sub-agent engine powered by Gemini 3.5 Flash.
- [Document Zero: The One-Page Thesis](document_zero_one_page_thesis.md) — Interactor core thesis.
- [Interactor Journeys & Defensibility](creator_and_explorer_journeys.md) — Creator integrations, explorer distribution loop, and platform defensibility.
- [Agentic Development Lifecycle](agentic-dev-lifecycle.md) — **Full 8-stage lifecycle: work tree → develop → verify → PR → staging → production → KB handoff.** Every agent must follow this end-to-end.
- [Code Development Lifecycle](development-lifecycle.md) — Standard branch→verify→commit→push→PR→merge flow + deprecate-before-delete rule for code.
- [Storage Management](storage-management.md) — C: ↔ E: strategy: delete regeneratable deps (node_modules, venvs, pycache) + mirror heavy folders to E:\navakanth001\ via symlinks.
- [Generative Production Workflows](production-workflows.md) — Best practices and identified pitfalls for creating generative media.
- [Agent OS Speech — Next Steps](agent-os-speech-next-steps.md)
- [Usage Efficiency — Next Steps](usage-efficiency-next-steps.md) — Roadmap for minimizing token context drift under the ULCOP v2.1 standard.
- [Agent OS Execution Framework — Next Steps](agent-os-execution-next-steps.md) — Mixture-of-Agents Phase 1 handoff (PR #29, cold-start for Antigravity).
- [Assessment-OS Next Steps](assessment-os-next-steps.md) — Mobile validation and production readiness roadmap for multiplatform delivery.
- [Validator Research — Next Steps](20260702-next-steps.md) — Cold-start handoff (P0–P7) for the next agent continuing the speech pipeline.
- [CRP Next Steps](crp-next-steps.md) — Cold-start handoff for CRP Plan 3/3 after M3-M4 shipped.
- [MVCT Core Consolidation — Next Steps](mvct-mrp-core-consolidation-next-steps.md) — Cold-start handoff: merge consolidation done, Azure Dev (P0) provisioning in progress (rg-mvct-dev-centralus), roadmap conflict unresolved.
- [MVCT Core Platform Contract](mvct-mrp-core-platform-contract.md) — Platform execution contract and priorities post-PR #35.
- [NAC Current State](CURRENT.md) — live operating manual: Production Readiness Gate, Stop Line, Definition of Done, Milestone Lifecycle. Start here for NAC status.
- [NAC Roadmap](ROADMAP.md) — what comes after the Gate passes (UX Pass 2 → Restore Manager → Character Department → ...).
- [NAC Decisions](DECISIONS.md) — architecture decision log (Departments replace Compilers, Genome composition, local-first, etc.).
- [NAC Changelog](CHANGELOG.md) — one line per dated milestone.
- [NAC Next Steps](nac-next-steps.md) — historical session-by-session handoffs (journal, not live status — see CURRENT.md instead).
- [Microsoft Fabric (DP-700)](fabric-dp700.md) — Fabric data-engineering study stack.
- [Microsoft 365 Developer Program & MCT Sandbox](m365-developer-program-mct.md) — Instant renewable E5 developer sandbox, 25 licenses, Graph/Teams/SharePoint datasets, and MCT auth troubleshooting.
- [Retention Intelligence: AI Foundry Integration](retention-intelligence-ai-integration.md) — DLI retention engine evolution with a serverless small-LLM explanation layer; IaC in project repo's `infra/`.
- [Retention Intelligence: Antigravity Handoff](retention-intelligence-antigravity-handoff.md) — phased plan to reconcile two disconnected retention-decision engines (RetentionDecisionEngine vs. certified IPEDecisionEngine); read before touching skillify/gbrain.
- [KB Sync Test](sync-test.md) — Canary verification page for Claude & Antigravity.
- [Book/Magazine OCR Pipeline](book-ocr-pipeline.md) — Tesseract-based multi-language OCR (Telugu + 11 other Indian scripts, auto-detected) for 100+ scanned books/epubs; set up as a global Antigravity skill after ruling out GPU-only Unlimited-OCR and bulk Claude-vision OCR as infeasible on this hardware/usage budget.
- [Class 7 Telugu FA2 OCR Answer Key](telugu-fa2-ocr-answer-key.md) — Telugu literature/language FA2 answer-key package with line-level OCR audit, low-confidence CSV, DOCX/PDF outputs, and upload human-gate notes.
- [Telugu Sahitya & Cultural Knowledge Base](telugu-sahitya-cultural-knowledge-base.md) — Directory of Indian & foreign research centres, digital lexicons (DDSA, Andhra Bharati, Wikisource, LTRC IIIT-H), and 4-tier post-extraction validation architecture.


## Academic
- [Curriculum Answer Key Wizard](curriculum_answer_key_wizard_gbrain.md) — Zero-skimming textbook-photo answer-key pipeline; Maths, Science, and Telugu FA2 verified implementations.
- [Science FA2 Revision](science-fa2-revision.md) — Bilingual Science FA2 revision material.

## Knowledge Base System
- [Memory OS](memory-os.md) — The persistent memory, governance, and preference layer for all agents.
- [Knowledge Base Protocol](knowledge-base-protocol.md) — Shared AI-tool contract: graph + wiki layers, extract/feed order.
- [Knowledge Base Map](knowledge-base-map.md) — Front door across all repos: which has a graph / wiki.
- [AI Tool Sync](ai-tool-sync.md) — Inventory of tool folders, Markdown bridges, and sync rules across Claude, Antigravity, Gemini, and Codex.
- [Open Source AI Tools Matrix](open-source-ai-tools-matrix.md) — Tool recommendations, redundancy prioritization, and execution patterns.
- [External Open Source Tool Adoption Register](external_tool_adoption_gbrain.md) — GBrain register for externally validated GitHub/app tools, split into generic workspace capabilities, per-project guardrails, domain references, installer paths, and sandbox-only pilots.

## Administration
- [Operating Brief](CLAUDE.md) — How ingest / answer / tidy and the nightly loop work.
- [Log](log.md) — Activity history.

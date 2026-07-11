---
date: 2026-06-06
tags: [core, identity, agent-os]
project: "AI-Automation"
source: "Agent OS Setup"
---

# Navakanth's Core Identity Note

> This note is tagged `core` — it is always loaded as Layer 1 context for every AI agent session.
> Edit this file to update your permanent context. Keep it concise.

## Who I Am
- **Name:** Navakanth Reddy Dumpa
- **Platform:** Windows 11, Claude Code CLI
- **Stack:** Python, Flutter, JavaScript — still learning, learning by building
- **Email:** navkanthr@gmail.com

## Active Projects
1. **Agent OS** — Central AI orchestration system (Obsidian + NotebookLM + Claude + Hermes)
2. **DAAVA** — Cinematic production pipeline (Visual DNA, Seedance, Veo3)
3. **Learning Dashboard** — Flutter app with AI tutoring (Fabric Guru, DP-700)
4. **AutoGrade** — AI-powered grading tool (Flutter + backend)

## How I Work
- Learn by building — show working examples, not just theory
- Detailed + teaching mode — explain the *why*, not just the *what*
- Full code, not snippets
- Save everything to Obsidian: date-tagged, project-linked

## My Obsidian Vault
- **Path:** `obsidian-vault/Obsidian Vault/` (inside project)
- **Structure:** 00-Inbox → 01-Projects → 02-Areas → 03-Resources → 04-Archive
- New captures always go to `00-Inbox/` first

## Agent OS Architecture
- **obsidian_bridge.py** — memory read/write layer
- **notebooklm_agent.py** — Playwright browser automation for NotebookLM
- **server.py** — HTTP API on localhost:8765 for Flutter dashboard
- **agent_os.py** — CLI command loop

## Current Focus (update this section each session)
- **Resolve P0 Research Blocker (Control Isolation) (2026-07-11):** Implemented pure pluggable strategies (SequentialStrategy vs BKTStrategy), separated context builders, backend capability flags, and hid MasteryGauge for Control group in Feed.tsx. Created routing/contract tests and updated validate_experiment.ts. Opened Draft PR #2.
- **Usage Efficiency & Log Sync (2026-07-11):** Executed the usage efficiency protocol for session `047dbc86-f63f-4094-bb68-d3e1677b1cf6`. Logged session details to `model-usage-log.json`, updated `wiki/log.md`, ran `validate_usage_efficiency.py` (Today's Cost: $0.00/$2.00, Routing Efficiency: 100.0%, OpenRouter Remaining: $19.7908), generated the `usage_efficiency_analysis.md` report, and successfully completed `session_end.py` syncing to the Obsidian vault.
- **Google Anti-Gravity Ingestion & Workspace Highlight Mandate (2026-07-11):** Ingested detailed architectural guidelines for Anti-Gravity (Desktop App, Git work trees, sidebar redesign). Codified a new directive in `AGENTS.md` requiring all active agents to highlight Git work tree operations and sub-agent transitions, and proactively remind the user of workspace features (sidebar toggles, grouping, etc.).
- **MVCT MRP Core - M0 (2026-07-10):** Successfully completed M0 (Operational Validation) for Boolean Logic research. Infrastructure deployed, flexible server IP whitelisting configured, schema migration applied, BKT concepts/metadata seeded, and /health & determinism replay tests verified 100% green against the live Azure PostgreSQL DB. Next: Sprint 2 (BKT Ingestion API).
- **NAC Director Studio V2 — Gates A/B/C shipped, awaiting review (2026-07-04):** ground-up React/TS/Vite rewrite of the Director Studio UI on `feat/director-studio-v2` in `E:\nth-absolute-cinema` (separate repo). Built in three human-reviewed gates, not one unsupervised pass: Gate A scaffold (693a5a1), Gate B architecture — layout/routing/4-way Zustand/typed API layer/design system (052a497), Gate C experience layer — Welcome + Creation Wizard, verified live end-to-end (c42830f). Old vanilla-JS dashboard untouched at `:8421/`. wiki/nac-next-steps.md split into `wiki/CURRENT.md`/`DECISIONS.md`/`ROADMAP.md`/`CHANGELOG.md` this session (navakanth001 commit f2b33386). **Next:** await user go-ahead before Gate D (storage/snapshot/package UI); full handoff in wiki/nac-next-steps.md's "HANDOFF TO ANTIGRAVITY" section.
- **Agent OS Speech subsystem — V1.1 shipped (2026-06-27):** 8-stage artifact-driven TTS DAG (Kokoro ONNX) hardened, architecture **frozen** and git-tagged `v1.1.0` on branch `milestone/v1.1.0`. Deterministic benchmark harness + scaling/thread-matrix studies done (Baselines 1–4; thread-tuning was a documented negative result). Docs: `docs/ARCHITECTURE_STATUS.md`, `docs/BASELINE.md`, `docs/HANDOFF.md`. **Next — Antigravity takes V1.2:** start with the **Asset Manifest** (`assets_manifest.json`, highest-value reproducibility), then Doctor++/EngineRegistry, then ADR-gated Protocol/VoiceManager. Defer voice blending/download manager/routing until a 2nd engine exists.
- **NTH Brain / MVCT — Milestone M1 reached (2026-06-25):** MVCT V1 "The Microscope" built & merged to `master` (PR #2). A validated capability sensor (`transfer-detector-v0`) is now coupled to a Python-enforced constitutional governor (`mvct-v1/`) via the `TransferSensor` seam. Constitution (HMAC PermissionToken, deterministic guard, fail-closed) lives in code, not prompts. 28 offline tests green.
- **Next — Stage B (real-human validation):** the detector passed only a *synthetic* ceiling. Run a small human pilot; annotate transcripts **blind to detector output** (permanent rule: never evaluate the detector against labels derived from its own output); compute real κ_human; feed failure modes back via the `TransferSensor` seam (no tutor changes).
- **Then — Stage C:** controlled gated-vs-ungated comparative study (SAIR, unlock latency).
- **Model routing:** implementation/codegen → Gemini 2.5 Flash (Tier 1/2); reserve Opus for architecture/design.
- **CRP — Gate 2 FROZEN (2026-07-03):** IR compiler merged to master (PR #26, #27); Compiler Conformance Report published (`crp/docs/GATE2-CONFORMANCE.md`, 12/12 hard criteria from real test evidence, self-verifying hash test added after review) and R1-PROGRESS.md updated to 2/4 gates — PR #28 open (https://github.com/navakanth1984/AgentOSClaude/pull/28). Along the way found local `master` had silently diverged 15 commits behind origin (missing crp/, pyrefly.toml search-path, crp-ci.yml, docs/superpowers CRP plans) — synced from origin/master so the PR diff stayed clean. Next: merge #28, start Gate 3 provenance.
- **TITAN/CRP alignment (2026-07-03):** CRP is the execution platform inside TITAN's vision, not a sibling — layer model Vision(TITAN)→Governance(Constitution/Determinism/ABI/IR-Spec/Roadmap)→Implementation(CRP Gates 1-4)→Research(R2-R5)→Future(TITAN capabilities). Session split: TITAN owns vision/architecture/RFCs/freezes, CRP owns code/tests/PRs/evidence. `docs/vision/TITAN.md` — initially believed missing (git ref search found nothing) — was recovered same-day from orphaned commit `784a22fc` (superseded branch, never merged, so invisible to `git log --all` but recoverable via `git show <sha>:<path>`) and recommitted as `46cf11dd` with the layer-model correction folded in, now on `docs/crp-gate2-freeze` / PR #28.
- **Pending (2026-07-02):** Claude Desktop install blocked by orphaned MSIX Helium hive at `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc` (HRESULT 0x80073CF6). User is rebooting to release the locked hive; next session should confirm the folder deleted cleanly and the reinstall (`Claude Setup (5).exe`) succeeded. See `wiki/log.md` (2026-07-02 entry) for full diagnosis.

## Operational Infrastructure
- **AntigravityUsageMonitor** — 5-hour scheduled background cost and economics check.
- **Agent OS** — Centralized execution, session archiving (`session_end.py`), and memory bridge.
- **Obsidian Sync** — Vault bridging for session notes and profile context.

## What's Built (Agent OS v1.0)
- `obsidian_bridge.py` — vault read/write, hybrid context (core + recent 5)
- `notebooklm_agent.py` — Playwright automation, cookie auth, 261 notebooks scraped, studio scraper, network interception for audio download
- `server.py` — REST API: /health /status /context /search /recent /notebooks /assets /save
- `agent_os.py` — CLI: context, save, search, recent, assets, notebook, hermes, session
- `session_end.py` — session auto-save hook
- Flutter `agent_os_screen.dart` — live dashboard tab with notebooks panel
- `notebook_cache.json` — 261 notebooks cached

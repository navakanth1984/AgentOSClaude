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
- **Agent OS Speech subsystem — V1.1 shipped (2026-06-27):** 8-stage artifact-driven TTS DAG (Kokoro ONNX) hardened, architecture **frozen** and git-tagged `v1.1.0` on branch `milestone/v1.1.0`. Deterministic benchmark harness + scaling/thread-matrix studies done (Baselines 1–4; thread-tuning was a documented negative result). Docs: `docs/ARCHITECTURE_STATUS.md`, `docs/BASELINE.md`, `docs/HANDOFF.md`. **Next — Antigravity takes V1.2:** start with the **Asset Manifest** (`assets_manifest.json`, highest-value reproducibility), then Doctor++/EngineRegistry, then ADR-gated Protocol/VoiceManager. Defer voice blending/download manager/routing until a 2nd engine exists.
- **NTH Brain / MVCT — Milestone M1 reached (2026-06-25):** MVCT V1 "The Microscope" built & merged to `master` (PR #2). A validated capability sensor (`transfer-detector-v0`) is now coupled to a Python-enforced constitutional governor (`mvct-v1/`) via the `TransferSensor` seam. Constitution (HMAC PermissionToken, deterministic guard, fail-closed) lives in code, not prompts. 28 offline tests green.
- **Next — Stage B (real-human validation):** the detector passed only a *synthetic* ceiling. Run a small human pilot; annotate transcripts **blind to detector output** (permanent rule: never evaluate the detector against labels derived from its own output); compute real κ_human; feed failure modes back via the `TransferSensor` seam (no tutor changes).
- **Then — Stage C:** controlled gated-vs-ungated comparative study (SAIR, unlock latency).
- **Model routing:** implementation/codegen → Gemini 2.5 Flash (Tier 1/2); reserve Opus for architecture/design.

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

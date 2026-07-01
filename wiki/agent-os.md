# Agent OS
> The central operating system for orchestrating AI agents, workflows, and creative pipelines.

## Overview
Agent OS is a comprehensive framework for running autonomous AI agents. It appears to provide a core engine for defining workflows, managing agent memory, and parsing natural language. It includes a command-line interface (`cli.py`), a web server (`server.py`), and extensive testing suites. The system is designed to connect to and orchestrate various internal and external tools and services.

## Key Subsystems
- **Core Engine:** A central workflow system (`workflow.py`, `agent_os.py`) that manages the lifecycle of agent tasks.
- **Speech & Audio:** A major subsystem for text-to-speech and audio processing, including an audiobook generation pipeline. See [Agent OS Speech Pipeline](agent-os-speech-pipeline.md) for details.
- **Agentic & Swarm Intelligence:** Contains logic for agentic loops, goal-oriented execution, swarm capabilities, and cinematic model routing.
- **Integrations:** Bridges to external services like NotebookLM, Obsidian, WhatsApp, OpenRouter, and Google Cloud Platform.
- **Creative & Filmmaking Tools:** Includes specialized modules for cinematic services, filmmaking swarms, and a novelist swarm, connecting the technical OS to the creative projects.

## AI Filmmaking Long-Form Pipeline
The dashboard's Filmmaking tab drives chunked long-form generation and screenplay export:
- **`creative_pipeline.generate_longform`** — outline-free chunked generation for `screenplay`, `novel`, `video_prompts`, `audio_design`, `image_prompts`, with continuity carried forward via a per-chunk summary seed. Frontend/subtab names are normalised through `_MODE_ALIASES` (e.g. the Novelist Swarm's `novelist` → `novel`). Because LLMs reliably under-deliver against their per-chunk word target, `_CHUNK_MULTIPLIER = 3` triples the computed chunk count so a page selection (30/100/200/300) lands near the requested length instead of ~⅓ of it.
- **`longform_engine.py`** — an alternate outline→generate→stitch background-job engine (local-first Ollama with cloud fallback), used by the studio path.
- **`creative_exporter.py`** — renders a parsed screenplay/novel to MD, HTML, DOCX, and PDF. Screenplay dialogue is the industry-standard **centered column** (equal 1.5in L/R indents, text left-aligned) with the **CHARACTER cue centered above** it; the same geometry is applied across HTML, DOCX (`python-docx`), and PDF (Playwright renders from the same HTML, so it inherits the layout).
- **Console safety:** `server.py` forces UTF-8 `stdout`/`stderr` on the Windows cp1252 console so Unicode glyphs (`→ ─ ✓`) in any `print()` can't raise `UnicodeEncodeError` and crash a generation thread.

## Dev Tooling
- **`dev_reload.py`** — a zero-dependency auto-reload supervisor. Watches `agent_os/**/*.py` (mtime polling, 0.4s debounce) and restarts `server.py` on save; also relaunches it if it exits/crashes. Run `python dev_reload.py` instead of `python server.py` during development so backend edits take effect without a manual restart.

## Connections
- The [Agent OS Speech Pipeline](agent-os-speech-pipeline.md) is a major component of this system.
- The architecture is informed by the principles in [Agentic Loops Architecture](agentic-loops-architecture.md).
- Code changes here follow the [Development Lifecycle](development-lifecycle.md) (branch → verify → pyrefly-clean commit → PR → merge).
- It is one of the primary "live workspaces" in this repository.

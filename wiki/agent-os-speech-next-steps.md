# Agent OS Speech — Next Steps (Handoff to Antigravity)

> Cold-start brief for the next agent (Antigravity) picking up the speech pipeline. Assumes no prior session context. Pairs with [agent-os-speech-pipeline.md](agent-os-speech-pipeline.md) (architecture) and [development-lifecycle.md](development-lifecycle.md) (how to land changes).

**As of 2026-06-29:** speech V1.1 + Sarvam (Indian languages) + audiobook orchestrator are merged to `master` (PR #3, #4). `master` is branch-protected: every change needs a **PR + green `build` CI check** (compileall `agent_os/speech` + `pytest test_parse_stage.py`), `enforce_admins=true`. Follow the [Code Development Lifecycle](development-lifecycle.md): branch → verify with a real run → commit (pyrefly hook) → push → PR → merge.

## P0 — Hygiene / unblock (COMPLETED 2026-06-29)
1. **Resolve the dirty working tree on `milestone/v1.1.0`.** (Completed: Cleaned and triaged working tree, fixed IncrementalExecutor cooperative cancellation bug).
2. **Commit the speech test suite.** (Completed: Added tests/speech fixtures and all offline test files, extended CI workflow `.github/workflows/ci.yml` to run the test suite).
3. **Commit the `CLAUDE.md` ADLC + handoff-process edits** (Completed: Staged and merged CLAUDE.md/AGENTS.md edits to master).

## P1 — Sarvam + audiobook completeness (COMPLETED 2026-06-29)
4. **Multi-speaker Indian-language casting.** (Completed: voice_map.json cycles available voices per speaker, enabling distinct speakers/voices for multi-speaker screenplays).
5. **Wire Sarvam `pace`/speed.** (Completed: Wired pace/speed to convert(), populated voice gender metadata for all 38 bulbul speakers, implemented auto-chunking & joining of texts >1000 characters).
6. **Audiobook book-level features.** (Completed: Implemented chapter resume skipping, parallel ThreadPoolExecutor chapter synthesis, and regex-based in-file chapter splitting).

## P2 — Governance / cleanup
7. **Resolve `EngineName.GCP`.** The enum value remains (`schema/models.py`) but the legacy GCP engine was deleted. Either implement a GCP engine in the new pipeline or remove the enum value.
8. **Harden CI.** Add a `pyrefly` type-check job (mirror the local pre-commit hook) and pip caching to `.github/workflows/ci.yml`.
9. **ADR-020.** Document the multi-engine cloud TTS (Sarvam) + audiobook orchestration decisions (repo convention: ADRs 014–019 already exist).
10. **Break-glass doc.** With `enforce_admins=true`, document how to temporarily relax `master` protection for an emergency hotfix.

## Pointers
- Engines: `agent_os/speech/engines/{kokoro,piper,sarvam}_engine.py`, registry `engines/registry.py`.
- Audiobook: `agent_os/speech/audiobook.py` + `cli audiobook`. Service/DAG: `agent_os/speech/service.py`.
- `.env` loads via `agent_os/env_boot.py` (keys: `GEMINI_API_KEY`, `SARVAM_API_KEY`). `.env` is gitignored.
- Verify: `python -m agent_os.cli audiobook corpus\telugu_sample.txt --engine sarvam` / `... corpus\book_demo --engine kokoro --parser benchmark --mp3`.

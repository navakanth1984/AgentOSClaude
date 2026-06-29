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
7. **Resolve `EngineName.GCP`.** (Completed: removed the dead enum member — legacy GCP engine was already gone — and migrated its only consumer, the `benchmark.py` mock fallback, to `EngineName.PIPER`; isolated `refactor:` commit.)
8. **Harden CI.** (Completed: added a `pyrefly` type-check step mirroring the local pre-commit hook, with `--python-interpreter-path "$(which python)"` to override the Windows path pinned in `pyrefly.toml`; enabled pip caching; folded in `test_audiobook_features.py` so CI runs all 9 offline test files. **Gotchas hit:** pyrefly is local-clean but CI-red because optional engine SDKs aren't installed there — use `--ignore-missing-imports <module>` *repeated once per module* (comma-lists don't split); and the Sarvam test executes `import sarvamai`, so that lightweight SDK had to be pip-installed in CI, not merely ignored for typing.)
9. **ADR-020.** (Completed: `docs/adrs/020-cloud-tts-and-audiobook-orchestration.md` — Sarvam bulbul:v3 as a drop-in `TTSEngine`, per-engine request chunking, audiobook orchestrator composing `SpeechService`.)
10. **Break-glass doc.** (Completed: `docs/devops/break-glass.md` — minimal-relaxation `gh` procedure grounded in the live `master` protection policy, with mandatory restore+verify steps.)

## P3 — Repo hygiene follow-ups (COMPLETED 2026-06-29)
> `.agents/` (tool-installed skill content, ~99MB / 543 files) was gitignored (PR #10). The remaining follow-ups have been resolved:
11. **Gitignore the remaining agent-tool dot-dirs.** (Completed: Gitignored ~29 editor/agent tool dot-dirs in `.gitignore` via PR #11, leaving `.claude/` user-controlled).
12. **Investigate the broken `nano-banana-pro-prompts-recommend-skill/` dirs.** (Completed: Cleaned up the dangling directory junctions/symlinks across all tool subdirectories, resolving the git warnings permanently).

## P4 — Dashboard Integration (COMPLETED 2026-06-29)

## P5 — Ingestion Fixes (COMPLETED 2026-06-29)
14. **DOCX/PDF Chapter Splitting.** (Completed: Patched `_split_in_file_chapters` in `audiobook.py` to extract text from `.docx` and `.pdf` files instead of reading them as plain text via PR #14).
15. **SpeechService Ingestion.** (Completed: Patched file loader in `SpeechService._execute_inner` (`service.py`) to parse binary `.docx`/`.pdf` files, resolving `UnicodeDecodeError` issues via PR #15).

## P6 — Endpoint + scale fixes (COMPLETED 2026-06-29, Claude/Opus session)
> Verified the audiobook path **end-to-end through the live `/speech/audiobook` web endpoint** (the dashboard "Create Audiobook" button), not just `/health`. Two real, previously-uncaught bugs surfaced and were fixed.
16. **Endpoint crashed on every request — package shadow.** (Completed, PR #17, merged.) `python agent_os/server.py` runs in script mode with `agent_os/` at `sys.path[0]`, so the speech subsystem's `import agent_os.env_boot` resolved to the sibling script `agent_os/agent_os.py` (a module that shadows the package) → `ModuleNotFoundError: ... 'agent_os' is not a package`, crashing the request thread. Fix: prepend the repo root to `sys.path` in `server.py` so the package wins. Verified: POST → completed job → `UI_Smoke.wav` (benchmark) and `Gemini_Smoke.wav` (live Gemini parser, 3 speakers → distinct voices).
17. **Whole book fails for kokoro AND sarvam — oversized single chapter.** (Completed, PR #19, merged.) A markerless doc was processed as one chapter; `KAALIKA_Screenplay.docx` (65k chars) → **one chapter of 863 chunks**. kokoro: `SynthesizeStage` rebuilds the ONNX session **per chunk** → OpenBLAS arena fragmentation → hard `abort()`. sarvam: 863 sequential HTTP calls, first failure raises → FAILED. Both show the generic `Chapter '<file>' failed (state=failed)`. Fix (`audiobook.py`): when no chapter markers exist, split docs > `MAX_MARKERLESS_CHAPTER_CHARS` (5000) into bounded chapters on line boundaries. Verified: full screenplay → 14 chapters (≤4997 chars); a bounded chapter → `COMPLETED`, 54 chunks, no abort.

## P7 — Next tasks (HANDOFF TO ANTIGRAVITY, opened 2026-06-29)
> Diagnosis is done and documented above; these are the follow-ups P6 deliberately deferred. Follow the ADLC (branch → verify with a real run → pyrefly commit → PR → merge). `master` is branch-protected; never `--no-verify`.
18. **[ROOT-CAUSE, kokoro speed] Reuse one warm engine across chunks.** The real driver behind the OpenBLAS crash is that `SynthesizeStage.run` calls `engine.initialize()/validate_model()/warmup()/shutdown()` **on every chunk** (`pipeline/stages/synthesize.py:62-68,223`), and `IncrementalExecutor` invokes it once per chunk (`pipeline/incremental_executor.py:114`). The reuse guard `session_reused` (`synthesize.py:63`) is **dead code**. Result: ~6s/chunk warmup overhead → a full kokoro book is ~90 min even after P6. Fix: gate `initialize/validate/warmup` on `not session_reused` and move `shutdown()` out of the per-chunk path (defer to `service._execute_inner` after `executor.run()`). The engine object is already shared via `context.config["tts_engine"]`. **Verify** warmup prints ONCE for a multi-chunk chapter and a full book completes. This is the P6 Option-B deferral.
19. **[robustness] Make `ContextStage` scale.** It calls Gemini in batches of 10 **regardless of the `parser` flag** (`pipeline/stages/context.py:82-88,103-113`) — a big chapter = dozens of slow sequential calls. Consider skipping context for `parser=benchmark`, parallelizing batches, or making it opt-in.
20. **[robustness] sarvam per-chunk failure shouldn't abort the book.** One failed network chunk among hundreds raises `RuntimeError` (`synthesize.py:144-146`) → whole job FAILED. Consider degrading (silent/placeholder chunk + recorded failure) like `ContextStage` does, so a transient 429/5xx doesn't nuke a long book.
21. **[hardening] Make the server launch package-safe by construction.** P6 fixed the `sys.path` shadow, but the root smell is `agent_os/agent_os.py` (a script) colliding with the `agent_os` package in script mode. Consider renaming the script (e.g. `orchestrator.py`) or running the server as `python -m agent_os.server` (requires converting `server.py`'s script-style imports to package-style).

## Pointers
- Engines: `agent_os/speech/engines/{kokoro,piper,sarvam}_engine.py`, registry `engines/registry.py`.
- Audiobook: `agent_os/speech/audiobook.py` + `cli audiobook`. Service/DAG: `agent_os/speech/service.py`.
- `.env` loads via `agent_os/env_boot.py` (keys: `GEMINI_API_KEY`, `SARVAM_API_KEY`). `.env` is gitignored.
- Verify: `python -m agent_os.cli audiobook corpus\telugu_sample.txt --engine sarvam` / `... corpus\book_demo --engine kokoro --parser benchmark --mp3`.

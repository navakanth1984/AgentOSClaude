# Agent OS Speech — Next Steps (Handoff to Antigravity)

> Cold-start brief for the next agent (Antigravity) picking up the speech pipeline. Assumes no prior session context. Pairs with [agent-os-speech-pipeline.md](agent-os-speech-pipeline.md) (architecture) and [development-lifecycle.md](development-lifecycle.md) (how to land changes).

**As of 2026-06-29:** speech V1.1 + Sarvam (Indian languages) + audiobook orchestrator are merged to `master` (PR #3, #4). `master` is branch-protected: every change needs a **PR + green `build` CI check** (compileall `agent_os/speech` + `pytest test_parse_stage.py`), `enforce_admins=true`. Follow the [Code Development Lifecycle](development-lifecycle.md): branch → verify with a real run → commit (pyrefly hook) → push → PR → merge.

## P0 — Hygiene / unblock (do first)
1. **Resolve the dirty working tree on `milestone/v1.1.0`.** ~41 uncommitted changes remain (WIP edits to `agent_os/speech/{service,executor,incremental_executor,route,interfaces,api}.py`, deletions, `memory_os/model-usage-log.json`, and the `CLAUDE.md` ADLC edit). Triage each: commit the keepers via branch→PR, discard the rest. Until this is sorted, branch switching/merging on that branch is risky.
2. **Commit the speech test suite.** These are untracked and missing from CI: `tests/speech/`, `test_segment_route_stage.py`, `test_synthesis_slice.py`, `test_smoke_kokoro.py`, `test_chaos.py`. Add them (branch→PR) and extend `.github/workflows/ci.yml` to run them so the gate is meaningful (currently only `test_parse_stage.py`).
3. **Commit the `CLAUDE.md` ADLC + handoff-process edits** (currently on disk only, in the WIP tree) so the per-session brief is durable on `master`.

## P1 — Sarvam + audiobook completeness
4. **Multi-speaker Indian-language casting.** Verify/finish per-character voice assignment for Sarvam via `voice_map.json` (route stage). Goal: a Telugu/Hindi screenplay casts distinct Sarvam speakers per character (38 v3 speakers available). Acceptance: a 2-speaker Telugu sample produces two distinct voices.
5. **Wire Sarvam `pace`/speed.** `SarvamEngine.synthesize` currently ignores `speed` — pass it as `pace` to `text_to_speech.convert`. Populate voice gender metadata (currently `"unknown"`) and validate `max_text_length=1000` against Sarvam's real per-request limit + multi-segment join.
6. **Audiobook book-level features.** Add: resume (skip already-completed chapters), parallel chapter processing (currently sequential), and in-file chapter splitting (split one file on `Chapter N` markers). File: `agent_os/speech/audiobook.py`.

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

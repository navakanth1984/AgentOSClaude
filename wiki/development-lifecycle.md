# Code Development Lifecycle

> The standard process for code changes in this workspace: branch → verify → commit → push → PR → merge, with a deprecate-before-delete rule for legacy removal.

This is the engineering counterpart to the KB "Continuous Loop" in [AGENTS.md](../AGENTS.md). It applies to **version-controlled code**; the wiki "never delete" guardrail applies to `sources/` KB content, not code.

## The lifecycle

1. **Branch** — never commit to `master`; use a feature or `milestone/*` branch.
2. **Implement + verify** — prove it works with a real run (not just type checks), keep tests green, and pass `pyrefly` (the pre-commit hook blocks on type errors; never bypass with `--no-verify`).
3. **Commit** — focused conventional commits (`feat`/`fix`/`refactor`/`docs`); keep deletions/refactors separate from features; end with the `Co-Authored-By: Claude …` trailer.
4. **Push** — `git push -u origin <branch>` (first time sets upstream).
5. **PR** — `gh pr create --base master`. Draft while a milestone is ongoing, ready when the unit of work is complete. The PR is the CI gate and the durable reviewable record. Branch-only work is **not** the finish line.
6. **Review/CI → merge** — merge via PR (one revertable merge commit), then delete the branch.

## Removing legacy code (deprecation lifecycle)

Never blind-delete. The safe, best-practice order is:

**deprecate → migrate every importer → verify each still works → delete → isolated `refactor:` commit**

- **Deprecate**: add a `DeprecationWarning` and point to the replacement.
- **Migrate**: grep for *all* call sites; repoint each (behavior preserved where possible).
- **Verify**: run each migrated caller before deleting anything.
- **Delete**: legitimate here because git makes it revertable — distinct from the KB "never delete" rule.

Worked example (2026-06-29): retiring `agent_os/audiobook_pipeline.py` + `agent_os/tts/` — deprecated, migrated `agent_os.py`'s `audiobook` command + `direct_tts.py` to the V1.1 pipeline, verified both, then deleted in a standalone `refactor:` commit. See [agent-os-speech-pipeline.md](agent-os-speech-pipeline.md) and [PR #3](https://github.com/navakanth1984/AgentOSClaude/pull/3).

## Why a PR (not branch-only)
- A permanent, linkable, reviewable record of the diff + rationale.
- An explicit CI gate before code reaches `master`.
- An atomic, revertable merge commit.

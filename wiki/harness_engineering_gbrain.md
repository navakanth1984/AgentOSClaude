# Harness Engineering Platform (gbrain)

**Status**: Verified 2026-09-09 | Canonical Knowledge Base | Governing Operating System

---

## 1. System Identity & Core Philosophy

Harness Engineering formalizes the operational shift from "prompting raw models" to building deterministic, cybernetically governed execution environments:

$$\text{Agent} = \text{Model} + \text{Harness}$$

- **The Model** is a probabilistic token predictor (the engine).
- **The Harness** is the deterministic control plane, sensory nervous system, and steering apparatus (scaffolding, feedback sensors, oracles, mutation gates, and ambient affordances).

### The Cybernetic Steering Law (Ashby's Law Applied to AI)
> **When an agent errs, do not merely re-prompt the model.**  
> **Upgrade the harness**: engineer a missing feedforward guide or add an automated feedback sensor into the repository so the failure class is mechanically eliminated forever.

---

## 2. Architecture Invariants

1. **Shift Computational Left**: Computational sensors (typechecks, AST linters, module boundary checks) must execute in $<5$ seconds. Never burn expensive reasoning tokens on errors a compiler catches in milliseconds.
2. **Positive Prompt Injection**: Linters and test formatters must never output raw error codes. They must inject actionable self-correction instructions (the "why", the violated layer, and the exact refactoring remedy).
3. **Anti-Vacuous Test Gate**: High line coverage is an unreliable proxy for correctness. Mutation testing (`Stryker` / `mutmut`) is mandatory on AI-generated unit tests to verify that tests actively kill synthetic bugs.
4. **The 3-File Oracle Boundary for Subagents**:
   - `program.md` — Read-only goal contract, constraints, and scalar metric ($S$).
   - `train.py` / target code — The single agent-modifiable implementation file.
   - `prepare.py` / test oracle — **Locked Evaluator Oracle** (zero read/write access for the generating agent).
5. **Universal Verification Order**:
   $$\text{Implementation} \rightarrow \text{Typecheck} \rightarrow \text{Tests} \rightarrow \text{Mutation Check} \rightarrow \text{Build} \rightarrow \text{DevTools/Browser QA} \rightarrow \text{Staging}$$
6. **One Canonical Copy (Skillify Discipline)**: Canonical skills live strictly at `C:\Users\navka\.claude\skills\<name>\`. All other roots link via NTFS junctions. Non-NTFS drives (`E:`) mirror explicitly without drift.

---

## 3. Verified Implementations & Tool Map

### Verified
- **Canonical Skill Structure**: `C:\Users\navka\.claude\skills\harness-engineering\` created and verified containing `SKILL.md`, `scripts/verify_harness.py`, `templates/` (`dependency-cruiser.js`, `stryker.config.json`, `subagent_oracle_contract.md`), and `references/harness_engineering_spec.md`.
- **Multi-Runtime NTFS Distribution**: Verified active junctions via `Get-Item | Select LinkType, Target`:
  - `C:\Users\navka\.agents\skills\harness-engineering` $\rightarrow$ `Junction`
  - `C:\Users\navka\.gemini\config\skills\harness-engineering` $\rightarrow$ `Junction`
  - `C:\Users\navka\.codex\skills\harness-engineering` $\rightarrow$ `Junction`
  - `C:\Users\navka\.gemini\skills\harness-engineering` $\rightarrow$ `Junction`
  - `e:\navakanth001\.agents\skills\harness-engineering` $\rightarrow$ Mirrored physical copy (exFAT volume constraint).
- **System Directives Synchronized**:
  - `C:\Users\navka\.claude\CLAUDE.md`: Injected Harness Mandate, Cybernetic Steering Law, and skill triggers.
  - `C:\Users\navka\.codex\AGENTS.md`: Injected Pillar 1 Harness & Control-Layer Governance.
  - `C:\Users\navka\.gemini\config\AGENTS.md`: Injected Golden Formula, cybernetic rules, and 7-stage verification order.
  - `C:\Users\navka\.gemini\GEMINI.md`: Directive bound to canonical harness standards.
  - `C:\Users\navka\AGENTS.md` & `e:\navakanth001\AGENTS.md`: Injected Pillar 1 governance and sub-minute verification loops.
- **Automated Sensor Audit**: `py C:\Users\navka\.claude\skills\harness-engineering\scripts\verify_harness.py e:\navakanth001` executed in $<2$ seconds, evaluating lean `AGENTS.md`, typecheck sensors, module boundary rules, and mutation gates.
- **Session Auto-Save Hook**: `py C:\Users\navka\navakanth001\agent_os\session_end.py` executed cleanly, writing Obsidian note to `01-Projects/AI-Automation/` and updating `memory_os/session_memory/session_20260909.md`.
- **Global Skill Ingestion & Anti-Bloat Harness (Verified 2026-09-12)**:
  - Onboarded high-leverage agent skill suites (`DietrichGebert/ponytail`, `tt-a1i/archify`, `blader/humanizer`, `ayghri/i-have-adhd`, `mattpocock/skills`, `humanlayer/skills`, `timharris707/skills`) into canonical home `C:\Users\navka\.claude\skills`.
  - Resolved 26 circular junction loops (restored from backups and G: workspace), bringing canonical root `C:\Users\navka\.claude\skills` to **253 pure physical skills** with 0 internal links.
  - Deployed universal synchronizer `scripts/sync-skills.ps1` linking **1,265 NTFS junctions** across all 5 C: and G: agent roots (`C:\Users\navka\.agents\skills`, `C:\Users\navka\.gemini\config\skills`, `C:\Users\navka\.codex\skills`, `C:\Users\navka\navakanth001\.agents\skills`, and `G:\navakanth001\.agents\skills`) plus 100% robocopy mirror to `E:\navakanth001\.agents\skills`.
  - Upgraded `CLAUDE.md` with **`improve-claude-md`** `<important if>` blocks and **`i-have-adhd`** immediate-action / zero-filler output discipline.
  - Verified **`ponytail`** anti-bloat ladder: demonstrated -75.9% LOC cut on real code benchmark while preserving 100% safety invariants.
  - Integrated and verified **`context-mode`** MCP server (v1.0.169) with local SQLite FTS5 BM25 search and Bun/Python runtime support.
  - Delivered 2 verified showcase interactive architecture maps via **`archify`** (`mvct-architecture.html` and `whiteboard-architecture.html`).
  - Cleared DOS reserved device collision `nul` in `mvct-mrp-core` using Windows extended UNC syntax.

---

## 4. Known Gaps

1. **Root-Level Monorepo Sensor Deficit**: The root workspace directory `e:\navakanth001` scores 30/100 on `verify_harness.py` because root-level `tsconfig.json`, `.dependency-cruiser.js`, and `stryker.config.json` are absent. Subprojects (e.g. `loans-ai-platform`, `nthdimensionacademy-react`) possess their own build configurations, but cross-subproject boundary validation is not yet unified.
2. **Project-Level Mutation Testing Rollout**: `stryker.config.json` and `mutmut` configuration templates are packaged in the skill, but have not yet been instantiated inside individual web and Python service projects.
3. **Live Subagent Oracle Test**: The 3-file subagent isolation boundary (`docs/subagent_harness_template.md` and `templates/subagent_oracle_contract.md`) is specified and published, but has not yet executed a production multi-agent PR workflow under an adversarial critic agent.
4. **`python` App Execution Alias shadowing the real interpreter (found 2026-09-09, not yet fixed)**: on this machine, the bare `python` command resolves to the Windows Store's App Execution Alias stub ("Python was not found; run without arguments to install...") rather than `C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe`. This silently broke every `PreToolUse`/`PostToolUse` Bash hook that shells out to `python` for the length of a session before being noticed — a harness sensor was firing failures the whole time with no one watching. Per the Cybernetic Steering Law this should not be re-prompted around each time; the actual fix is one of: (a) disable the `python.exe`/`python3.exe` execution aliases in Settings → Apps → Advanced app settings → App execution aliases, or (b) point hook configs at the absolute interpreter path instead of the bare `python` command. Neither has been applied yet.
5. **Locked-file reads need a lock-free signal, not admin (found 2026-09-09)**: a Windows process (e.g. Chrome) holding a file open under an OS-level exclusive lock blocks even a plain read-only copy (`shutil.copy2` → `WinError 32`) — the standard "read it anyway" library fallback (`browser_cookie3`'s VSS shadow-copy path) requires admin, which a harness generally shouldn't assume it has. General pattern worth reusing: when the state you need lives inside a file you can't safely read, look for the *same information already exposed through an unlocked side-channel* — here, a window's title string (readable via `pywin32`/`win32gui` with zero privilege) carried the exact signal (signed-in vs. not) that the locked cookie database would have. Applied in [agent-os.md](agent-os.md#notebooklm-sync-data-loss-fix-2026-09-09); generalized into the new [[windows-desktop-app-diagnosis-skillify]] skill.

---

## 5. Companion Documents

- `wiki/agent_control_taxonomy.md` — Section 7: Harness, Loop, and Graph Engineering.
- `wiki/log.md` — Dated execution entries.
- `docs/subagent_harness_template.md` — Subagent 3-file isolation contract.
- `~/.claude/skills/harness-engineering/SKILL.md` — Canonical skill manual.

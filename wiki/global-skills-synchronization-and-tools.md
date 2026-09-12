# Global Skills Synchronization & AI Tools Engine

> **Status:** Superseded — see §0. The copy-based watcher described below is not the current
> mechanism; junction-based linking (per `CLAUDE.md` standing rules) is now enforced instead.
> **Last Verified:** 2026-08-24
> **Canonical Implementation (current):** NTFS directory junctions from `.agents\skills`,
> `.gemini\config\skills`, `.codex\skills` → `C:\Users\navka\.claude\skills\<name>` (one canonical
> copy, link never copy — see `CLAUDE.md` standing rules and the `skillify` skill).
> **Canonical Implementation (legacy, do not trust):** [`scripts/sync_global_skills.py`](file:///c:/Users/navka/navakanth001/scripts/sync_global_skills.py) | [`scripts/watch_skills_sync.py`](file:///c:/Users/navka/navakanth001/scripts/watch_skills_sync.py)

## 0. 2026-08-24 correction

This document's original body (§1–§4 below) described a **copy-based** watcher achieving
"100% Parity" across four roots. That claim was not evidence-backed for the current state:

- **Verified 2026-08-24** by direct filesystem inspection (`Get-ChildItem ... Attributes -match
  "ReparsePoint"`): before today's fix, `.agents\skills` had only 2/168 real junctions (166 were
  plain duplicate folders), `.gemini\config\skills` had 10/169, `.codex\skills` had 154/169.
  These were copies, not links — exactly what this doc's watcher would produce, and exactly
  what `CLAUDE.md`'s "one canonical copy — link, never copy" rule forbids.
- **Verified 2026-08-24**: `GlobalSkillsWatcher.vbs` does **not** exist at the claimed Startup
  path, and no running process matches `watch_skills_sync.py`. The watcher is not currently
  active. If it is ever restarted, it will re-introduce duplicate copies and undo the junction
  fix below — **do not re-enable it without first changing it to create junctions, not copies.**
- **Fix applied 2026-08-24**: all non-junction skill folders in the three global roots
  (`.agents\skills`, `.gemini\config\skills`, `.codex\skills`) that had a canonical match in
  `~/.claude/skills` were renamed to `<name>.pre-link-20260824` (never deleted) and replaced
  with real NTFS junctions to the canonical copy. Verified after the fact with
  `Get-Item | Select LinkType, Target` — not trusted from the fix script's own "OK" output.
  Final state: **168/168 real junctions** in all three roots. `super-skill` (`.gemini`, no
  canonical source) and `.system` (`.codex`, not a skill) were left untouched — no guessing.
- **Backups relocated 2026-08-24**: the 338 renamed backup folders (166 + 158 + 14, after
  excluding backups pre-dating today, plus a self-corrected mistake — see below) were moved
  to `C:\Users\navka\.claude\skills-backup-archive-20260824\{agents,gemini,codex}\`. Nothing
  deleted, per standing rule.
- **Self-caught error during cleanup**: the first move pass matched folder names containing
  `.pre-link-\d{8}`, which also matched *real, currently-valid* junctions whose canonical name
  legitimately contains that substring (e.g. `higgsfield.pre-link-20260822`,
  `agent-studio-master.pre-link-20260806` — these are actual distinct skills in
  `~/.claude/skills`, not backups). 21 real junctions (7 per root) were mistakenly archived,
  caught by checking `ReparsePoint` on the archived items, and moved back. Final verification
  confirmed 168/168 junctions in every root with zero non-junction items misplaced.

**Numbers in §2 below (164/163/161/161, "100% Parity") are legacy and describe the pre-fix,
copy-based state. Do not cite them as current.**

### 0.1 2026-09-12 expansion & verification
- **New Skill Suites Onboarded**: `ponytail` (+5 helpers), `archify`, `humanizer`, `i-have-adhd`, `mattpocock/skills` (37 skills), `humanlayer/skills` (5 skills), and `timharris707/skills` (24 skills) installed directly to canonical root `C:\Users\navka\.claude\skills`.
- **Circular Junction Repair & Full Restoration**: Identified and healed 26 circular mutual junction references (e.g. `cinematic-pipeline`, `firecrawl*`, `hyperframes*`, `mcp-builder`, `multimodal-llm`, `gsap`, etc.) by restoring canonical physical directories from `C:\Users\navka\.claude\skills-backup-archive-20260824` and `G:\navakanth001\.agents\skills`. Canonical root `C:\Users\navka\.claude\skills` now houses **253 100% physical skills** with 0 internal symlinks/junctions.
- **Universal Dual-Drive Sync (`scripts/sync-skills.ps1`)**:
  - Upgraded `sync-skills.ps1` to detect mount points and automatically mesh across all 5 NTFS runtime roots:
    - `C:\Users\navka\.agents\skills` (253 junctions)
    - `C:\Users\navka\.gemini\config\skills` (253 junctions)
    - `C:\Users\navka\.codex\skills` (253 junctions)
    - `C:\Users\navka\navakanth001\.agents\skills` (253 junctions)
    - `G:\navakanth001\.agents\skills` (253 junctions)
  - Successfully linked **1,265 active NTFS directory junctions** across all C: and G: roots.
  - Automated robocopy mirroring to `E:\navakanth001\.agents\skills` (exFAT volume, 253 physical copies).
- **Context Mode MCP Integration**: Registered and validated `context-mode` (v1.0.169) for sandboxed code evaluation and local SQLite FTS5 search.

---

## 1. Overview & Architecture

The **Global Skills Synchronization Engine** solves cross-volume context isolation across multiple AI agent harnesses (Antigravity, Claude Code, Gemini CLI, Codex). When operating on external drives (e.g., `E:\` or remote worktrees), AI tools cannot load workspace-scoped skills (`navakanth001\.agents\skills\`) and must load from global user configuration paths.

The engine establishes a **4-way full-mesh synchronization** across all global and local runtime directories:

```
        ┌──────────────────────────────────────────────────────────┐
        │       REAL-TIME SKILLS SYNCHRONIZATION WATCHER           │
        │             (1.5s Debounce, Sub-3s Parity)               │
        └───────┬────────────────────┬────────────────────┬────────┘
                │                    │                    │
                ▼                    ▼                    ▼
     ~/.claude/skills     ~/.gemini/config/skills   ~/.agents/skills
      (Claude Global)       (Antigravity/Gemini)     (Codex Global)
                ▲                    ▲                    ▲
                │                    │                    │
                └────────────────────┴────────────────────┘
                                     ▲
                                     │
                        navakanth001/.agents/skills
                             (Local Workspace)
```

---

## 2. Directory Parity & Telemetry

| Path | Runtime Scope | Initial Count | Synchronized Count | Status |
| :--- | :--- | :---: | :---: | :---: |
| `C:\Users\navka\.claude\skills\` | Claude Code Global | 38 | **164** | 🟢 100% Parity |
| `C:\Users\navka\.gemini\config\skills\` | Antigravity / Gemini CLI Global | 45 | **163** | 🟢 100% Parity |
| `C:\Users\navka\.agents\skills\` | Codex / Agents Framework Global | 35 | **161** | 🟢 100% Parity |
| `C:\Users\navka\navakanth001\.agents\skills\` | Primary Workspace Local | 95 | **161** | 🟢 100% Parity |

---

## 3. Real-Time Watcher Daemon & Automation

- **Watcher Engine:** `scripts/watch_skills_sync.py` powered by Python `watchdog 6.0.0`.
- **Debounce Window:** 1.5 seconds. Batches multiple consecutive file writes into a single atomic synchronization pass.
- **Self-Trigger Guard:** Automatically suppresses synthetic events generated by the sync pass itself.
- **Windows Startup Integration:** `C:\Users\navka\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\GlobalSkillsWatcher.vbs` executes on Windows user logon in silent hidden window mode.

### Control Commands
```powershell
# Start background watcher
powershell -File scripts/start_skill_watcher.ps1

# Stop background watcher
powershell -File scripts/stop_skill_watcher.ps1

# Run manual one-shot sync
uv run python scripts/sync_global_skills.py
```

---

## 4. Deployed AI Tools & Frameworks (Session 2026-08-22)

### A. Needle 2.0 (Cactus Compute SLM)
- **Directory:** [`tools/needle/`](file:///c:/Users/navka/navakanth001/tools/needle/)
- **Runtime:** Python 3.12, `cactus-needle==2.0.9`, on-device CPU execution.
- **Resource Footprint:** **43.3 MB RAM**, 114–223 tokens/s decode.
- **Active Agent:** [`tools/needle/query_repo_agent.py`](file:///c:/Users/navka/navakanth001/tools/needle/query_repo_agent.py) querying repository lore (*Vaayuthram*, *DAAVA*, *KAALIKA*) and engineering milestones (*MVCT*, *BLEUUBOARD*) with 0 cloud tokens.

### B. MoneyPrinterTurbo Automated Video Synthesis
- **Directory:** [`tools/MoneyPrinterTurbo/`](file:///c:/Users/navka/navakanth001/tools/MoneyPrinterTurbo/)
- **Integration:** System FFmpeg 8.1, Edge-TTS (ChristopherNeural / SoniaNeural), MoviePy.
- **Verified Output:** Generated the official *Vaayuthram Vaalagaathram* teaser trailer (1080p, 19s) combining 8 visual plate assets with synchronized voiceover.

### C. Minto Pyramid Structured Communication Skill
- **Location:** [`.agents/skills/minto-pyramid/SKILL.md`](file:///c:/Users/navka/navakanth001/.agents/skills/minto-pyramid/SKILL.md)
- **Protocol:** Enforces Barbara Minto's Pyramid Principle:
  1. *Answer First* (Executive conclusion directly stated).
  2. *SCQ Context* (Situation -> Complication -> Question).
  3. *MECE Arguments* (Mutually Exclusive, Collectively Exhaustive grouping).
  4. *Grounded Evidence* (File paths, concrete code symbols, latency benchmarks).

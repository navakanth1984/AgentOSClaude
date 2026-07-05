# AI Tool Sync
AI tool instructions in this workspace are synced through one canonical knowledge-base contract, then mirrored into each tool's Markdown entry point.

## Canonical Contract
- [Operating Brief](CLAUDE.md) is the canonical operating brief for the shared knowledge base.
- [Knowledge Base Protocol](knowledge-base-protocol.md) defines the graph layer plus wiki layer read/feed contract.
- [Knowledge Base Map](knowledge-base-map.md) is the cross-repo front door for locating each project and its graph/wiki layers.
- [AGENTS.md](../AGENTS.md) is the tool-neutral root mirror for agents that read repository instructions directly.

## Tool Entry Points
- Claude Code / Claude Desktop: [CLAUDE.md](../CLAUDE.md) and [.claude/CLAUDE.md](../.claude/CLAUDE.md).
- Antigravity: [.antigravity.md](../.antigravity.md).
- Gemini CLI: [GEMINI.md](../GEMINI.md) plus Gemini agent profiles under [.gemini/agents/](../.gemini/agents/).
- Codex: [AGENTS.md](../AGENTS.md) plus the local Codex bridge [.codex/AGENTS.md](../.codex/AGENTS.md).
- Shared agent assets: [.agents/rules/](../.agents/rules/), [.agents/workflows/](../.agents/workflows/), and [.agents/skills/](../.agents/skills/) provide reusable rules, workflows, skills, and sub-agent profiles for tools that can consume them.

## Sync Rules
- Keep [Operating Brief](CLAUDE.md), [Knowledge Base Protocol](knowledge-base-protocol.md), and [Knowledge Base Map](knowledge-base-map.md) as the source of truth; tool-specific Markdown files should point back to them instead of duplicating full policy.
- When a tool changes behavior or gains a new folder, update this page, [AGENTS.md](../AGENTS.md), and the relevant tool entry point in the same session.
- **Standard practice:** any new Claude Code command or skill that encodes a reusable practice (not a one-off task) must be mirrored into [.agents/workflows/](../.agents/workflows/) (or `.agents/skills/`) in the same session it's created, plus a short wiki page if the practice is stable expertise worth documenting once (OKF-style). This keeps Gemini, Antigravity, and Codex able to run the same practice instead of it being Claude-only. Example: [design-extract](../.claude/commands/design-extract.md) mirrored to [.agents/workflows/design-extract.md](../.agents/workflows/design-extract.md), documented in [design-extraction-workflow.md](design-extraction-workflow.md).
- Do not fold live project workspaces or tool caches into `sources/`; map them with overview pages and graph layers instead.
- Do not commit secrets, auth files, logs, SQLite state, cache folders, or generated plugin caches from `.codex/`, `.claude/`, `.gemini/`, `.agents/`, or other tool directories unless a specific tracked source file is intentionally being changed.
- After code changes, refresh the relevant graph with `graphify update <repo-path>` and record the result in [log.md](log.md).

## Current Tool Folders
- `.claude/` contains Claude-specific commands, graphify skill bridge, local settings, and launch configuration.
- `.gemini/` contains Gemini CLI settings and agent profiles.
- `.codex/` contains Codex local runtime state, skills, plugin caches, automations, logs, sessions, and the local `AGENTS.md` bridge.
- `.agents/` contains shared skills, rules, workflows, and agent profiles usable by multiple agent tools.
- `.antigravitycli/` contains Antigravity CLI local state.

## Maintenance Checklist
- Root instructions mention all active tools: Claude Code, Antigravity, Gemini, Codex, and generic agents.
- Each tool-specific Markdown bridge points to the same KB protocol and map.
- `wiki/index.md` links this sync page.
- `wiki/log.md` records sync work with the exact files changed.

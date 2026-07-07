# Codex Local Bridge

Codex in this workspace follows the same self-improving knowledge-base contract as Claude Code, Antigravity, Gemini, and other agents.

Read first:
- `../AGENTS.md` — root tool-neutral instructions.
- `../wiki/CLAUDE.md` — canonical operating brief.
- `../wiki/knowledge-base-protocol.md` — graph + wiki read/feed contract.
- `../wiki/knowledge-base-map.md` — cross-repo front door.
- `../wiki/ai-tool-sync.md` — AI tool folder and Markdown bridge inventory.

Do not treat `.codex/` runtime state, logs, auth, SQLite files, plugin caches, or generated imports as knowledge sources to ingest wholesale. Map durable behavior in `wiki/` pages and keep cache/state out of source commits unless explicitly requested.

# Claude Local Bridge

Claude-specific commands and skills in `.claude/` defer to the shared workspace knowledge-base contract.

Read first:
- `wiki/CLAUDE.md` — canonical operating brief.
- `wiki/knowledge-base-protocol.md` — graph + wiki read/feed contract.
- `wiki/knowledge-base-map.md` — cross-repo front door.
- `AGENTS.md` — tool-neutral root mirror.
- `wiki/ai-tool-sync.md` — AI tool folder and Markdown bridge inventory.

Graph rule: use `.graphify/` per repo/app, prefer `graphify query/path/explain` or MCP graph tools before raw grep for architecture questions, and run `graphify update <repo-path>` after code changes.

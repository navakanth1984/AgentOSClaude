---
date: 2026-06-11
tags: [obsidian, dashboard, integration, note-viewer]
project: "Personal Knowledge System"
source: "Agent OS Dashboard Upgrade"
---

# Agent OS Dashboard Note Viewer Upgrade

## Key Idea
The Agent OS Dashboard now supports viewing and opening Obsidian notes directly from the "Vault Search" and "Recent Notes" lists. Clicking a note displays its content inside a responsive split-pane previewer on the dashboard, alongside a direct deep-link to open it in desktop Obsidian.

## Details
1. **Endpoint Implementation**:
   - Added `GET /note?path=...` in `server.py` which resolves and reads the target markdown file.
   - Built-in path traversal security checks to ensure only files within the configured `VAULT_PATH` are accessible.
2. **Dashboard UI Improvements**:
   - Updated `tab-search` to use a responsive flexbox split layout (hiding/showing the previewer dynamically).
   - Rendered YAML frontmatter inside a nice monospace box.
   - Constructed Obsidian deep links (`obsidian://open?vault=Obsidian%20Vault&file=<relative-path>`) dynamically for every note.
   - Wired up click handlers on both search results and recent notes to open the viewer.

## Action / Next Steps
- [ ] Open http://localhost:8765/dashboard.
- [ ] Click the **Vault Search** tab.
- [ ] Select any note from the **Recent Notes** list to view its contents and frontmatter.
- [ ] Click **Obsidian ↗** next to any note to test launching desktop Obsidian directly to that file.

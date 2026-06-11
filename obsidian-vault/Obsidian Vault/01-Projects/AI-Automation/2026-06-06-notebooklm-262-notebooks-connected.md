---
date: 2026-06-06
tags: [notebooklm, agent-os, milestone]
project: "AI-Automation"
source: "Agent OS"
---

# NotebookLM — 262 Notebooks Connected

## Key Idea
Agent OS successfully connected to NotebookLM via Playwright cookie injection. 262 notebooks found.

## Details
NotebookLM connection fully working via cookie injection.
262 notebooks discovered. Titles show as 'Untitled' — scraper needs selector fix.
URLs are all correctly captured (UUIDs).

First notebook URL: /notebook/2c4f0f26-0797-4cc0-a350-48c4b70d14cc
Last notebook URL:  /notebook/6ddbb534-fb9e-47a5-ac2c-06c65ecd07ec

Next: fix list_notebooks() selector to read actual titles from NotebookLM DOM.

## Action / Next Steps
- [ ] Fix list_notebooks() CSS selector to get real titles
- [ ] Open a notebook and scrape its sources/studio content
- [ ] Wire studio content → asset_library auto-download

---
date: 2026-06-30
time: Session End
session_id: 2026-06-30-notebooklm-fix
tags: [session, memory, notebooklm-agent, dom-debugging, fix]
---

# Session Summary: NotebookLM Agent DOM Selector Fix

## What We Worked On

**NotebookLM agent source/notebook name extraction bug**: The `notebooklm_agent.py` was displaying "Untitled" for all notebooks instead of their real names. Debugged the root cause in NotebookLM's Angular app HTML structure and implemented the correct DOM selector pattern using `aria-labelledby`.

## Key Findings and Fix

### Root Cause Analysis
- NotebookLM's notebook link has structure: `<a href="/notebook/{uuid}">` with empty text content
- Real title is NOT a child element — it's a **sibling** element using an accessibility pattern
- The link uses `aria-labelledby="project-{uuid}-title ..."` to reference the title element
- Title lives in `<span id="project-{uuid}-title">Notebook Name</span>`

### First Attempt (Failed)
- Checked for `aria-label` attribute on the link — didn't exist
- This was a dead end

### Correct Solution (Working)
```javascript
// Extract the aria-labelledby IDs
const ariaLabelledBy = link.getAttribute('aria-labelledby');
const ids = ariaLabelledBy.split(/\s+/);

// Find the ID that ends with '-title'
const titleId = ids.find(id => id.endsWith('-title'));

// Fetch the actual title from the sibling element
if (titleId) {
  const titleElement = document.getElementById(titleId);
  if (titleElement) {
    name = titleElement.textContent.trim();
  }
}
```

### Evidence
- Examined NotebookLM DOM snapshot at `agent_os/asset_library/notebooklm_dom.html`
- Pattern confirmed: `aria-labelledby` points to a **sibling**, not a child
- Multiple aria-labelledby IDs can exist (space-separated); filter for `-title` suffix

## Implementation Location
- **File**: `C:\Users\navka\navakanth001\agent_os\notebooklm_agent.py`
- **Function**: Source/notebook name extraction logic
- **Method**: Parse `aria-labelledby`, find `-title` ID, use `document.getElementById()` to resolve the sibling

## Concepts Learned
- ARIA accessibility attributes (especially `aria-labelledby`) can point to **sibling** elements, not just children
- Angular/modern web apps often hide text content and rely on accessibility attributes for rendering
- Multi-ID aria-labelledby requires space-split + filter logic, not naive first-element grab
- Always inspect the actual DOM structure when a simple `.querySelector()` fails

## Open Threads / Next Steps
- None — fix is complete and verified against the actual DOM snapshot
- Similar pattern may apply to other NotebookLM elements; worth checking if display names fail elsewhere

## Files Modified
- `agent_os/notebooklm_agent.py` — updated source/notebook name extraction function
- Evidence file: `agent_os/asset_library/notebooklm_dom.html` (snapshot of NotebookLM page DOM)

## Technical Details
- Session focus: Tier 1-2 debugging (DOM analysis)
- Model used: Haiku 4.5
- No commits made this session — fix was isolated debugging work

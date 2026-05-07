Take the user's input and save it as a structured note to the Obsidian vault Inbox.

Vault inbox path: C:\Users\navka\OneDrive\Documents\Obsidian Vault\00-Inbox\

Steps:
1. Parse the user's input to extract: title, key idea, details, tags, project (AI-Automation or Personal-Knowledge), and source if provided
2. Generate a filename: YYYY-MM-DD-kebab-case-title.md using today's date
3. Write the note using this exact format:

```
---
date: YYYY-MM-DD
tags: [tag1, tag2]
project: "Project Name"
source: "URL or description"
---

# Title

## Key Idea
One sentence summary of the core idea.

## Details
Full details, expanded from user's input.

## Action / Next Steps
- [ ] First next step
```

4. Save to the vault Inbox folder
5. Confirm to the user: filename, path, tags used, and which project it was linked to

The user's input to forge is: $ARGUMENTS

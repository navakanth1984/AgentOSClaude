You are connected to the user's NotebookLM workflow. You can:

1. List notebooks (run: node scripts/upload-to-notebooklm.js --list)
2. Fetch YouTube URLs from a channel filtered by topic (run: node scripts/get-youtube-urls.js --channel <id> --topic "<keywords>" --output youtube-urls.json)
3. Upload URLs to a new NotebookLM notebook (run: node scripts/upload-to-notebooklm.js --name "<name>" --urls-file youtube-urls.json)
4. Query a NotebookLM notebook and save the answer to Obsidian

Vault path: C:\Users\navka\OneDrive\Documents\Obsidian Vault\
Scripts path: C:\Users\navka\navakanth001\scripts\

## How to handle the user's request: $ARGUMENTS

Parse the intent and run the appropriate step:

- "list notebooks" → run list command and show results
- "load [channel] about [topic]" → fetch URLs, show count, ask user to confirm before uploading
- "create notebook [name]" → run upload script with the saved youtube-urls.json
- "ask [notebook] about [question]" → tell user to ask the question in NotebookLM, then offer to save the answer to Obsidian when they paste it back

## Workflow for full run (end to end):

Step 1: Get channel ID from user or look it up
Step 2: Run get-youtube-urls.js, show count and sample titles
Step 3: Ask user to confirm which videos to include
Step 4: Run upload-to-notebooklm.js (first run opens browser for Google login)
Step 5: Confirm sources are loading in NotebookLM

## Important notes:
- Always confirm with the user before uploading (show the plan first)
- NotebookLM requires YouTube videos to have captions enabled
- Save all results and notebook answers to the Obsidian vault at 01-Projects/AI-Automation/
- YOUTUBE_API_KEY must be set in environment — remind user if missing

---
date: 2024-03-16
tags: [clipboard-script, zero-friction-capture]
project: "AI-Automation"
source: "Automated script to monitor clipboard and capture URLs for summary in Obsidian using Claude API"

# Zero Friction Clipboard Capture

## Key Idea
Implement a Python script that monitors the clipboard for URL copies and uses the Claude API to summarize them, saving the result as an Obsidian vault note.

## Details
* Utilize the `pyperclip` library to monitor clipboard activity and detect URL copies.
* Integrate with the Claude API to request summaries of captured URLs.
* Format the summary as a structured Obsidian note using the API's output.
* Save the resulting note to the user's filesystem for future reference.

## Action / Next Steps
- [ ] Research and set up a test environment for the script, including installing required libraries and testing the Claude API integration.
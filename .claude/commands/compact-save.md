# /compact-save

Save current context to memory, then compact the chat to free up tokens.

## Steps

1. Write a session note to `memory/YYYY-MM-DD-session.md` capturing:
   - What was built
   - Key decisions made
   - Open questions
   - Next steps
2. Append a one-liner to CLAUDE.md change log
3. Run `/compact` to clear non-essential tokens from context

Use this when context usage exceeds 50%.

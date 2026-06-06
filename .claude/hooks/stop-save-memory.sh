#!/bin/bash
# Runs on every Claude Code session stop.
# Saves a session note to memory/ and appends a change log entry to CLAUDE.md.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MEMORY_DIR="$REPO_DIR/memory"
CLAUDE_MD="$REPO_DIR/CLAUDE.md"
DATE=$(date +%Y-%m-%d)
SESSION_FILE="$MEMORY_DIR/$DATE-session.md"
OBSIDIAN_VAULT_PATH="${OBSIDIAN_VAULT_PATH:-C:\\Users\\navka\\navakanth001\\obsidian-vault}"
OBSIDIAN_AGENT_DIR="$OBSIDIAN_VAULT_PATH/01-Projects/AgentOS"

mkdir -p "$MEMORY_DIR"

# Write session note if it doesn't exist yet today
if [[ ! -f "$SESSION_FILE" ]]; then
  cat > "$SESSION_FILE" <<EOF
---
date: $DATE
session: auto
tags: [agentOS, session-note]
---

## What was built

<!-- Fill in or let Claude auto-populate -->

## Key decisions

## Next steps
- [ ]
EOF
  echo "Session note created: $SESSION_FILE"
fi

# Append change log entry to CLAUDE.md
if ! grep -q "$DATE:" "$CLAUDE_MD" 2>/dev/null; then
  echo "$DATE: Session completed — see memory/$DATE-session.md" >> "$CLAUDE_MD"
fi

# Sync session note to Obsidian vault if path exists
if [[ -d "$OBSIDIAN_VAULT_PATH" ]]; then
  mkdir -p "$OBSIDIAN_AGENT_DIR"
  cp "$SESSION_FILE" "$OBSIDIAN_AGENT_DIR/"
  echo "Synced to Obsidian: $OBSIDIAN_AGENT_DIR/"
fi

# Auto-push if GITHUB_TOKEN is set
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  cd "$REPO_DIR"
  REPO_SLUG=$(git remote get-url origin | sed 's|https://.*github.com/||')
  git remote set-url origin "https://${GITHUB_TOKEN}@github.com/${REPO_SLUG}" 2>/dev/null || true

  if [[ -n "$(git status --porcelain)" ]]; then
    git config user.email "noreply@anthropic.com"
    git config user.name "Claude"
    git add -A
    git commit -m "chore: auto-save session memory $DATE"
    git push -u origin "$(git branch --show-current)"
    echo "Changes pushed to remote."
  fi
fi

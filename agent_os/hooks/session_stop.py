"""
session_stop.py — Claude Code Stop Hook

Fires automatically when Claude Code finishes a task.
Reads session data from stdin, extracts what changed,
and appends a session summary to CLAUDE.md + Obsidian vault.

Wired in ~/.claude/settings.json under hooks.Stop
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────
PROJECT_ROOT  = Path(r"C:\Users\navka\navakanth001")
CLAUDE_MD     = PROJECT_ROOT / "CLAUDE.md"
VAULT_INBOX   = PROJECT_ROOT / "obsidian-vault" / "Obsidian Vault" / "00-Inbox"
SESSION_LOG   = PROJECT_ROOT / "agent_os" / "session_log.json"

MAX_SESSION_LOG = 100  # keep last N sessions


def read_stdin_safe() -> dict:
    """Read JSON from stdin (Claude Code sends session data here)."""
    try:
        raw = sys.stdin.read()
        if raw.strip():
            return json.loads(raw)
    except Exception:
        pass
    return {}


def extract_summary(data: dict) -> dict:
    """Pull useful fields from Claude Code's stop hook payload."""
    return {
        "session_id":    data.get("session_id", "unknown"),
        "transcript_path": data.get("transcript_path", ""),
        "stop_hook_active": data.get("stop_hook_active", False),
    }


def append_to_claude_md(date_str: str, time_str: str, session_id: str):
    """Append a session marker to CLAUDE.md so future sessions know what ran."""
    if not CLAUDE_MD.exists():
        return

    marker = (
        f"\n\n---\n"
        f"## Last Session — {date_str} {time_str}\n"
        f"- Session ID: `{session_id}`\n"
        f"- Hook fired: session_stop.py\n"
        f"- See vault inbox for session note\n"
    )

    content = CLAUDE_MD.read_text(encoding="utf-8")

    # Remove previous "Last Session" block to avoid accumulation
    if "## Last Session —" in content:
        idx = content.rfind("\n\n---\n## Last Session —")
        if idx != -1:
            content = content[:idx]

    CLAUDE_MD.write_text(content + marker, encoding="utf-8")


def save_session_note(date_str: str, time_str: str, session_id: str):
    """Save a brief session note to Obsidian inbox."""
    VAULT_INBOX.mkdir(parents=True, exist_ok=True)
    filename = f"{date_str}-session-{session_id[:8]}.md"
    note_path = VAULT_INBOX / filename

    # Don't overwrite if already exists (multiple stops per session)
    if note_path.exists():
        return str(note_path)

    note = f"""---
date: {date_str}
tags: [session, agent-os, auto-captured]
project: "AI-Automation"
source: "Claude Code stop hook"
---

# Session — {date_str} {time_str}

## Key Idea
Auto-captured Claude Code session snapshot.

## Details
- Session ID: `{session_id}`
- Hook: `session_stop.py`
- Time: {date_str} {time_str}

## Action / Next Steps
- [ ] Review session and move relevant notes to Projects
"""
    note_path.write_text(note, encoding="utf-8")
    return str(note_path)


def append_session_log(entry: dict):
    """Append to rolling session log JSON."""
    log = []
    if SESSION_LOG.exists():
        try:
            log = json.loads(SESSION_LOG.read_text(encoding="utf-8"))
        except Exception:
            log = []
    log.append(entry)
    SESSION_LOG.parent.mkdir(parents=True, exist_ok=True)
    SESSION_LOG.write_text(
        json.dumps(log[-MAX_SESSION_LOG:], indent=2),
        encoding="utf-8"
    )


def main():
    now       = datetime.now()
    date_str  = now.strftime("%Y-%m-%d")
    time_str  = now.strftime("%H:%M:%S")

    data       = read_stdin_safe()
    summary    = extract_summary(data)
    session_id = summary["session_id"]

    # 1. Update CLAUDE.md last-session block
    append_to_claude_md(date_str, time_str, session_id)

    # 2. Save session note to Obsidian inbox
    note_path = save_session_note(date_str, time_str, session_id)

    # 3. Append to rolling session log
    append_session_log({
        "date":       date_str,
        "time":       time_str,
        "session_id": session_id,
        "note":       note_path,
    })

    # Hook must exit 0 — non-zero blocks Claude Code
    sys.exit(0)


if __name__ == "__main__":
    main()

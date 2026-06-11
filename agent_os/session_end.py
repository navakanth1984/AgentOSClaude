"""
session_end.py — Session Auto-Save Hook for Agent OS
Run this at the END of any Claude/AI session to preserve what happened.

Usage:
  python session_end.py                        # interactive — prompts you
  python session_end.py "title" "summary"      # one-liner from CLI
  python session_end.py --from-clipboard        # paste session content from clipboard

What it does:
  1. Writes a dated session note to Obsidian (01-Projects/AI-Automation/)
  2. Updates memory_os/session_memory/ with today's log
  3. Prints the "Current Focus" update reminder for core-identity.md

This is the "save before quit" habit — one command closes the loop.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add agent_os to path
sys.path.insert(0, str(Path(__file__).parent))
from obsidian_bridge import save_note, VAULT_PATH

SESSION_MEMORY_DIR = Path(__file__).parent.parent / "memory_os" / "session_memory"
CORE_NOTE = VAULT_PATH / "01-Projects" / "AI-Automation" / "core-identity.md"


def get_from_clipboard() -> str:
    """Read text from Windows clipboard."""
    try:
        import subprocess
        result = subprocess.run(
            ["powershell.exe", "-Command", "Get-Clipboard"],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception:
        return ""


def write_session_memory(title: str, summary: str, actions: list[str], date_str: str):
    """Append to memory_os/session_memory/session_YYYYMMDD.md"""
    SESSION_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    filename = SESSION_MEMORY_DIR / f"session_{date_str.replace('-', '')}.md"

    timestamp = datetime.now().strftime("%H:%M")
    entry = f"""
## [{timestamp}] {title}

### Actions Taken
{chr(10).join(f"- {a}" for a in actions)}

### Summary
{summary}

---
"""
    with open(filename, "a", encoding="utf-8") as f:
        if not filename.exists() or filename.stat().st_size == 0:
            f.write(f"# Session Log: {date_str}\n")
        f.write(entry)

    print(f"[Session] Memory written: {filename.name}")


def save_session(title: str, summary: str, actions: list[str] = None, tags: list[str] = None):
    """Full session save — Obsidian note + memory log."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    actions = actions or ["(no actions listed)"]
    tags = tags or ["session", "agent-os"]

    # 1. Save to Obsidian vault
    path = save_note(
        title=f"Session: {title}",
        key_idea=summary[:200] if len(summary) > 200 else summary,
        details=summary,
        next_steps=actions,
        tags=tags,
        project="AI-Automation",
        source="Agent OS Session End",
        folder="ai",
    )
    print(f"[Session] Obsidian note: {path.name}")

    # 2. Write to memory_os session log
    write_session_memory(title, summary, actions, date_str)

    # 3. Remind about core-identity update
    print(f"""
[Session] Reminder: update your core-identity.md "Current Focus" section.
  File: {CORE_NOTE}
  Section to update: ## Current Focus (update this section each session)
""")

    return path


def interactive_save():
    """Prompt user for session details interactively."""
    print("\n=== Agent OS Session Save ===\n")

    title = input("Session title (what did you build today?): ").strip()
    if not title:
        title = f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    print("Summary (what happened, decisions made, outcomes):")
    print("  (enter blank line to finish)")
    lines = []
    while True:
        line = input("  ")
        if not line:
            break
        lines.append(line)
    summary = "\n".join(lines) or "(no summary)"

    print("Next actions (enter each on a new line, blank to finish):")
    actions = []
    while True:
        action = input("  - ").strip()
        if not action:
            break
        actions.append(action)

    tags_raw = input("Tags (comma-separated, e.g. agent-os,flutter): ").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] or ["session"]

    save_session(title, summary, actions, tags)


def quick_save(title: str, summary: str):
    """One-liner save from CLI args."""
    # Parse pipe-separated actions from summary if present
    # Format: "summary text || action1 | action2"
    actions = []
    if "||" in summary:
        parts = summary.split("||")
        summary = parts[0].strip()
        actions = [a.strip() for a in parts[1].split("|") if a.strip()]

    save_session(title, summary, actions)


# ─── Entry Point ──────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        interactive_save()

    elif args[0] == "--from-clipboard":
        content = get_from_clipboard()
        if not content:
            print("[!] Clipboard is empty.")
            sys.exit(1)
        title = input("Session title: ").strip() or "Clipboard Session"
        save_session(title, content)

    elif len(args) >= 2:
        quick_save(title=args[0], summary=" ".join(args[1:]))

    else:
        print("Usage:")
        print("  python session_end.py                   # interactive")
        print('  python session_end.py "title" "summary" # quick save')
        print("  python session_end.py --from-clipboard  # from clipboard")

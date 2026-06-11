"""
obsidian_bridge.py — Obsidian Memory Layer for Agent OS
Reads and writes Markdown files to your Obsidian Vault.
Any AI agent in the system uses this to share memory.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# ─── Vault Config ─────────────────────────────────────────────
# Dynamic: uses Git-cloned vault in cloud mode, local Windows path otherwise
try:
    from vault_sync import get_vault_path
    VAULT_PATH = get_vault_path()
except ImportError:
    VAULT_PATH = Path(r"C:\Users\navka\navakanth001\obsidian-vault\Obsidian Vault")

FOLDERS = {
    "inbox":      VAULT_PATH / "00-Inbox",
    "ai":         VAULT_PATH / "01-Projects" / "AI-Automation",
    "knowledge":  VAULT_PATH / "01-Projects" / "Personal-Knowledge",
    "areas":      VAULT_PATH / "02-Areas",
    "resources":  VAULT_PATH / "03-Resources",
    "archive":    VAULT_PATH / "04-Archive",
    "daily":      VAULT_PATH / "02-Areas" / "Daily",
    "experiments":VAULT_PATH / "01-Projects" / "AI-Automation" / "Experiments",
}

NOTE_TEMPLATE = """\
---
date: {date}
tags: [{tags}]
project: "{project}"
source: "{source}"
---

# {title}

## Key Idea
{key_idea}

## Details
{details}

## Action / Next Steps
{next_steps}
"""


# ─── Core Functions ────────────────────────────────────────────

def save_note(
    title: str,
    key_idea: str,
    details: str,
    next_steps: list[str],
    tags: list[str] = None,
    project: str = "AI-Automation",
    source: str = "Agent OS",
    folder: str = "inbox",
) -> Path:
    """
    Save a structured note to the Obsidian vault.
    Returns the path of the created file.

    folder: one of 'inbox', 'ai', 'knowledge', 'experiments', 'daily', etc.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}-{_slugify(title)}.md"

    # Ensure the target folder exists
    target_dir = FOLDERS.get(folder, FOLDERS["inbox"])
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / filename

    # Format next steps as a checklist
    steps_md = "\n".join(f"- [ ] {step}" for step in next_steps) if next_steps else "- [ ] (none)"

    content = NOTE_TEMPLATE.format(
        date=date_str,
        tags=", ".join(tags or ["agent-os"]),
        project=project,
        source=source,
        title=title,
        key_idea=key_idea,
        details=details,
        next_steps=steps_md,
    )

    file_path.write_text(content, encoding="utf-8")
    print(f"[Obsidian] OK Note saved: {file_path}")

    # Sync to Git repo if running in cloud mode
    try:
        from vault_sync import commit_and_push, is_cloud_mode
        if is_cloud_mode():
            commit_and_push(str(file_path), f"Agent OS: save {title}")
    except ImportError:
        pass

    return file_path


def read_note(filename: str, folder: str = "inbox") -> Optional[str]:
    """Read a note from the vault by filename."""
    target = FOLDERS.get(folder, FOLDERS["inbox"]) / filename
    if target.exists():
        return target.read_text(encoding="utf-8")
    return None


def search_vault(query: str, max_results: int = 10) -> list[dict]:
    """
    Full-text search across the entire vault.
    Returns list of {path, title, excerpt} dicts.
    """
    results = []
    query_lower = query.lower()

    for md_file in VAULT_PATH.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
            if query_lower in text.lower():
                # Extract title (first # heading)
                title = md_file.stem
                for line in text.splitlines():
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                # Get excerpt around the match
                idx = text.lower().find(query_lower)
                excerpt = text[max(0, idx - 80):idx + 120].strip()
                results.append({
                    "path": str(md_file),
                    "title": title,
                    "excerpt": excerpt,
                })
                if len(results) >= max_results:
                    break
        except Exception:
            continue

    return results


def get_context_for_agent(recent_n: int = 5) -> str:
    """
    Build a context string for any AI agent using the HYBRID strategy:

      Layer 1 — CORE notes: any note tagged 'core' in its frontmatter.
                These are permanent facts: your name, active projects, goals.
                You write them once; they're always loaded.

      Layer 2 — RECENT notes: the N most recently modified notes.
                These capture what you're working on right now, automatically.
                No tagging required.

    The two layers together give Claude stable identity context + live
    working memory, without any manual curation beyond the initial core notes.
    """
    lines = ["# Agent Context from Obsidian Vault\n"]
    seen_paths = set()

    # ── Layer 1: Core notes (tagged 'core') ───────────────────
    core_notes = []
    for md_file in VAULT_PATH.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
            # Check frontmatter for core tag
            if "core" in _extract_tags(text):
                core_notes.append((md_file, text))
                seen_paths.add(str(md_file))
        except Exception:
            continue

    if core_notes:
        lines.append("## Core Knowledge (always loaded)\n")
        for md_file, text in core_notes:
            title = _extract_title(text, md_file.stem)
            body = _extract_body(text)
            lines.append(f"### {title}")
            lines.append(f"{body}\n")

    # ── Layer 2: Recent notes (sliding window) ─────────────────
    all_notes = [
        (md_file, md_file.stat().st_mtime)
        for md_file in VAULT_PATH.rglob("*.md")
        if str(md_file) not in seen_paths
    ]
    all_notes.sort(key=lambda x: x[1], reverse=True)
    recent = all_notes[:recent_n]

    if recent:
        lines.append(f"## Recent Activity (last {len(recent)} notes)\n")
        for md_file, mtime in recent:
            try:
                text = md_file.read_text(encoding="utf-8")
                title = _extract_title(text, md_file.stem)
                body = _extract_body(text)
                from datetime import datetime
                ts = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                lines.append(f"### [{ts}] {title}")
                lines.append(f"{body}\n")
            except Exception:
                continue

    if len(lines) == 1:
        lines.append("(Vault is empty — no context available yet.)")

    return "\n".join(lines)


# ─── Frontmatter Helpers ──────────────────────────────────────

def _extract_tags(text: str) -> list[str]:
    """Pull tags list from YAML frontmatter."""
    import re
    match = re.search(r"^tags:\s*\[(.+?)\]", text, re.MULTILINE)
    if match:
        return [t.strip().strip('"') for t in match.group(1).split(",")]
    return []


def _extract_title(text: str, fallback: str) -> str:
    """Get the first # heading from a note."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _extract_body(text: str, max_chars: int = 400) -> str:
    """Return note body (after frontmatter), trimmed to max_chars."""
    lines = text.splitlines()
    # Skip YAML frontmatter block
    in_frontmatter = False
    body_lines = []
    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if not in_frontmatter:
            body_lines.append(line)
    body = "\n".join(body_lines).strip()
    if len(body) > max_chars:
        body = body[:max_chars] + "..."
    return body


def save_session_to_vault(session_title: str, content: str, tags: list[str] = None) -> Path:
    """
    Quick helper: dump a whole session summary into the AI-Automation folder.
    Used at the end of every Claude/Hermes session automatically.
    """
    return save_note(
        title=session_title,
        key_idea=content[:300] + "..." if len(content) > 300 else content,
        details=content,
        next_steps=["Review and tag this note", "Link to related notes"],
        tags=tags or ["session", "agent-os"],
        project="AI-Automation",
        source="Agent OS Session",
        folder="ai",
    )


# ─── Helpers ──────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Convert title to kebab-case filename."""
    import re
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text[:60]


def list_recent_notes(n: int = 10) -> list[dict]:
    """Return the N most recently modified notes in the vault."""
    notes = []
    for md_file in VAULT_PATH.rglob("*.md"):
        notes.append({
            "path": str(md_file),
            "name": md_file.name,
            "modified": md_file.stat().st_mtime,
        })
    notes.sort(key=lambda x: x["modified"], reverse=True)
    return notes[:n]


# ─── Quick Test ───────────────────────────────────────────────

if __name__ == "__main__":
    # Test: save a note, search for it, read context
    path = save_note(
        title="Agent OS Setup",
        key_idea="Central Agent OS system connecting NotebookLM, Claude, and Obsidian.",
        details="The Agent OS uses a Python orchestrator, Playwright for NotebookLM automation, and Obsidian as the shared memory layer.",
        next_steps=["Wire up NotebookLM Playwright agent", "Add Flutter dashboard tab", "Test end-to-end loop"],
        tags=["agent-os", "notebooklm", "obsidian", "automation"],
        project="AI-Automation",
        folder="ai",
    )
    print(f"\nCreated: {path}")

    results = search_vault("Agent OS")
    print(f"\nSearch results for 'Agent OS': {len(results)} found")
    for r in results:
        print(f"  - {r['title']}: {r['excerpt'][:80]}...")

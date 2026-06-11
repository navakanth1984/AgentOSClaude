"""
omi_bridge.py — OMI (Open Memory Interface) → Obsidian bridge

OMI records your conversations, screen activity, and daily notes.
This module receives OMI memory exports via webhook and routes them
into your Obsidian vault as structured notes.

Usage:
  # Called by server.py on POST /omi
  # Or test directly:
  python omi_bridge.py --test

OMI Webhook format (sent by OMI app):
  {
    "id": "memory_abc123",
    "created_at": "2026-06-07T14:32:00Z",
    "transcript": "...",
    "summary": "...",
    "action_items": ["...", "..."],
    "structured": {
      "title": "...",
      "overview": "...",
      "action_items": [...],
      "category": "meeting|task|idea|conversation"
    }
  }
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from obsidian_bridge import save_note, VAULT_PATH

# ── Constants ─────────────────────────────────────────────────

OMI_LOG = Path(__file__).parent / "omi_log.json"
OMI_TAG_MAP = {
    "meeting":      ["omi", "meeting", "agent-os"],
    "task":         ["omi", "task", "agent-os"],
    "idea":         ["omi", "idea", "capture", "agent-os"],
    "conversation": ["omi", "conversation", "agent-os"],
}


# ── Main entry point ──────────────────────────────────────────

def receive_memory(payload: dict) -> dict:
    """
    Process a single OMI memory payload and save it to Obsidian.

    Returns:
        {"saved": True, "path": "...", "title": "..."}
    """
    structured = payload.get("structured", {})
    transcript = payload.get("transcript", "")
    created_at = payload.get("created_at", datetime.now(timezone.utc).isoformat())

    # Parse timestamp
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except Exception:
        dt = datetime.now(timezone.utc)

    date_str = dt.strftime("%Y-%m-%d")
    time_str = dt.strftime("%H:%M")

    # Extract fields
    title    = structured.get("title") or payload.get("summary", "OMI Memory")[:60]
    overview = structured.get("overview") or payload.get("summary", "")
    actions  = structured.get("action_items") or payload.get("action_items", [])
    category = structured.get("category", "idea").lower()

    tags = OMI_TAG_MAP.get(category, ["omi", "agent-os"])

    # Build details body
    details_lines = []
    if transcript:
        details_lines.append("## Transcript\n")
        # Trim long transcripts
        transcript_preview = transcript[:2000]
        if len(transcript) > 2000:
            transcript_preview += "\n\n*[transcript truncated — full version in omi_log.json]*"
        details_lines.append(transcript_preview)

    if overview:
        details_lines.append(f"\n## Summary\n{overview}")

    details = "\n".join(details_lines) if details_lines else overview

    # Format action items as next steps
    next_steps = [f"[ ] {a}" for a in actions] if actions else ["[ ] Review this memory"]

    # Save to vault inbox
    file_path = save_note(
        title=f"{date_str} {time_str} — {title}",
        key_idea=overview or title,
        details=details,
        next_steps=next_steps,
        tags=tags,
        folder="inbox",
        source=f"OMI — {category}",
    )

    # Log to omi_log.json
    _append_log({
        "id":         payload.get("id", ""),
        "title":      title,
        "category":   category,
        "saved_to":   str(file_path),
        "created_at": created_at,
        "logged_at":  datetime.now().isoformat(),
    })

    return {
        "saved":    True,
        "path":     str(file_path),
        "title":    title,
        "category": category,
        "tags":     tags,
    }


def receive_batch(memories: list[dict]) -> list[dict]:
    """Process a list of OMI memories in one call."""
    return [receive_memory(m) for m in memories]


# ── Log helper ────────────────────────────────────────────────

def _append_log(entry: dict):
    log = []
    if OMI_LOG.exists():
        try:
            log = json.loads(OMI_LOG.read_text(encoding="utf-8"))
        except Exception:
            log = []
    log.append(entry)
    # Keep last 500 entries
    OMI_LOG.write_text(json.dumps(log[-500:], indent=2), encoding="utf-8")


# ── CLI test ──────────────────────────────────────────────────

if __name__ == "__main__":
    test_payload = {
        "id": "test_001",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "transcript": "Today I was thinking about building the infinite context engine. "
                      "The key idea is to connect OMI with NotebookLM and Obsidian so that "
                      "Claude always has full context about what I'm working on.",
        "summary": "Planning the Infinite Context Engine integration",
        "action_items": [
            "Set up OMI webhook endpoint in server.py",
            "Test OMI memory flow end to end",
            "Add OMI panel to Flutter dashboard",
        ],
        "structured": {
            "title": "Infinite Context Engine Planning Session",
            "overview": "Discussed connecting OMI → NotebookLM → Obsidian → Claude "
                        "as a unified second-brain pipeline.",
            "action_items": [
                "Set up OMI webhook endpoint in server.py",
                "Test OMI memory flow end to end",
                "Add OMI panel to Flutter dashboard",
            ],
            "category": "idea",
        }
    }

    result = receive_memory(test_payload)
    print(json.dumps(result, indent=2))
    print(f"\nSaved to: {result['path']}")

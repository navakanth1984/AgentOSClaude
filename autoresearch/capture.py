"""
capture.py — Zero-friction Obsidian vault capture

Usage:
    py capture.py                          # read from clipboard
    py capture.py "some rough idea"        # capture a brain dump
    py capture.py https://example.com      # fetch a URL and capture it
    py capture.py --watch                  # watch clipboard, auto-capture new URLs

The prompt is always loaded from train.py — so as the AutoResearch loop
improves your prompt, every future capture automatically gets better.
"""

import sys
import os
import re
import time
import argparse
from datetime import date
from pathlib import Path

import requests
import pyperclip
from bs4 import BeautifulSoup

# ── Config ─────────────────────────────────────────────────────────────────────

VAULT_INBOX = Path(r"C:\Users\navka\OneDrive\Documents\Obsidian Vault\00-Inbox")
TODAY = date.today().isoformat()
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"   # free, local, no API key needed

# ── Load prompt from train.py (auto-updates as AutoResearch improves it) ──────

def get_system_prompt() -> str:
    train_path = Path(__file__).parent / "train.py"
    if not train_path.exists():
        raise FileNotFoundError("train.py not found — run this from the autoresearch/ folder")

    # Dynamically import so we always get the latest version
    import importlib.util
    spec = importlib.util.spec_from_file_location("train", train_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.get_prompt(today=TODAY)


# ── URL detection & fetching ───────────────────────────────────────────────────

def is_url(text: str) -> bool:
    return bool(re.match(r"https?://\S+", text.strip()))


def fetch_url(url: str) -> tuple[str, str]:
    """Fetch a URL and return (source_label, extracted_text)."""
    print(f"  Fetching: {url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; VaultCapture/1.0)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove boilerplate
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Prefer article/main content
        content_block = (
            soup.find("article") or
            soup.find("main") or
            soup.find(id=re.compile(r"content|article|post", re.I)) or
            soup.find("body")
        )

        raw_text = content_block.get_text(separator="\n", strip=True) if content_block else ""

        # Truncate to avoid token limits (keep first ~3000 chars)
        truncated = raw_text[:3000]
        if len(raw_text) > 3000:
            truncated += "\n\n[... truncated for capture ...]"

        title = soup.title.string.strip() if soup.title else url
        return f"{title} — {url}", f"URL: {url}\n\n{truncated}"

    except Exception as e:
        print(f"  Warning: fetch failed ({e}) — capturing URL as-is")
        return url, f"URL: {url}\n\nFetch failed. Capture the URL for later reading."


# ── Claude capture ─────────────────────────────────────────────────────────────

def capture(raw_input: str, source: str | None = None) -> str:
    """Send raw input to Ollama and return the formatted vault note."""
    prompt = get_system_prompt()

    user_message = raw_input
    if source and source not in raw_input:
        user_message = f"Source: {source}\n\n{raw_input}"

    full_prompt = f"{prompt}\n\nNow capture this input:\n\n{user_message}"

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": full_prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        note = response.json()["response"].strip()
        # Always force the correct date — local models hallucinate it
        note = re.sub(r"date:.*", f"date: {TODAY}", note, count=1)
        return note
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Ollama is not running. Start it with: ollama serve\n"
            "Or open the Ollama app from your Start menu."
        )


# ── Related notes ─────────────────────────────────────────────────────────────

VAULT_ROOT = Path(r"C:\Users\navka\OneDrive\Documents\Obsidian Vault")


def extract_tags(note: str) -> set[str]:
    """Pull tags list from YAML frontmatter."""
    match = re.search(r"tags:\s*\[([^\]]+)\]", note)
    if not match:
        return set()
    raw = match.group(1)
    return {t.strip().strip('"').strip("'") for t in raw.split(",")}


def note_keywords(note: str, filepath: Path) -> set[str]:
    """Extract searchable keywords from tags, title, and filename."""
    words = set()

    # From tags
    for tag in extract_tags(note):
        words.update(re.split(r"[-_]", tag.lower()))

    # From # title
    title_match = re.search(r"^# (.+)$", note, re.MULTILINE)
    if title_match:
        words.update(re.findall(r"[a-z]{3,}", title_match.group(1).lower()))

    # From filename stem (strip date prefix)
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", filepath.stem)
    words.update(re.split(r"[-_]", stem.lower()))

    # Remove noise words
    noise = {"the", "and", "for", "with", "this", "that", "using", "can", "how", "are"}
    return words - noise


def find_related(new_note: str, new_filepath: Path, top_n: int = 3) -> list[str]:
    """
    Scan vault for notes that share keywords with new_note.
    Matches on tags, title words, and filename — not just exact tags.
    Returns wiki-link strings, e.g. ['[[2026-04-10-ai-agents]]', ...]
    """
    new_keywords = note_keywords(new_note, new_filepath)
    if not new_keywords:
        return []

    scored = []
    for md_file in VAULT_ROOT.rglob("*.md"):
        if md_file == new_filepath:
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            existing_keywords = note_keywords(content, md_file)
            overlap = len(new_keywords & existing_keywords)
            if overlap >= 2:  # at least 2 words in common
                scored.append((overlap, md_file.stem))
        except Exception:
            continue

    scored.sort(key=lambda x: x[0], reverse=True)
    return [f"[[{stem}]]" for _, stem in scored[:top_n]]


def append_related(note: str, related: list[str]) -> str:
    """Append a Related Notes section to the note."""
    if not related:
        return note
    links = "\n".join(f"- {link}" for link in related)
    return note.rstrip() + f"\n\n## Related Notes\n{links}\n"


# ── Save to vault ──────────────────────────────────────────────────────────────

def slugify(title: str) -> str:
    title = title.lower().strip()
    title = re.sub(r"[^\w\s-]", "", title)
    title = re.sub(r"[\s_]+", "-", title)
    return title[:60].strip("-")


def extract_title(note: str) -> str:
    match = re.search(r"^# (.+)$", note, re.MULTILINE)
    return match.group(1).strip() if match else "captured-note"


def save_to_vault(note: str) -> Path:
    title = extract_title(note)
    slug = slugify(title)
    filename = f"{TODAY}-{slug}.md"
    filepath = VAULT_INBOX / filename

    # Avoid overwriting — append counter if file exists
    counter = 1
    while filepath.exists():
        filepath = VAULT_INBOX / f"{TODAY}-{slug}-{counter}.md"
        counter += 1

    VAULT_INBOX.mkdir(parents=True, exist_ok=True)
    filepath.write_text(note, encoding="utf-8")
    return filepath


# ── Clipboard watch mode ───────────────────────────────────────────────────────

def watch_clipboard(interval: int = 2):
    """Poll clipboard every N seconds. Auto-capture new URLs."""
    print("Watching clipboard for URLs... (Ctrl+C to stop)\n")
    last_seen = pyperclip.paste()

    try:
        while True:
            current = pyperclip.paste()
            if current != last_seen and is_url(current):
                last_seen = current
                print(f"\nURL detected: {current}")
                run_capture(current)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped watching clipboard.")


# ── Main entry ─────────────────────────────────────────────────────────────────

def run_capture(raw_input: str):
    source = None
    content = raw_input

    if is_url(raw_input.strip()):
        source, content = fetch_url(raw_input.strip())

    print("  Generating note...")
    note = capture(content, source=source or raw_input[:80])

    # Save first so related search excludes the new file itself
    filepath = save_to_vault(note)

    # Find related notes and append them
    related = find_related(note, filepath)
    if related:
        note = append_related(note, related)
        filepath.write_text(note, encoding="utf-8")
        print(f"  Related: {', '.join(related)}")

    print(f"  Saved: {filepath.name}")
    print(f"  Path:  {filepath}")
    print()
    print("-" * 50)
    print(note)
    print("-" * 50)


def main():
    parser = argparse.ArgumentParser(description="Zero-friction Obsidian vault capture")
    parser.add_argument("input", nargs="*", help="Text, URL, or leave blank to read from clipboard")
    parser.add_argument("--watch", action="store_true", help="Watch clipboard and auto-capture new URLs")
    args = parser.parse_args()

    if args.watch:
        watch_clipboard()
        return

    if args.input:
        raw = " ".join(args.input)
    else:
        raw = pyperclip.paste()
        if not raw.strip():
            print("Clipboard is empty. Pass text as argument or copy something first.")
            sys.exit(1)
        print(f"Reading from clipboard ({len(raw)} chars)...")

    run_capture(raw)


if __name__ == "__main__":
    main()

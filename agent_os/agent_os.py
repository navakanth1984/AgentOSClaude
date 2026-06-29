"""
agent_os.py — Agent OS Orchestrator
The central command loop that routes tasks between:
  - Obsidian (memory layer)
  - NotebookLM (content generation)
  - Asset Library (file management)
  - Claude context injection (read vault -> pass to Claude)

Run: python agent_os.py
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from obsidian_bridge import (
    save_note,
    save_session_to_vault,
    search_vault,
    get_context_for_agent,
    list_recent_notes,
    VAULT_PATH,
)

ASSET_LIBRARY = Path(__file__).parent / "asset_library"
ASSET_LIBRARY.mkdir(exist_ok=True)

LOG_FILE = Path(__file__).parent / "agent_os.log"


# ─── Logging ──────────────────────────────────────────────────

def log(message: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ─── Command Router ───────────────────────────────────────────

COMMANDS = {
    "help":       "Show this help",
    "status":     "Show Agent OS status",
    "context":    "Load Obsidian vault context for Claude (pass topics as args)",
    "save":       "Save a quick note to Obsidian inbox",
    "search":     "Search the vault for a keyword",
    "recent":     "List recently modified vault notes",
    "assets":     "List files in the asset library",
    "notebook":   "NotebookLM: list | studio <url> | generate <url> | screenshot <url>",
    "hermes":     "Hermes video agent: load <file> | generate <file> (Step 4)",
    "cloud":      "Cloud Agent: self-correcting task execution in background",
    "creative":   "Creative: screenplay | audiography | prompt | novelist | studio (AI filmmaking tools)",
    "sql":        "Translate natural language questions into executable SQL queries against jobs.db",
    "session":    "Save the current session summary to Obsidian",
    "audiobook":  "Generate an audiobook from a text file: audiobook <file> [--voice] [--engine] [--output] [--resume] [--parallel] [--cache]",
    "quit":       "Exit Agent OS",
}


def show_help():
    print("\n=== Agent OS Commands ===")
    for cmd, desc in COMMANDS.items():
        print(f"  {cmd:<12} {desc}")
    print()


def show_status():
    print("\n=== Agent OS Status ===")

    # Vault
    vault_notes = list(VAULT_PATH.rglob("*.md"))
    print(f"  Obsidian Vault : {VAULT_PATH}")
    print(f"  Total notes    : {len(vault_notes)}")

    # Asset library
    assets = list(ASSET_LIBRARY.iterdir()) if ASSET_LIBRARY.exists() else []
    print(f"  Asset library  : {len(assets)} files")

    # Log
    if LOG_FILE.exists():
        with open(LOG_FILE, encoding="utf-8") as f:
            lines = f.readlines()
        print(f"  Log entries    : {len(lines)}")

    print()


def cmd_context(args: list[str]):
    """Pull vault context (core notes + recent) and print it for pasting into Claude."""
    n = int(args[0]) if args and args[0].isdigit() else 5
    context = get_context_for_agent(recent_n=n)
    print("\n--- Vault Context ---")
    print(context)
    print("--- End Context ---\n")
    log(f"Context loaded (recent_n={n})")


def cmd_save(args: list[str]):
    """Quickly save a note to inbox. Usage: save <title> | <key idea>"""
    if not args:
        title = input("  Note title: ").strip()
        idea = input("  Key idea: ").strip()
        details = input("  Details (optional): ").strip()
        tags_raw = input("  Tags (comma-separated): ").strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    else:
        full_text = " ".join(args)
        parts = full_text.split("|")
        title = parts[0].strip()
        idea = parts[1].strip() if len(parts) > 1 else title
        details = parts[2].strip() if len(parts) > 2 else ""
        tags = ["quick-note", "agent-os"]

    path = save_note(
        title=title,
        key_idea=idea,
        details=details or idea,
        next_steps=["Review and expand this note"],
        tags=tags,
        folder="inbox",
    )
    log(f"Note saved: {path.name}")


def cmd_search(args: list[str]):
    """Search vault. Usage: search <query>"""
    query = " ".join(args) if args else input("  Search query: ").strip()
    results = search_vault(query)
    if not results:
        print(f"  No results for '{query}'")
        return
    print(f"\n  Found {len(results)} result(s) for '{query}':\n")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['title']}")
        print(f"     {r['excerpt'][:100]}...")
        print(f"     {r['path']}\n")
    log(f"Search: '{query}' -> {len(results)} results")


def cmd_recent(args: list[str]):
    """List recently modified notes."""
    n = int(args[0]) if args else 5
    notes = list_recent_notes(n)
    print(f"\n  Last {n} modified notes:")
    for note in notes:
        from datetime import datetime
        ts = datetime.fromtimestamp(note["modified"]).strftime("%Y-%m-%d %H:%M")
        print(f"    {ts}  {note['name']}")
    print()


def cmd_assets(args: list[str]):
    """List asset library files."""
    files = sorted(ASSET_LIBRARY.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        print("  Asset library is empty.")
        return
    print(f"\n  Asset library ({len(files)} files):")
    for f in files[:20]:
        size_kb = f.stat().st_size // 1024
        print(f"    {f.name}  ({size_kb} KB)")
    print()


def cmd_session(args: list[str]):
    """Save a session summary to Obsidian."""
    title = " ".join(args) if args else input("  Session title: ").strip()
    print("  Enter session summary (end with a line containing only '.'): ")
    lines = []
    while True:
        line = input()
        if line == ".":
            break
        lines.append(line)
    content = "\n".join(lines)
    path = save_session_to_vault(title, content)
    log(f"Session saved: {path.name}")


def cmd_hermes(args: list[str]):
    """
    Step 4 — Hermes video agent integration.
    Takes a file from the asset library and sends it to Hermes for avatar video generation.

    Usage:
      hermes load <filename>     — load an audio file from asset_library into Hermes
      hermes generate <filename> — trigger Hermes to create an avatar video from the audio

    Currently: prints the Hermes workflow steps. Wire in your Hermes API key to activate.
    When Hermes provides an API or webhook, replace the print statements with real calls.
    """
    sub = args[0] if args else "help"
    filename = args[1] if len(args) > 1 else ""

    if sub == "load" and filename:
        file_path = ASSET_LIBRARY / filename
        if not file_path.exists():
            print(f"  [Hermes] File not found in asset library: {filename}")
            print(f"  Available: {[f.name for f in ASSET_LIBRARY.iterdir()]}")
            return
        size_kb = file_path.stat().st_size // 1024
        print(f"\n  [Hermes] File ready: {filename} ({size_kb} KB)")
        print(f"  [Hermes] Next step: run 'hermes generate {filename}'")
        print(f"  [Hermes] Or open Hermes manually and upload: {file_path}")
        log(f"Hermes: loaded {filename}")

    elif sub == "generate" and filename:
        file_path = ASSET_LIBRARY / filename
        print(f"\n  [Hermes] To generate avatar video from '{filename}':")
        print(f"  1. Open Hermes in your browser")
        print(f"  2. Upload: {file_path}")
        print(f"  3. Select avatar + voice settings")
        print(f"  4. Click Generate — Hermes will produce a polished video")
        print(f"\n  [Hermes] When Hermes provides an API, this will happen automatically.")
        print(f"  Hermes API docs: https://www.hermes.ai (check for API/webhook access)\n")
        log(f"Hermes: generate workflow shown for {filename}")

    else:
        print("\n  Hermes — Step 4: Avatar video generation from NotebookLM audio")
        print("  Usage:")
        print("    hermes load <filename.wav>    — inspect file from asset library")
        print("    hermes generate <filename>    — show Hermes upload workflow")
        print(f"\n  Asset library files:")
        for f in sorted(ASSET_LIBRARY.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
            if f.suffix in ('.wav', '.mp3', '.mp4', '.m4a'):
                print(f"    {f.name} ({f.stat().st_size // 1024} KB)")
        print()


async def cmd_notebook(args: list[str]):
    """NotebookLM commands. Usage: notebook list | studio <url> | generate <url> | screenshot"""
    from notebooklm_agent import run_session

    sub_cmd = args[0] if args else "list"
    url = args[1] if len(args) > 1 else ""

    log(f"NotebookLM: {sub_cmd} {url}")
    result = await run_session(sub_cmd, url)

    print("\n  NotebookLM Result:")
    print(json.dumps(result, indent=4))

    # Auto-save result to Obsidian
    if "notebooks" in result:
        nb_list = "\n".join(f"- {nb['title']}: {nb['url']}" for nb in result["notebooks"])
        save_note(
            title="NotebookLM - Notebook List",
            key_idea=f"Found {len(result['notebooks'])} notebooks",
            details=nb_list,
            next_steps=["Pick a notebook to work with", "Generate an audio overview"],
            tags=["notebooklm", "agent-os"],
            folder="ai",
        )
    elif "assets" in result:
        asset_list = "\n".join(f"- [{a.get('type','?')}] {a.get('title', a.get('text',''))}" for a in result["assets"])
        save_note(
            title="NotebookLM - Studio Assets",
            key_idea=f"Found {len(result['assets'])} studio assets",
            details=asset_list,
            next_steps=["Download audio overview", "Pass to Hermes for video generation"],
            tags=["notebooklm", "studio", "agent-os"],
            folder="ai",
        )
    elif result.get("downloaded"):
        save_note(
            title=f"Asset Downloaded — {Path(result['path']).name}",
            key_idea="Audio overview auto-downloaded from NotebookLM to asset library.",
            details=f"File: `{result['path']}`\nNotebook URL: {url}",
            next_steps=[
                "Load into Hermes: notebook hermes " + Path(result['path']).name,
                "Review audio content",
            ],
            tags=["notebooklm", "audio", "asset", "agent-os"],
            folder="ai",
        )
        print(f"\n  [Agent OS] Audio saved to asset library and noted in Obsidian.")


def cmd_cloud(args: list[str]):
    """Cloud Agent: self-correcting task execution in background."""
    if not args:
        print("  Usage: cloud \"<task description>\" [--model <model_id>]")
        return

    import threading
    import subprocess

    # Find and extract --model if present
    model = "google/gemini-2.5-flash"
    task_words = []
    i = 0
    while i < len(args):
        if args[i] == "--model" and i + 1 < len(args):
            model = args[i+1]
            i += 2
        else:
            task_words.append(args[i])
            i += 1

    task_desc = " ".join(task_words)
    # Remove outer quotes if present
    if (task_desc.startswith('"') and task_desc.endswith('"')) or (task_desc.startswith("'") and task_desc.endswith("'")):
        task_desc = task_desc[1:-1]

    runner_path = Path(__file__).parent / "cloud_agent_runner.py"

    log(f"Cloud task started: '{task_desc}'")

    def bg_run():
        try:
            cmd_to_run = [sys.executable, str(runner_path), task_desc, "--model", model]
            res = subprocess.run(cmd_to_run, stdin=subprocess.DEVNULL, capture_output=True, text=True)
            if res.returncode == 0:
                log(f"Cloud task completed successfully: '{task_desc}'")
            else:
                log(f"Cloud task failed with exit code {res.returncode}: '{task_desc}'. Error: {res.stderr.strip()}")
        except Exception as e:
            log(f"Error running cloud agent: {e}")

    t = threading.Thread(target=bg_run)
    t.daemon = True
    t.start()
    print(f"  [Agent OS] Started cloud task in background: '{task_desc}'")


def cmd_creative(args: list[str]):
    """Creative filmmaking pipeline commands. Usage: creative screenplay | audiography | prompt | novelist <prompt/script> [--model <model_id>]"""
    if not args:
        print("  Usage: creative screenplay | audiography | prompt | novelist | studio \"<content/prompt>\" [--model <model_id>]")
        return

    sub = args[0].lower()
    content_args = args[1:]

    # Parse --model if specified
    model = None
    if "--model" in content_args:
        try:
            m_idx = content_args.index("--model")
            if m_idx + 1 < len(content_args):
                model = content_args[m_idx + 1]
                content_args = content_args[:m_idx] + content_args[m_idx+2:]
        except ValueError:
            pass

    # ── Filmmaking Studio: canon-chained bible → screenplay → novel → sound ──
    if sub == "studio":
        concept = " ".join(content_args).strip().strip('"').strip("'")
        if not concept:
            print('  Usage: creative studio "<concept>" [--model <id>]')
            return
        import time
        from filmmaking_studio import start_studio, status_studio
        r = start_studio(concept, model=model)
        if not r.get("started"):
            print(f"  Error: {r.get('error')}")
            return
        jid = r["job_id"]
        print(f"[Studio] Started job {jid}. Local-first generation — this is a long run.")
        print(f"[Studio] Targets: {r['targets']}")
        last = None
        while True:
            s = status_studio(jid)
            line = f"[{s.get('percent',0):>3}%] {s.get('phase','')}"
            if line != last:
                print(f"  {line}")
                last = line
            st = s.get("status")
            if st == "done":
                print(f"\n[Studio] ✓ Complete · {s.get('words_done')} words")
                print(f"[Studio] Bundle: {s.get('bundle_dir')}")
                for k, p in (s.get("vault_paths") or {}).items():
                    print(f"  - {k}: {p}")
                return
            if st == "error":
                print(f"\n[Studio] ✗ Error: {s.get('error')}")
                return
            time.sleep(5)

    content = " ".join(content_args).strip()
    if (content.startswith('"') and content.endswith('"')) or (content.startswith("'") and content.endswith("'")):
        content = content[1:-1]

    if not content:
        print(f"  Error: Missing prompt/text content for 'creative {sub}'")
        return

    from creative_pipeline import generate_screenplay, generate_audiography, generate_visual_prompt

    try:
        res = None
        is_screenplay = False
        if sub == "screenplay":
            print(f"[Creative] Writing screenplay with AI...")
            res = generate_screenplay(content, model=model)
            print("\n--- SCREENPLAY OUTPUT ---\n")
            print(res)
            print("\n--- END OF SCREENPLAY ---")
            is_screenplay = True
        elif sub == "audiography":
            print(f"[Creative] Designing soundscape with AI...")
            res = generate_audiography(content, model=model)
            print("\n--- AUDIOGRAPHY OUTPUT ---\n")
            print(res)
            print("\n--- END OF AUDIOGRAPHY ---")
        elif sub == "prompt":
            print(f"[Creative] Designing visual prompt with AI...")
            res = generate_visual_prompt(content, model=model)
            print("\n--- VISUAL PROMPT OUTPUT ---\n")
            print(res)
            print("\n--- END OF PROMPT ---")
        elif sub == "novelist":
            print(f"[Creative] Running Novelist Swarm Team (Writer -> Critic -> Rewriter)...")
            from novelist_swarm import run_novelist_swarm
            import asyncio
            results = asyncio.run(run_novelist_swarm(content, model=model))
            res = (
                f"# NOVEL DRAFT WRITER\n\n{results['draft']}\n\n"
                f"# LITERARY CRITIQUE\n\n{results['critique']}\n\n"
                f"# FINAL POLISHED NOVEL CHAPTER\n\n{results['polish']}"
            )
            print("\n--- NOVELIST SWARM OUTPUT ---\n")
            print(res)
            print("\n--- END OF NOVELIST SWARM ---")
            is_screenplay = False
        else:
            print(f"  Unknown creative subcommand: '{sub}'. Choose: screenplay, audiography, prompt, novelist.")
            return

        if res:
            # Export to output/ directory
            from creative_exporter import export_document
            out_dir = Path(__file__).parent / "output"
            out_dir.mkdir(parents=True, exist_ok=True)
            import hashlib
            short_hash = hashlib.md5(content.encode("utf-8")).hexdigest()[:6]
            base_name = f"{sub}_{short_hash}"
            base_path = out_dir / base_name
            
            print(f"\n[Creative] Exporting formats (MD, HTML, DOCX, PDF)...")
            export_results = export_document(res, str(base_path), is_screenplay=is_screenplay)
            print(f"[Creative] Exported successfully to output/ directory:")
            for fmt, p in export_results.items():
                print(f"  - {fmt.upper()}: {p}")

    except Exception as e:
        print(f"[ERROR] Error in creative pipeline: {e}")


def cmd_sql(args: list[str]):
    """Translate natural language to SQL and execute. Usage: sql <question>"""
    if not args:
        question = input("  Enter natural language query: ").strip()
    else:
        question = " ".join(args)
    
    if not question:
        print("  Please provide a question.")
        return
        
    try:
        from sql_translator import translate_and_execute
        result = translate_and_execute(question)
        if result["success"]:
            print("\n=== Result Summary ===")
            print(f"SQL Query: {result['sql']}")
            print(f"Columns: {result['columns']}")
            print("Rows:")
            for row in result["results"]:
                print(row)
        else:
            print(f"\n=== Execution Failed after {result['attempts']} attempts ===")
            print(f"Final Error: {result['error']}")
            print(f"Final SQL Tried: {result['sql']}")
    except Exception as e:
        print(f"  [ERROR] Failed to run SQL translator: {e}")


def cmd_audiobook(args: list[str]):
    """Audiobook generation — delegates to the V1.1 speech pipeline."""
    import argparse
    from agent_os.speech.audiobook import build_audiobook

    if not args:
        print("  Usage: audiobook <file-or-dir> [--name <name>] [--voice <voice>] "
              "[--engine kokoro|sarvam|piper] [--output wav/mp3] [--parser benchmark]")
        return

    parser = argparse.ArgumentParser(prog="audiobook", description="Generate an audiobook (V1.1 pipeline).")
    parser.add_argument("file", help="Input text/markdown file, or a directory of chapter files")
    parser.add_argument("--name", default=None, help="Book name (output folder under audiobooks/)")
    parser.add_argument("--voice", default="default", help="Voice/speaker id (engine-specific)")
    parser.add_argument("--engine", default="kokoro", choices=["kokoro", "sarvam", "piper"], help="TTS engine")
    parser.add_argument("--output", default="wav", choices=["wav", "mp3"], help="Output format")
    parser.add_argument("--parser", default=None, choices=["benchmark"],
                        help="Use the offline benchmark parser (no API key)")

    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        return

    if not Path(parsed_args.file).exists():
        print(f"  [ERROR] Path not found: {parsed_args.file}")
        return

    try:
        m = build_audiobook(
            parsed_args.file, book_name=parsed_args.name, engine=parsed_args.engine,
            voice=parsed_args.voice, export_mp3=(parsed_args.output == "mp3"),
            parser=parsed_args.parser,
        )
    except Exception as e:
        print(f"  [ERROR] {e}")
        return

    print(f"  Audiobook complete: {m['book_wav']} ({m['duration_sec']}s, {m['chapter_count']} chapters)")
    if m.get("book_mp3"):
        print(f"  MP3: {m['book_mp3']}")


# ─── Main Loop ────────────────────────────────────────────────

def run():
    print("\n" + "=" * 50)
    print("  Agent OS — v1.0")
    print("  Obsidian + NotebookLM + Claude bridge")
    print("=" * 50)
    print("  Type 'help' for commands, 'quit' to exit\n")

    log("Agent OS started")
    show_status()

    while True:
        try:
            raw = input("agent-os> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Goodbye.")
            log("Agent OS stopped")
            break

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("quit", "exit", "q"):
            log("Agent OS stopped")
            break
        elif cmd == "help":
            show_help()
        elif cmd == "status":
            show_status()
        elif cmd == "context":
            cmd_context(args)
        elif cmd == "save":
            cmd_save(args)
        elif cmd == "search":
            cmd_search(args)
        elif cmd == "recent":
            cmd_recent(args)
        elif cmd == "assets":
            cmd_assets(args)
        elif cmd == "session":
            cmd_session(args)
        elif cmd == "notebook":
            asyncio.run(cmd_notebook(args))
        elif cmd == "hermes":
            cmd_hermes(args)
        elif cmd == "cloud":
            cmd_cloud(args)
        elif cmd == "creative":
            cmd_creative(args)
        elif cmd == "sql":
            cmd_sql(args)
        elif cmd == "audiobook":
            cmd_audiobook(args)
        else:
            print(f"  Unknown command: '{cmd}'. Type 'help' for options.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        args = sys.argv[2:]
        if cmd == "help":
            show_help()
        elif cmd == "status":
            show_status()
        elif cmd == "context":
            cmd_context(args)
        elif cmd == "save":
            cmd_save(args)
        elif cmd == "search":
            cmd_search(args)
        elif cmd == "recent":
            cmd_recent(args)
        elif cmd == "assets":
            cmd_assets(args)
        elif cmd == "session":
            cmd_session(args)
        elif cmd == "notebook":
            asyncio.run(cmd_notebook(args))
        elif cmd == "hermes":
            cmd_hermes(args)
        elif cmd == "cloud":
            cmd_cloud(args)
        elif cmd == "creative":
            cmd_creative(args)
        elif cmd == "sql":
            cmd_sql(args)
        elif cmd == "audiobook":
            cmd_audiobook(args)
        else:
            print(f"  Unknown command: '{cmd}'.")
    else:
        run()

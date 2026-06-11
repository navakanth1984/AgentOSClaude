"""
workflow.py — Agent OS Content Pipeline
========================================
Prompt → NotebookLM → Obsidian → Build Suggestion

ARCHITECTURE (from agentic-engineering + context-engineering):

  program.md  = this docstring + user prompt (the contract)
  train.py    = the pipeline stages below (agent modifies this search space)
  prepare.py  = obsidian_bridge validation (locked: was the note saved correctly?)

CDLC Mapping:
  GENERATE   → analyze prompt, find notebooks, trigger NotebookLM
  TEST       → verify content exists (audio >50KB, note has required fields)
  DISTRIBUTE → save structured Obsidian note with proper frontmatter
  OBSERVE    → log to workflow_log.json (BIT Integrate), surface suggestions

Usage Limit Strategy:
  - Cache-first: search notebook_cache.json before opening browser
  - Browser only when --browser flag is set or auto_notebooklm=True
  - Batch: one browser session for all NotebookLM operations
  - Skip-if-fresh: if cache < 24h old, don't re-scrape

Run:
  python workflow.py "summarize CDLC framework into a skill"
  python workflow.py "build audio overview for agent os notebook" --browser
"""

import asyncio
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Force UTF-8 console output on Windows (✓ ✗ ═ ① etc. in print statements)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─── Re-exports from extracted modules ────────────────────────
# These modules were split out of workflow.py for cohesion.
# Import them here so existing callers (server.py, goal_mode.py, etc.)
# can still do `from workflow import run_swarm` without changes.
from openrouter_client import call_openrouter as _call_openrouter  # noqa: F401
from swarm import run_swarm                                          # noqa: F401
from builders import (                                               # noqa: F401
    build_output,
    suggest_actions,
    _next_steps_for,
    _scaffold_skill,
    _scaffold_flutter_screen,
)

# Load .env from project root if present (OpenRouter key, etc.)
_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())


# ─── Config ───────────────────────────────────────────────────

ASSET_LIBRARY  = Path(__file__).parent / "asset_library"
NOTEBOOK_CACHE = Path(__file__).parent / "notebook_cache.json"
WORKFLOW_LOG   = Path(__file__).parent / "workflow_log.json"
SKILLS_DIR     = Path(__file__).parent.parent / ".claude" / "skills"

ASSET_LIBRARY.mkdir(exist_ok=True)


# ─── WorkflowResult — Tracks state across all stages ─────────

class WorkflowResult:
    """
    Single object threaded through every pipeline stage.
    Every stage reads from it and writes back to it.
    This is the context window for the pipeline — structured, not a dump of text.
    """
    def __init__(self, prompt: str):
        self.prompt        = prompt
        self.started_at    = datetime.now().isoformat()
        self.intent        = {}       # from analyze_prompt()
        self.notebooks     = []       # matching notebooks from cache
        self.notebook      = None     # best match {title, url}
        self.audio_path    = None     # path to captured audio file
        self.note_path     = None     # path to saved Obsidian note
        self.suggestions   = []       # [{action, description, command, priority}]
        self.built         = []       # things actually built this run
        self.errors        = []
        self.stages        = {}       # stage_name → {data, ts}

    def record(self, stage: str, data: dict):
        self.stages[stage] = {"data": data, "ts": datetime.now().isoformat()}

    def to_dict(self) -> dict:
        return {
            "prompt":       self.prompt,
            "started_at":   self.started_at,
            "intent":       self.intent,
            "notebook":     self.notebook,
            "audio_path":   self.audio_path,
            "note_path":    self.note_path,
            "suggestions":  self.suggestions,
            "built":        self.built,
            "errors":       self.errors,
            "stages":       self.stages,
        }


# ─── Stage 1: Analyze Prompt ─────────────────────────────────

def analyze_prompt(prompt: str) -> dict:
    """
    CDLC Phase: GENERATE
    Extract structured intent from natural language.

    Returns {topic, keywords, output_type, action, tags}.
    This is the 'spec' that drives every downstream stage.
    """
    p = prompt.lower()

    # Output type — what does the user want to produce?
    output_type = "note"
    if any(w in p for w in ["skill", "skills", "reusable"]):
        output_type = "skill"
    elif any(w in p for w in ["app", "dashboard", "flutter", "screen", "panel"]):
        output_type = "app"
    elif any(w in p for w in ["audio", "podcast", "listen", "sound"]):
        output_type = "audio"
    elif any(w in p for w in ["video", "avatar", "hermes", "seedance"]):
        output_type = "video"

    # Action — what should the agent DO with the content?
    action = "summarize"
    if any(w in p for w in ["build", "create", "generate", "make", "write"]):
        action = "build"
    elif any(w in p for w in ["deep dive", "explore", "research", "investigate"]):
        action = "deep_dive"
    elif any(w in p for w in ["enhance", "improve", "upgrade", "extend"]):
        action = "enhance"

    # Topic extraction: remove common filler words, keep meaningful tokens
    stop = {
        "build","create","summarize","get","make","about","from","the","a","an",
        "into","to","and","or","for","with","using","my","our","its","this","that",
        "please","can","you","help","me","us","how","what","where","when","why",
        "workflow","pipeline","automate","automation","process","take","prompt",
    }
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]*", prompt)
    topic_words = [w for w in words if w.lower() not in stop and len(w) > 2]
    topic = " ".join(topic_words[:7])

    # Keywords for notebook cache search (deduplicated, sorted by length desc)
    keywords = list(dict.fromkeys(w.lower() for w in topic_words))
    keywords.sort(key=len, reverse=True)
    keywords = keywords[:5]

    # Auto-tags
    tags = ["agent-os", "workflow", action, output_type]
    tags += [kw.replace(" ", "-") for kw in keywords[:3]]

    return {
        "topic":       topic,
        "keywords":    keywords,
        "output_type": output_type,
        "action":      action,
        "tags":        tags,
        "prompt":      prompt,
    }


def analyze_prompt_llm(prompt: str) -> Optional[dict]:
    """
    LLM-powered intent extraction via OpenRouter.
    Used when OPENROUTER_API_KEY is set in .env — replaces the rule-based version.
    Falls back gracefully to None (caller uses rule-based fallback).

    Model priority (Usage Limit Optimizer: free tier routing):
      1. perplexity/sonar — live search context, best quality but paid
      2. google/gemma-4-31b-it:free — free fallback, works on free-tier accounts
    """
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return None

    system = (
        "You are an intent parser for an AI knowledge workflow system. "
        "Given a user prompt, return ONLY valid JSON with these exact keys: "
        "topic (string, max 7 words), keywords (list of 5 strings), "
        "output_type (one of: note/skill/app/audio/video), "
        "action (one of: summarize/build/deep_dive/enhance/research), "
        "tags (list of 5 strings). No explanation, no markdown fences, just JSON."
    )

    # Try paid model first, fall back to free model on any error
    for model in ["perplexity/sonar", "google/gemma-4-31b-it:free"]:
        try:
            from openrouter_client import call_openrouter
            content = call_openrouter(model, system, prompt, api_key, max_tokens=200, temperature=0.1)
            # Strip markdown code fences if model ignores the "no fences" instruction
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            parsed = json.loads(content.strip())
            parsed["prompt"] = prompt
            label = "(free)" if "free" in model else ""
            print(f"[Workflow] LLM intent {label} (OpenRouter): topic='{parsed.get('topic')}'")
            return parsed
        except Exception as e:
            print(f"[Workflow] Model {model} failed ({e}), trying next...")

    print("[Workflow] All LLM models failed, using rule-based fallback.")
    return None


# ─── Stage 2: Find Notebooks ─────────────────────────────────

def find_matching_notebooks(keywords: list, max_results: int = 5) -> list:
    """
    CDLC Phase: GENERATE (context gathering)
    Search notebook_cache.json for notebooks matching topic keywords.
    Cache-first: no browser needed.
    """
    if not NOTEBOOK_CACHE.exists():
        print("[Workflow] No notebook cache. Run: python notebooklm_agent.py list")
        return []

    data = json.loads(NOTEBOOK_CACHE.read_text(encoding="utf-8"))

    # Check cache age — warn if stale (>7 days)
    cached_at = data.get("cached_at", "")
    if cached_at:
        try:
            age = datetime.now() - datetime.fromisoformat(cached_at)
            if age > timedelta(days=7):
                print(f"[Workflow] ⚠ Cache is {age.days} days old. Consider refreshing: python notebooklm_agent.py list")
        except Exception:
            pass

    all_notebooks = data.get("notebooks", [])
    print(f"[Workflow] Searching {len(all_notebooks)} notebooks for: {keywords}")

    scored = []
    for nb in all_notebooks:
        title = nb.get("title", "").lower()
        # Score: exact keyword match = 2pts, partial = 1pt
        score = 0
        for kw in keywords:
            if kw in title:
                score += 2 if f" {kw} " in f" {title} " else 1
        if score > 0:
            scored.append((score, nb))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [nb for _, nb in scored[:max_results]]


# ─── Stage 3: NotebookLM Content Generation ──────────────────

async def generate_notebooklm_content(notebook_url: str, result: WorkflowResult):
    """
    CDLC Phase: GENERATE
    Open the notebook, play existing audio (Strategy A) or generate new (Strategy B).
    Only runs when auto_notebooklm=True — respects usage-limit-optimizer batching rule.
    """
    try:
        from notebooklm_agent import run_session
        print(f"[Workflow] Opening NotebookLM: {notebook_url[:60]}...")
        audio_result = await run_session("generate", notebook_url)

        if audio_result.get("downloaded"):
            result.audio_path = audio_result["path"]
            print(f"[Workflow] ✓ Audio: {Path(result.audio_path).name}")
        else:
            print(f"[Workflow] Audio not captured: {audio_result.get('error', 'unknown')}")

        result.record("generate", audio_result)

    except Exception as e:
        err = f"NotebookLM error: {e}"
        result.errors.append(err)
        print(f"[Workflow] ✗ {err}")


# ─── Stage 4: Save to Obsidian ───────────────────────────────

def save_to_obsidian(intent: dict, result: WorkflowResult) -> Optional[str]:
    """
    CDLC Phase: DISTRIBUTE
    Save a structured Obsidian note using the proper capture format.
    This is the locked 'prepare.py' output — the eval criterion.
    A workflow run is ONLY considered successful if this step saves a note.
    """
    try:
        from obsidian_bridge import save_note

        topic       = intent["topic"]
        output_type = intent["output_type"]
        action      = intent["action"]

        # Build details section
        lines = []
        lines.append(f"**Prompt:** {result.prompt}")
        lines.append(f"**Action:** `{action}` → `{output_type}`")
        lines.append("")

        if result.notebook:
            title = result.notebook.get("title", "Unknown")
            url   = result.notebook.get("url", "")
            lines.append(f"**Source Notebook:** [{title}](https://notebooklm.google.com{url})")

        if result.audio_path:
            audio_name = Path(result.audio_path).name
            lines.append(f"**Audio Overview:** `asset_library/{audio_name}` ({Path(result.audio_path).stat().st_size // 1024} KB)")

        if result.errors:
            lines.append("")
            lines.append("**Errors:**")
            for e in result.errors:
                lines.append(f"- {e}")

        # Next steps based on output type
        next_steps = _next_steps_for(output_type, result, intent)

        file_path = save_note(
            title=f"Workflow: {topic}",
            key_idea=f"{action.title()} — {output_type}. Auto-generated via Agent OS workflow pipeline.",
            details="\n".join(lines),
            next_steps=next_steps,
            tags=intent["tags"],
            folder="inbox",
        )

        print(f"[Workflow] ✓ Obsidian note: {file_path}")
        return str(file_path)

    except Exception as e:
        err = f"Obsidian save error: {e}"
        result.errors.append(err)
        print(f"[Workflow] ✗ {err}")
        return None


# ─── Stage 5 & 6 functions live in builders.py ────────────────
# _next_steps_for, build_output, _scaffold_skill,
# _scaffold_flutter_screen, suggest_actions
# are imported at the top of this file from builders.py


# ─── Stage 7: Log (BIT Integrate) ────────────────────────────

def log_workflow(result: WorkflowResult):
    """
    BIT Integrate phase: append this run to workflow_log.json.
    Keeps last 100 runs. The log feeds the BIT Tune phase —
    reviewing it shows patterns in what topics/output_types are most used.
    """
    log = []
    if WORKFLOW_LOG.exists():
        try:
            log = json.loads(WORKFLOW_LOG.read_text(encoding="utf-8"))
        except Exception:
            log = []

    log.append({
        "ts":          result.started_at,
        "prompt":      result.prompt,
        "topic":       result.intent.get("topic", ""),
        "output_type": result.intent.get("output_type", ""),
        "action":      result.intent.get("action", ""),
        "notebook":    result.notebook.get("title", "") if result.notebook else None,
        "audio_path":  result.audio_path,
        "note_path":   result.note_path,
        "built":       result.built,
        "errors":      result.errors,
    })

    WORKFLOW_LOG.write_text(
        json.dumps(log[-100:], indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


# ─── Swarm functions live in swarm.py / openrouter_client.py ──
# _call_openrouter → openrouter_client.py
# _swarm_agent, run_swarm → swarm.py
# Both re-exported at the top of this file.


# ─── Main Pipeline ────────────────────────────────────────────

async def run_workflow(
    prompt: str,
    auto_notebooklm: bool = False,
    build: bool = False,
) -> dict:
    """
    Full CDLC pipeline.

    Args:
      prompt:          natural language request
      auto_notebooklm: open browser + capture NotebookLM audio
      build:           scaffold skill/app files (no browser needed)

    Returns: WorkflowResult.to_dict()
    """
    result = WorkflowResult(prompt)
    print(f"\n{'═'*60}")
    print(f"[Workflow] Prompt: {prompt[:80]}...")
    print(f"{'═'*60}\n")

    # ── GENERATE: Analyze ─────────────────────────────────────
    print("[Workflow] ① Analyzing prompt...")
    intent = analyze_prompt_llm(prompt) or analyze_prompt(prompt)
    result.intent = intent
    result.record("analyze", intent)
    print(f"           Topic: '{intent['topic']}'")
    print(f"           Action: {intent['action']} | Output: {intent['output_type']}")
    print(f"           Keywords: {intent['keywords']}")

    # ── GENERATE: Find Notebooks ──────────────────────────────
    print("\n[Workflow] ② Searching notebook cache...")
    matches = find_matching_notebooks(intent["keywords"])
    result.notebooks = matches
    result.record("find_notebook", {"count": len(matches), "matches": [m.get("title") for m in matches]})

    if matches:
        result.notebook = matches[0]
        print(f"           ✓ Best match: '{result.notebook.get('title', '')}'")
        for i, m in enumerate(matches[1:4], 2):
            print(f"           #{i}: {m.get('title', '')}")
    else:
        print("           No matches found in cache.")

    # ── GENERATE: NotebookLM (browser, optional) ──────────────
    if auto_notebooklm and result.notebook:
        print(f"\n[Workflow] ③ NotebookLM pipeline (browser opening)...")
        await generate_notebooklm_content(result.notebook["url"], result)
    else:
        reason = "notebook not found" if not result.notebook else "use --browser to enable"
        print(f"\n[Workflow] ③ Skipping NotebookLM browser ({reason})")
        result.record("generate", {"skipped": True})

    # ── GENERATE: Build Outputs ───────────────────────────────
    if build:
        print(f"\n[Workflow] ④ Building {intent['output_type']} output...")
        result.built = build_output(intent, result)
        result.record("build", {"built": result.built})
    else:
        print(f"\n[Workflow] ④ Skipping build (use --build to scaffold files)")

    # ── DISTRIBUTE: Save to Obsidian ─────────────────────────
    print(f"\n[Workflow] ⑤ Saving to Obsidian...")
    note_path = save_to_obsidian(intent, result)
    result.note_path = note_path
    result.record("save", {"note_path": note_path})

    # ── OBSERVE: Suggest + Log ────────────────────────────────
    print(f"\n[Workflow] ⑥ Generating suggestions...")
    result.suggestions = suggest_actions(intent, result)
    log_workflow(result)
    result.record("observe", {"suggestions": len(result.suggestions)})

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"[Workflow] ✓ Pipeline complete")
    print(f"  Notebook:    {result.notebook.get('title', 'none') if result.notebook else 'none'}")
    print(f"  Audio:       {Path(result.audio_path).name if result.audio_path else 'not captured'}")
    print(f"  Note:        {result.note_path or 'not saved'}")
    print(f"  Built:       {len(result.built)} artifact(s)")
    print(f"\n  Next steps:")
    for s in result.suggestions[:3]:
        print(f"    [{s['priority'].upper():6}] {s['action']}: {s['command']}")
    print(f"{'─'*60}\n")

    return result.to_dict()


# ─── CLI ──────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args == ["--help"]:
        print("""
Agent OS Workflow Pipeline
==========================
Usage:
  python workflow.py "your prompt" [--browser] [--build]

Flags:
  --browser  Open NotebookLM browser to capture audio overview
  --build    Scaffold skill/Flutter screen files locally

Examples:
  python workflow.py "summarize CDLC framework"
  python workflow.py "build a skill from agent os notebooks" --build
  python workflow.py "get audio overview for notebooklm obsidian notebook" --browser
  python workflow.py "create flutter app for context engineering" --build

The pipeline runs these stages:
  ① Analyze prompt → extract topic, keywords, output type
  ② Search notebook cache → find matching notebooks
  ③ NotebookLM → capture audio (--browser only)
  ④ Build output → scaffold skill/app files (--build only)
  ⑤ Save to Obsidian → structured note in 00-Inbox
  ⑥ Suggest next actions → logged to workflow_log.json
""")
        sys.exit(0)

    browser = "--browser" in args
    build   = "--build" in args
    prompt  = " ".join(a for a in args if not a.startswith("--")).strip()

    if not prompt:
        print("Error: please provide a prompt. Run with --help for usage.")
        sys.exit(1)

    result = asyncio.run(run_workflow(prompt, auto_notebooklm=browser, build=build))
    print(json.dumps({
        "notebook": result.get("notebook", {}).get("title") if result.get("notebook") else None,
        "audio":    result.get("audio_path"),
        "note":     result.get("note_path"),
        "built":    result.get("built"),
        "errors":   result.get("errors"),
        "next":     [s["command"] for s in result.get("suggestions", [])[:3]],
    }, indent=2))

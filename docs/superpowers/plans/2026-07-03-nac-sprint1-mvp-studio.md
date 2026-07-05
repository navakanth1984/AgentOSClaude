# NAC Sprint 1 — First Usable NAC Studio (MVP) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Idea → Story Bible → Screenplay → Audio Screenplay → Motion Poster prompt →
`.nac`-style project export, working end to end, local-first, on the frozen
`E:\nth-absolute-cinema\` architecture (`ARCHITECTURE_FINGERPRINT.md`,
`30637b99...`) — packaged as a standalone, pip-installable SDK (`nac`) with a CLI on
top, and a thin bridge module inside `navakanth001/agent_os/` that consumes NAC only
through that SDK. NAC remains fully independent and reusable; Agent OS becomes one
consumer of it, not its host.

**Hybrid architecture decision (2026-07-03, revises the original "CLI only" framing
below without touching anything frozen in `docs/specs/v1/`):** NAC is never built
inside `agent_os/`. It stays a standalone package rooted at `E:\nth-absolute-cinema\`,
installed via `pip install -e E:\nth-absolute-cinema`, exposing a public `nac` package
(`from nac import Studio`) as the *only* surface anything outside the NAC repo may
touch — internals (`engine.knowledge`, `engine.compilers`, `engine.storage`,
`engine.model_manager`, etc.) stay private to NAC, exactly as `MODULE_BOUNDARIES.md`
already requires for `engine.api`. Agent OS gets one new, small module,
`agent_os/filmmaking/nac_bridge.py`, that imports `nac.Studio` and exposes the same
six actions the CLI exposes (create project, generate story bible, generate
screenplay, generate audio, generate prompt, export) — no filmmaking logic, no graph
knowledge, no compiler code lives in `agent_os/`. Both the CLI (Task 11) and the
future Agent OS Filmmaking UI call the same SDK, so there is exactly one
implementation of the pipeline, not two.

**Architecture:** One vertical slice through the frozen ABIs — real but minimal
implementations of `PathResolver` (`WORKSPACE_SPEC.md`), a SQLite-backed subset of the
Knowledge Graph (`CREATIVE_GRAPH_SPEC.md` §2, just enough node types for this slice),
and four compilers (`COMPILER_ABI.md`'s 8 stages, collapsed to the steps that matter
for MVP — no Repair-stage retry logic yet, no Review Graph human-approval gate yet;
both are explicit MVP simplifications, called out per task, not silent omissions).
Local LLM via Ollama (pattern reused from
`C:\Users\navka\navakanth001\agent_os\cinematic_model_router.py`, confirmed present in
this workspace — same `OllamaConfig(base_url="http://localhost:11434", model=...)`
shape, reimplemented standalone inside NAC so `engine.model_manager` has no
cross-repo dependency per `MODULE_BOUNDARIES.md` rule 7). Local TTS via `pyttsx3`
(stdlib-adjacent, zero model download, ships with Windows SAPI voices) — this is an
intentional MVP choice over Kokoro (which needs an on-demand model download,
`COMPUTE_MANAGER_SPEC.md` §19) to keep Sprint 1 runnable with nothing pre-installed
beyond `pip install`.

**Tech Stack:** Python 3.12 (`py -3`, per this workspace's existing convention —
bare `python` resolves to the Windows Store alias stub). `sqlite3` (stdlib). `requests`
for Ollama HTTP calls. `pyttsx3` for offline TTS. `pytest` for tests. No web framework,
no FastAPI, no dashboard — `engine.api` (per `MODULE_BOUNDARIES.md`) is a Phase-later
concern; the CLI calls compiler classes directly for Sprint 1.

## Execution amendment (2026-07-03, before implementation begins)

- **Checkpoint grouping, not task-by-task stops:** A=Tasks 1-4 (Studio() + create_project
  works), B=Tasks 5-8 (Idea→Screenplay works), C=Tasks 9-12 (full `nac create` works,
  exports files), C.5=director validation (status/regenerate_stage/record_review/
  import_asset added to Studio + CLI, additive, no new import surface — inserted
  2026-07-03 after Checkpoint C shipped, per user request, before D), D=Task 13
  (Agent OS bridge). Report back at each checkpoint boundary.
- **Checkpoint C.5 also marks `nac.Studio`, the Knowledge Graph schema
  (`engine.storage.db.SCHEMA`), compiler contracts, and the Production Package/`.nac`
  layout as versioned public interfaces going forward** (`nac.SDK_VERSION`, currently
  `0.1.0`) — new fields/methods are additive; removing or renaming an existing one is
  a breaking change requiring a version bump, mirroring `VERSIONING_POLICY.md`'s
  semver rules already frozen in Sprint 0.
- **Every commit leaves the system runnable and its own smoke test passing** — never a
  commit that only makes sense once a later commit lands.
- **Optimize for demonstrability over completeness.** A simple compiler that works beats
  a sophisticated one that's 30% done.
- **Structured metrics on every compiler run**, alongside the artifact text, not instead
  of it: `{compiler, duration_s, tokens, model, cost_usd, confidence, warnings,
  output_hash, knowledge_version, compiler_version}`. `CompilerBase.run()` (or each
  subclass's `run()`) returns `(output_text, Provenance, metrics_dict)` — a three-tuple,
  not two — applied uniformly to Tasks 4-8's `run()` signatures as implemented (this
  supersedes the two-tuple `(output, Provenance)` shown in Tasks 5-8's plan code below;
  the actual implementation adds the metrics dict).
- **SDK import surface stays absolute:** only `from nac import Studio` is public.
  `from nac.compilers...`, `from nac.storage...`, `from nac.graphs...` never exist as
  supported imports — enforced by `nac/__init__.py` not re-exporting anything but
  `Studio`/`OllamaNotReachableError`.
- **`nac build` alias:** Task 11's CLI gets a `build` subcommand as an alias for
  `create` (matches the recommended end-of-sprint UX: `nac create "<idea>"` then
  `nac build` — for MVP, `build` on an existing project re-runs stages 2-6 against
  the most recent project id).
- **Demo regression artifact:** after Checkpoint C, generate one real example end to
  end and commit its output under `examples/temple_of_varuna/` — not test fixtures,
  actual generated output, becoming the baseline for comparing future compiler changes.

## Global Constraints

- Everything under `E:\nth-absolute-cinema\engine\` — a separate repo from
  `navakanth001`, per `WORKSPACE_SPEC.md`.
- No compiler skips `COMPILER_ABI.md`'s Validation or Export stages — those are
  non-negotiable even in MVP form. Planning/Estimation, Repair, and Review are
  simplified (see per-task notes) but not silently dropped: each simplified stage
  still exists as a real method that does the minimal correct thing (e.g. Planning
  returns a rough token-count estimate, not nothing).
- `abi_version="1.0"` and `graph_spec_version="1.0"` recorded on every artifact's
  Provenance block (`CREATIVE_GRAPH_SPEC.md` §9) — Sprint 1 code targets the frozen
  fingerprint, not a moving target.
- Ollama must actually be running locally for the Story/Screenplay/Prompt compilers to
  produce real output — if it isn't, the CLI fails loudly with an actionable error
  ("Ollama not reachable at http://localhost:11434 — install from ollama.com and run
  `ollama pull gemma2:9b`"), never a silent stub or mock response outside of tests.
- `pytest` for every compiler's logic (Ollama/`pyttsx3` calls mocked); one real,
  unmocked smoke-test script (Task 9) exercises the full pipeline against a live
  Ollama instance — this is the "does it actually work" proof, run manually, not in
  CI (no Ollama in CI for Sprint 1).
- Pyrefly is a `navakanth001`-repo concept (its pre-commit hook); the NAC repo has no
  such hook yet — Sprint 1 does not add one (that's tooling, not architecture, out of
  scope per `SPRINT0_FREEZE.md` non-goals — CI/lint enforcement is explicitly deferred).

---

## File Structure

```
E:\nth-absolute-cinema\
  engine\
    kernel\
      __init__.py
      paths.py                 (Task 1 — PathResolver)
      models.py                 (Task 1 — shared dataclasses: Provenance, Estimate)
    storage\
      __init__.py
      db.py                      (Task 2 — SQLite connection + schema)
      knowledge_repo.py           (Task 2 — KnowledgeGraphRepository impl, MVP subset)
    model_manager\
      __init__.py
      ollama_provider.py          (Task 3 — local LLM HTTP client)
      tts_provider.py               (Task 3 — pyttsx3 wrapper)
    compilers\
      __init__.py
      base.py                        (Task 4 — Compiler ABC, 8-stage skeleton)
      story_compiler.py                (Task 5)
      screenplay_compiler.py            (Task 6)
      audio_compiler.py                  (Task 7)
      prompt_compiler.py                  (Task 8)
    portability\
      __init__.py
      export.py                            (Task 9 — MVP folder export)
  nac\
    __init__.py                              (Task 10 — public SDK: `from nac import Studio`)
  cli\
    __init__.py
    __main__.py                                (Task 11 — `nac` CLI, calls nac.Studio only)
  tests\
    test_paths.py                           (Task 1)
    test_knowledge_repo.py                   (Task 2)
    test_ollama_provider.py                   (Task 3)
    test_story_compiler.py                     (Task 5)
    test_screenplay_compiler.py                 (Task 6)
    test_audio_compiler.py                       (Task 7)
    test_prompt_compiler.py                       (Task 8)
    test_export.py                                 (Task 9)
    test_sdk.py                                      (Task 10)
  scratchpad\
    smoke_test_full_pipeline.py                     (Task 12 — manual, unmocked)
  pyproject.toml                                        (Task 10 — `pip install -e .`)
  requirements.txt                                        (Task 1)
  .nac-root                                                 (Task 1 — marker file, empty)
```

In `navakanth001` (existing repo, new files only — no existing agent_os code
modified):
```
agent_os\
  filmmaking\
    __init__.py
    nac_bridge.py                (Task 13 — thin wrapper over nac.Studio only)
```

---

### Task 1: Kernel — PathResolver + shared models + repo dependencies

**Files:**
- Create: `E:\nth-absolute-cinema\.nac-root` (empty marker file)
- Create: `E:\nth-absolute-cinema\requirements.txt`
- Create: `E:\nth-absolute-cinema\engine\kernel\__init__.py`
- Create: `E:\nth-absolute-cinema\engine\kernel\paths.py`
- Create: `E:\nth-absolute-cinema\engine\kernel\models.py`
- Test: `E:\nth-absolute-cinema\tests\test_paths.py`

**Interfaces:**
- Produces: `PathResolver` class (matches `WORKSPACE_SPEC.md`'s
  `find_root/resolve/root` method names exactly), `Provenance` and `Estimate`
  dataclasses (field names match `CREATIVE_GRAPH_SPEC.md` §9 and §6 exactly).

- [ ] **Step 1: Write the failing test**

`E:\nth-absolute-cinema\tests\test_paths.py`:
```python
import os
from pathlib import Path
import pytest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine.kernel.paths import PathResolver, NacRootNotFoundError


def test_find_root_walks_up_to_marker(tmp_path):
    root = tmp_path / "project"
    (root / "engine" / "kernel").mkdir(parents=True)
    (root / ".nac-root").write_text("")
    start = root / "engine" / "kernel"
    resolver = PathResolver()
    assert resolver.find_root(start) == root


def test_find_root_raises_when_no_marker(tmp_path):
    resolver = PathResolver()
    with pytest.raises(NacRootNotFoundError):
        resolver.find_root(tmp_path)


def test_resolve_joins_root_and_relative(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / ".nac-root").write_text("")
    resolver = PathResolver()
    resolver.find_root(root)
    assert resolver.resolve("projects/demo") == root / "projects" / "demo"


def test_root_returns_cached_root(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / ".nac-root").write_text("")
    resolver = PathResolver()
    resolver.find_root(root)
    assert resolver.root() == root
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_paths.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'engine.kernel.paths'`

- [ ] **Step 3: Write `requirements.txt`**

```
requests>=2.31
pyttsx3>=2.90
pytest>=8.0
```

- [ ] **Step 4: Write `engine/kernel/__init__.py`** (empty file, makes it a package)

- [ ] **Step 5: Write `engine/kernel/paths.py`**

```python
"""PathResolver — WORKSPACE_SPEC.md. No module outside this file may build an
absolute path via string concatenation or a hardcoded drive letter."""
from __future__ import annotations

from pathlib import Path

ROOT_MARKER = ".nac-root"


class NacRootNotFoundError(RuntimeError):
    """Raised when no .nac-root marker is found walking up from start_path."""


class PathResolver:
    def __init__(self) -> None:
        self._root: Path | None = None

    def find_root(self, start_path: Path) -> Path:
        current = Path(start_path).resolve()
        while True:
            if (current / ROOT_MARKER).is_file():
                self._root = current
                return current
            if current.parent == current:
                raise NacRootNotFoundError(
                    f"No {ROOT_MARKER} found walking up from {start_path}"
                )
            current = current.parent

    def resolve(self, relative: str) -> Path:
        if self._root is None:
            raise NacRootNotFoundError("find_root() must be called before resolve()")
        return self._root / Path(relative)

    def root(self) -> Path:
        if self._root is None:
            raise NacRootNotFoundError("find_root() must be called before root()")
        return self._root
```

- [ ] **Step 6: Write `engine/kernel/models.py`**

```python
"""Shared dataclasses whose field names are fixed by CREATIVE_GRAPH_SPEC.md.
Every other module imports Provenance/Estimate from here — never redefines them."""
from __future__ import annotations

from dataclasses import dataclass, field
import uuid


@dataclass
class Provenance:
    knowledge_version: str
    compiler_id: str
    compiler_version: str
    model: str
    output_hash: str
    pack_id: str | None = None
    pack_version: str | None = None
    seed: int | None = None


@dataclass
class Estimate:
    job_id: str
    estimated_tokens: int
    estimated_gpu_hours: float
    estimated_ram_mb: int
    estimated_time_s: int
    estimated_cost_usd: float
    confidence: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_paths.py -v`
Expected: 4 passed

- [ ] **Step 8: Commit**

```powershell
cd E:\nth-absolute-cinema
git add .nac-root requirements.txt engine\kernel\__init__.py engine\kernel\paths.py engine\kernel\models.py tests\test_paths.py
git commit -m "feat(kernel): PathResolver + shared Provenance/Estimate models"
```

---

### Task 2: Storage — SQLite schema + minimal Knowledge Graph repository

**Files:**
- Create: `E:\nth-absolute-cinema\engine\storage\__init__.py`
- Create: `E:\nth-absolute-cinema\engine\storage\db.py`
- Create: `E:\nth-absolute-cinema\engine\storage\knowledge_repo.py`
- Test: `E:\nth-absolute-cinema\tests\test_knowledge_repo.py`

**Interfaces:**
- Consumes: `PathResolver` (Task 1).
- Produces: `KnowledgeRepo` class with `create_story(idea_text) -> str (story_id)`,
  `save_story_bible(story_id, content) -> None`,
  `save_screenplay(story_id, fountain_text) -> None`,
  `get_story(story_id) -> dict`. This is the MVP subset of
  `CREATIVE_GRAPH_SPEC.md` §2's `Story`/`StoryBible` node types — only the fields
  Sprint 1's pipeline actually reads/writes, not the full schema (Beats/Scenes/
  Characters are Sprint 2+ per `SPRINT0_FREEZE.md`'s non-goals).

- [ ] **Step 1: Write the failing test**

`E:\nth-absolute-cinema\tests\test_knowledge_repo.py`:
```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine.storage.db import init_db
from engine.storage.knowledge_repo import KnowledgeRepo


def test_create_story_and_round_trip(tmp_path):
    db_path = tmp_path / "test.db"
    conn = init_db(db_path)
    repo = KnowledgeRepo(conn)

    story_id = repo.create_story("A forgotten temple beneath the sea")
    assert story_id

    story = repo.get_story(story_id)
    assert story["idea_text"] == "A forgotten temple beneath the sea"
    assert story["story_bible"] is None
    assert story["screenplay"] is None

    repo.save_story_bible(story_id, "# Story Bible\n...")
    repo.save_screenplay(story_id, "INT. TEMPLE - DAY\n...")

    story = repo.get_story(story_id)
    assert story["story_bible"] == "# Story Bible\n..."
    assert story["screenplay"] == "INT. TEMPLE - DAY\n..."
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_knowledge_repo.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `engine/storage/db.py`**

```python
"""SQLite connection + schema init. Project-tier storage per WORKSPACE_SPEC.md —
this file only ever writes into the project tier, never cache/renders/temp."""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS story (
    id TEXT PRIMARY KEY,
    idea_text TEXT NOT NULL,
    story_bible TEXT,
    screenplay TEXT,
    audio_path TEXT,
    motion_poster_prompt TEXT,
    graph_spec_version TEXT NOT NULL DEFAULT '1.0',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
```

- [ ] **Step 4: Write `engine/storage/knowledge_repo.py`**

```python
"""KnowledgeRepo — MVP subset of KnowledgeGraphRepository (REPOSITORY_INTERFACES.md).
Sprint 1 scope only: Story node with idea/story_bible/screenplay/audio/prompt fields.
Beats, Scenes, Characters (full CREATIVE_GRAPH_SPEC.md §2) are Sprint 2+."""
from __future__ import annotations

import sqlite3
import uuid


class KnowledgeRepo:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create_story(self, idea_text: str) -> str:
        story_id = str(uuid.uuid4())
        self._conn.execute(
            "INSERT INTO story (id, idea_text) VALUES (?, ?)",
            (story_id, idea_text),
        )
        self._conn.commit()
        return story_id

    def get_story(self, story_id: str) -> dict:
        row = self._conn.execute(
            "SELECT * FROM story WHERE id = ?", (story_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"No story with id {story_id}")
        return dict(row)

    def save_story_bible(self, story_id: str, content: str) -> None:
        self._conn.execute(
            "UPDATE story SET story_bible = ? WHERE id = ?", (content, story_id)
        )
        self._conn.commit()

    def save_screenplay(self, story_id: str, fountain_text: str) -> None:
        self._conn.execute(
            "UPDATE story SET screenplay = ? WHERE id = ?", (fountain_text, story_id)
        )
        self._conn.commit()

    def save_audio_path(self, story_id: str, audio_path: str) -> None:
        self._conn.execute(
            "UPDATE story SET audio_path = ? WHERE id = ?", (audio_path, story_id)
        )
        self._conn.commit()

    def save_motion_poster_prompt(self, story_id: str, prompt_text: str) -> None:
        self._conn.execute(
            "UPDATE story SET motion_poster_prompt = ? WHERE id = ?",
            (prompt_text, story_id),
        )
        self._conn.commit()
```

- [ ] **Step 5: Write `engine/storage/__init__.py`** (empty)

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_knowledge_repo.py -v`
Expected: 1 passed

- [ ] **Step 7: Commit**

```powershell
cd E:\nth-absolute-cinema
git add engine\storage\__init__.py engine\storage\db.py engine\storage\knowledge_repo.py tests\test_knowledge_repo.py
git commit -m "feat(storage): SQLite schema + MVP KnowledgeRepo (Story node subset)"
```

---

### Task 3: Model Manager — Ollama provider + TTS provider

**Files:**
- Create: `E:\nth-absolute-cinema\engine\model_manager\__init__.py`
- Create: `E:\nth-absolute-cinema\engine\model_manager\ollama_provider.py`
- Create: `E:\nth-absolute-cinema\engine\model_manager\tts_provider.py`
- Test: `E:\nth-absolute-cinema\tests\test_ollama_provider.py`

**Interfaces:**
- Produces: `OllamaProvider.generate(prompt: str, system: str = "") -> str`,
  `OllamaNotReachableError`, `TtsProvider.synthesize(text: str, out_path: Path) ->
  Path`.

- [ ] **Step 1: Write the failing test**

`E:\nth-absolute-cinema\tests\test_ollama_provider.py`:
```python
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine.model_manager.ollama_provider import OllamaProvider, OllamaNotReachableError


def test_generate_returns_response_text():
    provider = OllamaProvider(model="gemma2:9b")
    fake_response = MagicMock()
    fake_response.json.return_value = {"response": "Once upon a time..."}
    fake_response.raise_for_status.return_value = None
    with patch("requests.post", return_value=fake_response) as mock_post:
        result = provider.generate("Write a story opening.")
    assert result == "Once upon a time..."
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args.kwargs
    assert call_kwargs["json"]["model"] == "gemma2:9b"
    assert call_kwargs["json"]["prompt"] == "Write a story opening."
    assert call_kwargs["json"]["stream"] is False


def test_generate_raises_actionable_error_when_unreachable():
    provider = OllamaProvider(model="gemma2:9b")
    import requests

    with patch("requests.post", side_effect=requests.ConnectionError("refused")):
        try:
            provider.generate("hello")
            assert False, "expected OllamaNotReachableError"
        except OllamaNotReachableError as e:
            assert "ollama.com" in str(e)
            assert "gemma2:9b" in str(e)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_ollama_provider.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `engine/model_manager/ollama_provider.py`**

```python
"""Local LLM provider via Ollama HTTP API. Pattern reused (standalone, no import)
from C:\\Users\\navka\\navakanth001\\agent_os\\cinematic_model_router.py's
OllamaProvider/OllamaConfig — reimplemented here per MODULE_BOUNDARIES.md rule 7
(engine.model_manager may import engine.kernel only, no cross-repo dependency)."""
from __future__ import annotations

import requests


class OllamaNotReachableError(RuntimeError):
    pass


class OllamaProvider:
    def __init__(
        self,
        model: str = "gemma2:9b",
        base_url: str = "http://localhost:11434",
        timeout_s: float = 120.0,
        temperature: float = 0.7,
    ) -> None:
        self.model = model
        self.base_url = base_url
        self.timeout_s = timeout_s
        self.temperature = temperature

    def generate(self, prompt: str, system: str = "") -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        if system:
            payload["system"] = system
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=self.timeout_s
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise OllamaNotReachableError(
                f"Ollama not reachable at {self.base_url} for model '{self.model}' "
                f"— install from ollama.com and run `ollama pull {self.model}`. "
                f"Underlying error: {e}"
            ) from e
        return resp.json()["response"]
```

- [ ] **Step 4: Write `engine/model_manager/tts_provider.py`**

```python
"""Offline TTS via pyttsx3 (Windows SAPI voices) — Sprint 1's TTS choice over Kokoro
(COMPUTE_MANAGER_SPEC.md on-demand install is a Sprint 2+ upgrade path for this)."""
from __future__ import annotations

from pathlib import Path

import pyttsx3


class TtsProvider:
    def synthesize(self, text: str, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        engine = pyttsx3.init()
        engine.save_to_file(text, str(out_path))
        engine.runAndWait()
        return out_path
```

- [ ] **Step 5: Write `engine/model_manager/__init__.py`** (empty)

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_ollama_provider.py -v`
Expected: 2 passed

- [ ] **Step 7: Commit**

```powershell
cd E:\nth-absolute-cinema
git add engine\model_manager\__init__.py engine\model_manager\ollama_provider.py engine\model_manager\tts_provider.py tests\test_ollama_provider.py
git commit -m "feat(model_manager): OllamaProvider + pyttsx3 TtsProvider"
```

---

### Task 4: Compiler base class (simplified 8-stage skeleton for MVP)

**Files:**
- Create: `E:\nth-absolute-cinema\engine\compilers\__init__.py`
- Create: `E:\nth-absolute-cinema\engine\compilers\base.py`

**Interfaces:**
- Consumes: `Provenance`, `Estimate` (Task 1).
- Produces: `CompilerBase` ABC that Tasks 5-8 subclass. Implements
  `COMPILER_ABI.md`'s 8 stages, with `plan()`, `repair()`, and the human half of
  `review()` given real-but-minimal MVP bodies (documented per method, not silently
  dropped — see docstrings).

- [ ] **Step 1: Write `engine/compilers/base.py`** (no test — this is an abstract
  base with no standalone behavior; Tasks 5-8's tests exercise it through subclasses)

```python
"""CompilerBase — COMPILER_ABI.md's 8-stage pipeline, MVP-scoped.

MVP simplifications (intentional, not omissions):
  - plan(): returns a rough Estimate from a word-count heuristic, not a calibrated
    model — COMPUTE_MANAGER_SPEC.md-integrated real estimation is Sprint 2+.
  - repair(): bounded to zero retries in Sprint 1 (a failed Measurement just fails
    the job) — real repair logic needs a defect taxonomy that doesn't exist yet.
  - review(): only ai_self_review is implemented (a trivial non-empty-output check);
    human_review (CREATIVE_GRAPH_SPEC.md §7 ReviewEntry, stage="human_review") is a
    Sprint 2+ UI concern — the CLI prints the artifact and the human reads it, which
    is the review, just not persisted as a ReviewEntry row yet.
Every subclass still implements validate/plan/generate/measure/repair/review/export
as real methods — none of these are stubs that silently no-op.
"""
from __future__ import annotations

import hashlib
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from engine.kernel.models import Estimate, Provenance


@dataclass
class ValidationResult:
    layer: str
    passed: bool
    violations: list[str]


class CompilerBase(ABC):
    compiler_id: str
    compiler_version: str = "0.1.0"
    abi_version: str = "1.0"

    @abstractmethod
    def validate(self, input_text: str) -> list[ValidationResult]:
        ...

    def plan(self, input_text: str) -> Estimate:
        approx_tokens = max(1, len(input_text.split()) * 2)
        return Estimate(
            job_id=str(uuid.uuid4()),
            estimated_tokens=approx_tokens,
            estimated_gpu_hours=0.0,
            estimated_ram_mb=512,
            estimated_time_s=max(5, approx_tokens // 20),
            estimated_cost_usd=0.0,
            confidence=0.3,
        )

    @abstractmethod
    def generate(self, input_text: str) -> str:
        ...

    def measure(self, output_text: str) -> dict:
        return {"output_chars": len(output_text), "output_words": len(output_text.split())}

    def repair(self, output_text: str, measurement: dict) -> str:
        return output_text

    def review(self, output_text: str) -> dict:
        passed = len(output_text.strip()) > 0
        return {"stage": "ai_self_review", "verdict": "approved" if passed else "rejected"}

    def export(self, knowledge_version: str, model: str, output_text: str) -> Provenance:
        output_hash = hashlib.sha256(output_text.encode("utf-8")).hexdigest()
        return Provenance(
            knowledge_version=knowledge_version,
            compiler_id=self.compiler_id,
            compiler_version=self.compiler_version,
            model=model,
            output_hash=output_hash,
        )
```

- [ ] **Step 2: Write `engine/compilers/__init__.py`** (empty)

- [ ] **Step 3: Commit**

```powershell
cd E:\nth-absolute-cinema
git add engine\compilers\__init__.py engine\compilers\base.py
git commit -m "feat(compilers): CompilerBase — MVP-scoped 8-stage skeleton"
```

---

### Task 5: Story Compiler (Idea → Story Bible)

**Files:**
- Create: `E:\nth-absolute-cinema\engine\compilers\story_compiler.py`
- Test: `E:\nth-absolute-cinema\tests\test_story_compiler.py`

**Interfaces:**
- Consumes: `CompilerBase` (Task 4), `OllamaProvider` (Task 3).
- Produces: `StoryCompiler.run(idea_text: str) -> tuple[str, Provenance]` (story
  bible markdown text + provenance).

- [ ] **Step 1: Write the failing test**

`E:\nth-absolute-cinema\tests\test_story_compiler.py`:
```python
from pathlib import Path
import sys
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine.compilers.story_compiler import StoryCompiler


def test_run_produces_story_bible_and_provenance():
    fake_provider = MagicMock()
    fake_provider.model = "gemma2:9b"
    fake_provider.generate.return_value = "# Story Bible\n\nA sunken temple guards a secret."

    compiler = StoryCompiler(provider=fake_provider)
    bible_text, provenance = compiler.run("A forgotten temple beneath the sea")

    assert "Story Bible" in bible_text
    fake_provider.generate.assert_called_once()
    prompt_arg = fake_provider.generate.call_args.args[0]
    assert "forgotten temple beneath the sea" in prompt_arg
    assert provenance.compiler_id == "story_compiler"
    assert provenance.model == "gemma2:9b"
    assert len(provenance.output_hash) == 64


def test_validate_rejects_empty_idea():
    compiler = StoryCompiler(provider=MagicMock())
    results = compiler.validate("")
    assert any(not r.passed for r in results)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_story_compiler.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `engine/compilers/story_compiler.py`**

```python
"""StoryCompiler — Idea -> Story Bible. First stage of the Sprint 1 vertical slice."""
from __future__ import annotations

from engine.compilers.base import CompilerBase, ValidationResult
from engine.kernel.models import Provenance

SYSTEM_PROMPT = (
    "You are a story development assistant. Given a one-line creative idea, write a "
    "concise Story Bible in Markdown: Logline, Theme, Setting, Main Character, "
    "Central Conflict, Tone. Keep it under 400 words."
)


class StoryCompiler(CompilerBase):
    compiler_id = "story_compiler"

    def __init__(self, provider) -> None:
        self._provider = provider

    def validate(self, input_text: str) -> list[ValidationResult]:
        violations = []
        if not input_text.strip():
            violations.append("idea_text is empty")
        return [ValidationResult(layer="structural", passed=not violations, violations=violations)]

    def generate(self, input_text: str) -> str:
        prompt = f"Idea: {input_text}\n\nWrite the Story Bible now."
        return self._provider.generate(prompt, system=SYSTEM_PROMPT)

    def run(self, idea_text: str) -> tuple[str, Provenance]:
        results = self.validate(idea_text)
        if any(not r.passed for r in results):
            raise ValueError(f"Validation failed: {results}")
        output = self.generate(idea_text)
        output = self.repair(output, self.measure(output))
        self.review(output)
        provenance = self.export(
            knowledge_version="1.0", model=self._provider.model, output_text=output
        )
        return output, provenance
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_story_compiler.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```powershell
cd E:\nth-absolute-cinema
git add engine\compilers\story_compiler.py tests\test_story_compiler.py
git commit -m "feat(compilers): StoryCompiler — Idea to Story Bible"
```

---

### Task 6: Screenplay Compiler (Story Bible → Screenplay)

**Files:**
- Create: `E:\nth-absolute-cinema\engine\compilers\screenplay_compiler.py`
- Test: `E:\nth-absolute-cinema\tests\test_screenplay_compiler.py`

**Interfaces:**
- Consumes: `CompilerBase` (Task 4), `OllamaProvider` (Task 3).
- Produces: `ScreenplayCompiler.run(story_bible_text: str) -> tuple[str, Provenance]`
  (Fountain-format screenplay text + provenance).

- [ ] **Step 1: Write the failing test**

`E:\nth-absolute-cinema\tests\test_screenplay_compiler.py`:
```python
from pathlib import Path
import sys
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine.compilers.screenplay_compiler import ScreenplayCompiler


def test_run_produces_screenplay_and_provenance():
    fake_provider = MagicMock()
    fake_provider.model = "gemma2:9b"
    fake_provider.generate.return_value = "INT. SUNKEN TEMPLE - DAY\n\nWater drips."

    compiler = ScreenplayCompiler(provider=fake_provider)
    screenplay_text, provenance = compiler.run("# Story Bible\n\nA sunken temple.")

    assert "INT." in screenplay_text
    assert provenance.compiler_id == "screenplay_compiler"


def test_validate_rejects_empty_bible():
    compiler = ScreenplayCompiler(provider=MagicMock())
    results = compiler.validate("")
    assert any(not r.passed for r in results)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_screenplay_compiler.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `engine/compilers/screenplay_compiler.py`**

```python
"""ScreenplayCompiler — Story Bible -> Screenplay (Fountain-ish plain text)."""
from __future__ import annotations

from engine.compilers.base import CompilerBase, ValidationResult
from engine.kernel.models import Provenance

SYSTEM_PROMPT = (
    "You are a screenwriter. Given a Story Bible, write a short screenplay opening "
    "(2-4 scenes) in standard screenplay format: scene headings in ALL CAPS "
    "(INT./EXT. LOCATION - TIME), action lines, character names centered before "
    "dialogue. Keep it under 800 words."
)


class ScreenplayCompiler(CompilerBase):
    compiler_id = "screenplay_compiler"

    def __init__(self, provider) -> None:
        self._provider = provider

    def validate(self, input_text: str) -> list[ValidationResult]:
        violations = []
        if not input_text.strip():
            violations.append("story_bible text is empty")
        return [ValidationResult(layer="structural", passed=not violations, violations=violations)]

    def generate(self, input_text: str) -> str:
        prompt = f"Story Bible:\n{input_text}\n\nWrite the screenplay now."
        return self._provider.generate(prompt, system=SYSTEM_PROMPT)

    def run(self, story_bible_text: str) -> tuple[str, Provenance]:
        results = self.validate(story_bible_text)
        if any(not r.passed for r in results):
            raise ValueError(f"Validation failed: {results}")
        output = self.generate(story_bible_text)
        output = self.repair(output, self.measure(output))
        self.review(output)
        provenance = self.export(
            knowledge_version="1.0", model=self._provider.model, output_text=output
        )
        return output, provenance
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_screenplay_compiler.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```powershell
cd E:\nth-absolute-cinema
git add engine\compilers\screenplay_compiler.py tests\test_screenplay_compiler.py
git commit -m "feat(compilers): ScreenplayCompiler — Story Bible to Screenplay"
```

---

### Task 7: Audio Compiler (Screenplay → Audio Screenplay narration)

**Files:**
- Create: `E:\nth-absolute-cinema\engine\compilers\audio_compiler.py`
- Test: `E:\nth-absolute-cinema\tests\test_audio_compiler.py`

**Interfaces:**
- Consumes: `CompilerBase` (Task 4), `TtsProvider` (Task 3).
- Produces: `AudioCompiler.run(screenplay_text: str, out_path: Path) ->
  tuple[Path, Provenance]`.

- [ ] **Step 1: Write the failing test**

`E:\nth-absolute-cinema\tests\test_audio_compiler.py`:
```python
from pathlib import Path
import sys
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine.compilers.audio_compiler import AudioCompiler


def test_run_produces_audio_file_and_provenance(tmp_path):
    fake_tts = MagicMock()
    out_path = tmp_path / "screenplay_audio.wav"
    fake_tts.synthesize.return_value = out_path

    compiler = AudioCompiler(tts_provider=fake_tts)
    result_path, provenance = compiler.run(
        "INT. TEMPLE - DAY\n\nWater drips.", out_path
    )

    assert result_path == out_path
    fake_tts.synthesize.assert_called_once()
    narration_arg = fake_tts.synthesize.call_args.args[0]
    assert "Water drips" in narration_arg
    assert "INT." not in narration_arg  # scene headings stripped from narration
    assert provenance.compiler_id == "audio_compiler"
    assert provenance.model == "pyttsx3"


def test_validate_rejects_empty_screenplay():
    compiler = AudioCompiler(tts_provider=MagicMock())
    results = compiler.validate("")
    assert any(not r.passed for r in results)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_audio_compiler.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `engine/compilers/audio_compiler.py`**

```python
"""AudioCompiler — Screenplay -> narrated Audio Screenplay (.wav).
Strips scene-heading/action-line formatting into flowing narration text before TTS."""
from __future__ import annotations

import re
from pathlib import Path

from engine.compilers.base import CompilerBase, ValidationResult
from engine.kernel.models import Provenance

SCENE_HEADING_RE = re.compile(r"^(INT\.|EXT\.).*$", re.MULTILINE)


class AudioCompiler(CompilerBase):
    compiler_id = "audio_compiler"

    def __init__(self, tts_provider) -> None:
        self._tts = tts_provider

    def validate(self, input_text: str) -> list[ValidationResult]:
        violations = []
        if not input_text.strip():
            violations.append("screenplay text is empty")
        return [ValidationResult(layer="structural", passed=not violations, violations=violations)]

    def _to_narration(self, screenplay_text: str) -> str:
        without_headings = SCENE_HEADING_RE.sub("", screenplay_text)
        lines = [ln.strip() for ln in without_headings.splitlines() if ln.strip()]
        return " ".join(lines)

    def generate(self, input_text: str) -> str:
        return self._to_narration(input_text)

    def run(self, screenplay_text: str, out_path: Path) -> tuple[Path, Provenance]:
        results = self.validate(screenplay_text)
        if any(not r.passed for r in results):
            raise ValueError(f"Validation failed: {results}")
        narration = self.generate(screenplay_text)
        result_path = self._tts.synthesize(narration, out_path)
        self.review(narration)
        provenance = self.export(
            knowledge_version="1.0", model="pyttsx3", output_text=narration
        )
        return result_path, provenance
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_audio_compiler.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```powershell
cd E:\nth-absolute-cinema
git add engine\compilers\audio_compiler.py tests\test_audio_compiler.py
git commit -m "feat(compilers): AudioCompiler — Screenplay to narrated Audio Screenplay"
```

---

### Task 8: Prompt Compiler (Screenplay → Motion Poster prompt, rules + local LLM)

**Files:**
- Create: `E:\nth-absolute-cinema\engine\compilers\prompt_compiler.py`
- Test: `E:\nth-absolute-cinema\tests\test_prompt_compiler.py`

**Interfaces:**
- Consumes: `CompilerBase` (Task 4), `OllamaProvider` (Task 3).
- Produces: `PromptCompiler.run(screenplay_text: str) -> tuple[str, Provenance]` —
  a Google-Flow-style motion poster prompt. This is the MVP stand-in for the full
  Pack ABI (`PACK_ABI.md`) — a real pack (with `CapabilityMatrix`, per-platform
  `PlatformTarget` variants) is Sprint 2+; Sprint 1 hardcodes one aspect ratio
  (16:9, motion poster default) and formats output in Google Flow's documented
  prompt structure directly, without the full pack discovery machinery.

- [ ] **Step 1: Write the failing test**

`E:\nth-absolute-cinema\tests\test_prompt_compiler.py`:
```python
from pathlib import Path
import sys
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine.compilers.prompt_compiler import PromptCompiler


def test_run_produces_motion_poster_prompt_and_provenance():
    fake_provider = MagicMock()
    fake_provider.model = "gemma2:9b"
    fake_provider.generate.return_value = (
        "A sunken stone temple glowing with bioluminescent light, cinematic, 16:9"
    )

    compiler = PromptCompiler(provider=fake_provider)
    prompt_text, provenance = compiler.run("INT. SUNKEN TEMPLE - DAY\n\nWater drips.")

    assert "16:9" in prompt_text or "aspect_ratio: 16:9" in prompt_text
    assert provenance.compiler_id == "prompt_compiler"
    assert provenance.pack_id == "google_flow_mvp"


def test_validate_rejects_empty_screenplay():
    compiler = PromptCompiler(provider=MagicMock())
    results = compiler.validate("")
    assert any(not r.passed for r in results)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_prompt_compiler.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `engine/compilers/prompt_compiler.py`**

```python
"""PromptCompiler — Screenplay -> Motion Poster prompt (Google Flow style).
MVP: single hardcoded PlatformTarget (16:9), no pack discovery — see task docstring
in the Sprint 1 plan for what's deferred to a real PACK_ABI.md pack (Sprint 2+)."""
from __future__ import annotations

from engine.compilers.base import CompilerBase, ValidationResult
from engine.kernel.models import Provenance

SYSTEM_PROMPT = (
    "You are a visual prompt engineer for AI image/video generation. Given a "
    "screenplay excerpt, write ONE vivid, cinematic image-generation prompt "
    "describing the poster's key visual moment: subject, setting, lighting, mood, "
    "camera framing. One paragraph, no scene-heading jargon. End with the aspect "
    "ratio '16:9'."
)

ASPECT_RATIO = "16:9"


class PromptCompiler(CompilerBase):
    compiler_id = "prompt_compiler"
    pack_id_mvp = "google_flow_mvp"
    pack_version_mvp = "0.1.0"

    def __init__(self, provider) -> None:
        self._provider = provider

    def validate(self, input_text: str) -> list[ValidationResult]:
        violations = []
        if not input_text.strip():
            violations.append("screenplay text is empty")
        return [ValidationResult(layer="structural", passed=not violations, violations=violations)]

    def generate(self, input_text: str) -> str:
        prompt = f"Screenplay excerpt:\n{input_text}\n\nWrite the motion poster prompt now."
        return self._provider.generate(prompt, system=SYSTEM_PROMPT)

    def run(self, screenplay_text: str) -> tuple[str, Provenance]:
        results = self.validate(screenplay_text)
        if any(not r.passed for r in results):
            raise ValueError(f"Validation failed: {results}")
        output = self.generate(screenplay_text)
        if ASPECT_RATIO not in output:
            output = f"{output}\n\naspect_ratio: {ASPECT_RATIO}"
        output = self.repair(output, self.measure(output))
        self.review(output)
        provenance = self.export(
            knowledge_version="1.0", model=self._provider.model, output_text=output
        )
        provenance.pack_id = self.pack_id_mvp
        provenance.pack_version = self.pack_version_mvp
        return output, provenance
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_prompt_compiler.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```powershell
cd E:\nth-absolute-cinema
git add engine\compilers\prompt_compiler.py tests\test_prompt_compiler.py
git commit -m "feat(compilers): PromptCompiler — Screenplay to Motion Poster prompt (MVP google_flow_mvp pack)"
```

---

### Task 9: Export — assemble the project folder

**Files:**
- Create: `E:\nth-absolute-cinema\engine\portability\__init__.py`
- Create: `E:\nth-absolute-cinema\engine\portability\export.py`
- Test: `E:\nth-absolute-cinema\tests\test_export.py`

**Interfaces:**
- Consumes: `KnowledgeRepo.get_story()` (Task 2).
- Produces: `export_project(story: dict, out_dir: Path) -> Path`. Writes the
  `MyMovie/` layout from the design doc: `story.md`, `screenplay.md` (Fountain-ish
  text; `.pdf` rendering is a Sprint 2+ nicety, not MVP-blocking),
  `screenplay_audio.wav` (copied from the audio compiler's output path),
  `motion_poster_prompt.md`, and `manifest.json` (a deliberately small
  MVP subset of `NAC_PACKAGE_SPEC.md`'s full manifest schema — full `.nac` zip
  packaging with genomes/graphs/provenance-per-artifact is Sprint 2+; Sprint 1 proves
  the pipeline produces something a person can open and use, not the full portable
  package format).

- [ ] **Step 1: Write the failing test**

`E:\nth-absolute-cinema\tests\test_export.py`:
```python
from pathlib import Path
import json
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine.portability.export import export_project


def test_export_project_writes_expected_files(tmp_path):
    audio_src = tmp_path / "source_audio.wav"
    audio_src.write_bytes(b"RIFF....")

    story = {
        "id": "abc-123",
        "idea_text": "A forgotten temple beneath the sea",
        "story_bible": "# Story Bible\n\nA sunken temple.",
        "screenplay": "INT. TEMPLE - DAY\n\nWater drips.",
        "audio_path": str(audio_src),
        "motion_poster_prompt": "Bioluminescent ruins, cinematic, 16:9",
    }

    out_dir = tmp_path / "MyMovie"
    result_dir = export_project(story, out_dir)

    assert result_dir == out_dir
    assert (out_dir / "story.md").read_text() == story["idea_text"]
    assert (out_dir / "story_bible.md").read_text() == story["story_bible"]
    assert (out_dir / "screenplay.md").read_text() == story["screenplay"]
    assert (out_dir / "screenplay_audio.wav").read_bytes() == b"RIFF...."
    assert (out_dir / "motion_poster_prompt.md").read_text() == story["motion_poster_prompt"]

    manifest = json.loads((out_dir / "manifest.json").read_text())
    assert manifest["story_id"] == "abc-123"
    assert manifest["graph_spec_version"] == "1.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_export.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `engine/portability/export.py`**

```python
"""MVP export — the design doc's MyMovie/ layout, a deliberate subset of the full
.nac package format (NAC_PACKAGE_SPEC.md). No zip, no embedded genomes/graphs — just
enough for a person to open the folder and use what NAC produced."""
from __future__ import annotations

import json
import shutil
from pathlib import Path


def export_project(story: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "story.md").write_text(story["idea_text"], encoding="utf-8")
    (out_dir / "story_bible.md").write_text(story["story_bible"] or "", encoding="utf-8")
    (out_dir / "screenplay.md").write_text(story["screenplay"] or "", encoding="utf-8")
    (out_dir / "motion_poster_prompt.md").write_text(
        story["motion_poster_prompt"] or "", encoding="utf-8"
    )

    if story.get("audio_path"):
        shutil.copyfile(story["audio_path"], out_dir / "screenplay_audio.wav")

    manifest = {
        "story_id": story["id"],
        "graph_spec_version": "1.0",
        "nac_format_version": "0.1.0-mvp",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return out_dir
```

- [ ] **Step 4: Write `engine/portability/__init__.py`** (empty)

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_export.py -v`
Expected: 1 passed

- [ ] **Step 6: Commit**

```powershell
cd E:\nth-absolute-cinema
git add engine\portability\__init__.py engine\portability\export.py tests\test_export.py
git commit -m "feat(portability): MVP project export (MyMovie/ folder layout)"
```

---

### Task 10: Public SDK (`nac` package) + `pyproject.toml`

**Files:**
- Create: `E:\nth-absolute-cinema\nac\__init__.py`
- Create: `E:\nth-absolute-cinema\pyproject.toml`
- Test: `E:\nth-absolute-cinema\tests\test_sdk.py`

**Interfaces:**
- Consumes: everything from Tasks 1-9 (`engine.*` internals).
- Produces: `nac.Studio` — the **only** class anything outside this repo (the CLI in
  Task 11, and later `agent_os/filmmaking/nac_bridge.py` in Task 13) is allowed to
  import. `Studio` methods: `create_project(idea_text) -> str (project_id)`,
  `generate_story(project_id) -> str`, `generate_screenplay(project_id) -> str`,
  `generate_audio(project_id) -> Path`, `generate_prompt(project_id) -> str`,
  `export(project_id, out_dir) -> Path`. No method takes or returns an `engine.*`
  type — only strings, `Path`, and project IDs cross the SDK boundary.

- [ ] **Step 1: Write the failing test**

`E:\nth-absolute-cinema\tests\test_sdk.py`:
```python
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nac import Studio


def test_studio_full_pipeline_calls_each_stage_once(tmp_path, monkeypatch):
    monkeypatch.setenv("NAC_ROOT_OVERRIDE", str(tmp_path))
    (tmp_path / ".nac-root").write_text("")

    fake_provider = MagicMock()
    fake_provider.model = "gemma2:9b"
    fake_provider.generate.side_effect = [
        "# Story Bible\n...",
        "INT. TEMPLE - DAY\n\nWater drips.",
        "Bioluminescent ruins, cinematic, 16:9",
    ]
    fake_tts = MagicMock()
    audio_out = tmp_path / "fake_audio.wav"
    audio_out.write_bytes(b"RIFF")
    fake_tts.synthesize.return_value = audio_out

    with patch("nac.OllamaProvider", return_value=fake_provider), \
         patch("nac.TtsProvider", return_value=fake_tts):
        studio = Studio()
        project_id = studio.create_project("A forgotten temple beneath the sea")
        bible = studio.generate_story(project_id)
        screenplay = studio.generate_screenplay(project_id)
        audio_path = studio.generate_audio(project_id)
        prompt = studio.generate_prompt(project_id)
        out_dir = studio.export(project_id, tmp_path / "MyMovie")

    assert "Story Bible" in bible
    assert "INT." in screenplay
    assert audio_path.exists()
    assert "16:9" in prompt
    assert (out_dir / "manifest.json").exists()
    assert fake_provider.generate.call_count == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_sdk.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'nac'`

- [ ] **Step 3: Write `nac/__init__.py`**

```python
"""nac — the public NAC SDK. This is the ONLY module anything outside the
E:\\nth-absolute-cinema repository may import (MODULE_BOUNDARIES.md's engine.api
boundary rule, applied here for Sprint 1's SDK-shaped surface instead of a REST API).
Consumers (the CLI, agent_os/filmmaking/nac_bridge.py) see only Studio — never
engine.knowledge, engine.compilers, engine.storage, or engine.model_manager
directly."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from engine.kernel.paths import PathResolver
from engine.storage.db import init_db
from engine.storage.knowledge_repo import KnowledgeRepo
from engine.model_manager.ollama_provider import OllamaProvider, OllamaNotReachableError
from engine.model_manager.tts_provider import TtsProvider
from engine.compilers.story_compiler import StoryCompiler
from engine.compilers.screenplay_compiler import ScreenplayCompiler
from engine.compilers.audio_compiler import AudioCompiler
from engine.compilers.prompt_compiler import PromptCompiler
from engine.portability.export import export_project

__all__ = ["Studio", "OllamaNotReachableError"]


class Studio:
    """The NAC public SDK. One Studio instance = one Ollama model + one project DB."""

    def __init__(self, model: str = "gemma2:9b") -> None:
        resolver = PathResolver()
        start = Path(os.environ.get("NAC_ROOT_OVERRIDE", str(_repo_root)))
        self._root = resolver.find_root(start)
        self._resolver = resolver
        db_path = resolver.resolve("projects/mvp.db")
        self._conn = init_db(db_path)
        self._repo = KnowledgeRepo(self._conn)
        self._provider = OllamaProvider(model=model)
        self._tts = TtsProvider()

    def create_project(self, idea_text: str) -> str:
        return self._repo.create_story(idea_text)

    def generate_story(self, project_id: str) -> str:
        story = self._repo.get_story(project_id)
        bible_text, _ = StoryCompiler(self._provider).run(story["idea_text"])
        self._repo.save_story_bible(project_id, bible_text)
        return bible_text

    def generate_screenplay(self, project_id: str) -> str:
        story = self._repo.get_story(project_id)
        screenplay_text, _ = ScreenplayCompiler(self._provider).run(story["story_bible"])
        self._repo.save_screenplay(project_id, screenplay_text)
        return screenplay_text

    def generate_audio(self, project_id: str) -> Path:
        story = self._repo.get_story(project_id)
        audio_out = self._resolver.resolve(f"projects/{project_id}_audio.wav")
        audio_path, _ = AudioCompiler(self._tts).run(story["screenplay"], audio_out)
        self._repo.save_audio_path(project_id, str(audio_path))
        return audio_path

    def generate_prompt(self, project_id: str) -> str:
        story = self._repo.get_story(project_id)
        prompt_text, _ = PromptCompiler(self._provider).run(story["screenplay"])
        self._repo.save_motion_poster_prompt(project_id, prompt_text)
        return prompt_text

    def export(self, project_id: str, out_dir: Path) -> Path:
        story = self._repo.get_story(project_id)
        return export_project(story, Path(out_dir))
```

- [ ] **Step 4: Write `pyproject.toml`**

```toml
[project]
name = "nac"
version = "0.1.0"
description = "Nth Absolute Cinema — Creative Operating System SDK"
requires-python = ">=3.12"
dependencies = ["requests>=2.31", "pyttsx3>=2.90"]

[project.scripts]
nac = "cli.__main__:main"

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["nac", "engine", "cli"]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/test_sdk.py -v`
Expected: 1 passed

- [ ] **Step 6: Install the package editable, confirm the import surface works**

```powershell
cd E:\nth-absolute-cinema
py -3 -m pip install -e .
py -3 -c "from nac import Studio; print(Studio)"
```

Expected: prints `<class 'nac.Studio'>`, no import errors.

- [ ] **Step 7: Commit**

```powershell
cd E:\nth-absolute-cinema
git add nac\__init__.py pyproject.toml tests\test_sdk.py
git commit -m "feat(sdk): public nac.Studio SDK — the only cross-boundary import surface"
```

---

### Task 11: CLI entrypoint (`cli/`), calling only `nac.Studio`

**Files:**
- Create: `E:\nth-absolute-cinema\cli\__init__.py`
- Create: `E:\nth-absolute-cinema\cli\__main__.py`

**Interfaces:**
- Consumes: `nac.Studio` (Task 10) — **never** `engine.*` directly; this is the CLI
  dogfooding the same SDK boundary `agent_os/filmmaking/nac_bridge.py` (Task 13) will
  use.
- Produces: `nac create "<idea>" --out <dir>` — runs the full pipeline via `Studio`,
  prints progress per step, writes the export folder.

- [ ] **Step 1: Write `cli/__main__.py`**

```python
"""nac CLI — the Sprint 1 MVP surface, built entirely on nac.Studio (Task 10).
`py -3 -m cli create "<idea>"` or, once pip-installed, `nac create "<idea>"`."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from nac import Studio, OllamaNotReachableError


def run_pipeline(idea_text: str, out_dir: Path, model: str = "gemma2:9b") -> Path:
    studio = Studio(model=model)

    print(f"[1/6] Creating project for idea: {idea_text!r}")
    project_id = studio.create_project(idea_text)

    print("[2/6] Generating Story Bible...")
    studio.generate_story(project_id)

    print("[3/6] Generating Screenplay...")
    studio.generate_screenplay(project_id)

    print("[4/6] Generating Audio Screenplay...")
    studio.generate_audio(project_id)

    print("[5/6] Generating Motion Poster prompt...")
    studio.generate_prompt(project_id)

    print("[6/6] Exporting project...")
    result_dir = studio.export(project_id, out_dir)

    return result_dir


def main() -> None:
    parser = argparse.ArgumentParser(prog="nac")
    sub = parser.add_subparsers(dest="command", required=True)

    create_p = sub.add_parser("create", help="Create a project from an idea")
    create_p.add_argument("idea", help="One-line creative idea")
    create_p.add_argument("--out", default="MyMovie", help="Export directory name")
    create_p.add_argument("--model", default="gemma2:9b", help="Ollama model name")

    args = parser.parse_args()

    if args.command == "create":
        try:
            out_dir = Path(args.out).resolve()
            result_dir = run_pipeline(args.idea, out_dir, model=args.model)
            print(f"\nDone. Project exported to: {result_dir}")
        except OllamaNotReachableError as e:
            print(f"\nERROR: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write `cli/__init__.py`** (empty)

- [ ] **Step 3: Manual smoke test (Ollama must be running)**

```powershell
cd E:\nth-absolute-cinema
py -3 -m cli create "A forgotten temple beneath the sea" --out projects\demo_movie --model gemma2:9b
```

Expected: 6 numbered progress lines print, no traceback, `projects\demo_movie\`
contains `story.md`, `story_bible.md`, `screenplay.md`, `screenplay_audio.wav`,
`motion_poster_prompt.md`, `manifest.json`. If Ollama isn't running or the model
isn't pulled, expect the actionable `OllamaNotReachableError` message, not a
traceback.

- [ ] **Step 4: Commit**

```powershell
cd E:\nth-absolute-cinema
git add cli\__init__.py cli\__main__.py
git commit -m "feat(cli): nac create — CLI built entirely on the nac.Studio SDK boundary"
```

---

### Task 12: Unmocked smoke-test script (proof, not CI)

**Files:**
- Create: `E:\nth-absolute-cinema\scratchpad\smoke_test_full_pipeline.py`

**Interfaces:**
- Consumes: `cli.__main__.run_pipeline` (Task 11), which itself only calls
  `nac.Studio` (Task 10). Not part of `pytest` — run manually.

- [ ] **Step 1: Write `scratchpad/smoke_test_full_pipeline.py`**

```python
"""Manual, UNMOCKED smoke test — requires a running Ollama instance with a pulled
model. Not part of pytest/CI (per the plan's Global Constraints — no Ollama in CI
for Sprint 1). Run: py -3 scratchpad\\smoke_test_full_pipeline.py"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cli.__main__ import run_pipeline

IDEA = "A forgotten temple beneath the sea, guarded by something that still remembers"
OUT_DIR = Path(__file__).resolve().parents[1] / "projects" / "smoke_test_movie"

if OUT_DIR.exists():
    shutil.rmtree(OUT_DIR)

result_dir = run_pipeline(IDEA, OUT_DIR)

expected_files = [
    "story.md", "story_bible.md", "screenplay.md",
    "screenplay_audio.wav", "motion_poster_prompt.md", "manifest.json",
]
missing = [f for f in expected_files if not (result_dir / f).exists()]
if missing:
    print(f"FAIL — missing files: {missing}")
    sys.exit(1)

for f in expected_files:
    size = (result_dir / f).stat().st_size
    print(f"  {f}: {size} bytes")
    if size == 0 and f != "manifest.json":
        print(f"FAIL — {f} is empty")
        sys.exit(1)

print(f"\nPASS — full pipeline produced a usable project at {result_dir}")
```

- [ ] **Step 2: Run it manually and record the result**

```powershell
cd E:\nth-absolute-cinema
py -3 scratchpad\smoke_test_full_pipeline.py
```

Report the actual output (PASS or FAIL with details) back — this is the real proof
the six-step MVP works, not just that unit tests pass with mocks.

- [ ] **Step 3: Commit**

```powershell
cd E:\nth-absolute-cinema
git add scratchpad\smoke_test_full_pipeline.py
git commit -m "test: add unmocked full-pipeline smoke test script"
```

---

### Task 13: Minimal Agent OS Filmmaking bridge (in `navakanth001`, SDK-only)

**Files:**
- Create: `C:\Users\navka\navakanth001\agent_os\filmmaking\__init__.py`
- Create: `C:\Users\navka\navakanth001\agent_os\filmmaking\nac_bridge.py`

**Interfaces:**
- Consumes: `nac.Studio` (Task 10) via the pip-installed `nac` package — **never**
  `engine.*`, never a relative filesystem import into `E:\nth-absolute-cinema\`. If
  `import nac` fails, that means the package wasn't installed into whatever venv
  `agent_os` uses — see Step 1's install note, not a code fix.
- Produces: the six bridge functions the user specified verbatim:
  `launch_nac_project(idea_text)`, `generate_story(project_id)`,
  `generate_screenplay(project_id)`, `generate_audio(project_id)`,
  `generate_prompt(project_id)`, `export_project(project_id, out_dir)`. This module
  contains zero filmmaking logic — it is a 1:1 rename/passthrough onto `Studio`'s
  methods, existing only so Agent OS's eventual "Filmmaking" UI has stable,
  Agent-OS-flavored function names to call instead of reaching into a third-party
  SDK's class directly everywhere.

- [ ] **Step 1: Install `nac` into the environment `agent_os` runs in**

Confirm which Python/venv `agent_os/server.py` actually runs under (per
[[agent-os-runner-fixes]] memory: `py -3`, Python312), then install NAC editable into
that same environment:

```powershell
py -3 -m pip install -e E:\nth-absolute-cinema
py -3 -c "from nac import Studio; print('nac import OK:', Studio)"
```

Expected: `nac import OK: <class 'nac.Studio'>` — if this fails, stop here and fix
the install (wrong venv, or Task 10 wasn't completed) before writing the bridge file.

- [ ] **Step 2: Write `agent_os/filmmaking/nac_bridge.py`**

```python
"""Thin bridge from Agent OS into the NAC SDK. Contains NO filmmaking logic —
every function here is a direct passthrough to nac.Studio (E:\\nth-absolute-cinema).
Agent OS must never import engine.* directly; this file is the only permitted door."""
from __future__ import annotations

from pathlib import Path

from nac import Studio

_studio: Studio | None = None


def _get_studio() -> Studio:
    global _studio
    if _studio is None:
        _studio = Studio()
    return _studio


def launch_nac_project(idea_text: str) -> str:
    return _get_studio().create_project(idea_text)


def generate_story(project_id: str) -> str:
    return _get_studio().generate_story(project_id)


def generate_screenplay(project_id: str) -> str:
    return _get_studio().generate_screenplay(project_id)


def generate_audio(project_id: str) -> Path:
    return _get_studio().generate_audio(project_id)


def generate_prompt(project_id: str) -> str:
    return _get_studio().generate_prompt(project_id)


def export_project(project_id: str, out_dir: str) -> Path:
    return _get_studio().export(project_id, Path(out_dir))
```

- [ ] **Step 3: Write `agent_os/filmmaking/__init__.py`** (empty — this package
  intentionally has no other files yet; a real UI/route layer is Sprint 2+, this task
  only proves the SDK boundary works from inside Agent OS)

- [ ] **Step 4: Manual verification (Ollama must be running)**

```powershell
cd C:\Users\navka\navakanth001
py -3 -c "from agent_os.filmmaking.nac_bridge import launch_nac_project, generate_story; pid = launch_nac_project('A forgotten temple beneath the sea'); print(generate_story(pid)[:200])"
```

Expected: prints the first 200 characters of a generated Story Bible — proof that
Agent OS can drive NAC through the bridge without touching any `engine.*` internals.

- [ ] **Step 5: Commit (in the `navakanth001` repo)**

```powershell
cd C:\Users\navka\navakanth001
git add agent_os\filmmaking\__init__.py agent_os\filmmaking\nac_bridge.py
git commit -m "feat(agent_os): add filmmaking bridge module consuming nac.Studio SDK only"
```

Note: this repo has a pyrefly pre-commit hook — `nac_bridge.py` imports `from nac
import Studio`, which requires `nac` to be installed (Step 1) for pyrefly to resolve
the import; if the hook fails on an unresolved import, that confirms Step 1 needs to
be re-run in whichever environment the hook itself runs under.

---

## Self-Review

**Spec coverage** — the six user-specified pipeline steps (Open→Create Project→Enter
Idea→Story Bible→Screenplay→Audio→Motion Poster→Export) map onto Tasks 1-12 in order;
the hybrid-architecture requirement (standalone pip-installable NAC, SDK-only
boundary, thin Agent OS bridge with zero filmmaking logic) maps onto Tasks 10 and 13;
"what NOT to build" (dashboard, collaboration, marketplace, plugins, multi-user, cloud
sync, 8K, IMAX, mobile, Experience Graph, Director Memory) has no corresponding task —
confirmed absent by design, not by oversight.

**Placeholder scan** — every task's code is complete and runnable; MVP
simplifications (Repair as no-op, Review as ai_self_review-only, Export as a folder
not a `.nac` zip, `agent_os/filmmaking/` as a bridge module with no UI yet) are
explicitly documented as intentional scope decisions in `base.py`'s docstring, Task
9's description, and Task 13's interface note, not left as silent gaps or TODOs.

**Type consistency** — `Provenance`/`Estimate` field names (Task 1) are reused
verbatim by `base.py` (Task 4) and all four compilers (Tasks 5-8); `KnowledgeRepo`'s
method names (Task 2) are reused verbatim inside `nac.Studio` (Task 10);
`OllamaProvider`/`TtsProvider` constructor signatures (Task 3) match how `Studio`
instantiates them exactly; `cli/__main__.py` (Task 11) and
`agent_os/filmmaking/nac_bridge.py` (Task 13) both call the identical `Studio` method
names (`create_project`, `generate_story`, `generate_screenplay`, `generate_audio`,
`generate_prompt`, `export`) — no drift between the two consumers of the SDK boundary.

---

**Plan complete and saved to `docs/superpowers/plans/2026-07-03-nac-sprint1-mvp-studio.md`.**

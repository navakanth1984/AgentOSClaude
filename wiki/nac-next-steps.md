# NAC Next Steps — Sprint 2 Handoff (Director Experience)

Sprint 0 (Architecture Freeze) and Sprint 1 (MVP Studio engine) are both **complete
and live-verified** as of 2026-07-03. This is a cold-start handoff for the next
agent (Antigravity) to pick up Sprint 2 — the current session is stopping here to
respect the usage limit, not because there's a blocker.

## Current State (2026-07-03)

- **Repo:** `E:\nth-absolute-cinema\` (separate git repo, not staged under
  `navakanth001`). 40+ commits, 49/49 tests green.
- **Frozen architecture:** 15 documents under `docs/specs/v1/` (Manifesto through
  `ARCHITECTURE_FINGERPRINT.md`) — see [Nth Absolute Cinema](nth-absolute-cinema.md).
  Do not modify these without a version bump per `VERSIONING_POLICY.md`.
- **Working engine:** `nac.Studio` SDK, pip-installable (`pip install -e
  E:\nth-absolute-cinema`), `SDK_VERSION = "0.1.0"` — treated as a versioned public
  interface from this point forward (additive-only changes).
- **CLI:** `nac create/build/status/regenerate/review/import-asset`, all built on
  the SDK only.
- **Provider abstraction:** `LlmOrchestrator` → Ollama → OpenRouter → MockProvider
  fallback chain (`engine/model_manager/resolver.py`). Ollama was not running this
  session; OpenRouter free tier (`google/gemma-4-26b-a4b-it:free`) is the current
  working default — confirm Ollama status before assuming which provider will be
  used.
- **Capability Registry** (`engine/packs/capability_registry.py`): honestly marks
  `google_flow`/`elevenlabs` as `available=False` — no fake integrations.
- **Real example:** `E:\nth-absolute-cinema\examples\temple_of_varuna\` — a genuine
  end-to-end generation (Story Bible, Screenplay, 21.8MB narrated audio, motion
  poster prompt), the regression baseline for comparing future compiler changes.
- **Agent OS bridge:** `agent_os/filmmaking/nac_bridge.py` (in this `navakanth001`
  repo) — thin passthrough to `nac.Studio`, zero filmmaking logic, verified live.
  Required adding `E:\nth-absolute-cinema` to `pyrefly.toml`'s search-path (pyrefly
  doesn't resolve modern setuptools `__editable__` finder installs on its own, even
  though the package imports fine at runtime).
- **Four Phase 2+ extension interfaces** exist but are **not implemented or wired**:
  `CreditEstimator`, `ProviderAdapter`, `CreativeExecutionPlanner`, `FeedbackEngine`
  in `E:\nth-absolute-cinema\engine\extensions\interfaces.py` — hooks only.
- **Deferred, not built:** Timeline Compiler, per-project Provider Manifest YAML,
  full Character/Scene/Beat Knowledge Graph population (node types exist in
  `CREATIVE_GRAPH_SPEC.md` but Sprint 1's compilers don't populate them), and a
  9-subsystem "true AI filmmaking OS" wishlist (Execution Mode Manager, Credit
  Manager, Dual-output Compilers, Provider Adapter SDK, Creative Execution Planner,
  Feedback Engine, Creative Confidence Scoring) — explicitly out of scope until a
  future session reopens them.

## Sprint 2 Directive: NAC Studio (Director Experience)

**Do not communicate this as "build a UI."** Framing it that way tends to produce a
React app before the underlying workflow is proven. Frame it as building the
**Director Experience** — the UI is one manifestation of that, not the goal itself.

### Primary Principle

The engine is finished enough. The user experience is now the product.

- Do **not** redesign the engine.
- Do **not** replace the SDK.
- Build strictly on top of the existing `nac.Studio` architecture.

### The Director Experience

Users should never think about: Knowledge Graph, Production Graph, Asset Graph,
Review Graph, Compilers, Providers, Ollama, OpenRouter, ElevenLabs, or Google Flow
prompts. Those stay internal. The user experiences a guided filmmaking workflow:

```
Idea → Story Bible → Screenplay → Audio Screenplay → Character Bible →
Location Bible → Storyboard → Motion Poster → Teaser → Trailer →
Feature Film Assets → Production Package (.nac)
```

Each stage becomes available only after the previous stage is approved.

### Review Loop

Every stage supports: View, Listen (where applicable), Approve, Regenerate, Give
Feedback, View History. Nothing automatically proceeds — the human remains the
director. (Sprint 1's `nac status/regenerate/review` already cover View/Regenerate/
approve-via-verdict at the CLI level — Sprint 2 builds a proper interface on top of
that same `Studio` surface, not a parallel mechanism.)

### Audio-First Workflow (preserve, don't build further)

```
Story → Screenplay → Audio Screenplay → Director Review → Visual Generation →
Editing → Export
```

The audio screenplay is the timing reference for later visual sync. **Do not build
the Timeline Compiler yet** — just preserve the workflow shape.

### Provider Philosophy (unchanged from Sprint 1)

- **Local** — planning, story generation, screenplay generation, prompt generation.
- **API** — fully automatable services (e.g. ElevenLabs, once integrated).
- **UI-based** — NAC generates a prompt package (Google Flow, Google Flow Music);
  the user generates externally; the asset imports back into NAC
  (`Studio.import_asset`, already built in Sprint 1's Checkpoint C.5).
- **Do not fake unavailable APIs.** The Capability Registry's `available=False`
  entries stay honest.

### Production Package

Continue producing the Production Package / `.nac` — Story Bible, Screenplay, Audio
Screenplay, Character Bible, Location Bible, Prompt Packages, Asset Metadata,
Provenance, Manifest. **Maintain backward compatibility** — this is a versioned
interface as of `SDK_VERSION 0.1.0`; new fields are additive.

### Minimal Director Dashboard

Do not build the final polished dashboard. Build the simplest useful workflow
manager — e.g.:

```
Project
  Story Bible          [done]
  Screenplay           [review]
  Audio                [waiting]
  Characters           [waiting]
  Locations            [waiting]
  Motion Poster         [waiting]
  Trailer               [waiting]
```

### Minimal User Interface

Users should be able to: create a project, open a project, continue a project,
review any stage, regenerate a stage, import generated assets, export the project.
**Everything calls only the public `Studio` SDK. No UI component may import
`engine.*` modules directly** — same boundary discipline as the CLI and the Agent OS
bridge.

### Sprint 2 Scope

**Build:** Director Dashboard, Stage Review, Feedback workflow, Audio playback,
Asset import (UI on top of `import_asset`), Project management, Production package
browser.

**Do NOT build:** Director Memory, Experience Graph, Marketplace, Cloud Sync, Beat
Graph expansion, Timeline Compiler, Credit Manager, Creative Execution Planner,
Advanced analytics. If additional architecture genuinely seems needed, expose an
extension point only (see `engine/extensions/interfaces.py`'s existing pattern) —
don't implement it.

### UX Goal

A first-time filmmaker should be able to install NAC, type a movie idea, and
complete a short film project without learning prompt engineering or AI model
configuration. The engine disappears behind the filmmaking process.

### Evaluation question for every Sprint 2 decision

> Does this make filmmaking simpler for the director? If a feature primarily
> exposes internal architecture rather than improving the creative workflow, defer
> it.

## Commands

- Run the full test suite: `cd E:\nth-absolute-cinema && py -3 -m pytest tests/ -v`
- Confirm the SDK imports from outside the repo: `py -3 -c "from nac import Studio; print(Studio)"`
- Full pipeline smoke test (needs Ollama or `OPENROUTER_API_KEY`):
  `py -3 -m cli create "<idea>" --out projects/smoke_test`
- Agent OS bridge smoke test (from `navakanth001`):
  `py -3 -c "from agent_os.filmmaking.nac_bridge import launch_nac_project, generate_story; pid = launch_nac_project('test idea'); print(generate_story(pid)[:200])"`
- Check Ollama status before assuming a provider: `curl -s http://localhost:11434/api/tags`

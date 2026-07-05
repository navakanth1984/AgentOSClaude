# Nth Absolute Cinema — Phase 1 "Micro Studio" Design

- **Date:** 2026-07-03
- **Status:** Approved design, pending Sprint 0 (Manifesto + Spec freeze)
- **Relationship to TITAN/CRP:** Nth Absolute Cinema is a **separate project**, not a
  capability inside CRP's TITAN vision (`docs/vision/TITAN.md`). TITAN's mission is a
  "quantum-inspired adaptive runtime for discovering optimal mathematical
  representations" — a filmmaking/creative platform does not fit that mission and does
  not enter through TITAN's RFC process. Nth Absolute Cinema may optionally call CRP as
  an execution substrate later, the same relationship CRP itself has to TITAN, but
  `docs/vision/TITAN.md` is not modified by this project.

---

## 1. Mission

Turn an idea into a finished short film (Phase 1: 15-20 minutes) by treating filmmaking
as a **compilation problem**, not a prompting problem:

```
Idea → Knowledge → Creative Graphs → Domain Compilers → Assets
```

The user never interacts with models or prompts directly. They interact with their
movie. Every artifact (screenplay, audio, storyboard, prompt, video) is *compiled* from
a canonical graph state — never hand-authored in isolation.

This is Phase 1 of a longer trajectory: once the compiler framework, graph model, and
provenance system are proven on film, the same foundation is expected to support
novels, comics, games, documentaries, podcasts, and courses with the same architecture
(Creative Compiler Infrastructure) — see Manifesto principle 1. Phase 1 scope is
deliberately constrained to film only; other domains are not built now.

## 2. Governing documents (frozen in Sprint 0, before any compiler code)

### 2.1 Creative Compiler Manifesto v1.0

Philosophy that every compiler and every future domain (novel, comic, game...) must
obey. Stable across implementation churn.

1. The Creative Knowledge Graph is the single source of truth.
2. Every artifact is compiled, never authored in isolation.
3. Humans direct; AI proposes.
4. Outputs must be reproducible through provenance.
5. Offline-first by default; cloud only when it adds measurable value.
6. Quality and consistency outweigh generation speed.
7. Economic efficiency is a first-class optimization objective.
8. Every creative decision is traceable back to the project state that produced it.

### 2.2 Creative Graph Specification v1.0

Technical schema, frozen before Sprint 1 begins so no compiler is built against a
moving foundation. Must define, at minimum:
- Node/edge types for all five graphs (below)
- Story hierarchy: Story → Acts → Sequences → Scenes → Beats → Shots (non-linear;
  supports Director's Cut / trailer / alternate-ending views without data duplication)
- Style Genome schema (below)
- Four-layer validation contract (below)
- Compiler contract (Input Schema → Validation → Planning → Generation → Measurement →
  Repair → Review → Export)
- Provenance schema (below)
- Aspect-ratio / platform-target schema for shots
- Versioning rules for graph snapshots

## 3. The five graphs

Splitting one graph avoids a monolith as projects scale toward feature-length.

```
Project
├── Knowledge Graph    — story facts, characters, mythology, locations, timeline
├── Cinematic Graph    — shots, camera, cuts, music cues (never lives in Knowledge)
├── Asset Graph         — images, audio, video, prompts (hashed, cached, reused)
├── Production Graph    — jobs, queues, cost/time estimates, dependencies
└── Review Graph          — approvals, comments, versions, human edits
```

Knowledge Graph never contains camera/edit decisions — that is Cinematic Graph's
domain. Each Beat in the story hierarchy carries an **Emotional Graph** node: audience
emotion, character emotion, intensity, pacing, conflict, mystery, release — enabling
detection of issues like "Act II has no tension" or "music enters too late."

## 4. Style Genome (formerly "DNA")

First-class, versioned entities referenced (not copied) by compilers for consistency:

`CharacterGenome, VisualGenome, DialogueGenome, MusicGenome, EditingGenome,
CameraGenome, LightingGenome, CostumeGenome, EnvironmentGenome`

## 5. Validation (four layers, run before any compiler sees a snapshot)

- **Structural** — missing character, broken timeline, missing location
- **Creative** — inconsistent motivation, dialogue not matching personality, scene
  lacking conflict
- **Technical** — prompt exceeds pack token/duration limits, invalid seed
- **Platform** — aspect ratio invalid for target platform, duration exceeds platform
  limit, missing required asset (e.g. thumbnail)

Fail-fast: validation runs before generation is triggered, not after.

## 6. Aspect-ratio-native generation (hard requirement, not a post-process)

Platform target (Reels/Shorts 9:16, YouTube 16:9, LinkedIn 1:1 or 4:5, etc.) is an
input to the Cinematic Graph's Shot nodes, not a post-processing step. Each `Shot`
carries `target_platforms: [{platform, aspect_ratio}]`. The Prompt Compiler generates
**one native prompt per aspect ratio per shot** — framing and composition recomputed
per ratio, not just canvas dimensions changed. **Cropping a single master render to fit
multiple platforms is an explicit anti-pattern and is disallowed.**

## 7. Compiler Packs + Capability Registry

Tool-specific integrations (Google Flow, Higgsfield, OpenArt, Flux, ComfyUI, ...) are
packs, not hardcoded branches:

```
packs/<tool>/  {parser, prompt_compiler, validator, capability_matrix, limits, templates}
```

`Prompt Compiler → Capability Registry → target Pack`. Adding a new tool means adding a
pack; no core changes.

## 8. Creative Compiler Framework

Every compiler (Screenplay, Novel, Audio, Prompt, Storyboard, Motion Poster, Teaser,
Trailer) implements one base contract, mirroring CRP's own compiler discipline:

```
Input Schema → Validation → Planning → Generation → Measurement → Repair → Review → Export
```

`ScreenplayCompiler(Compiler)`, `AudioCompiler(Compiler)`, etc. This consistency is the
project's durability: new domains (novel, comic, game) are new Compiler subclasses on
the same framework, not new architectures.

## 9. Provenance + Creative Replay

Every generated artifact stores:

```
{knowledge_version, compiler_version, pack_version, model, seed, output_hash}
```

**Creative Replay**: re-run generation for a single axis (e.g. only music, only camera,
only dialogue) against a frozen graph snapshot while holding everything else constant —
critical for iteration without full re-generation.

## 10. Film Constitution

Per-project constraints document, validated against on every compile:

`max_runtime, target_audience, genre, age_rating, narrative_rules, visual_rules,
language_rules, distribution_targets, budget_targets, legal_constraints`

## 11. Creative Economics + Production Planner

Every compiler reports an estimate before generation runs:

```
{estimated_tokens, estimated_gpu_hours, estimated_ram, estimated_time,
 estimated_cost_usd, confidence}
```

The **Production Planner** aggregates these across the whole Knowledge Graph before any
generation is triggered, surfacing e.g. "$37, 18 GPU-hours, 420 images, 95 videos"
up front, so creators know cost before committing.

## 12. Model Manager

Promoted from a routing utility to its own subsystem:

```
Model Manager → Capability Registry → Scheduler → GPU Manager → Router
```

Owns Tier 0-4 routing decisions (Python deterministic → local LLM → local image →
local audio → cloud), local model lifecycle, and GPU scheduling.

## 13. Storage

Storage is split into three tiers (see §20.3) rather than one undifferentiated
filesystem tree:

- **SQLite** — authoritative store for all five graphs, version history, task/job
  state, provenance, asset metadata. Primary query/inspection layer. Lives in the
  **project tier**.
- **Filesystem** — all generated artifacts (screenplays, prompts, audio, images, video,
  music, exports), organized per project, content-addressed by hash for reuse/cache.
  Split across **cache**, **project**, and **archive** tiers per §20.3.
- **DuckDB** — optional analytics layer, introduced in a later phase, not Phase 1.
- **Local vector DB** — optional semantic retrieval feature, not a dependency.

All paths are resolved relative to a runtime-detected project root (§20.1) — no
component hardcodes an absolute path.

## 14. Tech stack

- **Engine (core, compilers, graphs, storage, routing):** Python — reuses existing
  `crp-runtime` patterns and `agent_os/` local-model glue (Kokoro, transformers).
- **Dashboard (Sprint 6, Director Dashboard):** Node/React.
- **Location:** `E:\nth-absolute-cinema\` — an external SSD, chosen from the start so
  the project is portable and hardware-adaptive by construction (§20). Not staged
  under `C:\Users\navka\navakanth001\`: this project's storage tiers (cache/renders/
  assets/temp/archive) are large and drive-portability is a first-class requirement,
  which the usual staging-workshop pattern (`[[staging-to-repo-workflow]]`) doesn't
  need to handle. Git remains the source of truth for `engine/`, `dashboard/`,
  `templates/`, `docs/`, `examples/`, `tests/`; `local_models/`, `projects/`, `cache/`,
  `renders/`, `assets/`, `temp/`, `archive/` are gitignored, populated at runtime.

## 15. Folder structure

```
E:\nth-absolute-cinema\
  engine\
    kernel\          # Compiler base class, contracts, event bus
    knowledge\        # Knowledge Graph, Style Genome, four-layer Validators
    cinematic\          # Cinematic Graph: shots, camera, cuts, music cues
    assets\               # Asset Graph, hashing, cache
    production\             # Production Graph, Production Planner, job queue
    review\                   # Review Graph, multi-stage approval workflow
    compilers\                 # ScreenplayCompiler, AudioCompiler, PromptCompiler, ...
    packs\                       # google_flow/, higgsfield/, openart/, ...
    model_manager\                 # Model Manager, Scheduler, GPU Manager, Router
    compute_manager\                 # Hardware profiling + execution profile selection
    storage\                         # SQLite (5 graphs) + filesystem (assets)
    portability\                       # .nac package export/import (§20.4)
    api\                                # FastAPI boundary (only door to the dashboard/CLI)
    plugins\                              # extension points
  dashboard\           # Node/React Director Dashboard (Sprint 6)
  local_models\        # installed model weights/configs (on-demand, §20.2 — gitignored)
  projects\              # per-project SQLite DB + project-tier asset tree (gitignored)
  templates\            # pack templates, project templates
  docs\
  examples\
  cache\                  # cache tier: derived/regeneratable data (§20.3 — gitignored)
  renders\                  # rendered video/image outputs pending review (gitignored)
  assets\                     # shared/reusable asset library across projects (gitignored)
  temp\                         # scratch space, safe to delete anytime (gitignored)
  archive\                        # archive tier: cold storage, exported .nac packages
  tests\
```

## 16. Review workflow (multi-stage, not a single gate)

```
Compile → AI Self-Review → Human Review → Graph Update → Recompile
```

Every compiler supports this loop, not just a final approval screen.

## 17. Portability (relocatable project root)

The project root is never hardcoded. At startup, the engine resolves its root by
walking up from the running module's location to find a marker file
(`.nac-root`) rather than reading a fixed path — the same mechanism whether the
project lives at `E:\nth-absolute-cinema\`, `D:\...`, or a different drive letter
entirely on another machine. All internal path construction (storage, packs,
local_models, cache/renders/assets/temp/archive) goes through a single
`engine.kernel.paths` resolver that returns paths relative to that detected root; no
other module is allowed to build an absolute path itself. This makes "copy the
`E:\nth-absolute-cinema\` directory (or move the SSD) to another computer and keep
working" a property of the architecture, not a migration step.

This is additive to the existing design: it constrains how `engine.storage` and
`engine.model_manager` are implemented, it does not change the graph schema, compiler
contract, or any Sprint 0-6 deliverable.

## 18. Compute Manager (hardware-adaptive execution profiles)

New subsystem, `engine.compute_manager`, sitting alongside Model Manager. At startup
(and on demand) it profiles the host machine — CPU, RAM, GPU, VRAM, storage speed/free
space, and which local models are already installed — and selects one of four
execution profiles. Nothing else in the architecture assumes a fixed hardware tier;
every compiler asks Model Manager for a model, and Model Manager asks Compute Manager
which tier it's allowed to use.

| Profile  | Maps to (your terms) | Local scope |
|----------|----------------------|-------------|
| Micro    | Profile A — Laptop   | Lightweight local LLMs, local TTS, prompt compilation, story generation, audio screenplay. Cloud video generation only when needed. |
| Standard | Profile B — Gaming PC | Everything local except premium video. |
| Pro      | Profile C — Studio Workstation | Almost everything local. |
| Studio   | Profile D — Cloud    | Heavy rendering, distributed generation, team collaboration. |

The same project — same Knowledge Graph, same compilers, same `.nac` package — runs
unmodified on all four; only which Tier 0-4 route Model Manager picks changes. Profile
selection is re-evaluated whenever Compute Manager detects the hardware changed (e.g.
project moved to a different machine) — see §17 and §20.

This is additive: it does not change the Tier 0-4 routing concept already in the
design (§9 Model Manager), it adds the automatic profiling step that decides which
tiers are actually available on the current machine.

## 19. On-demand model installation

Model Manager (§9/§12) is extended, not replaced: instead of requiring all local
models up front, it installs models lazily, one at a time, the first time a compiler
actually needs them:

```
Compiler requests capability (e.g. narration)
  → Model Manager checks Capability Registry: is a model installed for this?
    → No → Compute Manager profile permits it? → download that one model package
    → Yes → use it
```

Each local model (Kokoro, Whisper, Gemma, etc.) is its own installable package under
`local_models/`, with its own manifest (size, VRAM requirement, capability tags). There
is no "download everything" step; a fresh `Micro`-profile install may end up with only
a couple of small models present, and that is expected and correct.

## 20. Storage tiers

Storage under the project root is split into three tiers, each with different
portability and lifecycle guarantees:

- **Cache tier** (`cache/`) — fully derived/regeneratable data: model inference caches,
  resized/thumbnailed intermediates, compiled prompt caches. Safe to delete entirely;
  never included in a `.nac` export; rebuilt on demand from the project tier.
- **Project tier** (`projects/<project>/`) — authoritative, non-regeneratable data: the
  five graphs (SQLite), Style Genomes, provenance, review history, source assets. This
  is what a `.nac` package is built from.
- **Archive tier** (`archive/`) — cold storage: exported `.nac` packages, completed
  project snapshots, old versions kept for provenance/replay but not actively worked
  on.

`renders/`, `assets/`, and `temp/` (§15 folder structure) are cache-tier siblings used
by specific subsystems (Cinematic/Asset Graph renders, shared asset library, scratch
space respectively) — same "safe to delete, not exported" guarantee as `cache/`.

## 21. Portable Project Package (`.nac`)

`engine.portability` (new module) can export any project to a single `.nac` file and
import it back on a different machine.

**Exported (project-tier data only — reproducible/authoritative):**
- Creative Graph Specification version + all five graphs (Knowledge, Cinematic, Asset
  metadata, Production, Review) as of export time
- Style Genomes
- Provenance records (`knowledge_version, compiler_version, pack_version, model, seed,
  output_hash` per artifact, §9)
- Prompts (compiled Prompt IR, not just raw text)
- Review history
- Manifest: Creative Graph Spec version, Manifesto version, compiler versions, pack
  versions used, list of referenced local models (by name+version, not weights)
- References to assets (content hashes + relative paths), not necessarily the full
  binary asset payload for large renders — see below

**Not exported (cache-tier, regeneratable on the destination machine):**
- Local model weights
- Derived caches, thumbnails, inference caches
- Anything under `cache/`, `renders/` (unless the referenced render is also the
  authoritative source asset — see next point), `temp/`

**Asset handling:** small/source assets (reference images, approved takes) are
embedded in the package by content hash; large generated renders are referenced by
hash with an optional embed toggle at export time, so a `.nac` can be either a full
self-contained archive or a lightweight "resume-me" package that regenerates renders
from provenance on import.

**Import flow on the destination machine:**
```
Import .nac → verify manifest/graph-spec version compatible
  → restore five graphs + genomes + provenance + review history into projects/
  → Compute Manager profiles destination hardware → selects execution profile
  → Model Manager diffs manifest's referenced models against what's installed
    → installs only what's missing, per §19
  → missing cache-tier data (thumbnails, renders not embedded) regenerated on demand
    from provenance, not re-generated from scratch via new AI calls unless the
    original asset truly wasn't embedded and can't be re-derived deterministically
```

This preserves Manifesto principle 4 (reproducibility through provenance): a `.nac`
import reconstructs project state exactly, even when the destination's installed
models or cache are empty.

This is additive: `.nac` is a new export/import format layered on top of the existing
Storage design (§13) and Provenance schema (§9); it introduces no change to any graph
node/edge type or compiler contract.

## 22. Compatibility statement

Everything in §17-21 is additive to the design approved in §1-16: no graph schema,
compiler contract, pack format, or review workflow changes. The only structural change
to prior sections is the project root moving from `C:\Users\navka\navakanth001\
nth-absolute-cinema\` to `E:\nth-absolute-cinema\` (§14-15) and the addition of three
new engine subsystems (`compute_manager/`, `portability/`) plus the three storage-tier
directories (`cache/`, `renders/`, `assets/`, `temp/`, `archive/`) — none of which
existing sections' compilers, graphs, or contracts need to know about directly; they
only ever go through `engine.kernel.paths` and `engine.model_manager`.

## 23. Sprint plan

```
Sprint 0 — Manifesto v1.0 + Creative Graph Specification v1.0 (frozen), including
           path-resolver contract (§17), execution-profile schema (§18), and .nac
           manifest schema (§21)
Sprint 1 — Kernel (incl. engine.kernel.paths, §17), Knowledge Graph, Storage (3 tiers,
           §20), Model Manager with on-demand install (§19), Compute Manager (§18)
Sprint 2 — Story Compiler (Screenplay/Story Bible/Novel), 4-layer Validators, Review Graph
Sprint 3 — Prompt Compiler, Capability Packs, Asset Graph, Cinematic Graph,
           aspect-ratio-native shots (Google Flow pack first)
Sprint 4 — Audio Compiler, Narration, Dialogue (local TTS routing)
Sprint 5 — Generation: Storyboard, Motion Poster, Teaser, Trailer compilers,
           Production Planner wired to real estimates
Sprint 6 — Director Dashboard, .nac export/import (§21), full-pipeline cost-optimizer
           tuning, cross-profile verification (run one project on Micro and Standard
           profiles, confirm identical graph output)
```

Rationale for this order over a naive Core→Story→Audio→Prompt sequence: everything
visual depends on the Prompt Compiler and Cinematic Graph, so those move up; audio can
progress independently once story structure (Sprint 2) is stable, so it moves after
Prompt.

Each sprint = its own branch → implementation + real verification → commit (pyrefly
clean) → push → PR into `master` → CI/review → merge → delete branch, per this repo's
standard ADLC (`wiki/development-lifecycle.md`, `AGENTS.md`). No sprint merges over
uncommitted work from a prior sprint.

## 24. Explicit non-goals for Phase 1

- Director Memory (reusable cross-project style profiles) — real value, deferred to
  Phase 2. Sprint 0 spec should leave a schema hook for it but it is not implemented.
- Feature-length film support — Phase 1 targets 15-20 minutes only; architecture must
  not preclude scaling later (hence Acts/Sequences/Scenes/Beats/Shots hierarchy now),
  but scaling itself is out of scope.
- Non-film domains (novel, comic, game, podcast, course compilers) — the framework must
  not preclude them, but none are built in Phase 1.
- DuckDB analytics layer, local vector DB — optional, later phase.
- Cloud-only generation paths without a local fallback — violates Manifesto principle 5.
- Automated cross-machine sync/merge of two live `.nac`-derived projects (conflict
  resolution) — Phase 1 supports export/import as a snapshot handoff, not concurrent
  multi-machine editing.
- Team collaboration features under the Studio (Cloud) profile — Compute Manager can
  *select* that profile, but multi-user collaboration workflows are Phase 2.

## 25. Success criteria for Phase 1

- A single idea, entered once, produces: Story Bible, Screenplay (20-30 pages),
  Audio Screenplay, Storyboard, Motion Poster, Teaser, and at least one aspect-ratio
  variant set (9:16 + 16:9) of prompt packages for the same shots, all traceable via
  provenance back to one Knowledge Graph version.
- Re-running Creative Replay on a single axis (e.g. music only) for one scene does not
  regenerate unrelated artifacts.
- Production Planner estimate is produced before generation starts for at least one
  full sprint-5 pipeline run, and actual cost/time is logged against the estimate for
  comparison (measurement over assumption, per Manifesto principle 4/7).
- No component contains a hardcoded absolute path; the engine runs correctly when
  `E:\nth-absolute-cinema\` is copied to a different drive letter on the same machine
  (minimum portability smoke test for §17).
- A project exported to `.nac` on one profile (e.g. Micro) imports successfully on a
  machine with none of the referenced local models installed, and Model Manager
  installs only the models actually needed to resume work — not a full bundle (§19,
  §21).

## 26. Sprint 0 status and naming update (2026-07-03)

**Naming:** the engine/SDK codename is **NAC**. Product naming going forward:
- **NAC** — the core engine and SDK (this document's `engine/` tree).
- **Nth Absolute Cinema Studio** — the desktop application (Sprint 6, Director
  Dashboard evolves into this).
- **`.nac`** — the portable project/package format (§21).
- **NAC Packs** — tool integrations (§7), e.g. the Google Flow pack.

**Sprint 0 complete:** all 14 governing documents (Manifesto, Creative Graph Spec,
Compiler ABI, Pack ABI, `.nac` Package Spec, Event Spec, Plugin ABI, Workspace Spec,
Compute Manager Spec, Module Boundaries, Repository Interfaces, Extensibility,
Versioning Policy, and the Sprint 0.5 Architecture Validation gate) are frozen under
`E:\nth-absolute-cinema\docs\specs\v1\` — see
`docs/superpowers/plans/2026-07-03-nac-sprint0-architecture-freeze.md` in this repo
for the plan that produced them, and `SPRINT0_FREEZE.md` at the NAC repo root for the
freeze declaration itself. Sprint 0.5 validation (`SPRINT0.5-VALIDATION.md`) passed
all 8 architecture-guarantee questions (replay, traceability, tool extensibility,
machine portability, offline operation, generation reproducibility, independent
compiler replacement, independent graph evolution) before this freeze was declared.
This document (`2026-07-03-nth-absolute-cinema-design.md`) remains the origin design
rationale; the `docs/specs/v1/` documents are now the authoritative technical specs
Sprint 1+ build against.

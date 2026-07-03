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

- **SQLite** — authoritative store for all five graphs, version history, task/job
  state, provenance, asset metadata. Primary query/inspection layer.
- **Filesystem** — all generated artifacts (screenplays, prompts, audio, images, video,
  music, exports), organized per project, content-addressed by hash for reuse/cache.
- **DuckDB** — optional analytics layer, introduced in a later phase, not Phase 1.
- **Local vector DB** — optional semantic retrieval feature, not a dependency.

## 14. Tech stack

- **Engine (core, compilers, graphs, storage, routing):** Python — reuses existing
  `crp-runtime` patterns and `agent_os/` local-model glue (Kokoro, transformers).
- **Dashboard (Sprint 6, Director Dashboard):** Node/React.
- **Location:** new top-level folder `nth-absolute-cinema/` under
  `C:\Users\navka\navakanth001\` (staging workshop pattern — graduates to its own repo
  later, same as `nth-brain`).

## 15. Folder structure

```
nth-absolute-cinema/
  engine/
    kernel/          # Compiler base class, contracts, event bus
    knowledge/        # Knowledge Graph, Style Genome, four-layer Validators
    cinematic/          # Cinematic Graph: shots, camera, cuts, music cues
    assets/               # Asset Graph, hashing, cache
    production/             # Production Graph, Production Planner, job queue
    review/                   # Review Graph, multi-stage approval workflow
    compilers/                 # ScreenplayCompiler, AudioCompiler, PromptCompiler, ...
    packs/                       # google_flow/, higgsfield/, openart/, ...
    model_manager/                 # Model Manager, Scheduler, GPU Manager, Router
    storage/                         # SQLite (5 graphs) + filesystem (assets)
    api/                                # FastAPI boundary (only door to the dashboard/CLI)
    plugins/                              # extension points
  dashboard/           # Node/React Director Dashboard (Sprint 6)
  local_models/        # model weights/configs
  templates/            # pack templates, project templates
  projects/              # per-project SQLite DB + asset tree (gitignored)
  examples/
  docs/
  tests/
```

## 16. Review workflow (multi-stage, not a single gate)

```
Compile → AI Self-Review → Human Review → Graph Update → Recompile
```

Every compiler supports this loop, not just a final approval screen.

## 17. Sprint plan

```
Sprint 0 — Manifesto v1.0 + Creative Graph Specification v1.0 (frozen)
Sprint 1 — Kernel, Knowledge Graph, Storage, Model Manager (Tier 0/1)
Sprint 2 — Story Compiler (Screenplay/Story Bible/Novel), 4-layer Validators, Review Graph
Sprint 3 — Prompt Compiler, Capability Packs, Asset Graph, Cinematic Graph,
           aspect-ratio-native shots (Google Flow pack first)
Sprint 4 — Audio Compiler, Narration, Dialogue (local TTS routing)
Sprint 5 — Generation: Storyboard, Motion Poster, Teaser, Trailer compilers,
           Production Planner wired to real estimates
Sprint 6 — Director Dashboard, export, full-pipeline cost-optimizer tuning
```

Rationale for this order over a naive Core→Story→Audio→Prompt sequence: everything
visual depends on the Prompt Compiler and Cinematic Graph, so those move up; audio can
progress independently once story structure (Sprint 2) is stable, so it moves after
Prompt.

Each sprint = its own branch → implementation + real verification → commit (pyrefly
clean) → push → PR into `master` → CI/review → merge → delete branch, per this repo's
standard ADLC (`wiki/development-lifecycle.md`, `AGENTS.md`). No sprint merges over
uncommitted work from a prior sprint.

## 18. Explicit non-goals for Phase 1

- Director Memory (reusable cross-project style profiles) — real value, deferred to
  Phase 2. Sprint 0 spec should leave a schema hook for it but it is not implemented.
- Feature-length film support — Phase 1 targets 15-20 minutes only; architecture must
  not preclude scaling later (hence Acts/Sequences/Scenes/Beats/Shots hierarchy now),
  but scaling itself is out of scope.
- Non-film domains (novel, comic, game, podcast, course compilers) — the framework must
  not preclude them, but none are built in Phase 1.
- DuckDB analytics layer, local vector DB — optional, later phase.
- Cloud-only generation paths without a local fallback — violates Manifesto principle 5.

## 19. Success criteria for Phase 1

- A single idea, entered once, produces: Story Bible, Screenplay (20-30 pages),
  Audio Screenplay, Storyboard, Motion Poster, Teaser, and at least one aspect-ratio
  variant set (9:16 + 16:9) of prompt packages for the same shots, all traceable via
  provenance back to one Knowledge Graph version.
- Re-running Creative Replay on a single axis (e.g. music only) for one scene does not
  regenerate unrelated artifacts.
- Production Planner estimate is produced before generation starts for at least one
  full sprint-5 pipeline run, and actual cost/time is logged against the estimate for
  comparison (measurement over assumption, per Manifesto principle 4/7).

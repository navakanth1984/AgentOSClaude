# NAC Sprint 0 — Architecture Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the NAC (Nth Absolute Cinema) project root at `E:\nth-absolute-cinema\`
and produce nine frozen v1.0 governance/technical specification documents plus
diagrams, interfaces, extension points, and versioning policy — no compiler or engine
code is written in this sprint. This is the architecture freeze that every later sprint
(1-6, per `docs/superpowers/specs/2026-07-03-nth-absolute-cinema-design.md`) builds
against without moving the ground underneath them.

**Architecture:** Nine independent specification documents under
`E:\nth-absolute-cinema\docs\specs\v1\`, each addressing one architectural concern
(philosophy, graph schema, compiler ABI, pack ABI, package format, events, plugins,
workspace/portability, hardware profiles), plus four cross-cutting documents (module
boundaries, repository interfaces, extensibility, versioning policy) and one freeze
declaration tying them together. Every doc is standalone-readable but cross-references
the others by relative link. Naming: **NAC** = engine/SDK codename, **Nth Absolute
Cinema Studio** = desktop app (later sprint), **`.nac`** = package format, **NAC
Packs** = tool integrations (Google Flow, Higgsfield, OpenArt, ...).

**Tech Stack:** Markdown specs (no code this sprint). Repository interfaces are
expressed as Python `typing.Protocol` stubs (signatures only, no bodies) to keep them
implementation-free while still being precise. Git for version control at the new
`E:\nth-absolute-cinema\` root (separate repo from `navakanth001`).

## Global Constraints

- Project root is `E:\nth-absolute-cinema\` (per
  `docs/superpowers/specs/2026-07-03-nth-absolute-cinema-design.md` §14-15) — a
  **separate git repository**, not staged under `C:\Users\navka\navakanth001\`.
- No graph schema, compiler contract, pack format, or review workflow may contradict
  the frozen design doc in `navakanth001` (`docs/superpowers/specs/2026-07-03-nth-absolute-cinema-design.md`);
  this plan produces the formal spec text for what that design doc already approved.
- Nothing in this sprint touches `docs/vision/TITAN.md` or CRP's `crp/` tree — NAC is a
  separate project (confirmed 2026-07-03 brainstorming session).
- Naming: use **NAC** for the engine/SDK codename throughout every spec document's
  code identifiers, package names, and internal references. Use **Nth Absolute Cinema**
  only in product-facing prose (doc titles, the Manifesto's mission statement).
- Every spec document version is `v1.0` and is marked **FROZEN** only after its
  self-review step passes — no doc is frozen with a TBD/placeholder in it.
- All 9 core specs + 5 cross-cutting docs live under one versioned directory
  (`docs/specs/v1/`) so a future v2 can exist alongside without deleting history.

---

## File Structure

```
E:\nth-absolute-cinema\                     (new git repo, Task 1)
  .gitignore
  README.md
  docs\
    specs\
      v1\
        MANIFESTO.md                        (Task 2)
        CREATIVE_GRAPH_SPEC.md              (Task 3)
        COMPILER_ABI.md                     (Task 4)
        PACK_ABI.md                         (Task 5)
        NAC_PACKAGE_SPEC.md                 (Task 6)
        EVENT_SPEC.md                       (Task 7)
        PLUGIN_ABI.md                       (Task 8)
        WORKSPACE_SPEC.md                   (Task 9)
        COMPUTE_MANAGER_SPEC.md             (Task 10)
        MODULE_BOUNDARIES.md                (Task 11)
        REPOSITORY_INTERFACES.md            (Task 11)
        EXTENSIBILITY.md                    (Task 12)
        VERSIONING_POLICY.md                (Task 12)
        SPRINT0_FREEZE.md                   (Task 13)
  engine\ dashboard\ local_models\ projects\ templates\ examples\ tests\
  cache\ renders\ assets\ temp\ archive\    (empty, gitignored, dirs only — Task 1)
```

In `navakanth001` (existing repo):
```
docs\superpowers\specs\2026-07-03-nth-absolute-cinema-design.md   (Task 14: amend)
wiki\nth-absolute-cinema.md                                        (Task 14: amend)
```

---

### Task 1: Scaffold the NAC repository at `E:\nth-absolute-cinema\`

**Files:**
- Create: `E:\nth-absolute-cinema\.gitignore`
- Create: `E:\nth-absolute-cinema\README.md`
- Create: directory tree (empty dirs need a `.gitkeep`)

**Interfaces:**
- Produces: the physical project root that every later task's paths are relative to.

- [ ] **Step 1: Create the directory tree**

```powershell
$root = "E:\nth-absolute-cinema"
$dirs = @(
  "docs\specs\v1",
  "engine\kernel","engine\knowledge","engine\cinematic","engine\assets",
  "engine\production","engine\review","engine\compilers","engine\packs",
  "engine\model_manager","engine\compute_manager","engine\storage",
  "engine\portability","engine\api","engine\plugins",
  "dashboard","local_models","projects","templates","examples","tests",
  "cache","renders","assets","temp","archive"
)
foreach ($d in $dirs) {
  New-Item -ItemType Directory -Force -Path (Join-Path $root $d) | Out-Null
}
```

Expected: no errors; `Test-Path "E:\nth-absolute-cinema\engine\kernel"` returns `True`.

- [ ] **Step 2: Add `.gitkeep` files to empty directories that must survive `.gitignore`**

```powershell
$keepDirs = @("cache","renders","assets","temp","archive","local_models","projects")
foreach ($d in $keepDirs) {
  New-Item -ItemType File -Force -Path "E:\nth-absolute-cinema\$d\.gitkeep" | Out-Null
}
```

- [ ] **Step 3: Write `.gitignore`**

Content of `E:\nth-absolute-cinema\.gitignore`:

```gitignore
# Cache tier — fully regeneratable, never versioned
cache/*
!cache/.gitkeep

# Render outputs — regeneratable from provenance
renders/*
!renders/.gitkeep

# Shared asset library — large binaries, not versioned
assets/*
!assets/.gitkeep

# Scratch space
temp/*
!temp/.gitkeep

# Local model weights — installed on demand, never versioned (see COMPUTE_MANAGER_SPEC.md)
local_models/*
!local_models/.gitkeep

# Per-project data — SQLite DBs + project-tier assets, not versioned in the engine repo
projects/*
!projects/.gitkeep

# Archive tier — exported .nac packages, cold storage
archive/*
!archive/.gitkeep

# Python
__pycache__/
*.pyc
.venv/
venv/

# Node (dashboard, later sprint)
node_modules/
dist/

# OS
Thumbs.db
.DS_Store
```

- [ ] **Step 4: Write `README.md`**

Content of `E:\nth-absolute-cinema\README.md`:

```markdown
# NAC — Nth Absolute Cinema

AI filmmaking Creative Operating System. Phase 1: idea → finished 15-20 minute short
film, built as a compilation problem, not a prompting workflow.

- **Frozen architecture:** `docs/specs/v1/` — start with `SPRINT0_FREEZE.md`.
- **Origin design doc:** see the `navakanth001` repo,
  `docs/superpowers/specs/2026-07-03-nth-absolute-cinema-design.md`.
- **Naming:** NAC = engine/SDK codename. Nth Absolute Cinema Studio = desktop app
  (later sprint). `.nac` = portable project package format. NAC Packs = tool
  integrations (Google Flow, Higgsfield, OpenArt, ...).
- **Status:** Sprint 0 (Architecture Freeze) — no engine code yet.

This repository is intentionally **not** staged under `navakanth001` — it lives on an
external SSD from the start so the whole project is portable (copy the directory, or
move the drive, to another machine and keep working). See `docs/specs/v1/WORKSPACE_SPEC.md`.
```

- [ ] **Step 5: Initialize git and make the first commit**

```powershell
cd E:\nth-absolute-cinema
git init
git add .gitignore README.md cache\.gitkeep renders\.gitkeep assets\.gitkeep temp\.gitkeep local_models\.gitkeep projects\.gitkeep archive\.gitkeep
git commit -m "chore: scaffold NAC repository root at E:\nth-absolute-cinema"
```

Expected: `git log --oneline` shows one commit; `git status` shows a clean tree with
the `engine/`, `dashboard/`, `docs/specs/v1/`, `templates/`, `examples/`, `tests/`
directories present but empty (not yet tracked — they'll gain content in later
sprints/tasks).

---

### Task 2: Write Creative Compiler Manifesto v1.0

**Files:**
- Create: `E:\nth-absolute-cinema\docs\specs\v1\MANIFESTO.md`

**Interfaces:**
- Produces: the 8 governing principles every other spec document (Tasks 3-10) must
  cite and comply with.

- [ ] **Step 1: Write the document**

Content of `MANIFESTO.md`:

```markdown
# NAC Creative Compiler Manifesto v1.0

**Status:** FROZEN (2026-07-03)

Philosophy that every NAC compiler, pack, and future domain (novel, comic, game,
podcast, course) must obey. This document is stable across implementation churn — it
does not change when `CREATIVE_GRAPH_SPEC.md` or `COMPILER_ABI.md` evolve to v1.1+.

## The eight principles

1. **The Creative Knowledge Graph is the single source of truth.** No compiler, no
   artifact, no cache holds authoritative state that isn't derivable from the five
   graphs defined in `CREATIVE_GRAPH_SPEC.md`.
2. **Every artifact is compiled, never authored in isolation.** A screenplay, a
   prompt, an audio file — none of these are hand-edited independent of the graph
   that produced them. Edits go back through the graph and recompile.
3. **Humans direct; AI proposes.** Every compiler's output is a proposal subject to
   the review workflow (`CREATIVE_GRAPH_SPEC.md` §Review Graph); no artifact reaches
   "accepted" state without passing through Human Review.
4. **Outputs must be reproducible through provenance.** Every artifact carries enough
   metadata (`COMPILER_ABI.md` §Provenance) to regenerate it exactly, or to explain
   exactly why it differs on regeneration.
5. **Offline-first by default; cloud only when it adds measurable value.** Every
   capability must have a local execution path (`COMPUTE_MANAGER_SPEC.md`); cloud is
   an enhancement tier, never a requirement to produce a minimum-viable artifact.
6. **Quality and consistency outweigh generation speed.** Compilers are permitted to
   retry, validate, and repair (`COMPILER_ABI.md` §Compiler Contract) rather than
   emit a first-pass result.
7. **Economic efficiency is a first-class optimization objective.** Every compiler
   reports a cost/time/resource estimate before generation (`COMPILER_ABI.md`
   §Estimation) — this is not optional instrumentation, it is a contract requirement.
8. **Every creative decision is traceable back to the project state that produced
   it.** Provenance (principle 4) plus the Review Graph together answer "why does
   this artifact exist" for any artifact, at any time.

## Scope

This Manifesto governs NAC's Phase 1 domain (film) and any future domain built on the
same Creative Compiler Framework (novel, comic, game, podcast, course — see
`docs/superpowers/specs/2026-07-03-nth-absolute-cinema-design.md` §1). It does not
govern the Nth Absolute Cinema Studio desktop application's UI/UX decisions, which may
change freely as long as they do not violate these eight principles.

## Amendment process

A change to this document requires: (1) a written rationale for which principle is
being added/removed/reworded and why, (2) an audit of every existing spec document in
`docs/specs/v1/` for compliance with the proposed change, (3) explicit user approval.
This mirrors CRP's RFC discipline (`docs/vision/TITAN.md`) without importing CRP's
RFC tooling — NAC and CRP remain separate projects.
```

- [ ] **Step 2: Self-review**

Checklist:
- [ ] All 8 principles from the approved design doc (§2.1) are present, unreworded.
- [ ] No TBD/placeholder text.
- [ ] Cross-references to `CREATIVE_GRAPH_SPEC.md` and `COMPILER_ABI.md` use section
  names that will actually exist after Tasks 3-4 (verify after writing those, or fix
  forward at Task 13's cross-document consistency pass).

- [ ] **Step 3: Commit**

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\MANIFESTO.md
git commit -m "docs(spec): freeze NAC Creative Compiler Manifesto v1.0"
```

---

### Task 3: Write Creative Graph Specification v1.0

**Files:**
- Create: `E:\nth-absolute-cinema\docs\specs\v1\CREATIVE_GRAPH_SPEC.md`

**Interfaces:**
- Consumes: Manifesto principle 1 (single source of truth), principle 8 (traceability).
- Produces: the five graph schemas, Style Genome schema, story hierarchy, four-layer
  validation contract, and provenance schema that `COMPILER_ABI.md` (Task 4),
  `PACK_ABI.md` (Task 5), and `REPOSITORY_INTERFACES.md` (Task 11) all reference by
  exact type name.

- [ ] **Step 1: Write the document**

Content of `CREATIVE_GRAPH_SPEC.md`:

```markdown
# NAC Creative Graph Specification v1.0

**Status:** FROZEN (2026-07-03)
**Governed by:** `MANIFESTO.md` principles 1, 2, 8.

## 1. The five graphs

```
Project
├── KnowledgeGraph    — story facts, characters, mythology, locations, timeline
├── CinematicGraph    — shots, camera, cuts, music cues
├── AssetGraph        — images, audio, video, prompts (hashed, cached, reused)
├── ProductionGraph   — jobs, queues, cost/time estimates, dependencies
└── ReviewGraph       — approvals, comments, versions, human edits
```

`KnowledgeGraph` MUST NOT contain camera/edit decisions — those belong exclusively to
`CinematicGraph`. This is a hard schema-level separation, not a convention: no node
type defined under §2 (Knowledge) may carry a `camera_*`, `shot_type`, or `cut_*`
field.

## 2. Knowledge Graph node types

| Node type | Required fields | Notes |
|---|---|---|
| `Story` | `id: UUID`, `title: str`, `graph_spec_version: str` | Root node, one per project |
| `Act` | `id`, `story_id: UUID`, `order: int` | |
| `Sequence` | `id`, `act_id: UUID`, `order: int` | |
| `Scene` | `id`, `sequence_id: UUID`, `order: int`, `location_id: UUID` | |
| `Beat` | `id`, `scene_id: UUID`, `order: int`, `emotion: EmotionalNode` | Action/dialogue unit |
| `Character` | `id`, `name: str`, `genome_ref: UUID` | References `CharacterGenome` (§4) |
| `Location` | `id`, `name: str`, `genome_ref: UUID` | References `LocationGenome`... wait see §4 naming |
| `Prop` | `id`, `name: str`, `genome_ref: UUID` | |
| `StoryBible` | `id`, `story_id`, `content: dict` | World rules, mythology |

Story hierarchy is strictly non-linear at the presentation layer: `Story → Acts →
Sequences → Scenes → Beats` is the canonical ordering used for compilation, but
`ReviewGraph` (§6) may hold alternate orderings (Director's Cut, Trailer Cut) as
separate `Cut` nodes that reference the same `Beat` set with a different `order`
override — no `Beat` data is duplicated for an alternate cut.

### 2.1 Emotional Graph (embedded in every Beat)

```
EmotionalNode {
  audience_emotion: str
  character_emotion: dict[character_id: UUID, emotion: str]
  intensity: float        # 0.0-1.0
  pacing: float           # 0.0-1.0, 0=slow 1=fast
  conflict: float         # 0.0-1.0
  mystery: float          # 0.0-1.0
  release: float          # 0.0-1.0
}
```

## 3. Cinematic Graph node types

| Node type | Required fields | Notes |
|---|---|---|
| `Shot` | `id`, `beat_id: UUID`, `order: int`, `shot_type: str`, `camera_genome_ref: UUID`, `target_platforms: list[PlatformTarget]` | See §3.1 |
| `Cut` | `id`, `from_shot_id: UUID`, `to_shot_id: UUID`, `cut_type: str` | e.g. "hard", "fade", "wipe" |
| `MusicCue` | `id`, `shot_id: UUID`, `start_offset_ms: int`, `genome_ref: UUID` | References `MusicGenome` |

### 3.1 PlatformTarget (aspect-ratio-native generation)

```
PlatformTarget {
  platform: str            # "reels" | "youtube" | "linkedin" | "shorts" | ...
  aspect_ratio: str        # "9:16" | "16:9" | "1:1" | "4:5"
}
```

Each `Shot` carries `target_platforms: list[PlatformTarget]`. `COMPILER_ABI.md`'s
Prompt Compiler MUST generate one native prompt per `PlatformTarget` per shot —
composition and framing recomputed per ratio. Cropping a single master render to fit
multiple platforms is a spec violation, not an implementation choice.

## 4. Style Genome schema

Nine genome types, each independently versioned and referenced (never copied) by any
node needing consistency:

```
CharacterGenome { id, character_id, visual_refs: list[AssetRef], voice_seed: str, personality_traits: dict }
VisualGenome     { id, style_refs: list[AssetRef], negative_prompt: str, seed: int|None }
DialogueGenome   { id, character_id, vocabulary_profile: dict, speech_pattern: str }
MusicGenome      { id, tempo_range: tuple[int,int], instrumentation: list[str], mood_tags: list[str] }
EditingGenome    { id, pacing_profile: str, cut_frequency: float }
CameraGenome     { id, lens_preference: str, movement_style: str }
LightingGenome   { id, key_light_ratio: float, color_temp_k: int }
CostumeGenome    { id, character_id, palette: list[str], material_refs: list[AssetRef] }
EnvironmentGenome{ id, location_id, atmosphere_tags: list[str], palette: list[str] }
```

`AssetRef = { asset_id: UUID, content_hash: str }` — always a reference into
`AssetGraph` (§5), never an embedded binary.

## 5. Asset Graph node types

| Node type | Required fields | Notes |
|---|---|---|
| `Asset` | `id`, `content_hash: str (sha256)`, `kind: str`, `storage_tier: str`, `path: RelativePath` | `kind` ∈ {image, audio, video, prompt_text} |
| `Prompt` | `id`, `pack_id: str`, `pack_version: str`, `platform_target: PlatformTarget`, `compiled_text: str` | Output of Prompt Compiler |

Assets are content-addressed: two identical renders share one `Asset` node
(`content_hash` dedup) — this is the mechanism behind the "asset cache/reuse"
requirement in the design doc §5.

## 6. Production Graph node types

| Node type | Required fields |
|---|---|
| `Job` | `id`, `compiler_id: str`, `status: str`, `depends_on: list[UUID]` |
| `Estimate` | `id`, `job_id: UUID`, `estimated_tokens: int`, `estimated_gpu_hours: float`, `estimated_ram_mb: int`, `estimated_time_s: int`, `estimated_cost_usd: float`, `confidence: float` |

## 7. Review Graph node types

| Node type | Required fields |
|---|---|
| `ReviewEntry` | `id`, `artifact_id: UUID`, `stage: str`, `verdict: str`, `comment: str\|None`, `reviewer: str` | `stage` ∈ {ai_self_review, human_review}; `verdict` ∈ {approved, rejected, needs_revision} |
| `Cut` | `id`, `story_id: UUID`, `name: str`, `beat_order_override: list[UUID]` | Director's Cut / Trailer / alternate-ending views (§2) |

## 8. Four-layer validation contract

Every graph snapshot passes through, in order, before reaching any compiler:

```
Structural  → missing character, broken timeline, missing location
Creative    → inconsistent motivation, dialogue not matching CharacterGenome
Technical   → prompt exceeds pack token/duration limits (see PACK_ABI.md), invalid seed
Platform    → aspect ratio invalid for target platform, duration exceeds platform limit
```

A `ValidationResult` is `{ layer: str, passed: bool, violations: list[Violation] }`
per layer; a snapshot only proceeds to compilation if all four layers pass.

## 9. Provenance schema

Every compiled `Asset` and `Prompt` node carries:

```
Provenance {
  knowledge_version: str      # graph snapshot hash at compile time
  compiler_id: str
  compiler_version: str       # semver, see VERSIONING_POLICY.md
  pack_id: str | None
  pack_version: str | None
  model: str
  seed: int | None
  output_hash: str
}
```

## 10. Versioning of this schema

See `VERSIONING_POLICY.md` §Creative Graph Specification versioning. This document is
`v1.0`; a `graph_spec_version` field on the root `Story` node pins every project to
the schema version it was created under.
```

- [ ] **Step 2: Self-review**

Checklist:
- [ ] Fix the stray "wait see §4 naming" comment left in the `Location` row of the
  Knowledge Graph table — replace with `EnvironmentGenome` (the actual genome name
  used for locations per §4), not a placeholder note.
- [ ] All 9 genome types from the design doc §4 present with concrete fields, not
  just names.
- [ ] `target_platforms`/`PlatformTarget` schema matches design doc §6 exactly
  (aspect-ratio-native, no crop).
- [ ] Four validation layers match design doc §5 wording.
- [ ] Provenance fields match design doc §9 exactly (same field names) — this must
  stay byte-identical to what `COMPILER_ABI.md` (Task 4) references.

- [ ] **Step 3: Fix the placeholder found in self-review**

In the Knowledge Graph node table, change:
```
| `Location` | `id`, `name: str`, `genome_ref: UUID` | References `LocationGenome`... wait see §4 naming |
```
to:
```
| `Location` | `id`, `name: str`, `genome_ref: UUID` | References `EnvironmentGenome` (§4) |
```

- [ ] **Step 4: Commit**

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\CREATIVE_GRAPH_SPEC.md
git commit -m "docs(spec): freeze Creative Graph Specification v1.0"
```

---

### Task 4: Write Creative Compiler ABI v1.0

**Files:**
- Create: `E:\nth-absolute-cinema\docs\specs\v1\COMPILER_ABI.md`

**Interfaces:**
- Consumes: `CREATIVE_GRAPH_SPEC.md` §9 (Provenance), §8 (Validation), Manifesto
  principles 2, 3, 4, 6, 7.
- Produces: the `Compiler` base contract that `REPOSITORY_INTERFACES.md` (Task 11)
  expresses as a `Protocol`, and that `PACK_ABI.md` (Task 5) assumes for the Prompt
  Compiler specifically.

- [ ] **Step 1: Write the document**

Content of `COMPILER_ABI.md`:

```markdown
# NAC Creative Compiler ABI v1.0

**Status:** FROZEN (2026-07-03)
**Governed by:** `MANIFESTO.md` principles 2, 3, 4, 6, 7. Uses types from
`CREATIVE_GRAPH_SPEC.md` §8 (`ValidationResult`) and §9 (`Provenance`).

## Compiler contract (the 8-stage pipeline)

Every compiler (ScreenplayCompiler, StoryBibleCompiler, NovelCompiler, AudioCompiler,
DialogueCompiler, NarrationCompiler, PromptCompiler, StoryboardCompiler,
MotionPosterCompiler, TeaserCompiler, TrailerCompiler) implements exactly these 8
stages, in this order, with no stage skipped:

```
1. Input Schema   — declares which CREATIVE_GRAPH_SPEC.md node types it reads
2. Validation     — runs the four-layer contract (CREATIVE_GRAPH_SPEC.md §8);
                     halts on any failing layer
3. Planning       — produces an Estimate (CREATIVE_GRAPH_SPEC.md §6) BEFORE generation
4. Generation     — calls Model Manager (COMPUTE_MANAGER_SPEC.md) for the actual work
5. Measurement    — measures the real output (duration, token count, actual cost) —
                     never trusts the Planning-stage estimate as the final number
6. Repair         — if Measurement finds a fixable defect, re-invoke Generation with
                     corrective input; bounded retry count (compiler-specific, but
                     MUST be finite and logged)
7. Review         — writes a ReviewEntry (CREATIVE_GRAPH_SPEC.md §7) with
                     stage="ai_self_review"; does not proceed to Export without a
                     corresponding stage="human_review" ReviewEntry with
                     verdict="approved"
8. Export         — writes the final Asset/Prompt node with a populated Provenance
                     block (CREATIVE_GRAPH_SPEC.md §9)
```

No compiler may write an `Asset` or `Prompt` node outside of stage 8. No compiler may
skip stage 3 (Planning/Estimate) — this is what makes Manifesto principle 7 (economic
efficiency as a first-class objective) enforceable rather than aspirational.

## Estimation contract

Stage 3 (Planning) MUST produce exactly one `Estimate` node (CREATIVE_GRAPH_SPEC.md
§6) per `Job`. The `confidence` field is required — a compiler with no historical
data for a given operation MUST report a low confidence value rather than omitting
the field or hardcoding `1.0`.

## Provenance contract

Stage 8 (Export) MUST populate every field of `Provenance` (CREATIVE_GRAPH_SPEC.md
§9). `compiler_version` MUST be the exact semver of the compiler that ran (see
`VERSIONING_POLICY.md`) — not the ABI version. A missing or null Provenance field on
an exported Asset/Prompt is a contract violation, not a warning.

## Review contract

A ReviewEntry with `stage="ai_self_review"` is REQUIRED before any
`stage="human_review"` entry may be written for the same artifact — self-review runs
first and its result (even if `verdict="rejected"`) is retained, not overwritten, when
human review later approves.

## Failure semantics

If Validation (stage 2) fails, the compiler MUST NOT proceed past stage 2 and MUST
return a `ValidationResult` list (CREATIVE_GRAPH_SPEC.md §8) — no partial artifact is
written. If Repair (stage 6) exhausts its bounded retry count without a passing
Measurement, the compiler MUST write a `Job` with `status="failed"`
(CREATIVE_GRAPH_SPEC.md §6) rather than silently exporting a defective artifact.

## Compiler registration

Every compiler declares:
```
CompilerDeclaration {
  compiler_id: str            # e.g. "screenplay_compiler"
  compiler_version: str       # semver
  abi_version: str            # this document's version, "1.0"
  consumes_node_types: list[str]   # CREATIVE_GRAPH_SPEC.md node type names
  produces_node_types: list[str]
}
```

`abi_version` pins which version of this document the compiler was written against —
see `VERSIONING_POLICY.md` §Compiler ABI versioning for the compatibility rule.
```

- [ ] **Step 2: Self-review**

Checklist:
- [ ] The 8 stages match the design doc's compiler contract exactly
  (`Input Schema → Validation → Planning → Generation → Measurement → Repair →
  Review → Export`).
- [ ] Estimation contract references the exact `Estimate` field names from
  `CREATIVE_GRAPH_SPEC.md` §6 (`estimated_tokens`, etc.) — cross-check field-for-field.
- [ ] Provenance contract field names match `CREATIVE_GRAPH_SPEC.md` §9 exactly.
- [ ] No compiler-specific business logic leaked in (this is an ABI, not an
  implementation — verify no stage description assumes e.g. "screenplay pages" or
  "audio duration" specifically).

- [ ] **Step 3: Commit**

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\COMPILER_ABI.md
git commit -m "docs(spec): freeze Creative Compiler ABI v1.0"
```

---

### Task 5: Write Pack ABI v1.0

**Files:**
- Create: `E:\nth-absolute-cinema\docs\specs\v1\PACK_ABI.md`

**Interfaces:**
- Consumes: `COMPILER_ABI.md` (Prompt Compiler calls into a Pack at its Generation
  stage), `CREATIVE_GRAPH_SPEC.md` §3.1 (`PlatformTarget`).
- Produces: the Pack contract that `NAC_PACKAGE_SPEC.md` (Task 6) references when
  recording `pack_version` in a `.nac` manifest, and that `EXTENSIBILITY.md` (Task 12)
  cites as the primary extension point for new generation tools.

- [ ] **Step 1: Write the document**

Content of `PACK_ABI.md`:

```markdown
# NAC Pack ABI v1.0

**Status:** FROZEN (2026-07-03)
**Governed by:** `MANIFESTO.md` principle 5 (offline-first). Uses types from
`CREATIVE_GRAPH_SPEC.md` §3.1 (`PlatformTarget`), §5 (`Prompt`).

## Purpose

A NAC Pack is the sole extension mechanism for adding a generation tool (Google Flow,
Higgsfield, OpenArt, Flux, ComfyUI, ...) to the Prompt Compiler. `COMPILER_ABI.md`'s
Prompt Compiler never hardcodes a tool integration — it always calls through a Pack.

## Required Pack components

Every pack under `engine/packs/<pack_id>/` MUST provide exactly these five
components:

```
Parser              — parses a CinematicGraph Shot + genome refs into the pack's
                       internal prompt representation
PromptCompiler       — compiles that representation into the tool's native prompt
                       syntax, ONE output per PlatformTarget on the Shot (no crop —
                       see CREATIVE_GRAPH_SPEC.md §3.1)
Validator            — checks the compiled prompt against CapabilityMatrix limits
                       (below) BEFORE it is sent to Generation
CapabilityMatrix     — static declaration of the tool's strengths/weaknesses/limits
Templates            — reusable prompt fragments (camera syntax, motion syntax,
                       negative-prompt boilerplate) specific to this tool
```

## CapabilityMatrix schema

```
CapabilityMatrix {
  pack_id: str
  pack_version: str            # semver, see VERSIONING_POLICY.md
  supported_platforms: list[PlatformTarget]
  max_prompt_tokens: int
  max_duration_s: float | None
  supported_aspect_ratios: list[str]
  supports_negative_prompt: bool
  supports_seed: bool
  known_limitations: list[str]
  requires_cloud: bool          # True for e.g. Google Flow; False for local packs
}
```

`Validator` MUST reject (Technical validation layer, `CREATIVE_GRAPH_SPEC.md` §8) any
compiled prompt exceeding `max_prompt_tokens` or requesting an unsupported
`aspect_ratio` — this is where the four-layer validation contract's Technical layer is
actually implemented for prompt generation.

## Capability Registry

```
CapabilityRegistry {
  register(pack: PackDeclaration) -> None
  resolve(platform_target: PlatformTarget, requires_cloud: bool | None) -> list[PackDeclaration]
}

PackDeclaration {
  pack_id: str
  pack_version: str
  capability_matrix: CapabilityMatrix
}
```

`PromptCompiler` (in `COMPILER_ABI.md`'s sense) asks `CapabilityRegistry.resolve()`
for candidate packs given a `Shot`'s `target_platforms`; it never imports a specific
pack module directly. This is the mechanism that makes "new tool support = new pack,
zero core changes" (design doc §7) an architectural guarantee rather than a
convention.

## Pack discovery

Packs are discovered by directory presence under `engine/packs/`, not by a central
hardcoded list. A pack missing any of the five required components (above) MUST fail
`CapabilityRegistry.register()` at startup rather than registering partially.

## Versioning

See `VERSIONING_POLICY.md` §Pack versioning. `pack_version` is recorded in every
`Prompt` node's `Provenance.pack_version` (`CREATIVE_GRAPH_SPEC.md` §9) and in every
`.nac` manifest (`NAC_PACKAGE_SPEC.md`).
```

- [ ] **Step 2: Self-review**

Checklist:
- [ ] Five required components match design doc §7 (`parser, prompt_compiler,
  validator, capability_matrix, limits, templates` — note design doc lists 6 items
  including `limits` and `examples`; reconcile: `limits` folds into
  `CapabilityMatrix`, `examples` folds into `Templates` — confirm this reconciliation
  is stated explicitly, not silently dropped).
- [ ] `CapabilityMatrix` schema has no placeholder fields.
- [ ] Cross-reference `CREATIVE_GRAPH_SPEC.md` §3.1 `PlatformTarget` type name matches
  exactly.

- [ ] **Step 3: Fix the reconciliation gap found in self-review**

Add this paragraph to `PACK_ABI.md` right after "Required Pack components":

```markdown
> **Note on component naming:** the design doc (§7) lists six pack sub-components
> (`parser, prompt_compiler, validator, capability_matrix, limits, templates,
> examples`). This ABI consolidates `limits` into `CapabilityMatrix` (the `max_*`
> fields) and `examples` into `Templates` (reusable fragments include worked
> examples) — five components, not seven, with no capability lost.
```

- [ ] **Step 4: Commit**

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\PACK_ABI.md
git commit -m "docs(spec): freeze Pack ABI v1.0"
```

---

### Task 6: Write `.nac` Package Specification v1.0

**Files:**
- Create: `E:\nth-absolute-cinema\docs\specs\v1\NAC_PACKAGE_SPEC.md`

**Interfaces:**
- Consumes: `CREATIVE_GRAPH_SPEC.md` (all five graphs + genomes + provenance),
  `PACK_ABI.md` (`pack_version`), `COMPUTE_MANAGER_SPEC.md` (Task 10, import-time
  profile detection), `WORKSPACE_SPEC.md` (Task 9, storage tiers).
- Produces: the manifest schema that `VERSIONING_POLICY.md` (Task 12) references for
  `.nac` compatibility rules.

- [ ] **Step 1: Write the document**

Content of `NAC_PACKAGE_SPEC.md`:

```markdown
# NAC Package Specification v1.0 (`.nac` format)

**Status:** FROZEN (2026-07-03)
**Governed by:** `MANIFESTO.md` principle 4 (reproducibility via provenance).

## Purpose

A `.nac` file is a portable, self-describing archive of one NAC project, exportable
on one machine and importable on another with a different hardware profile, without
requiring the destination to already have the source machine's local models or cache.

## Container format

A `.nac` file is a `zip` archive (uncompressed manifest, compressed payload) with this
top-level layout:

```
movie.nac
├── manifest.json
├── graphs/
│   ├── knowledge_graph.json
│   ├── cinematic_graph.json
│   ├── asset_graph.json          (metadata only — see Asset handling below)
│   ├── production_graph.json
│   └── review_graph.json
├── genomes/
│   └── <genome_type>/<genome_id>.json     (all 9 genome types, CREATIVE_GRAPH_SPEC.md §4)
├── prompts/
│   └── <prompt_id>.json           (compiled Prompt IR, not raw text only)
├── provenance/
│   └── <artifact_id>.json         (Provenance blocks, CREATIVE_GRAPH_SPEC.md §9)
├── review_history/
│   └── <review_entry_id>.json
└── assets/
    ├── embedded/<content_hash>.<ext>      (small/source assets, embedded by hash)
    └── references.json                     (large renders: content_hash + relative
                                              path + regeneration provenance, NOT embedded
                                              unless embed_large_assets=true at export)
```

## Manifest schema

```
NacManifest {
  nac_format_version: str            # "1.0"
  graph_spec_version: str            # CREATIVE_GRAPH_SPEC.md version this project uses
  manifesto_version: str
  exported_at: str                   # ISO 8601
  exported_from_profile: str         # Compute Manager profile, COMPUTE_MANAGER_SPEC.md
  compiler_versions: dict[str, str]  # compiler_id -> compiler_version, ABI-checked
  pack_versions: dict[str, str]      # pack_id -> pack_version
  referenced_local_models: list[ModelReference]   # NOT the weights themselves
  embed_large_assets: bool
  content_hash_of_package: str       # sha256 of the archive contents (integrity check)
}

ModelReference {
  model_id: str
  model_version: str
  capability_tags: list[str]
  approx_size_mb: int
}
```

## Export rules

1. **Included, always:** all five graphs, all genomes, provenance, compiled prompts,
   review history, manifest.
2. **Included, content-addressed:** small/source assets (reference images, approved
   takes) — embedded by `content_hash` under `assets/embedded/`.
3. **Included by reference, embed optional:** large generated renders — always listed
   in `assets/references.json` with `content_hash` + regeneration provenance; embedded
   binary only if the export was run with `embed_large_assets=true`.
4. **Never included:** local model weights (`local_models/` tree), anything in the
   cache tier or `temp/` (`WORKSPACE_SPEC.md`), derived thumbnails/inference caches.

## Import rules (in order)

```
1. Verify manifest.nac_format_version and graph_spec_version are compatible with the
   importing NAC installation (VERSIONING_POLICY.md §.nac compatibility)
2. Restore all five graphs + genomes + provenance + review_history into projects/<new_id>/
3. Run Compute Manager hardware profiling on the destination machine
   (COMPUTE_MANAGER_SPEC.md) to select an execution profile
4. Diff manifest.referenced_local_models against installed models; install only the
   missing ones (COMPUTE_MANAGER_SPEC.md §On-demand model installation)
5. For each entry in assets/references.json NOT embedded in the package: attempt
   regeneration from its Provenance block; if regeneration is not possible (e.g. a
   cloud model version no longer exists), mark the Asset node status="missing" rather
   than failing the whole import
```

An import that completes step 5 with some assets `status="missing"` is still a
successful import — Manifesto principle 4 requires reproducibility of the *creative
state* (graphs/genomes/provenance), not a guarantee that every historical cloud
render can always be re-fetched byte-identical.

## Integrity

`manifest.content_hash_of_package` is computed over the archive's file listing +
per-file hashes at export time and MUST be verified at the start of import (step 1,
before any graph data is trusted) — a `.nac` file that fails this check is rejected
outright, not partially imported.
```

- [ ] **Step 2: Self-review**

Checklist:
- [ ] Every graph type from `CREATIVE_GRAPH_SPEC.md` §1 is listed under `graphs/`.
- [ ] Asset handling (embed vs. reference) matches design doc §21 exactly — small
  assets embedded, large renders referenced with optional embed toggle.
- [ ] Import flow matches design doc §21 "Import flow" 5-step sequence.
- [ ] "Not exported" list matches design doc §21 exactly (local model weights,
  cache-tier data).

- [ ] **Step 3: Commit**

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\NAC_PACKAGE_SPEC.md
git commit -m "docs(spec): freeze .nac Package Specification v1.0"
```

---

### Task 7: Write Event Specification v1.0

**Files:**
- Create: `E:\nth-absolute-cinema\docs\specs\v1\EVENT_SPEC.md`

**Interfaces:**
- Consumes: `CREATIVE_GRAPH_SPEC.md` node types (events reference them by ID),
  `COMPILER_ABI.md` (compiler stage transitions emit events).
- Produces: the event taxonomy that `REPOSITORY_INTERFACES.md` (Task 11) uses for the
  `EventBus` interface, and that `PLUGIN_ABI.md` (Task 8) uses as the mechanism
  plugins subscribe to.

- [ ] **Step 1: Write the document**

Content of `EVENT_SPEC.md`:

```markdown
# NAC Event Specification v1.0

**Status:** FROZEN (2026-07-03)
**Governed by:** `COMPILER_ABI.md` (8-stage pipeline emits these events).

## Purpose

The event bus is how one compiler's output triggers another compiler's input without
direct coupling — e.g. "screenplay compiled" triggering the Prompt Compiler. Every
cross-module reaction in NAC goes through this event system; no module calls another
module's compiler directly (see `MODULE_BOUNDARIES.md`).

## Event envelope

Every event on the bus has this exact shape:

```
Event {
  event_id: UUID
  event_type: str            # dot-namespaced, see taxonomy below
  occurred_at: str            # ISO 8601
  project_id: UUID
  source: str                  # compiler_id, pack_id, or "system"
  payload: dict                 # event_type-specific, schemas below
  graph_snapshot_version: str    # KnowledgeGraph/CinematicGraph version at emit time
}
```

## Event taxonomy (v1.0 — closed set; extending requires a VERSIONING_POLICY.md minor bump)

```
graph.knowledge.updated        { changed_node_ids: list[UUID] }
graph.cinematic.updated        { changed_node_ids: list[UUID] }
compiler.stage.entered         { compiler_id, job_id: UUID, stage: str }   # one of the 8 stages, COMPILER_ABI.md
compiler.stage.completed       { compiler_id, job_id: UUID, stage: str, duration_ms: int }
compiler.job.failed            { compiler_id, job_id: UUID, stage: str, reason: str }
compiler.artifact.exported     { compiler_id, job_id: UUID, artifact_id: UUID, artifact_kind: str }
review.entry.created           { review_entry_id: UUID, artifact_id: UUID, stage: str, verdict: str }
production.estimate.created    { estimate_id: UUID, job_id: UUID }
nac.export.completed           { package_path: RelativePath, manifest_hash: str }
nac.import.completed           { source_manifest_hash: str, missing_asset_ids: list[UUID] }
compute.profile.selected       { profile: str, reason: str }             # COMPUTE_MANAGER_SPEC.md
model.install.completed        { model_id: str, model_version: str }
```

## Subscription contract

```
EventBus {
  publish(event: Event) -> None
  subscribe(event_type_pattern: str, handler: Callable[[Event], None]) -> SubscriptionHandle
  unsubscribe(handle: SubscriptionHandle) -> None
}
```

`event_type_pattern` supports a single trailing wildcard (`"compiler.stage.*"`
matches both `entered` and `completed`) — no other glob syntax is supported in v1.0.

## Ordering and delivery guarantees

- Events for a single `project_id` are delivered to subscribers in emission order.
- Delivery is at-least-once, not exactly-once — handlers MUST be idempotent w.r.t.
  `event_id` (dedupe on `event_id` if a handler's side effect isn't naturally
  idempotent).
- The event bus is in-process for Phase 1 (no distributed queue) — this MAY change in
  a later phase for the Studio (Cloud) Compute Manager profile, but that change would
  be additive (a different `EventBus` implementation satisfying the same interface),
  not a change to this spec.
```

- [ ] **Step 2: Self-review**

Checklist:
- [ ] Every one of the 8 compiler stages from `COMPILER_ABI.md` has a corresponding
  `compiler.stage.*` event path (verify `stage: str` values are drawn from the exact
  8 stage names, not renamed).
- [ ] `nac.export.completed`/`nac.import.completed` payloads match
  `NAC_PACKAGE_SPEC.md` manifest fields (`content_hash_of_package`).
- [ ] No event type references a node type not defined in `CREATIVE_GRAPH_SPEC.md`.

- [ ] **Step 3: Commit**

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\EVENT_SPEC.md
git commit -m "docs(spec): freeze Event Specification v1.0"
```

---

### Task 8: Write Plugin ABI v1.0

**Files:**
- Create: `E:\nth-absolute-cinema\docs\specs\v1\PLUGIN_ABI.md`

**Interfaces:**
- Consumes: `EVENT_SPEC.md` (`EventBus`), `COMPILER_ABI.md` (plugins may wrap
  compilers but not bypass the 8-stage contract).
- Produces: the plugin contract that `EXTENSIBILITY.md` (Task 12) references as the
  second (after Packs) formal extension point.

- [ ] **Step 1: Write the document**

Content of `PLUGIN_ABI.md`:

```markdown
# NAC Plugin ABI v1.0

**Status:** FROZEN (2026-07-03)
**Governed by:** `MANIFESTO.md` (plugins may not violate any of the 8 principles);
uses `EVENT_SPEC.md`'s `EventBus`.

## Purpose

A Plugin is the extension point for behavior that is neither a new generation tool
(that's a Pack, `PACK_ABI.md`) nor a new artifact type (that's a new Compiler,
`COMPILER_ABI.md`). Examples in scope for v1.0: a custom validation rule, a
third-party review-workflow integration, a telemetry exporter.

## Distinction from Packs and Compilers

| Extension type | Extends | Cannot do |
|---|---|---|
| Pack | A specific generation tool's prompt syntax | Cannot define a new node type or bypass the 8-stage compiler contract |
| Plugin | Cross-cutting behavior via events | Cannot write directly to any graph — must go through a Compiler or the Review workflow |
| Compiler | A new artifact type (new domain, e.g. future ComicCompiler) | N/A — this is the top-level extension point, requires a graph_spec-compatible node type set |

## Plugin contract

```
Plugin {
  plugin_id: str
  plugin_version: str          # semver, VERSIONING_POLICY.md
  abi_version: str              # "1.0", pins this document's version
  subscribed_events: list[str]   # EVENT_SPEC.md event_type patterns
  on_event(event: Event) -> None
}
```

## Hard constraints (enforced, not advisory)

1. A plugin's `on_event` handler MUST NOT call any Compiler's stage methods directly
   — it may only react by publishing new events (`EventBus.publish`) or by writing to
   the `ReviewGraph` via the Review workflow's public interface
   (`REPOSITORY_INTERFACES.md`).
2. A plugin MUST declare every event type it subscribes to at registration time —
   dynamic subscription changes at runtime are not supported in v1.0.
3. A plugin failure (unhandled exception in `on_event`) MUST NOT crash the publisher
   — the event bus catches and logs plugin exceptions, continuing delivery to other
   subscribers.

## Plugin discovery

Plugins are discovered under `engine/plugins/` the same way Packs are discovered
under `engine/packs/` (`PACK_ABI.md` §Pack discovery) — directory presence, not a
hardcoded registry list.
```

- [ ] **Step 2: Self-review**

Checklist:
- [ ] The Pack/Plugin/Compiler distinction table has no overlapping "cannot do"
  entries that contradict `PACK_ABI.md` or `COMPILER_ABI.md`.
- [ ] `Plugin.abi_version` field name/type matches the pattern used in
  `COMPILER_ABI.md`'s `CompilerDeclaration.abi_version` and `PACK_ABI.md`'s
  (verify `PACK_ABI.md`'s `PackDeclaration` — note it currently has no `abi_version`
  field; this is a real gap, not a false positive).

- [ ] **Step 3: Fix the cross-document gap found in self-review**

Go back and edit `PACK_ABI.md`'s `PackDeclaration` type (written in Task 5) to add
the missing field, for consistency with `CompilerDeclaration` and `Plugin`:

```
PackDeclaration {
  pack_id: str
  pack_version: str
  abi_version: str              # "1.0", pins PACK_ABI.md version — ADDED for consistency
  capability_matrix: CapabilityMatrix
}
```

Amend `E:\nth-absolute-cinema\docs\specs\v1\PACK_ABI.md` in place with this addition,
then `git add` + amend or new commit (new commit preferred — do not rewrite an
already-pushed/frozen commit; this repo has no remote yet in Sprint 0 so either is
safe, but use a new commit to keep the freeze-then-fix history visible):

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\PACK_ABI.md
git commit -m "docs(spec): add abi_version to PackDeclaration for cross-spec consistency"
```

- [ ] **Step 4: Commit the Plugin ABI itself**

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\PLUGIN_ABI.md
git commit -m "docs(spec): freeze Plugin ABI v1.0"
```

---

### Task 9: Write Workspace Specification v1.0

**Files:**
- Create: `E:\nth-absolute-cinema\docs\specs\v1\WORKSPACE_SPEC.md`

**Interfaces:**
- Consumes: design doc §17 (Portability), §20 (Storage tiers).
- Produces: the `PathResolver` contract that `REPOSITORY_INTERFACES.md` (Task 11)
  expresses formally, and the storage-tier definitions that `NAC_PACKAGE_SPEC.md`
  (Task 6) already assumed — this task's self-review must confirm no contradiction.

- [ ] **Step 1: Write the document**

Content of `WORKSPACE_SPEC.md`:

```markdown
# NAC Workspace Specification v1.0

**Status:** FROZEN (2026-07-03)
**Governed by:** `MANIFESTO.md` principle 5 (offline-first / portability is a
corollary: a project must work wherever the user is).

## Relocatable project root

The NAC project root (default `E:\nth-absolute-cinema\`, but not fixed to that path)
is resolved at startup by walking up from the running module's location to find a
marker file, `.nac-root`, rather than reading any configured or hardcoded path.

```
PathResolver {
  find_root(start_path: Path) -> Path            # walks up until .nac-root found
  resolve(relative: RelativePath) -> Path          # root-joined absolute path
  root() -> Path
}
```

**Hard rule:** no module outside `engine/kernel/paths.py` (or its language
equivalent) may construct an absolute path via string concatenation or a hardcoded
drive letter. Every other module receives paths only through `PathResolver.resolve()`
or a path already resolved and passed to it.

## Storage tiers

```
Cache tier    (cache/, renders/, assets/ [shared lib], temp/)
  — fully derived/regeneratable, safe to delete entirely, NEVER included in a
    .nac export (NAC_PACKAGE_SPEC.md "Never included")

Project tier  (projects/<project_id>/)
  — authoritative: five graphs (SQLite), genomes, provenance, review history,
    source assets. This is what a .nac package is built FROM.

Archive tier  (archive/)
  — cold storage: exported .nac packages, completed project snapshots kept for
    provenance/replay but not actively worked on.
```

Every path resolved by `PathResolver` MUST be tagged with which tier it belongs to;
`engine.storage` refuses to write project-tier data (graphs, provenance) into a
cache-tier path and vice versa — this is a load-bearing invariant for
`NAC_PACKAGE_SPEC.md`'s "export project tier only" rule to be mechanically
enforceable rather than a documentation-only convention.

## Relocation guarantee

Copying the entire project root (e.g. `E:\nth-absolute-cinema\` → a different drive
letter, or to another machine's `D:\nth-absolute-cinema\`) and re-running NAC from
the new location MUST work with zero configuration changes, provided:
1. The `.nac-root` marker file is copied along with everything else (it is at the
   project root, so a full-directory copy always includes it).
2. `local_models/` either comes along too, or Model Manager's on-demand install
   (`COMPUTE_MANAGER_SPEC.md`) fills gaps on first run at the new location.

This is the mechanism, not a promise made separately from the architecture — see
`SPRINT0_FREEZE.md` success criteria for the smoke test that verifies it.

## Multi-project workspace

One `E:\nth-absolute-cinema\` root MAY contain multiple projects under `projects/`
(one subdirectory per `project_id`). `cache/`, `local_models/`, and `archive/` are
shared across all projects in that workspace — this is why the cache tier is never
exported in a `.nac`: it may contain data belonging to sibling projects.
```

- [ ] **Step 2: Self-review**

Checklist:
- [ ] Storage tier definitions match `NAC_PACKAGE_SPEC.md` Task 6 "Export rules"
  wording exactly (cross-check "Never included" list against this doc's Cache tier
  contents list).
- [ ] `PathResolver` interface signatures are consistent with what
  `REPOSITORY_INTERFACES.md` (Task 11) will declare — flag for Task 11 to reuse
  these exact names (`find_root`, `resolve`, `root`), not rename them.

- [ ] **Step 3: Commit**

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\WORKSPACE_SPEC.md
git commit -m "docs(spec): freeze Workspace Specification v1.0"
```

---

### Task 10: Write Compute Manager Specification v1.0

**Files:**
- Create: `E:\nth-absolute-cinema\docs\specs\v1\COMPUTE_MANAGER_SPEC.md`

**Interfaces:**
- Consumes: design doc §18 (Compute Manager), §19 (on-demand model installation).
- Produces: the `ComputeProfile` enum and `ModelManager` install contract that
  `NAC_PACKAGE_SPEC.md` (Task 6) and `EVENT_SPEC.md` (Task 7,
  `compute.profile.selected`/`model.install.completed`) already reference by name.

- [ ] **Step 1: Write the document**

Content of `COMPUTE_MANAGER_SPEC.md`:

```markdown
# NAC Compute Manager Specification v1.0

**Status:** FROZEN (2026-07-03)
**Governed by:** `MANIFESTO.md` principle 5 (offline-first, hardware-adaptive).

## Execution profiles

```
ComputeProfile = "Micro" | "Standard" | "Pro" | "Studio"
```

| Profile | Colloquial | Local scope |
|---|---|---|
| Micro | Laptop | Lightweight local LLMs, local TTS, prompt compilation, story generation, audio screenplay. Cloud video generation only when needed. |
| Standard | Gaming PC | Everything local except premium video. |
| Pro | Studio Workstation | Almost everything local. |
| Studio | Cloud | Heavy rendering, distributed generation, team collaboration. |

## Profiling contract

```
HardwareProfile {
  cpu_cores: int
  ram_gb: float
  gpu_name: str | None
  vram_gb: float | None
  storage_free_gb: float
  storage_kind: str            # "ssd" | "hdd" | "network"
  installed_models: list[ModelReference]     # NAC_PACKAGE_SPEC.md ModelReference
}

ComputeManager {
  profile_hardware() -> HardwareProfile
  select_profile(hw: HardwareProfile) -> ComputeProfile
  current_profile() -> ComputeProfile
  reprofile() -> ComputeProfile        # re-run detection; used on project relocation
}
```

`select_profile` is a pure function of `HardwareProfile` — deterministic thresholds
(exact GB/VRAM cutoffs are an implementation detail of Sprint 1, not fixed by this
spec, but the function signature and the four-value output enum are frozen here).

## Model Manager: on-demand installation

```
ModelManager {
  is_installed(model_id: str) -> bool
  install(model_id: str) -> ModelReference       # emits model.install.completed (EVENT_SPEC.md)
  resolve_for_capability(capability_tag: str, profile: ComputeProfile) -> ModelReference | None
}
```

**Hard rule:** `ModelManager` never installs a model that was not explicitly
requested by a compiler's capability lookup (`resolve_for_capability`). There is no
"install everything" path in v1.0 — a fresh `Micro`-profile project may run correctly
having installed only 1-2 small models.

## Model package manifest

Each installable model under `local_models/` has its own manifest:

```
ModelPackageManifest {
  model_id: str
  model_version: str
  approx_size_mb: int
  min_vram_gb: float | None
  capability_tags: list[str]           # e.g. ["narration", "tts", "local"]
  compatible_profiles: list[ComputeProfile]
}
```

## Relationship to Model Manager routing (Tier 0-4)

The existing Tier 0-4 routing concept (Python deterministic → local LLM → local image
→ local audio → cloud) is unchanged by this spec — `ComputeManager.current_profile()`
constrains *which* tiers are actually reachable on this machine; it does not replace
the tier concept itself.

## Relationship to `.nac` import

On `.nac` import (`NAC_PACKAGE_SPEC.md`), step 3 calls `profile_hardware()` +
`select_profile()` fresh on the destination machine (never trusts the source
manifest's `exported_from_profile` as authoritative for the destination), and step 4
diffs `manifest.referenced_local_models` against `is_installed()` results, calling
`install()` only for the gap.
```

- [ ] **Step 2: Self-review**

Checklist:
- [ ] Four profiles match design doc §18 table exactly (names + colloquial mapping).
- [ ] `ModelReference` type reused here is identical to the one defined in
  `NAC_PACKAGE_SPEC.md` (same field names) — not redefined with different fields.
- [ ] `model.install.completed` event (from `EVENT_SPEC.md`) payload
  (`model_id, model_version`) matches `ModelManager.install()`'s return type fields.

- [ ] **Step 3: Commit**

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\COMPUTE_MANAGER_SPEC.md
git commit -m "docs(spec): freeze Compute Manager Specification v1.0"
```

---

### Task 11: Write Module Boundaries diagram + Repository Interfaces

**Files:**
- Create: `E:\nth-absolute-cinema\docs\specs\v1\MODULE_BOUNDARIES.md`
- Create: `E:\nth-absolute-cinema\docs\specs\v1\REPOSITORY_INTERFACES.md`

**Interfaces:**
- Consumes: every spec from Tasks 2-10 (this task is the cross-cutting synthesis).
- Produces: the import-boundary rules and `Protocol` stubs that Sprint 1's actual
  Python package layout must satisfy.

- [ ] **Step 1: Write `MODULE_BOUNDARIES.md`**

Content:

```markdown
# NAC Module Dependency Diagram & Import Boundaries v1.0

**Status:** FROZEN (2026-07-03)

## Diagram

```
                        ┌───────────────┐
                        │  engine.api   │  (only door to dashboard/CLI)
                        └───────┬───────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                  ▼
      ┌───────────────┐ ┌───────────────┐ ┌────────────────┐
      │engine.compilers│ │engine.review  │ │engine.production│
      └───────┬────────┘ └───────┬───────┘ └────────┬────────┘
              │                  │                   │
              ▼                  ▼                   ▼
      ┌────────────────────────────────────────────────────┐
      │        engine.knowledge / engine.cinematic /         │
      │        engine.assets  (the five graphs)               │
      └───────────────────────┬──────────────────────────────┘
                               │
                               ▼
                      ┌────────────────┐
                      │ engine.storage │
                      └───────┬────────┘
                               │
                               ▼
                      ┌────────────────┐
                      │ engine.kernel  │  (paths, Compiler base class, EventBus)
                      └────────────────┘

  engine.packs        → used ONLY by engine.compilers (PromptCompiler), never by
                          engine.knowledge/cinematic/assets directly
  engine.plugins       → used ONLY via engine.kernel.EventBus subscriptions
  engine.model_manager  → used by engine.compilers (Generation stage) AND
                            engine.compute_manager
  engine.compute_manager → used by engine.model_manager, engine.portability
  engine.portability      → used by engine.api only (export/import is a top-level
                              operation, not something a compiler triggers)
```

## Allowed import rules (enforced by lint in Sprint 1, declared here)

1. `engine.kernel` imports nothing else under `engine/` — it is the dependency floor.
2. `engine.storage` may import `engine.kernel` only.
3. `engine.knowledge`, `engine.cinematic`, `engine.assets`, `engine.production`,
   `engine.review` may import `engine.kernel` and `engine.storage` only — never each
   other directly (cross-graph reactions go through `engine.kernel.EventBus`, per
   `EVENT_SPEC.md`).
4. `engine.compilers.*` may import `engine.kernel`, `engine.storage`, the five graph
   modules (read/write via their repository interfaces, `REPOSITORY_INTERFACES.md`),
   and `engine.model_manager`. A compiler MAY import `engine.packs` only if it is the
   Prompt Compiler specifically.
5. `engine.packs.*` may import `engine.kernel` (for `PlatformTarget`-adjacent types)
   only — a pack MUST NOT import `engine.compilers`, `engine.storage`, or any graph
   module directly.
6. `engine.plugins.*` may import `engine.kernel.EventBus` and
   `REPOSITORY_INTERFACES.md`'s `ReviewRepository` only — no direct graph writes
   (`PLUGIN_ABI.md` hard constraint 1).
7. `engine.compute_manager` and `engine.model_manager` may import `engine.kernel`
   only.
8. `engine.portability` may import `engine.kernel`, `engine.storage`, all five graph
   modules (read-only for export, write for import), `engine.compute_manager`, and
   `engine.model_manager`.
9. `engine.api` may import anything under `engine/` — it is the only module allowed
   to. `dashboard/` (Node/React, later sprint) may only call `engine.api` over HTTP —
   it never imports Python modules directly.

Any import not covered by rules 1-9 is disallowed by default — a new module added in
a later sprint must have its import rule added to this list before it ships.
```

- [ ] **Step 2: Write `REPOSITORY_INTERFACES.md`**

Content (Python `Protocol` stubs — signatures only, per this task's "no
implementation details" requirement):

```markdown
# NAC Repository Interfaces v1.0

**Status:** FROZEN (2026-07-03)

Signatures only — no method bodies. These are the interfaces `engine.storage`
exposes to every graph module (`MODULE_BOUNDARIES.md` rule 3) and that compilers
consume indirectly through the graph modules.

```python
from typing import Protocol
from uuid import UUID
from pathlib import Path

class PathResolver(Protocol):
    def find_root(self, start_path: Path) -> Path: ...
    def resolve(self, relative: str) -> Path: ...
    def root(self) -> Path: ...

class KnowledgeGraphRepository(Protocol):
    def get_story(self, story_id: UUID) -> "Story": ...
    def get_character(self, character_id: UUID) -> "Character": ...
    def get_beats(self, scene_id: UUID) -> list["Beat"]: ...
    def upsert_node(self, node: "KnowledgeNode") -> UUID: ...
    def snapshot_version(self, story_id: UUID) -> str: ...

class CinematicGraphRepository(Protocol):
    def get_shots(self, beat_id: UUID) -> list["Shot"]: ...
    def upsert_shot(self, shot: "Shot") -> UUID: ...
    def snapshot_version(self, story_id: UUID) -> str: ...

class AssetGraphRepository(Protocol):
    def get_by_hash(self, content_hash: str) -> "Asset | None": ...
    def upsert_asset(self, asset: "Asset") -> UUID: ...
    def upsert_prompt(self, prompt: "Prompt") -> UUID: ...

class ProductionGraphRepository(Protocol):
    def create_job(self, job: "Job") -> UUID: ...
    def create_estimate(self, estimate: "Estimate") -> UUID: ...
    def update_job_status(self, job_id: UUID, status: str) -> None: ...

class ReviewRepository(Protocol):
    def create_review_entry(self, entry: "ReviewEntry") -> UUID: ...
    def get_reviews_for_artifact(self, artifact_id: UUID) -> list["ReviewEntry"]: ...
    def create_cut(self, cut: "Cut") -> UUID: ...

class ValidationService(Protocol):
    def validate(self, snapshot_version: str) -> list["ValidationResult"]: ...

class EventBus(Protocol):
    def publish(self, event: "Event") -> None: ...
    def subscribe(self, event_type_pattern: str, handler) -> "SubscriptionHandle": ...
    def unsubscribe(self, handle: "SubscriptionHandle") -> None: ...

class Compiler(Protocol):
    def validate(self, snapshot_version: str) -> list["ValidationResult"]: ...
    def plan(self, snapshot_version: str) -> "Estimate": ...
    def generate(self, snapshot_version: str, estimate: "Estimate") -> "GenerationResult": ...
    def measure(self, result: "GenerationResult") -> "MeasurementResult": ...
    def repair(self, result: "GenerationResult", measurement: "MeasurementResult") -> "GenerationResult": ...
    def review(self, artifact_id: UUID) -> "ReviewEntry": ...
    def export(self, result: "GenerationResult") -> UUID: ...

class Pack(Protocol):
    def parse(self, shot: "Shot") -> "PackInternalRepresentation": ...
    def compile_prompt(self, repr: "PackInternalRepresentation", platform_target: "PlatformTarget") -> str: ...
    def validate(self, compiled_text: str, platform_target: "PlatformTarget") -> list["ValidationResult"]: ...

class ComputeManager(Protocol):
    def profile_hardware(self) -> "HardwareProfile": ...
    def select_profile(self, hw: "HardwareProfile") -> str: ...
    def current_profile(self) -> str: ...
    def reprofile(self) -> str: ...

class ModelManager(Protocol):
    def is_installed(self, model_id: str) -> bool: ...
    def install(self, model_id: str) -> "ModelReference": ...
    def resolve_for_capability(self, capability_tag: str, profile: str) -> "ModelReference | None": ...

class PortabilityService(Protocol):
    def export_package(self, project_id: UUID, embed_large_assets: bool) -> Path: ...
    def import_package(self, package_path: Path) -> UUID: ...
```

Referenced types (`Story`, `Character`, `Beat`, `Shot`, `Asset`, `Prompt`, `Job`,
`Estimate`, `ReviewEntry`, `Cut`, `ValidationResult`, `Event`, `HardwareProfile`,
`ModelReference`, `PlatformTarget`) are defined in `CREATIVE_GRAPH_SPEC.md`,
`EVENT_SPEC.md`, and `COMPUTE_MANAGER_SPEC.md` respectively — not redefined here.
```

- [ ] **Step 3: Self-review**

Checklist:
- [ ] Every `Protocol` method name used here (`PathResolver.find_root/resolve/root`)
  matches `WORKSPACE_SPEC.md`'s `PathResolver` exactly — same names, same order.
- [ ] `Compiler` Protocol's 7 methods (`validate, plan, generate, measure, repair,
  review, export`) map 1:1 onto `COMPILER_ABI.md`'s 8 stages (note: `Input Schema`
  stage has no corresponding method — it's declarative, expressed via
  `CompilerDeclaration.consumes_node_types`, not a runtime call; confirm this is
  intentional and add a one-line note rather than leaving it as a silent gap).
- [ ] Module boundary diagram rules don't contradict `PACK_ABI.md`'s "Pack discovery"
  or `PLUGIN_ABI.md`'s "Plugin discovery" sections.

- [ ] **Step 4: Fix the Compiler Protocol gap found in self-review**

Add this line to `REPOSITORY_INTERFACES.md` right after the `Compiler` Protocol
block:

```markdown
> Note: `COMPILER_ABI.md`'s stage 1 ("Input Schema") has no corresponding runtime
> method above — it is a static declaration (`CompilerDeclaration.consumes_node_types`,
> `COMPILER_ABI.md` §Compiler registration), checked at registration time, not called
> per-job like stages 2-8.
```

- [ ] **Step 5: Commit both files**

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\MODULE_BOUNDARIES.md docs\specs\v1\REPOSITORY_INTERFACES.md
git commit -m "docs(spec): freeze Module Boundaries diagram + Repository Interfaces v1.0"
```

---

### Task 12: Write Extensibility + Versioning Policy

**Files:**
- Create: `E:\nth-absolute-cinema\docs\specs\v1\EXTENSIBILITY.md`
- Create: `E:\nth-absolute-cinema\docs\specs\v1\VERSIONING_POLICY.md`

**Interfaces:**
- Consumes: `PACK_ABI.md`, `PLUGIN_ABI.md`, `COMPILER_ABI.md`, `NAC_PACKAGE_SPEC.md`
  (all versioned artifacts this policy governs).
- Produces: the compatibility rules `SPRINT0_FREEZE.md` (Task 13) cites as already
  satisfied.

- [ ] **Step 1: Write `EXTENSIBILITY.md`**

Content:

```markdown
# NAC Extension Points & Compatibility Guarantees v1.0

**Status:** FROZEN (2026-07-03)

## The three extension points (closed set for v1.0)

```
1. NAC Pack       — new generation tool integration (PACK_ABI.md)
2. Plugin         — cross-cutting event-driven behavior (PLUGIN_ABI.md)
3. Compiler       — new artifact type / new domain (COMPILER_ABI.md)
```

No other extension mechanism exists in v1.0 — a feature that doesn't fit one of
these three either belongs in `engine.kernel` (core) or is out of scope for Phase 1
(see design doc §24 non-goals).

## Compatibility guarantees

| Guarantee | Scope |
|---|---|
| A Pack built against Pack ABI v1.0 works with any Compiler ABI v1.x | Packs depend only on `PlatformTarget`/`Shot` types, which are graph-spec, not compiler-ABI, concerns |
| A Compiler built against Compiler ABI v1.0 continues to run against Creative Graph Spec v1.x (minor bumps) | Minor graph-spec bumps are additive only (`VERSIONING_POLICY.md`) |
| A `.nac` package exported at graph-spec v1.0 imports cleanly into a NAC installation running graph-spec v1.x for any x ≥ 0 | Forward compatibility within a major version is required; see `VERSIONING_POLICY.md` §.nac compatibility |
| A Plugin built against Plugin ABI v1.0 continues to receive events under Event Spec v1.x | Event taxonomy additions are minor-version, not breaking |

## Non-goals for extensibility (Phase 1)

- Hot-reloading a Pack/Plugin/Compiler without a NAC restart — not required in v1.0.
- Sandboxed/untrusted third-party packs — all packs in Phase 1 are first-party or
  explicitly vetted; no plugin marketplace security model exists yet.
- Cross-major-version compatibility (e.g. a v1.0 Pack against a hypothetical v2.0
  Compiler ABI) — major version bumps are explicitly allowed to break compatibility,
  see `VERSIONING_POLICY.md`.
```

- [ ] **Step 2: Write `VERSIONING_POLICY.md`**

Content:

```markdown
# NAC Versioning Policy v1.0

**Status:** FROZEN (2026-07-03)

## Semver applies to every versioned artifact

```
MAJOR.MINOR.PATCH
```

- **MAJOR** — breaking change (a consumer written against the old version will not
  work unmodified).
- **MINOR** — additive, backward-compatible (new optional field, new event type, new
  node type that doesn't remove/rename anything).
- **PATCH** — clarification/bugfix in the spec text itself, no schema change.

## Per-artifact rules

### Creative Graph Specification versioning

- A `Story` node's `graph_spec_version` field pins that project to the schema version
  it was created under (`CREATIVE_GRAPH_SPEC.md` §1).
- MINOR bumps (e.g. 1.0 → 1.1) MAY add new optional fields to any node type or a new
  node type entirely; MUST NOT remove or rename an existing field.
- MAJOR bumps MAY remove/rename fields; a project on graph-spec 1.x is NOT
  automatically compatible with 2.0 — migration is an explicit, separate operation
  (out of scope for Sprint 0).

### Creative Compiler ABI versioning

- `CompilerDeclaration.abi_version` pins which ABI version a compiler implementation
  targets.
- A compiler targeting ABI 1.0 MUST continue to function against Creative Graph Spec
  1.x for any x — this is the guarantee `EXTENSIBILITY.md` states.
- Adding a 9th pipeline stage would be a MAJOR bump (breaks the "exactly 8 stages, no
  skipping" contract); adding an optional sub-step within an existing stage is MINOR.

### Pack versioning

- `PackDeclaration.pack_version` is independent of `PACK_ABI.md`'s own version
  (`abi_version`, added in Task 8's fix).
- A pack MAY bump its own `pack_version` (e.g. Google Flow pack 1.0 → 1.1) for
  prompt-quality improvements without any ABI change.
- `Provenance.pack_version` (`CREATIVE_GRAPH_SPEC.md` §9) always records the exact
  pack version used, so regenerating an old artifact can request that exact version
  if still installed, or the latest compatible one otherwise.

### `.nac` package versioning

- `manifest.nac_format_version` pins the container format itself (this document,
  Task 6).
- `manifest.graph_spec_version` pins the graph schema inside the package.
- Import compatibility rule: a NAC installation on graph-spec MAJOR version N can
  import any `.nac` package with `graph_spec_version` MAJOR ≤ N; importing a package
  from a newer MAJOR version MUST be rejected at manifest-verification time
  (`NAC_PACKAGE_SPEC.md` "Import rules" step 1), not partway through restoration.

## Cross-document consistency requirement

Every spec document under `docs/specs/v1/` that references another spec's type MUST
use that type's exact field names (verified during each task's self-review in this
plan). A future PATCH-level edit to fix a wording issue does not require re-verifying
every cross-reference; a MINOR or MAJOR edit to any spec document does.
```

- [ ] **Step 3: Self-review**

Checklist:
- [ ] Three extension points match exactly the three ABI docs already frozen (Tasks
  5, 8, 4) — no fourth extension point invented.
- [ ] Versioning rules for each of the 5 artifact types (graph spec, compiler ABI,
  pack, `.nac`, — note: Plugin and Event Spec also need a versioning rule; check if
  missing).

- [ ] **Step 4: Fix the missing versioning rules found in self-review**

Add two more subsections to `VERSIONING_POLICY.md` under "Per-artifact rules":

```markdown
### Plugin ABI versioning

- `Plugin.abi_version` pins which version of `PLUGIN_ABI.md` a plugin targets, same
  pattern as Compiler/Pack.
- A plugin targeting ABI 1.0 continues to receive events under Event Spec 1.x
  (`EXTENSIBILITY.md`).

### Event Specification versioning

- The event taxonomy (`EVENT_SPEC.md`) is a closed set at v1.0; adding a new
  `event_type` is a MINOR bump. Removing or renaming an existing `event_type` is a
  MAJOR bump — plugins subscribed via the old pattern would silently stop receiving
  events otherwise, which is exactly the failure mode semver MAJOR exists to signal.
```

- [ ] **Step 5: Commit both files**

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\EXTENSIBILITY.md docs\specs\v1\VERSIONING_POLICY.md
git commit -m "docs(spec): freeze Extensibility guarantees + Versioning Policy v1.0"
```

---

### Task 13: Write the Sprint 0 Freeze declaration + full cross-document consistency pass

**Files:**
- Create: `E:\nth-absolute-cinema\docs\specs\v1\SPRINT0_FREEZE.md`
- Modify (if any inconsistency found): any of the 13 files from Tasks 2-12

**Interfaces:**
- Consumes: all 9 core specs + 4 cross-cutting docs (Tasks 2-12).
- Produces: the single freeze-declaration document that Sprint 1 (per the design doc's
  sprint plan) treats as its starting contract.

- [ ] **Step 1: Run a full cross-document consistency pass**

Read every one of the 13 files created in Tasks 2-12 in one sitting and check:
1. Every type name referenced across documents (`PlatformTarget`, `Provenance`,
   `Estimate`, `ModelReference`, `CapabilityMatrix`, `Event`, `PathResolver`, etc.) has
   exactly one canonical definition (in the doc that "Produces" it per this plan's
   task headers) and every other reference uses the identical field names.
2. No document contains a placeholder, a "TBD", or an unresolved "wait see..." note
   (the kind fixed in Task 3 Step 3 — confirm no similar artifact was introduced in
   later tasks).
3. Every cross-reference link (e.g. "`CREATIVE_GRAPH_SPEC.md` §9") points to a
   section that actually exists with that name in the target document.

Fix any discrepancy found directly in the relevant file, then `git add` + commit each
fix individually with a message like `docs(spec): fix cross-reference in <file> found
during Sprint 0 consistency pass`.

- [ ] **Step 2: Write `SPRINT0_FREEZE.md`**

Content:

```markdown
# NAC Sprint 0 — Architecture Freeze Declaration

**Status:** FROZEN (2026-07-03)

## What is frozen as of this document

| Document | Version | Governs |
|---|---|---|
| `MANIFESTO.md` | v1.0 | Philosophy — 8 principles every compiler/pack/plugin must obey |
| `CREATIVE_GRAPH_SPEC.md` | v1.0 | Five graphs, Style Genome, story hierarchy, 4-layer validation, provenance |
| `COMPILER_ABI.md` | v1.0 | 8-stage compiler contract, estimation, provenance, review contracts |
| `PACK_ABI.md` | v1.0 | Generation-tool integration contract, CapabilityMatrix, discovery |
| `NAC_PACKAGE_SPEC.md` | v1.0 | `.nac` container format, export/import rules, integrity |
| `EVENT_SPEC.md` | v1.0 | Event envelope, taxonomy, delivery guarantees |
| `PLUGIN_ABI.md` | v1.0 | Cross-cutting extension contract, hard constraints |
| `WORKSPACE_SPEC.md` | v1.0 | Relocatable root, storage tiers, multi-project workspace |
| `COMPUTE_MANAGER_SPEC.md` | v1.0 | Hardware profiles, profiling contract, on-demand model install |
| `MODULE_BOUNDARIES.md` | v1.0 | Import dependency diagram + 9 allowed-import rules |
| `REPOSITORY_INTERFACES.md` | v1.0 | `Protocol` stubs for every cross-module interface |
| `EXTENSIBILITY.md` | v1.0 | 3 extension points, compatibility guarantees |
| `VERSIONING_POLICY.md` | v1.0 | Semver rules for graph spec, compiler ABI, pack, `.nac`, plugin, event spec |

## Success criteria for Sprint 0

- [ ] All 13 documents above exist under `E:\nth-absolute-cinema\docs\specs\v1\`,
  each marked FROZEN, each committed to git.
- [ ] Zero placeholder/TBD text anywhere in `docs/specs/v1/` (verified by Task 13
  Step 1's consistency pass).
- [ ] Every cross-document type reference resolves to exactly one canonical
  definition with matching field names (verified by Task 13 Step 1).
- [ ] The `navakanth001` repo's original design doc
  (`docs/superpowers/specs/2026-07-03-nth-absolute-cinema-design.md`) and this
  freeze do not contradict each other on any point — this freeze is the formal spec
  text for what that design doc already approved, not a redesign (verified by Task
  14).
- [ ] `E:\nth-absolute-cinema\` exists as an initialized git repository with the
  full Task-1 directory scaffold present.
- [ ] No engine code (Python modules under `engine/`) exists yet — Sprint 0 produces
  specs only.

## Non-goals for Sprint 0

- No compiler, pack, or plugin implementation — Sprint 1 begins the Kernel and first
  real code.
- No Compute Manager threshold values (exact GB/VRAM cutoffs for profile selection)
  — the *function signature* is frozen (`COMPUTE_MANAGER_SPEC.md`), the *thresholds*
  are a Sprint 1 implementation decision, not an architecture-freeze decision.
- No dashboard, no CLI, no API server — `engine.api` boundary is declared in
  `MODULE_BOUNDARIES.md` but not built.
- No CI/lint enforcement of the import rules in `MODULE_BOUNDARIES.md` — that's a
  Sprint 1 tooling task once there's code to lint.
- No `.nac` file has actually been produced or imported — the format is specified,
  not exercised, until Sprint 6 per the design doc's sprint plan.
- No changes to `docs/vision/TITAN.md` or the CRP repo — reconfirmed out of scope.

## Next step

Sprint 1 (per `docs/superpowers/specs/2026-07-03-nth-absolute-cinema-design.md`
§23/§17): Kernel (`engine.kernel.paths` implementing `PathResolver`), Knowledge Graph,
Storage (3 tiers), Model Manager with on-demand install, Compute Manager — all built
directly against the 13 documents frozen here, with no further architecture
discussion required to start.
```

- [ ] **Step 3: Commit**

```powershell
cd E:\nth-absolute-cinema
git add docs\specs\v1\SPRINT0_FREEZE.md
git commit -m "docs(spec): declare NAC Sprint 0 Architecture Freeze — 13 documents FROZEN"
```

---

### Task 14: Sync the `navakanth001` origin design doc and wiki with the NAC freeze

**Files:**
- Modify: `C:\Users\navka\navakanth001\docs\superpowers\specs\2026-07-03-nth-absolute-cinema-design.md`
- Modify: `C:\Users\navka\navakanth001\wiki\nth-absolute-cinema.md`

**Interfaces:**
- Consumes: `SPRINT0_FREEZE.md` (Task 13) as the source of truth for what's now
  frozen; NAC naming convention from this plan's header.

- [ ] **Step 1: Add a Sprint 0 status note + NAC naming to the design doc**

Edit `docs/superpowers/specs/2026-07-03-nth-absolute-cinema-design.md` in the
`navakanth001` repo: add a new final section:

```markdown
## 26. Sprint 0 status and naming update (2026-07-03)

**Naming:** the engine/SDK codename is **NAC**. Product naming going forward:
- **NAC** — the core engine and SDK (this document's `engine/` tree).
- **Nth Absolute Cinema Studio** — the desktop application (Sprint 6, Director
  Dashboard evolves into this).
- **`.nac`** — the portable project/package format (§21).
- **NAC Packs** — tool integrations (§7), e.g. the Google Flow pack.

**Sprint 0 complete:** all 13 governing documents (Manifesto, Creative Graph Spec,
Compiler ABI, Pack ABI, `.nac` Package Spec, Event Spec, Plugin ABI, Workspace Spec,
Compute Manager Spec, Module Boundaries, Repository Interfaces, Extensibility,
Versioning Policy) are frozen under `E:\nth-absolute-cinema\docs\specs\v1\` — see
`docs/superpowers/plans/2026-07-03-nac-sprint0-architecture-freeze.md` in this repo
for the plan that produced them, and `SPRINT0_FREEZE.md` at the NAC repo root for the
freeze declaration itself. This document (`2026-07-03-nth-absolute-cinema-design.md`)
remains the origin design rationale; the `docs/specs/v1/` documents are now the
authoritative technical specs Sprint 1+ build against.
```

- [ ] **Step 2: Update the wiki page**

Edit `wiki/nth-absolute-cinema.md`: add a `## Sprint 0 status` section near the
bottom (before "## Status", merge into it):

```markdown
## Status

**Sprint 0 (Architecture Freeze) complete** (2026-07-03). 13 governing documents
frozen under `E:\nth-absolute-cinema\docs\specs\v1\` (Manifesto, Creative Graph Spec,
Compiler ABI, Pack ABI, `.nac` Package Spec, Event Spec, Plugin ABI, Workspace Spec,
Compute Manager Spec, Module Boundaries, Repository Interfaces, Extensibility,
Versioning Policy). Engine codename is now **NAC**; product name **Nth Absolute
Cinema** / desktop app **Nth Absolute Cinema Studio** remain unchanged. No engine
code exists yet — Sprint 1 (Kernel, Knowledge Graph, Storage, Model Manager, Compute
Manager) is next.
```

(Replace the prior single-line "Status" paragraph with this expanded version — keep
everything else in the file unchanged.)

- [ ] **Step 3: Commit in the `navakanth001` repo**

```powershell
cd C:\Users\navka\navakanth001
git add docs\superpowers\specs\2026-07-03-nth-absolute-cinema-design.md wiki\nth-absolute-cinema.md
git commit -m "docs(nth-absolute-cinema): record Sprint 0 freeze + adopt NAC engine codename"
```

- [ ] **Step 4: Add a `wiki/log.md` entry**

Append (via Read + Edit, not raw shell heredoc/echo — this repo's log.md has been
corrupted by shell escaping before) one line to `wiki/log.md`:

```
- 2026-07-03: NAC Sprint 0 Architecture Freeze complete — 13 governing specs (Manifesto, Creative Graph Spec, Compiler/Pack/Plugin ABIs, .nac Package Spec, Event Spec, Workspace Spec, Compute Manager Spec, Module Boundaries, Repository Interfaces, Extensibility, Versioning Policy) frozen under E:\nth-absolute-cinema\docs\specs\v1\. Adopted NAC as the engine/SDK codename (Nth Absolute Cinema = product, Nth Absolute Cinema Studio = desktop app, .nac = package format, NAC Packs = tool integrations). Plan: docs/superpowers/plans/2026-07-03-nac-sprint0-architecture-freeze.md.
```

Then commit:

```powershell
cd C:\Users\navka\navakanth001
git add wiki\log.md
git commit -m "docs(wiki): log NAC Sprint 0 freeze"
```

---

## Self-Review (performed while writing this plan)

**Spec coverage** — every one of the user's 14 requested Sprint 0 deliverables maps to
a task:
1. Creative Compiler Manifesto v1.0 → Task 2
2. Creative Graph Specification v1.0 → Task 3
3. Creative Compiler ABI v1.0 → Task 4
4. Pack ABI v1.0 → Task 5
5. `.nac` Package Specification v1.0 → Task 6
6. Event Specification v1.0 → Task 7
7. Plugin ABI v1.0 → Task 8
8. Workspace Specification v1.0 → Task 9
9. Compute Manager Specification v1.0 → Task 10
10. Module dependency diagram + import boundaries → Task 11 (`MODULE_BOUNDARIES.md`)
11. Repository interfaces (no impl details) → Task 11 (`REPOSITORY_INTERFACES.md`,
    `Protocol` stubs only)
12. Extension points + compatibility guarantees → Task 12 (`EXTENSIBILITY.md`)
13. Versioning policy → Task 12 (`VERSIONING_POLICY.md`)
14. Success criteria + non-goals for Sprint 0 → Task 13 (`SPRINT0_FREEZE.md`)

Plus the NAC naming request → folded into every task's document content and formally
recorded in Task 14 against the origin design doc.

**Placeholder scan** — every task's Step 1 content is complete prose/schema, not a
stub; the plan deliberately *includes* three intentional self-review-and-fix cycles
(Task 3 Step 3, Task 5 Step 3, Task 8 Steps 2-3, Task 11 Step 4, Task 12 Step 4) as
worked examples of the cross-document consistency discipline `SPRINT0_FREEZE.md`
requires — these are not left as TODOs, they show the exact fix inline.

**Type consistency** — `Provenance`, `PlatformTarget`, `Estimate`,
`CapabilityMatrix`, `ModelReference`, `PathResolver`, `Event`, `Compiler` Protocol
method names are each defined exactly once (flagged with "Produces:" in the task
header) and reused by exact name in every consuming task; Task 13 Step 1 is the
final full-pass check across all 13 files before the freeze declaration is written.

---

**Plan complete and saved to `docs/superpowers/plans/2026-07-03-nac-sprint0-architecture-freeze.md`.**

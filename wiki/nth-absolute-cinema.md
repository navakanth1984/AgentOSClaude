# Nth Absolute Cinema

AI filmmaking Creative Operating System. Phase 1 goal: idea → finished 15-20 minute
short film, built as a compilation problem (`Idea → Knowledge → Creative Graphs →
Domain Compilers → Assets`), not a prompting workflow.

## Location
- **Code/data root:** `E:\nth-absolute-cinema\` — external SSD, chosen from project
  start so the whole project is portable (copy the directory or move the SSD to
  another machine and keep working, no hardcoded absolute paths).
- **Design doc (in this repo's git history):**
  [`docs/superpowers/specs/2026-07-03-nth-absolute-cinema-design.md`](../docs/superpowers/specs/2026-07-03-nth-absolute-cinema-design.md)
- Not staged under `navakanth001` — its cache/render/asset storage tiers are large and
  drive-portability is a first-class requirement, unlike the usual staging-workshop
  pattern used for other in-progress projects here (e.g. `nth-brain` before it
  graduated to its own repo).

## Relationship to CRP / TITAN
Deliberately **separate** from `docs/vision/TITAN.md` (CRP's north-star doc). TITAN's
mission is a quantum-inspired adaptive runtime for AI-workload representations — a
filmmaking platform doesn't fit that RFC-gated mission. Nth Absolute Cinema may call
CRP as an execution substrate later (same relationship CRP has to TITAN), but
`docs/vision/TITAN.md` is not modified by this project.

## Architecture (frozen, additive changes only past this point)
- **Five graphs per project:** Knowledge, Cinematic, Asset, Production, Review.
- **Creative Compiler Framework:** every compiler (Screenplay, Novel, Audio, Prompt,
  Storyboard, Motion Poster, Teaser, Trailer) implements
  `Input Schema → Validation → Planning → Generation → Measurement → Repair → Review → Export`,
  mirroring CRP's own compiler discipline.
- **Style Genome** (not "DNA"): Character/Visual/Dialogue/Music/Editing/Camera/
  Lighting/Costume/Environment genomes, referenced for consistency.
- **Aspect-ratio-native generation:** each shot generates one native prompt per target
  platform aspect ratio (9:16 Reels/Shorts, 16:9 YouTube, 1:1/4:5 LinkedIn, etc.) —
  cropping a single master render is an explicit anti-pattern.
- **Portability:** relocatable project root (`engine.kernel.paths` resolver, no
  hardcoded absolute paths), Compute Manager auto-selects a hardware execution profile
  (Micro/Standard/Pro/Studio ≈ Laptop/Gaming PC/Studio Workstation/Cloud), Model
  Manager installs local models on demand rather than requiring a full bundle upfront.
- **Storage tiers:** cache (regeneratable, never exported) / project (authoritative:
  graphs, genomes, provenance) / archive (cold storage, exported packages).
- **`.nac` portable project package:** exports the five graphs, genomes, provenance,
  prompts, review history, and asset references; on import, Compute Manager profiles
  the destination machine and Model Manager installs only the models actually needed —
  full reproducibility via provenance without requiring a full asset/model bundle.

## Governing documents (frozen before Sprint 1)
1. Creative Compiler Manifesto v1.0 — 8 principles (single source of truth, compiled
   not authored, humans direct AI proposes, reproducibility via provenance,
   offline-first, quality over speed, economics as first-class objective, full
   traceability).
2. Creative Graph Specification v1.0 — technical schema for all five graphs, Style
   Genome, four-layer validation, compiler contract, provenance, aspect-ratio schema,
   path-resolver contract, execution-profile schema, `.nac` manifest schema.

## Status

**Sprint 0 (Architecture Freeze) complete** (2026-07-03). 14 governing documents
frozen under `E:\nth-absolute-cinema\docs\specs\v1\` (Manifesto, Creative Graph Spec,
Compiler ABI, Pack ABI, `.nac` Package Spec, Event Spec, Plugin ABI, Workspace Spec,
Compute Manager Spec, Module Boundaries, Repository Interfaces, Extensibility,
Versioning Policy, and the Sprint 0.5 Architecture Validation gate). Sprint 0.5
validation passed all 8 architecture-guarantee questions (replay, traceability, tool
extensibility, machine portability, offline operation, generation reproducibility,
independent compiler replacement, independent graph evolution) before the freeze was
declared. Engine codename is now **NAC**; product name **Nth Absolute Cinema** /
desktop app **Nth Absolute Cinema Studio** remain unchanged. No engine code exists
yet — Sprint 1 (Kernel, Knowledge Graph, Storage, Model Manager, Compute Manager) is
next.

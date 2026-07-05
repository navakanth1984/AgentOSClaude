# NAC — Roadmap

What comes next, in order. See [CURRENT.md](CURRENT.md) for gate status (this roadmap assumes the Production Readiness Gate is the current blocker) and [DECISIONS.md](DECISIONS.md) for why it's sequenced this way (ADR-007).

## Immediate: close out Provider Orchestration

1. Update `ELEVENLABS_API_KEY` in `.env`, re-run `scripts/elevenlabs_smoke_test.py`
2. Live Gemini smoke test (one real Story/Screenplay generation call)
3. Live Sarvam smoke test (one real Audio synthesis call)
4. Merge `feat/provider-orchestration` into `master` (PR #3) once smoke tests pass

## Then: Director Studio UX Pass 2

Before building more backend infrastructure, improve the Director Studio into something a filmmaker would genuinely enjoy using.

### Workspace
* Better onboarding
* Guided workflow
* Progressive disclosure
* Empty states
* Helpful animations
* Keyboard shortcuts
* Drag & drop
* Better navigation

### Timeline
* Runtime ruler
* Pipeline visualization
* Department status
* Render progress
* Dependency graph

### Creative Graph
Make relationships understandable — not just nodes. Show flow, lineage, provenance.

### Providers
Diagnostics should become a live control center, displaying Gemini, OpenRouter, Ollama, ElevenLabs, Sarvam, and Mock with real status.

### Packages
Make snapshots visual. Users should understand `Project → Snapshot → .nac Package → Restore → Continue Working` without documentation.

### Storage
Visualize Local, External SSD, Azure (planned), Google (planned).

### UX Pass 2 checklist (feeds into the Gate's Definition of Done)
* UI feels intuitive
* No dead clicks
* No silent failures
* Providers report honestly
* Snapshots verified
* Packages verified
* Diagnostics complete
* Dogfooding completed
* Live provider smoke tests passed

## After the Gate passes

1. Restore Manager — deserialize a `.nac` container back into a memory-resident `Snapshot`, feed it to the Storage Manager to restore workspace files and repopulate SQLite. Disable the "Restore remains disabled in this build" UI notices once functional.
2. Migration Manager — move snapshots between storage providers: `Snapshot → Move → Verify → Register`.
3. Department Framework — build the reusable framework, not a one-off Character implementation (see [DECISIONS.md](DECISIONS.md) ADR-001).
4. Character Department — first concrete department built on the framework. Acceptance criteria: Create, Edit, Generate Character Bible, Generate Character Genome, Generate Character Visual Profile, Attach reference images, Record reviews, Approve/Reject, Version history, Regenerate selected sections, Export Character Package, SDK support, API support, Director Studio workspace, Tests, Documentation.
5. Location Department (Sprint 2C) — should not begin until every Character Department acceptance item works.
6. Scene, Beat departments — continuing the Character → Location → Scene → Beat vertical-slice order.

## Full studio model (target end state)

```
Director Studio
├── Story Department
├── Character Department
├── Location Department
├── Environment Department
├── Dialogue Department
├── Screenplay Department      (assembles from Story+Character+Location+Beats, does not invent story)
├── Cinematography Department  (Shot Graph, camera/lens/movement/blocking/lighting/color/composition/aspect ratio)
├── Music Department
├── Sound Design Department
├── Narration Department
├── Editing Department
├── Marketing Department       (Motion Poster/Posters/Teasers/Trailers/Shorts/per-platform variants/Press Kit)
├── Distribution Department    (per-target: Cinema/Netflix/Prime/YouTube/Shorts/Instagram/TikTok/Festivals)
├── Production Department      (Schedule/Budget/Credits/GPU hours/Storage/Render queue/Cost prediction)
└── AI Studio Operations       (Model Manager, Capability Registry, Provider Registry, GPU Scheduler, Cache, Sync)
```

**Production Board** (recommended, not yet built): opening a project should show department-level progress before any single stage's content — overall progress bar, checklist of departments, estimated cost/GPU/runtime/pages/assets/storage/provider/execution mode. Deferred pending Character Department scope.

## Deferred (explicitly out of scope until reopened)

* Timeline Compiler
* Per-project Provider Manifest YAML
* Full Character/Scene/Beat Knowledge Graph population beyond current node types
* Director Memory, Experience Graph, Marketplace, Cloud Sync (beyond current stubs), Credit Manager, Creative Execution Planner, Creative Confidence Scoring
* Feature-length screenplay generation via a hierarchical compiler pipeline (Story Bible → Character → Location → Act → Sequence → Scene → Beat → Screenplay Assembly) — waits for the Character/Location/Scene/Beat department pipeline; do not chunk the current monolithic `ScreenplayCompiler` as a stopgap

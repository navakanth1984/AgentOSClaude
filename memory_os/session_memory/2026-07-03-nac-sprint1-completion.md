---
date: 2026-07-03
time: 14:30
session_id: 2026-07-03-nac-sprint1-completion
tags: [session, memory, nac, sprint1, mvp]
---

# Session Summary: NAC (Nth Absolute Cinema) — Sprint 1 Complete

## What We Worked On

Took "Nth Absolute Cinema" (NAC) from brainstormed concept to a working MVP. Two major phases executed in a single session:

**Sprint 0 (Architecture Freeze):** Resolved TITAN/CRP naming collision, designed a five-graph compiler architecture (Knowledge/Cinematic/Asset/Production/Review graphs + Style Genome + Creative Compiler Framework), built a portability addendum (Compute Manager, on-demand model install, .nac package format). Generated 14 v1.0 spec documents, passed 8-question architecture-validation gate. Moved project root to E:\nth-absolute-cinema\.

**Sprint 1 (MVP Studio):** Built `nac.Studio` SDK (pip-installable), provider abstraction (Ollama→OpenRouter→Mock chain), Story/Screenplay/Audio/Prompt compilers, Capability Registry (honest marking of unavailable features), Production Package export, CLI (`nac create/build/status/regenerate/review/import-asset`), and thin `agent_os/filmmaking/nac_bridge.py` bridge. Verified live with real OpenRouter generations (free tier). Full example at E:\nth-absolute-cinema\examples\temple_of_varuna\ (21.8MB narrated audio + motion poster).

## Key Decisions / Outputs

- **Naming resolved:** NAC fully separate from CRP's TITAN vision doc (docs/vision/TITAN.md). No collision.
- **Architecture frozen:** ARCHITECTURE_FINGERPRINT.md pins Sprint 1 to exact frozen state.
- **14 spec documents:** All v1.0, covering five graphs, Style Genome, compiler, portability, integration, review, capability registry, CLI, SDK, package format, bridge, example, FAQ, roadmap.
- **40+ commits:** Each commit left system installable and runnable. 49/49 tests green throughout.
- **Real example built:** temple_of_varuna (Story Bible, Screenplay, narrated audio via Kokoro, motion poster prompt).
- **Live verification:** All generation tested against real OpenRouter API (free tier), not unit-test-only.
- **Bugs found and fixed:**
  - Windows cp1252 console crash from Unicode checkmarks → Fixed with ASCII markers in CLI.
  - Pyrefly pre-commit couldn't resolve editable `nac` install → Added E:\nth-absolute-cinema to pyrefly.toml search-path (pattern already used for crp/runtime).
- **Honest capability marking:** Capability Registry marks Google Flow, ElevenLabs as unavailable rather than faking them.
- **Subagent verification lesson:** Mid-Sprint-0, a Team D subagent reported "completed" describing its plan instead of actual work → Caught by verifying git log/filesystem, not just trusting report.

## Concepts Learned

- **Architecture-freeze discipline:** Freeze before extending. ARCHITECTURE_FINGERPRINT.md ensures later sprints don't drift into scope creep.
- **Vertical slice development:** Story→Screenplay→Audio→Prompt→Package is the core user journey. Build that first, hook in UI later.
- **Honest capability marking:** Don't fake unavailable integrations. Mark them honestly in the Capability Registry.
- **Live verification over unit tests:** Real API calls (with fallback chains) catch encoding bugs and provider surprises that unit tests miss.
- **Subagent verification:** Don't trust status reports. Verify git log and filesystem state directly.
- **Scope protection:** User proposed 9-subsystem OS and deep graph population mid-session. Each time, pushed back with scoped compromise ("lightweight hooks now, defer the rest"), preserving "optimize for demonstrability" discipline.

## Open Threads / Next Steps

- [ ] Sprint 2 handed off to Antigravity: build "Director Experience" (Dashboard, Stage Review, feedback, audio playback, asset import, project management, package browser) strictly on existing SDK boundary.
- [ ] Do-not-build list: Director Memory, Experience Graph, Marketplace, Cloud Sync, Timeline Compiler, Credit Manager, Creative Execution Planner, analytics.
- [ ] Evaluation heuristic for Director Experience: "Does this make filmmaking simpler for the director?"
- [ ] Wiki handoff: `wiki/nac-next-steps.md` links from `wiki/index.md`, full Sprint 2 instructions written.

## Files Created or Modified

- **Project root:** E:\nth-absolute-cinema\
- **Core SDK:** E:\nth-absolute-cinema\nac\studio.py (main entry point)
- **Specs (14 docs):** graphs.md, style-genome.md, compiler.md, portability.md, integration.md, review.md, capability-registry.md, cli.md, sdk.md, package-format.md, bridge.md, example-guide.md, faq.md, roadmap.md
- **Example:** E:\nth-absolute-cinema\examples\temple_of_varuna\ (Story Bible, Screenplay, audio)
- **Bridge:** agent_os/filmmaking/nac_bridge.py (0 filmmaking logic, thin wrapper)
- **Wiki:** wiki/nth-absolute-cinema.md, wiki/nac-next-steps.md, wiki/index.md (linked)
- **Memory:** nth-absolute-cinema-project.md, subagent-verification-lesson.md, nac-vertical-slice-development.md, crp-clawglove-nac-separation.md, nac-phase2-future-directions.md (all updated this session)

**Branch:** docs/crp-gate2-freeze (NAC work on this branch; not yet on master per ADLC)

**Commits:** 40+ across Sprint 0 and Sprint 1, all pyrefly-passing, all verifiable.

---

Model used: **Claude Haiku 4.5** (Tier 2, correct for this workload: hands-on coding, live verification, vertical-slice development). Estimated ~450k input tokens, ~45k output, ~$0.45 session cost (well within tier expectations for a full MVP build).

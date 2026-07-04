# NAC — Architecture Decision Log

Settled architecture, so future agents don't rediscover it mid-build. See [CURRENT.md](CURRENT.md) for live status and [nac-next-steps.md](nac-next-steps.md) for the session narratives these were extracted from.

---

### ADR-001 — Departments replace Compilers

**Status:** Accepted (2026-07-04)

**Reason:** Framing NAC's units of work as "compilers" (Character Compiler, Scene Compiler) treats generation logic as the whole deliverable. In practice every unit also needs a workspace, its own slice of the Creative Knowledge Graph, a review process, an asset library, exports, and metrics — the compiler is one of seven things, not the thing itself.

**Consequences:** Every department owns exactly seven things: Workspace, Knowledge Graph (its slice), Compiler, Review System, Asset Library, Metrics, Exporters. The Director Studio orchestrates departments; it never talks to compilers directly. "Build the Character Compiler" is the wrong framing — "stand up the Character Department" is right.

---

### ADR-002 — Character Genome composes by reference

**Status:** Accepted (2026-07-04), frozen in `docs/specs/v1/CHARACTER_GENOME_SPEC.md` v1.2

**Reason:** A genome (CharacterGenome, DialogueGenome, VisualGenome, etc.) needs to be reusable across projects (a film, its sequel, a marketing campaign) without duplication, and needs replayability — "Hanuman's VisualGenome at version 12, approved" must be pinned, not a bare UUID that could point anywhere.

**Consequences:** Genome Composition Rule (universal, not Character-specific): own only your department's data; reference any genome; never embed one; independent versioning; one owning department per genome; only the owner writes, others read the latest *approved* version. `GenomeReference = {genome_id, genome_type, version, status}` replaces bare `*_genome_ref: UUID` fields everywhere. A genome carries no `project_id` — reusability requires cost/GPU-time tracking to live in a separate `GenomeProductionRecord` keyed by `(project_id, genome_id)`, not embedded in the genome.

---

### ADR-003 — Snapshot precedes `.nac`

**Status:** Accepted (2026-07-04)

**Reason:** Serialization and compression are separate concerns from state collection. Building them together risks premature packaging complexity before the in-memory representation is even proven correct.

**Consequences:** Portability Service builds in strict phase order: Phase 1 Storage Manager (provider abstraction only, no serialization) → Phase 2 Snapshot Manager (collects Knowledge/Cinematic/Asset/Production/Review graphs + all Genome types into a memory-resident `Snapshot` object, still no serialization) → Phase 3 `.nac` Serializer/Deserializer (persists the `Snapshot`, starting as an *uncompressed* directory layout, zip compression added only after the directory-based version passes tests) → Phase 4 Restore Manager → Phase 5 Migration Manager.

---

### ADR-004 — Serializer never talks to storage

**Status:** Accepted (2026-07-04)

**Reason:** Keeping serialization (Snapshot ↔ `.nac` bytes) and storage (where those bytes live — local disk, external SSD, cloud) as separate layers means either can change independently. A serializer that reaches into `StorageProvider` directly couples file-format concerns to storage-backend concerns.

**Consequences:** `.nac` Serializer/Deserializer operates purely on in-memory `Snapshot` objects and produces/consumes a directory layout or archive. The Restore Manager is the layer that feeds a deserialized `Snapshot` back to the Storage Manager to repopulate the SQLite database and workspace files on disk — the Serializer itself has no knowledge of `StorageProvider`.

---

### ADR-005 — Cloud is optional

**Status:** Accepted (2026-07-03 → 2026-07-04)

**Reason:** NAC's Capability Registry philosophy is to never fake unavailable integrations. Azure/Google cloud storage and cloud-only providers (Google Flow, ElevenLabs before it was wired) must be honestly reported as unavailable rather than stubbed to look functional.

**Consequences:** `CloudStorage` is a stub that throws `NotImplementedError` for Azure/Google until actually implemented — never faked. `CapabilityRegistry` marks `available=False` honestly for anything not truly wired. Diagnostics report real provider status (`"unknown"` GPU name when undetectable, "Not Installed / Not Running" for absent Ollama) rather than fabricated values.

---

### ADR-006 — Local-first architecture

**Status:** Accepted (2026-07-03, reaffirmed 2026-07-04 with the Local Provider Smoke Gate)

**Reason:** Local/free paths (Ollama, MockProvider) must be proven working before any session spends real quota on cloud providers (Gemini, Sarvam, OpenRouter, ElevenLabs) — a safety-first ordering the user directed explicitly.

**Consequences:** Fallback chains resolve local-first: `Ollama → OpenRouter → MockProvider` for text generation, `ElevenLabs → Sarvam → pyttsx3` for voice (cloud-first only where local-quality TTS doesn't exist, but still with an offline `pyttsx3` floor). A `Local Provider Smoke Gate` (`tests/test_local_provider_smoke.py`, `scripts/local_provider_smoke_test.py`) must pass before any live cloud smoke test is authorized.

---

### ADR-007 — Production Gate before Character Department

**Status:** Accepted (2026-07-04)

**Reason:** NAC's history shows a repeating failure pattern: a milestone gets declared "complete" based on passing automated tests, then real bugs surface the moment a human drives it through the actual UI (Sprint 2A was declared complete three separate times before this stabilized — see Sprint 2A.1/2A.2 in [nac-next-steps.md](nac-next-steps.md)). Expanding into new departments (Character, Location, Scene, Beat) on top of an unverified Director Studio compounds that risk instead of fixing it.

**Consequences:** The [Production Readiness Gate](CURRENT.md) — with its Definition of Done, Stop Line, and Milestone Lifecycle — must PASS before Restore Manager, Migration Manager, Character Department, Department Framework expansion, or Creative Knowledge Graph Phase 2 begin. Highest-ROI work between now and Gate-pass is Director Studio UX Pass 2 and dogfooding, not new backend infrastructure.

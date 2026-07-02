# CRP Phase 0 — Plan 3/3: Experience DB + Replay + Closed Loop (Milestones 5–6)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans.

**Goal:** Persist every harness decision in a relational SQLite Experience
Database (ADR-002), prove 100% replay determinism (spec §2a), and close the
Phase 0 loop with a North-Star exit report backed by recorded evidence.

**Spec:** `docs/superpowers/specs/2026-07-02-crp-phase0-design.md` (Frozen).
**Branch:** `feat/crp-m3-m4-harness-representations` (continues; PR into `master`).

## Global constraints

- Deterministic serialization everywhere (sorted keys, canonical JSON) — R-004.
- Replay determinism: same spec + constraints + profile ⇒ byte-identical
  decision. Hard fail on any divergence.
- Telemetry event streams are evidence: stored verbatim, never normalized.
- Pyrefly must pass; frozen APIs (`crp_telemetry`, plugin protocol) unchanged.

---

### Task 1: Experience DB (`experience.py`, TDD)

Schema (SQLite, WAL off, single file `crp/experience.db` by default, path injectable):

- `runs(id INTEGER PK, recorded_at TEXT, spec_json TEXT, constraints_json TEXT,
   profile_json TEXT, chosen TEXT, decision_latency_ms REAL, dropped INTEGER,
   git_commit TEXT)`
- `scores(run_id, plugin, score)` / `rejections(run_id, plugin, reason)`
- `events(run_id, seq, timestamp_ns, kind, tensor_id, value)`

API: `ExperienceDB(path)`, `.insert_run(record, constraints, profile) -> int`,
`.get_run(run_id) -> StoredRun`, `.runs() -> list[int]`. Canonical JSON via
`json.dumps(..., sort_keys=True)`.

Tests: roundtrip insert/get; canonical JSON stable across dict ordering;
events stored verbatim in order.

### Task 2: Replay (`replay.py`, TDD)

`replay_run(db, run_id) -> ReplayResult` — rebuilds `WorkloadSpec`,
`Constraints`, `Profile` from stored JSON, calls `run_workload`, compares the
fresh `Decision` (chosen, scores, rejections) against the stored one.
`ReplayResult.deterministic: bool`, with a diff string when False.

Tests: replay of a synthetic and an embedding-search run is deterministic;
a tampered stored decision is detected as divergence.

### Task 3: Closed loop + Phase 0 exit evidence

`crp/tools/phase0_exit.py`: run both workloads under the default profile,
insert into the Experience DB, replay each run, then emit
`crp/docs/PHASE0-EXIT.md` checking every North-Star item (spec §2) against
recorded evidence, plus a ledger entry (`subject: "phase0-exit"`).
Full pytest suite + pyrefly green; commit, push, PR update.

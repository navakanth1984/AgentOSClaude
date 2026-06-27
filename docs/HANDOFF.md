# Handoff — Speech Subsystem (for Antigravity)

This is a cold-start brief. Read `docs/ARCHITECTURE_STATUS.md` and `docs/BASELINE.md`
first — they are the source of truth. This file says what's done, what's next, and
the traps to avoid.

## Where things are

- Branch: `milestone/v1.1.0`. Tag `v1.1.0` = first production backend.
- Recent commits (newest first):
  - `815657e5` ORT intra×workers thread matrix (Baseline 4) + `ort_intra_threads` knob
  - `ac47b025` worker scaling study (Baseline 3) + sweep aggregator
  - `d1020392` deterministic benchmark harness (BenchmarkParser + corpus generator)
  - `743898d4` Speech Execution Framework V1.1 (architecture frozen)
- The repo working tree has unrelated churn outside `agent_os/speech/**`, `tools/**`,
  `docs/**`, `corpus/**`, `benchmark_results/**`. **Do not stage it.** Keep commits
  scoped to the speech subsystem.

## Architecture is FROZEN (extend, don't change)

Per `docs/ARCHITECTURE_STATUS.md`, these are contracts; changing them needs an ADR:
DAG, `Stage.run(context, inputs) -> dict`, artifact schemas (`models.py`,
`performance_profile` v1.0, `context_manifest` v1.0), fingerprinting (enums → `.value`,
no `str(obj)` fallback — it raises `TypeError`). Typed objects cross every cache
boundary via `ensure_parse_result` / `ensure_speech_chunks` / `ensure_execution_plan`.

The pipeline is: Normalize → Parse → Segment → Context → Route → Synthesize → Trim → Merge.

## Hard-won gotchas (READ THESE)

1. **Pre-commit pyrefly hook is strict.** Every staged `.py` must type-check or the
   commit is blocked. Do NOT `--no-verify`. Common fixes already used: give
   `dict.get()` of required fields a default; coerce `float(...)` before comparisons;
   `Optional[...]` for `=None` params; for genuinely-optional imports (`fitz`, `docx`)
   use `# type: ignore`. The interpreter path in `pyrefly.toml` was stale (pointed at a
   nonexistent 3.13); it now points at the real 3.12 — leave it.
2. **Never edit benchmark runner/engine code while a sweep is running.** Each grid
   point is a separate `python` process; mid-run edits make points non-comparable.
   Freeze experiment code; only evolve aggregators/docs during a run.
3. `corpus_output_bench/` is generated output — never commit it. `*.wav` and
   `__pycache__/` are gitignored.
4. `parser="benchmark"` (BenchmarkParser) is offline/deterministic — no API key. The
   production Gemini parser needs `GEMINI_API_KEY` and is non-deterministic; never use
   it for benchmarks. Keep that boundary.
5. Write files as UTF-8 with LF. (Historical: an external tool corrupted `wiki/log.md`
   via UTF-16 — avoid that.)

## Empirical results to respect (don't re-chase)

`BASELINE.md` Baselines 3–4 (medium corpus, 12 logical cores, CPU):
- Worker scaling is strongly sublinear; w8 ≈ 1.87× w1 at 23% efficiency.
- **Negative result:** partitioning a fixed 12-thread budget (`ort_intra_threads`)
  does NOT beat unconstrained workers. Throughput tracks worker count; peak RSS tracks
  worker count. The `ort_intra_threads` knob is a weak throughput lever — its value is
  capping per-chunk latency / a small RAM trim, not speed.
- Don't build auto-tuning around thread partitioning. Trade worker count vs RAM per
  deployment profile (memory→w2, balanced→w4×i3, throughput→w6×i2≈w8).

## Next steps (ordered)

### A. Cheap cleanups now safe (runner no longer frozen)
1. **#1** Extract `KokoroEngine._rebuild_session(intra, inter, providers)` so the
   post-construction session swap in `warmup()` reads as intentional
   (`agent_os/speech/engines/kokoro_engine.py`).
2. **#5** Add `benchmark.schema_version` (and **#3** `protocol_version` +
   `measurement: {cache, warmup, provider}`) to the `benchmark` block in
   `tools/run_full_benchmark.py`; have aggregators refuse mismatched schema versions.
3. **#2** Enrich `benchmark.ort` with `estimated_total_threads`, `logical_cpus`,
   `oversubscription_ratio` so aggregators don't recompute.

### B. Phase 2 — highest value (additive; no ADR for the first two)
4. **Asset Manifest** (`assets_manifest.json`): canonical asset descriptor — engine
   name/version, `model_sha256`, `voice_pack_sha256`, voice count, provider,
   sample_rate. The performance profile should reference it (`"asset_manifest": "..."`),
   not duplicate the values. Highest-value reproducibility win. `model_sha256` is
   already computed in the profile environment block — reuse that logic.
5. **Doctor++** (`agent_os/cli.py`): add model checksum, engine version, languages,
   sample rate, and a measured-recommendation hint (see #6).
6. **#4 Recommendation block, hardware-fingerprinted.** Emit
   `{workers, ort_intra_threads, confidence, environment_hash}` from the benchmark;
   `doctor`/engine init may suggest it ONLY when the hardware fingerprint matches.
   Do NOT bake `recommended_workers` into `EngineCapabilities` globally — a number
   measured on a 12-core box must not become "truth" elsewhere.
7. **EngineRegistry** (`agent_os/speech/engines/registry.py`): thin config→engine
   resolver. Engine is already injected via `config["tts_engine"]`, so no stage change.

### C. Phase 2 — needs ADRs (touch frozen contracts)
8. Formalize the `TTSEngine` Protocol to include `get_capabilities`,
   `supports_language`, `supports_voice` (Kokoro already implements `get_capabilities`).
9. Extract `VoiceManager` from `route.py`'s `VoiceAssignmentPolicy`.
10. `warmup(profile="minimal"|"representative")` — representative uses ~median chunk
    length to fold the ~11 s first-chunk shape-specialization cost into warmup.

### D. Phase 3 — GATED (do not build speculatively)
- Second engine (Piper is the cleanest offline candidate) → THEN capability-based
  routing/fallback earns its keep. Until then it's YAGNI.

### Defer / sandbox only (until a forcing function exists)
- **Voice blending** — experimental sandbox, never touches production DAG, never
  overwrites official voices; treat interpolation claims as unverified.
- **Download manager / offline provisioning** — only when CI provisioning needs it.
- **Advanced routing (cost/latency/fallback)** — needs ≥2 engines first.

## Useful commands

```bash
# Generate deterministic corpora (smoke/medium/large)
python tools/generate_benchmark_corpus.py --all

# Full-pipeline benchmark (offline, deterministic parser)
python tools/run_full_benchmark.py --tier medium --workers 4 --ort-intra 3 --engine kokoro

# Aggregate studies into derived artifacts (benchmark_results/)
python tools/aggregate_sweep.py  --tier medium --engine kokoro --workers 1,2,4,8
python tools/aggregate_matrix.py --tier medium --engine kokoro --grid 2:6,4:3,6:2,12:1 --baselines 2,8

# Health check (real Kokoro)
python -m agent_os doctor speech

# Regression tests (offline, no model needed except where noted)
python test_warm_cache.py && python test_route_cache_key.py && python test_performance_profile.py
```

## Definition of done for V1.2

Pipeline contracts unchanged; offline-capable; reproducible benchmarks; asset manifest
emitted per run; doctor reports full diagnostics; recommendation is hardware-fingerprinted
(not a global default); every new `.py` passes the pyrefly hook; new behavior covered by
a regression test. Then tag `v1.2.0`.

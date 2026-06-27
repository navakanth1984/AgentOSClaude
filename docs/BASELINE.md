# Performance Baseline

This document records the **first production-backend baseline** and serves as the
comparison point for all future optimizations. Do not edit historical entries;
append new baselines as separate sections.

---

## Baseline 1 — V1.1 Smoke (CPU)

**Benchmark Tier:** Smoke (correctness / cold-start / cache behavior — **not** throughput)

> ⚠️ The input parses to a **single chunk**, so this baseline does **not** measure
> scheduling, work distribution, contention, or thread scaling. A medium-tier
> corpus (50–100 chunks) is required before the `1→2→4→8` worker sweep.

### Environment

| Field | Value |
|---|---|
| Date | 2026-06-27 |
| Git commit | `7839ed45917d82c8218423eb0f9f0fa90cceadc3` |
| Engine | Kokoro ONNX v0.19 |
| Provider | `CPUExecutionProvider` |
| Model SHA-256 | `dece567789190ebe987bd245d95c09d5ac86de28ff0c325c2e3faaf3de04442c` |
| Python | 3.12.10 |
| onnxruntime | 1.27.0 |
| OS | Windows 11 (10.0.26200) |
| CPU | AMD64 Family 25 Model 80 (AuthenticAMD) |
| Workers | 2 |
| Session | single shared ONNX session |
| Input | `corpus/chapter_1.txt` (739 bytes → 1 chunk) |

### Cold run (no cache)

| Metric | Value |
|---|---|
| cold_start_warmup_ms | 2781 |
| first_chunk_latency_ms | 761 |
| total_audio_sec (pre-trim) | 1.472 |
| synth wall_time_sec | 0.77 |
| **stage RTF** | **0.523** |
| average_chunk_rtf | 0.517 |
| steady_state_rtf | n/a (single chunk) |
| peak_rss_mb | 849 |
| peak_cpu_percent | 602 (cross-core sum) |
| cache_hit_ratio | 0.0 |

### Warm run (audio cache present, synthesize re-executed)

| Metric | Value |
|---|---|
| cache_hit_ratio | 1.0 |
| synth wall_time_sec | 0.018 |
| stage RTF | 0.012 |
| peak_rss_mb | 740 |

### Notes / interpretation

- **Synthesis is faster than real-time on CPU**: stage RTF **0.52** (~2× real-time).
- The pipeline-level RTF printed by `run_pipeline.py` (~8.9) is dominated by the
  fixed ~2.8 s warmup amortized over a sub-second clip; the isolated synthesis RTF
  is the meaningful figure.
- `total_audio_sec` is measured on the **pre-trim** synthesis output; the final
  merged chapter is shorter after silence trimming.
- `peak_cpu_percent` > 100 is psutil's per-core sum, not an error.

### How to reproduce

```bash
rm -rf corpus_output_kokoro
python run_pipeline.py            # cold
# preserve metrics/performance_profile.json, then force synthesize to re-run
# (delete its stage-cache JSON while keeping the .wav audio cache) for the warm run
```

Detailed artifacts: `corpus_output_kokoro/metrics/performance_profile.json`,
`corpus_output_kokoro/metrics/execution_history.json`.

---

## Baseline 2 — V1.1 Medium throughput (CPU, workers=2)

**Benchmark Tier:** Medium — first meaningful concurrency/throughput reference.

Deterministic input via `BenchmarkParser` (no LLM) over a generated corpus, so the
entire input pipeline is reproducible (corpus + transcript SHA stable across runs).

### Setup

| Field | Value |
|---|---|
| Date | 2026-06-27 |
| Engine / Provider | Kokoro ONNX v0.19 / `CPUExecutionProvider` |
| Parser | `BenchmarkParser` (deterministic, offline) |
| Corpus | `corpus/medium/chapter.txt` (generator v1.0, seed 20260627, 100 paragraphs) |
| Chunks | 100 |
| Workers | 2 |

### Synthesis metrics

| Metric | Value |
|---|---|
| total_audio_sec | 1188.8 |
| synth wall_time_sec | 522.3 |
| **stage RTF (2 workers)** | **0.439** |
| average_chunk_rtf (single-thread) | 0.892 |
| steady_state_rtf | 0.893 |
| cold_start_warmup_ms | 3209 |
| first_chunk_latency_ms | 10947 |
| peak_rss_mb | 1338 |
| peak_cpu_percent | 823 (cross-core sum) |
| load balance (max/min, stddev) | 1.04, 1.0 |

### Interpretation

- **2 workers ≈ 2× throughput**: per-chunk single-thread RTF 0.892 → stage RTF
  0.439 with 2 workers (≈2.03× efficiency). Near-linear at this width.
- **Even load balance** (max/min 1.04) confirms the ThreadPool distributes work
  fairly; no straggler at width 2.
- **First-chunk latency (10.9 s) ≫ warmup (3.2 s) ≫ steady per-chunk**: warmup uses
  a 1-word input, so the first *full-length* chunk triggers ONNX shape
  specialization. This is the cold-start tax the instrumentation isolates — it must
  not be averaged into steady-state RTF.
- This is the reference for the `1→2→4→8` worker sweep (separate study).

### Reproduce

```bash
python tools/generate_benchmark_corpus.py --tier medium
python tools/run_full_benchmark.py --tier medium --workers 2 --engine kokoro
```

---

## Baseline 3 — Worker Scaling Study (CPU, medium, 12 logical cores)

Generated artifact — regenerate with:
```bash
python tools/aggregate_sweep.py --tier medium --engine kokoro --workers 1,2,4,8
```
Source of truth: `benchmark_results/scaling_medium_kokoro.{json,csv}` and the
per-run `corpus_output_bench/medium_w<N>_kokoro/metrics/performance_profile.json`.

| workers | stage RTF | speedup | efficiency | per-chunk RTF | first-chunk ms | peak RSS MB | peak CPU % | load max/min |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | 0.569  | 1.00x | 1.00 | 0.567 | 7450  | 880  | 706  | 1.00 |
| 2 | 0.439  | 1.30x | 0.65 | 0.892 | 10947 | 1338 | 823  | 1.04 |
| 4 | 0.433  | 1.31x | 0.33 | 1.757 | 23279 | 1735 | 1059 | 1.08 |
| 8 | 0.304  | 1.87x | 0.23 | 2.407 | 27957 | 2731 | 1380 | 1.17 |

### Interpretation

- **Throughput scales, but badly.** 8 workers yields only **1.87× the throughput of
  1 worker (23% parallel efficiency)**. Adding workers helps far less than naive
  per-chunk numbers imply.
- **The plateau is real.** w=2 → w=4 is essentially flat (RTF 0.439 → 0.433); the
  gain to w=8 (0.304) comes only once concurrency finally saturates all 12 cores
  (peak CPU 706% → 1380%). No *inversion* within range — the earlier "regress at 8"
  prediction assumed 8 cores; this box has 12, so the saturation point is higher.
- **Root cause = ONNX intra-op parallelism.** Per-chunk RTF balloons 0.567 → 2.407
  as workers rise: each chunk gets slower because the ONNX runtime is *already*
  multi-threading every synthesis, so inter-op workers fight intra-op threads for
  the same cores. Aggregate throughput still rises only because more chunks overlap.
- **Cost of throughput is steep.** w=8 buys 1.87× throughput at **3.1× the memory**
  (880 → 2731 MB) and 4× the first-chunk latency (7.5 s → 28 s).

### Recommended workers — caveat on the rule

The "smallest within 95% of peak throughput" rule returns **8** (peak is at 8). But
that rule is throughput-only and ignores efficiency and memory. For a batch
audiobook job where wall-time dominates, **8** is defensible. For latency- or
memory-constrained contexts, **2** is the better default (1.30× at 0.65 efficiency,
1.3 GB). This argues the recommendation rule should gain an efficiency/RSS guardrail
before `recommended_workers` is baked into `EngineCapabilities`.

### Next: the real lever (Phase 0.5)

This curve measures the *uncontrolled* inter×intra thread grid. The actual
optimization is the **ORT intra-op × workers matrix** (e.g. workers=4 × intra=2 vs
workers=8 × intra=8 on 12 cores) — constraining intra so workers stop oversubscribing.
That requires the `SessionOptions` knob and is the next experiment.

---

## Benchmark Tiers (standard)

| Tier | Size | Purpose |
|---|---|---|
| **Smoke** | 1 chunk | correctness, CI, cold-start, cache |
| **Medium** | 50–100 chunks | concurrency, work distribution, RTF |
| **Large** | 500–1000 chunks | memory, scaling, stress |

The Medium and Large corpora are to be produced **deterministically** by a checked-in
generator (`tools/generate_benchmark_corpus.py`) and committed, so they never drift.

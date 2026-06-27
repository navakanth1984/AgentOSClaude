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

## Benchmark Tiers (standard)

| Tier | Size | Purpose |
|---|---|---|
| **Smoke** | 1 chunk | correctness, CI, cold-start, cache |
| **Medium** | 50–100 chunks | concurrency, work distribution, RTF |
| **Large** | 500–1000 chunks | memory, scaling, stress |

The Medium and Large corpora are to be produced **deterministically** by a checked-in
generator (`tools/generate_benchmark_corpus.py`) and committed, so they never drift.

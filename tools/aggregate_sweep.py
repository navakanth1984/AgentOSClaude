"""Aggregate worker-sweep performance profiles into a derived scaling artifact.

Reads corpus_output_bench/<tier>_w<N>_<engine>/metrics/performance_profile.json
for each worker count and emits:
  - benchmark_results/scaling_<tier>_<engine>.json   (machine-readable summary)
  - benchmark_results/scaling_<tier>_<engine>.csv     (spreadsheet-friendly)
  - a markdown table on stdout (paste into BASELINE.md, or regenerate any time)

Derived metrics:
  throughput is proportional to 1/RTF (lower RTF = faster), so
    speedup(N)    = rtf(1) / rtf(N)
    efficiency(N) = speedup(N) / N
  oversubscription_ratio = (N * ort_intra_threads) / logical_cpus
    (ort_intra_threads is None until the SessionOptions knob lands; shown as n/a)
  recommended_workers = smallest N whose speedup >= 0.95 * max(speedup)
"""
import argparse
import csv
import json
import os
from pathlib import Path

RESULTS_DIR = Path("benchmark_results")


def _load(tier: str, workers: int, engine: str):
    p = Path(f"corpus_output_bench/{tier}_w{workers}_{engine}/metrics/performance_profile.json")
    return json.load(open(p, encoding="utf-8")) if p.is_file() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="medium")
    ap.add_argument("--engine", default="kokoro")
    ap.add_argument("--workers", default="1,2,4,8")
    args = ap.parse_args()

    cpu_count = os.cpu_count() or 0
    worker_list = [int(w) for w in args.workers.split(",")]
    profiles = {w: _load(args.tier, w, args.engine) for w in worker_list}
    profiles = {w: p for w, p in profiles.items() if p}
    if not profiles:
        raise SystemExit("no profiles found; run the sweep first")

    base_w = min(profiles)
    base_rtf = profiles[base_w]["synthesis"]["rtf"]

    rows = []
    for w in sorted(profiles):
        s = profiles[w]["synthesis"]; st = profiles[w]["startup"]
        r = profiles[w]["resources"]; lb = profiles[w]["workers"]["load_balance"]
        bench = profiles[w].get("benchmark", {})
        intra = (bench.get("ort") or {}).get("intra_threads")  # None until knob lands
        rtf = s["rtf"]
        speedup = round(base_rtf / rtf, 3) if rtf else None
        oversub = round((w * intra) / cpu_count, 2) if (intra and cpu_count) else None
        rows.append({
            "workers": w, "ort_intra_threads": intra, "logical_cpus": cpu_count,
            "stage_rtf": rtf, "speedup": speedup,
            "efficiency": round(speedup / w, 3) if speedup is not None else None,
            "oversubscription_ratio": oversub,
            "avg_chunk_rtf": s["average_chunk_rtf"], "first_chunk_ms": st["first_chunk_latency_ms"],
            "peak_rss_mb": r["peak_rss_mb"], "peak_cpu_percent": r["peak_cpu_percent"],
            "load_max_min": lb["max_min_ratio"],
        })

    # Evidence-based recommendation: smallest worker count within 95% of peak
    # throughput. Computed from the typed profiles (int keys), not the heterogeneous
    # rows dicts, so the comparisons stay well-typed.
    rtf_by_w = {w: profiles[w]["synthesis"]["rtf"] for w in sorted(profiles)}
    speedups = {w: base_rtf / r for w, r in rtf_by_w.items() if r}
    recommended_workers = None
    if speedups:
        peak = max(speedups.values())
        recommended_workers = min(w for w, s in speedups.items() if s >= 0.95 * peak)

    best_w = min(rtf_by_w, key=lambda w: rtf_by_w[w] if rtf_by_w[w] else 9e9)
    best = {"workers": best_w, "stage_rtf": rtf_by_w[best_w]}

    summary = {
        "tier": args.tier, "engine": args.engine, "logical_cpus": cpu_count,
        "recommended_workers": recommended_workers,
        "recommendation_rule": "smallest workers within 95% of peak throughput",
        "best_throughput_workers": best["workers"], "best_stage_rtf": best["stage_rtf"],
        "rows": rows,
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    base = RESULTS_DIR / f"scaling_{args.tier}_{args.engine}"
    base.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with open(base.with_suffix(".csv"), "w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wtr.writeheader(); wtr.writerows(rows)

    # Render markdown
    print(f"### Worker Scaling Study - tier={args.tier}, engine={args.engine}, "
          f"logical_cpus={cpu_count}\n")
    print("| workers | stage RTF | speedup | efficiency | oversub | per-chunk RTF | "
          "first-chunk ms | peak RSS MB | peak CPU % | load max/min |")
    print("|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
    for row in rows:
        print(f"| {row['workers']} | {row['stage_rtf']} | {row['speedup']}x | {row['efficiency']} | "
              f"{row['oversubscription_ratio'] or 'n/a'} | {row['avg_chunk_rtf']} | "
              f"{row['first_chunk_ms']} | {row['peak_rss_mb']} | {row['peak_cpu_percent']} | "
              f"{row['load_max_min']} |")
    print(f"\n**Recommended workers:** {recommended_workers} "
          f"(rule: smallest within 95% of peak throughput).")
    print(f"**Best throughput:** workers={best['workers']} (stage RTF {best['stage_rtf']}).")

    prev = None
    for row in rows:
        if prev and row["stage_rtf"] and prev["stage_rtf"] and row["stage_rtf"] > prev["stage_rtf"]:
            print(f"- RTF regressed w={prev['workers']} ({prev['stage_rtf']}) -> "
                  f"w={row['workers']} ({row['stage_rtf']}) — oversubscription/contention.")
        prev = row
    print(f"\nArtifacts: {base.with_suffix('.json')}, {base.with_suffix('.csv')}")


if __name__ == "__main__":
    main()

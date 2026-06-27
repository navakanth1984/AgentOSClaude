"""Aggregate the ORT intra-op x workers thread-grid matrix into a derived artifact.

Reads corpus_output_bench/<tier>_w<W>_i<I>_<engine>/metrics/performance_profile.json
for each (workers, intra) pair and emits:
  - benchmark_results/thread_matrix_<tier>_<engine>.json / .csv
  - a markdown table on stdout

The goal: find a (workers x intra) config whose stage RTF matches/beats the
unconstrained w=8 run but with the memory/latency footprint closer to w=2. The
key derived metric is oversubscription = (workers * intra) / logical_cpus.
"""
import argparse
import csv
import json
import os
import statistics
from pathlib import Path

RESULTS_DIR = Path("benchmark_results")


def _check_schema(data, p):
    schema_ver = data.get("benchmark", {}).get("schema_version")
    if schema_ver != "1.1":
        raise ValueError(f"Mismatched schema version in {p}: expected 1.1, got {schema_ver}")


def _profile(tier, w, i, engine):
    p = Path(f"corpus_output_bench/{tier}_w{w}_i{i}_{engine}/metrics/performance_profile.json")
    if p.is_file():
        data = json.load(open(p, encoding="utf-8"))
        _check_schema(data, p)
        return data
    return None


def _baseline(tier, w, engine):
    p = Path(f"corpus_output_bench/{tier}_w{w}_{engine}/metrics/performance_profile.json")
    if p.is_file():
        data = json.load(open(p, encoding="utf-8"))
        _check_schema(data, p)
        return data
    return None


def _row(label, w, i, prof, cpu):
    s, st, r = prof["synthesis"], prof["startup"], prof["resources"]
    total = (w * i) if i else None

    # worker_idle_fraction = 1 - busy / (wall * active_workers), where busy is the
    # sum of per-worker chunk wall times the profile already records. High idle means
    # the pool is underused even if RTF looks fine.
    dist = prof["workers"]["distribution"]
    active = prof["workers"]["load_balance"].get("active_workers") or len(dist)
    walls = [v["wall_time_sec"] for v in dist.values()]
    busy = sum(walls)
    synth_wall = s["wall_time_sec"]
    idle = round(1 - busy / (synth_wall * active), 3) if (synth_wall and active) else None

    # Coefficient of variation of per-worker busy time: how evenly work was spread.
    # ~0 excellent, 0.05-0.10 normal noise, >0.2 imbalance, >0.4 partitioning problem.
    mean_w = statistics.mean(walls) if walls else 0
    cv = round(statistics.pstdev(walls) / mean_w, 3) if (len(walls) > 1 and mean_w) else 0.0

    return {
        "config": label, "workers": w, "intra": i,
        "total_threads": total,
        "oversubscription": round(total / cpu, 2) if (total and cpu) else None,
        "stage_rtf": float(s["rtf"]) if s["rtf"] else None,
        "per_chunk_rtf": s["average_chunk_rtf"],
        "worker_idle_fraction": idle,
        "worker_runtime_cv": cv,
        "first_chunk_ms": st["first_chunk_latency_ms"],
        "peak_rss_mb": r["peak_rss_mb"], "peak_cpu_percent": r["peak_cpu_percent"],
        "load_max_min": prof["workers"]["load_balance"]["max_min_ratio"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="medium")
    ap.add_argument("--engine", default="kokoro")
    ap.add_argument("--grid", default="2:6,4:3,6:2,12:1", help="comma list of workers:intra")
    ap.add_argument("--baselines", default="2,8", help="unconstrained worker runs to include for reference")
    args = ap.parse_args()

    cpu = os.cpu_count() or 0
    rows = []

    for w_str in args.baselines.split(","):
        w = int(w_str)
        prof = _baseline(args.tier, w, args.engine)
        if prof:
            rows.append(_row(f"w{w} (ORT default)", w, None, prof, cpu))

    for pair in args.grid.split(","):
        w_s, i_s = pair.split(":")
        w, i = int(w_s), int(i_s)
        prof = _profile(args.tier, w, i, args.engine)
        if prof:
            rows.append(_row(f"w{w} x i{i}", w, i, prof, cpu))

    if not rows:
        raise SystemExit("no matrix profiles found yet")

    rated = [r for r in rows if r["stage_rtf"] is not None]
    best = min(rated, key=lambda r: r["stage_rtf"]) if rated else None

    # Pareto recommendation over the grid configs. Objectives (all minimized):
    # stage_rtf, peak_rss_mb, worker_idle_fraction, worker_runtime_cv. A config is
    # dominated if another is <= on all four and < on at least one. From the
    # non-dominated frontier we pick the smallest worker count (smallest RSS to break
    # ties) — the cheapest config that nothing strictly beats.
    grid = [r for r in rows if r["intra"] is not None and r["stage_rtf"] is not None]
    OBJ = ("stage_rtf", "peak_rss_mb", "worker_idle_fraction", "worker_runtime_cv")

    def _dominates(a, b):
        le = all((a[k] or 0) <= (b[k] or 0) for k in OBJ)
        lt = any((a[k] or 0) < (b[k] or 0) for k in OBJ)
        return le and lt

    recommendation = None
    if grid:
        frontier = [a for a in grid if not any(_dominates(b, a) for b in grid if b is not a)]
        rec = min(frontier, key=lambda r: (r["workers"], r["peak_rss_mb"]))
        best_grid_rtf = min(r["stage_rtf"] for r in grid)
        fastest = min(grid, key=lambda r: r["stage_rtf"])
        reasons = [f"{round(best_grid_rtf / rec['stage_rtf'] * 100, 1)}% of peak grid throughput"]
        if rec is not fastest and fastest["peak_rss_mb"] and rec["peak_rss_mb"] < fastest["peak_rss_mb"]:
            reasons.append(f"{round((fastest['peak_rss_mb'] - rec['peak_rss_mb']) / fastest['peak_rss_mb'] * 100, 1)}% "
                           f"lower RSS than {fastest['config']}")
        reasons.append(f"idle fraction {rec['worker_idle_fraction']}, runtime CV {rec['worker_runtime_cv']}")
        reasons.append("smallest worker count on the Pareto frontier")
        
        import hashlib
        first_prof = _profile(args.tier, grid[0]["workers"], grid[0]["intra"], args.engine)
        env = first_prof["environment"] if first_prof else {}
        env_str = f"{env.get('os', '')}-{env.get('cpu', '')}-{cpu}"
        env_hash = hashlib.sha256(env_str.encode()).hexdigest()[:12]
        
        recommendation = {
            "config": rec["config"], "workers": rec["workers"], "ort_intra_threads": rec["intra"],
            "stage_rtf": rec["stage_rtf"], "peak_rss_mb": rec["peak_rss_mb"],
            "pareto_frontier": [r["config"] for r in frontier],
            "reason": reasons,
            "confidence": {"level": "measured", "benchmark_count": len(grid),
                           "corpus": args.tier, "repeated_runs": 1},
            "environment_hash": env_hash,
        }

    RESULTS_DIR.mkdir(exist_ok=True)
    base = RESULTS_DIR / f"thread_matrix_{args.tier}_{args.engine}"
    summary = {"tier": args.tier, "engine": args.engine, "logical_cpus": cpu,
               "best_config": best["config"] if best else None,
               "recommendation": recommendation, "rows": rows}
    base.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with open(base.with_suffix(".csv"), "w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wtr.writeheader(); wtr.writerows(rows)

    print(f"### ORT Thread-Grid Matrix - tier={args.tier}, engine={args.engine}, logical_cpus={cpu}\n")
    print("| config | total threads | oversub | stage RTF | per-chunk RTF | idle frac | "
          "runtime CV | peak RSS MB | peak CPU % |")
    print("|:--|--:|--:|--:|--:|--:|--:|--:|--:|")
    for r in rows:
        print(f"| {r['config']} | {r['total_threads'] or '-'} | {r['oversubscription'] or '-'} | "
              f"{r['stage_rtf']} | {r['per_chunk_rtf']} | {r['worker_idle_fraction']} | "
              f"{r['worker_runtime_cv']} | {r['peak_rss_mb']} | {r['peak_cpu_percent']} |")
    if best:
        print(f"\n**Fastest:** {best['config']} (RTF {best['stage_rtf']}, "
              f"peak RSS {best['peak_rss_mb']} MB).")
    if recommendation:
        print(f"**Recommended:** {recommendation['config']} "
              f"(RTF {recommendation['stage_rtf']}, RSS {recommendation['peak_rss_mb']} MB)")
        print(f"  Pareto frontier: {', '.join(recommendation['pareto_frontier'])}")
        for reason in recommendation["reason"]:
            print(f"  - {reason}")
    print(f"\nArtifacts: {base.with_suffix('.json')}, {base.with_suffix('.csv')}")


if __name__ == "__main__":
    main()

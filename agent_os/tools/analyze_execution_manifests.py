import json
import glob
import statistics
from pathlib import Path

def percentile(data, p):
    if not data:
        return 0
    data_sorted = sorted(data)
    k = (len(data_sorted) - 1) * (p / 100.0)
    f = int(k)
    c = int(k) + 1 if int(k) + 1 < len(data_sorted) else int(k)
    if f == c:
        return data_sorted[int(k)]
    d0 = data_sorted[f]
    d1 = data_sorted[c]
    return d0 + (d1 - d0) * (k - f)

def main():
    manifest_dir = Path(__file__).parent.parent / "output" / "execution_manifests"
    if not manifest_dir.exists():
        print(f"Directory {manifest_dir} does not exist. Run some executions first.")
        return

    files = glob.glob(str(manifest_dir / "*.json"))
    total_executions = len(files)
    if total_executions == 0:
        print("No manifests found.")
        return
        
    mode_counts = {}
    latencies = []
    latency_by_mode = {}
    total_consensus = 0
    consensus_count = 0
    
    # Category variance tracking
    category_consensus_sums = {}
    category_consensus_counts = {}
    
    success_count = 0
    aggregation_failures = 0
    total_models_used = 0
    
    # Missing field counts
    req_fields = ["execution_id", "mode", "models", "latency_ms", "aggregation", "final", "timeline"]
    missing_counts = {f: 0 for f in req_fields}
    
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            continue
            
        mode = data.get("mode", "unknown")
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        models = data.get("models", [])
        total_models_used += len(models)

        # Completeness Check
        is_complete = True
        for field in req_fields:
            if not data.get(field) and data.get(field) != 0:
                # aggregation can be None for single, final can be empty on failure
                # Let's count them specifically if they are missing
                if field == "aggregation" and mode == "single":
                    continue # valid to be None
                missing_counts[field] += 1
                is_complete = False
                
        # Success definition: final is present, no errors in timeline
        timeline = data.get("timeline", [])
        has_error = any(event.get("status") == "failed" for event in timeline)
        
        if data.get("final") and not has_error:
            success_count += 1
            
        # Aggregation failure detection
        if mode == "mixture" and not data.get("final"):
            if any(event.get("stage") == "aggregation" and event.get("status") == "failed" for event in timeline):
                aggregation_failures += 1
            elif not data.get("final"):
                # fallback if timeline doesn't have explicit stage info
                aggregation_failures += 1
                
        latency = data.get("latency_ms", 0)
        if latency > 0:
            latencies.append(latency)
            if mode not in latency_by_mode:
                latency_by_mode[mode] = []
            latency_by_mode[mode].append(latency)
        
        consensus = data.get("consensus_score")
        if consensus is not None:
            total_consensus += consensus
            consensus_count += 1
            
            # Track by category
            cat = data.get("prompt_category", "Unknown")
            category_consensus_sums[cat] = category_consensus_sums.get(cat, 0.0) + consensus
            category_consensus_counts[cat] = category_consensus_counts.get(cat, 0) + 1

    success_rate = (success_count / total_executions) * 100 if total_executions else 0
    agg_failure_rate = (aggregation_failures / total_executions) * 100 if total_executions else 0
    avg_models = total_models_used / total_executions if total_executions else 0
    
    def lat_stats(arr):
        if not arr: return {"p50": 0, "p95": 0, "max": 0}
        return {
            "p50": round(percentile(arr, 50), 2),
            "p95": round(percentile(arr, 95), 2),
            "max": round(max(arr), 2)
        }
        
    report = {
        "execution_count": total_executions,
        "success_rate_percent": round(success_rate, 2),
        "aggregation_failure_rate_percent": round(agg_failure_rate, 2),
        "average_participating_models": round(avg_models, 2),
        "manifest_completeness": missing_counts,
        "mode_distribution": mode_counts,
        "latency_overall_ms": lat_stats(latencies),
        "latency_by_mode_ms": {m: lat_stats(l) for m, l in latency_by_mode.items() if l},
        "average_consensus_score": round(total_consensus / consensus_count, 4) if consensus_count else None,
        "category_consensus_variance": {
            cat: round(category_consensus_sums[cat] / category_consensus_counts[cat], 4)
            for cat in category_consensus_sums
        }
    }
    
    print("Execution Framework Validation Report v1")
    print("========================================")
    print(f"Total Runs: {report['execution_count']}")
    print(f"Success Rate: {report['success_rate_percent']}%")
    print(f"Aggregation Failures: {report['aggregation_failure_rate_percent']}%")
    print(f"Average Models per Run: {report['average_participating_models']}")
    print("\nManifest Completeness:")
    completeness = (total_executions * len(req_fields) - sum(missing_counts.values())) / (total_executions * len(req_fields))
    print(f"  {round(completeness * 100, 2)}% complete overall")
    for f, count in report['manifest_completeness'].items():
        if count > 0:
            print(f"  {count} manifests missing '{f}'")
            
    print("\nMode Distribution:")
    for m, c in report['mode_distribution'].items():
        print(f"  {m}: {c}")
        
    print("\nLatency (ms):")
    overall = report['latency_overall_ms']
    print(f"  Overall: P50={overall['p50']}, P95={overall['p95']}, Max={overall['max']}")
    for m, stats in report['latency_by_mode_ms'].items():
        print(f"  {m}: P50={stats['p50']}, P95={stats['p95']}, Max={stats['max']}")
        
    if report['average_consensus_score'] is not None:
        print(f"\nAverage Consensus Score: {report['average_consensus_score']}")
        if report['category_consensus_variance']:
            print("\nAgreement variance by task category:")
            for cat, avg_cons in report['category_consensus_variance'].items():
                print(f"  {cat}: {avg_cons}")
        
    # Save JSON summary
    out_dir = Path(__file__).parent.parent / "output"
    out_dir.mkdir(exist_ok=True)
    report_file = out_dir / "validation_report_v1.json"
    with open(report_file, "w", encoding="utf-8") as rf:
        json.dump(report, rf, indent=2)
        
    print(f"\nReport saved to {report_file}")

if __name__ == "__main__":
    main()

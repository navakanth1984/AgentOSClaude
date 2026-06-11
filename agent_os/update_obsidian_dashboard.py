import json
from datetime import datetime
from pathlib import Path

# Paths
AGENT_OS_DIR = Path(__file__).parent
BATTLE_LOG_PATH = AGENT_OS_DIR / "battle_log.json"
VAULT_PATH = Path(r"C:\Users\navka\navakanth001\obsidian-vault\Obsidian Vault")
DASHBOARD_NOTE_PATH = VAULT_PATH / "00-Inbox" / f"{datetime.now().strftime('%Y-%m-%d')}-cgbench-simulation-dashboard.md"

def load_battle_logs():
    if not BATTLE_LOG_PATH.exists():
        return []
    try:
        with open(BATTLE_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading battle logs: {e}")
        return []

def format_timestamp(ts_str):
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts_str

def generate_markdown(logs):
    # Sort logs by timestamp descending (newest first)
    sorted_logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Group logs by type
    realworld_runs = [run for run in sorted_logs if run.get("type") == "realworld"]
    openclaw_runs = [run for run in sorted_logs if run.get("type") == "openclaw_vs_clawglove"]
    lead_behind_runs = [run for run in sorted_logs if run.get("type") == "lead_behind"]
    
    md_lines = []
    
    # YAML Frontmatter
    md_lines.append("---")
    md_lines.append(f"date: {datetime.now().strftime('%Y-%m-%d')}")
    md_lines.append("tags: [agent-os, cgbench, simulations, quantum, security-dashboard]")
    md_lines.append("project: \"AI-Automation\"")
    md_lines.append("source: \"CGBench Simulation Logs Database\"")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("# CGBench Threat Simulation Dashboard")
    md_lines.append("")
    md_lines.append("## Key Idea")
    md_lines.append("Persistent audit log and scorecard metrics tracking ClawGlove and OpenClaw simulation behaviors on the Qiskit quantum engine.")
    md_lines.append("")
    md_lines.append("## Details")
    md_lines.append(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    md_lines.append("")
    
    # ── Section 1: Real-World CVE Simulation (Phase 2) ───────────────────
    md_lines.append("### 1. Real-World CVE Battlefield Simulations (Phase 2)")
    md_lines.append("Evaluates ClawGlove's threat escalation and quarantine policies against 27 real-world attack vectors.")
    md_lines.append("")
    if realworld_runs:
        md_lines.append("| Timestamp | Backend | Block Rate | H_Escape | H_Quantum | Grade | PQC Signed |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for run in realworld_runs[:10]: # Limit to last 10
            metrics = run.get("metrics", {})
            block_rate = f"{metrics.get('block_rate', 0.0) * 100:.1f}%"
            h_escape = f"{metrics.get('h_escape', 0.0):.4f}"
            h_quantum = f"{metrics.get('h_quantum', 0.0):.4f}"
            pqc = "✅ Yes" if run.get("pqc_signed") else "❌ No"
            md_lines.append(f"| {format_timestamp(run.get('timestamp'))} | {run.get('backend', 'local')} | {block_rate} | {h_escape} | {h_quantum} | {run.get('grade', 'N/A')} | {pqc} |")
    else:
        md_lines.append("*No Real-World CVE simulation runs found.*")
    md_lines.append("")
    
    # ── Section 2: OpenClaw vs ClawGlove (Phase 1) ───────────────────
    md_lines.append("### 2. OpenClaw vs ClawGlove Threat Simulations (Phase 1)")
    md_lines.append("Evaluates the escalation behaviors between OpenClaw (attacker) and ClawGlove (governance).")
    md_lines.append("")
    if openclaw_runs:
        md_lines.append("| Timestamp | Backend | Block Rate | H_Escape | H_Gov | Dwell Time | Grade | PQC Signed |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for run in openclaw_runs[:10]: # Limit to last 10
            metrics = run.get("metrics", {})
            block_rate = f"{metrics.get('block_rate', 0.0) * 100:.1f}%"
            h_escape = f"{metrics.get('h_escape', 0.0):.4f}"
            h_gov = f"{metrics.get('h_gov', 0.0):.4f}"
            dwell = f"{metrics.get('dwell_ms', 0.0):.1f}ms"
            pqc = "✅ Yes" if run.get("pqc_signed") else "❌ No"
            md_lines.append(f"| {format_timestamp(run.get('timestamp'))} | {run.get('backend', 'local')} | {block_rate} | {h_escape} | {h_gov} | {dwell} | {run.get('grade', 'N/A')} | {pqc} |")
    else:
        md_lines.append("*No OpenClaw vs ClawGlove simulation runs found.*")
    md_lines.append("")
    
    # ── Section 3: Lead-Behind Coevolution (Phase 3) ───────────────────
    md_lines.append("### 3. Lead-Behind Coevolution Simulations (Phase 3)")
    md_lines.append("Measures ClawGlove's solo pre-evolution cycles and side-by-side (SBS) prediction precision.")
    md_lines.append("")
    if lead_behind_runs:
        md_lines.append("| Timestamp | Pre/SBS Cycles | Lead Value | Safety Intact | Prediction Precision | Grade | PQC Signed |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for run in lead_behind_runs[:10]: # Limit to last 10
            metrics = run.get("metrics", {})
            cycles = f"{metrics.get('pre_cycles', 0)} / {metrics.get('sbs_cycles', 0)}"
            lead = metrics.get('lead', 0)
            safety = "✅ Yes" if metrics.get('safety_intact', 0.0) == 1.0 else "❌ No"
            prec = f"{metrics.get('prediction_precision', 0.0) * 100:.1f}%"
            pqc = "✅ Yes" if run.get("pqc_signed") else "❌ No"
            md_lines.append(f"| {format_timestamp(run.get('timestamp'))} | {cycles} | {lead} | {safety} | {prec} | {run.get('grade', 'N/A')} | {pqc} |")
    else:
        md_lines.append("*No Lead-Behind Coevolution simulation runs found.*")
    md_lines.append("")
    
    # Action Checklist
    md_lines.append("## Action / Next Steps")
    md_lines.append("- [ ] Run a new Phase 2 simulation from the dashboard simulations panel to update this scorecard.")
    md_lines.append("- [ ] Verify PQC signatures on new logs.")
    md_lines.append("- [ ] Check the correlation ratio on noisy backend runs.")
    
    return "\n".join(md_lines)

def main():
    print("Reading simulation logs...")
    logs = load_battle_logs()
    if not logs:
        print("No logs to process.")
        return
        
    print("Generating dashboard markdown...")
    md_content = generate_markdown(logs)
    
    print(f"Writing dashboard to: {DASHBOARD_NOTE_PATH}")
    # Ensure folder exists
    DASHBOARD_NOTE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DASHBOARD_NOTE_PATH, "w", encoding="utf-8") as f:
        f.write(md_content)
    print("Dashboard updated successfully!")

if __name__ == "__main__":
    main()

import os
import json
import datetime
from pathlib import Path

class ObservationEngine:
    def __init__(self, log_dir="daava_production/logs"):
        self.log_dir = Path(log_dir)
        self.traces_dir = self.log_dir / "agent_traces"
        self.traces_dir.mkdir(parents=True, exist_ok=True)
        self.summary_file = self.log_dir / "context_feedback_summary.json"

    def log_trace(self, event_type, details, context_file=None):
        """Logs a specific agent event or generation trace."""
        timestamp = datetime.datetime.now().isoformat()
        trace_id = f"trace_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        
        trace_data = {
            "timestamp": timestamp,
            "event_type": event_type,
            "context_file": context_file,
            "details": details
        }
        
        with open(self.traces_dir / trace_id, 'w') as f:
            json.dump(trace_data, f, indent=2)
        
        print(f"[OBSERVE] Trace logged: {trace_id}")

    def analyze_friction(self):
        """Analyzes recent traces to identify context gaps or recurring errors."""
        gaps = []
        for trace_file in self.traces_dir.glob("*.json"):
            with open(trace_file, 'r') as f:
                trace = json.load(f)
                if trace.get("event_type") == "CONTEXT_FRICTION":
                    gaps.append(trace)
        
        # Aggregate gaps
        summary = {
            "last_analysis": datetime.datetime.now().isoformat(),
            "total_friction_events": len(gaps),
            "common_gaps": self._aggregate_gaps(gaps)
        }
        
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary

    def _aggregate_gaps(self, gaps):
        # Simple frequency count of issues
        issues = {}
        for gap in gaps:
            reason = gap.get("details", {}).get("reason", "Unknown")
            issues[reason] = issues.get(reason, 0) + 1
        return issues

if __name__ == "__main__":
    engine = ObservationEngine()
    # Example: Log a friction event manually for testing
    engine.log_trace("CONTEXT_FRICTION", {
        "reason": "Missing secondary harness color in DNA",
        "shot_id": "SHOT 1",
        "model": "Seedance 2.0"
    }, context_file="climber_dna.json")
    
    print(engine.analyze_friction())

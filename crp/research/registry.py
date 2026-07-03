import os
import json
import datetime
from research.hypothesis import Hypothesis
from research.scheduler import ExperimentResultRecord
from research.compiler import IRCompiler

class ExperimentRegistry:
    """Manages the Research Ledger journal and outputs self-contained recommendation bundles for human review."""
    
    def __init__(self, ledger_path: str, experiments_root: str):
        self.ledger_path = ledger_path
        self.experiments_root = experiments_root

    def log_to_ledger(self, record: ExperimentResultRecord, hypothesis: Hypothesis) -> None:
        """Appends a structured execution outcome to the JSONL Research Ledger."""
        log_entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "hypothesis_id": record.hypothesis_id,
            "hypothesis_name": hypothesis.name,
            "version": record.version,
            "baseline_run_id": record.baseline_run_id,
            "passed_constraints": record.passed_constraints,
            "reward_score": record.reward_score,
            "rejection_reason": record.rejection_reason,
            "metrics": {
                "candidate": {
                    "memory_bytes": record.candidate_metrics.memory_bytes,
                    "latency_ms": record.candidate_metrics.latency_ms,
                    "accuracy_loss": record.candidate_metrics.accuracy_loss,
                    "conversion_cost_ms": record.candidate_metrics.conversion_cost_ms,
                },
                "baseline": {
                    "memory_bytes": record.baseline_metrics.memory_bytes,
                    "latency_ms": record.baseline_metrics.latency_ms,
                    "accuracy_loss": record.baseline_metrics.accuracy_loss,
                }
            }
        }
        
        # Ensure parent folder exists
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
        
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def register_and_bundle(self, record: ExperimentResultRecord, hypothesis: Hypothesis) -> str:
        """Saves a self-contained candidate bundle if the experiment passed all constraints and has a positive score."""
        exp_id = f"EXP-{record.hypothesis_id.split('-')[-1]}-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}"
        bundle_dir = os.path.join(self.experiments_root, exp_id)
        os.makedirs(bundle_dir, exist_ok=True)

        # Compile IR to get plugin source, canonical IR, and manifest
        compiler = IRCompiler()
        artifact = compiler.compile_ir(hypothesis.plugin_ir)
        ir_data = json.loads(artifact.canonical_ir)

        # 1. Save candidate plugin code (plugin.py) and manifest (manifest.json)
        with open(os.path.join(bundle_dir, "plugin.py"), "w") as f:
            f.write(artifact.plugin_source)

        with open(os.path.join(bundle_dir, "manifest.json"), "w") as f:
            f.write(artifact.manifest_json)

        # 2. Save high-level summary (summary.json)
        summary = {
            "experiment_id": exp_id,
            "hypothesis_id": record.hypothesis_id,
            "name": hypothesis.name,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "reward_score": record.reward_score,
            "metrics": {
                "candidate_memory_bytes": record.candidate_metrics.memory_bytes,
                "candidate_latency_ms": record.candidate_metrics.latency_ms,
                "candidate_accuracy_loss": record.candidate_metrics.accuracy_loss,
                "baseline_memory_bytes": record.baseline_metrics.memory_bytes,
                "baseline_latency_ms": record.baseline_metrics.latency_ms,
                "baseline_accuracy_loss": record.baseline_metrics.accuracy_loss
            }
        }
        with open(os.path.join(bundle_dir, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2)

        # 3. Save comprehensive metrics and metadata (evidence.json)
        evidence = {
            "hypothesis": {
                "id": hypothesis.id,
                "name": hypothesis.name,
                "description": hypothesis.description,
                "target_workload": hypothesis.target_workload,
                "metadata": hypothesis.metadata
            },
            "evaluation": {
                "version": record.version,
                "baseline_run_id": record.baseline_run_id,
                "passed_constraints": record.passed_constraints,
                "reward_score": record.reward_score,
                "candidate": {
                    "memory_bytes": record.candidate_metrics.memory_bytes,
                    "latency_ms": record.candidate_metrics.latency_ms,
                    "accuracy_loss": record.candidate_metrics.accuracy_loss,
                    "conversion_cost_ms": record.candidate_metrics.conversion_cost_ms,
                },
                "baseline": {
                    "memory_bytes": record.baseline_metrics.memory_bytes,
                    "latency_ms": record.baseline_metrics.latency_ms,
                    "accuracy_loss": record.baseline_metrics.accuracy_loss,
                }
            }
        }
        with open(os.path.join(bundle_dir, "evidence.json"), "w") as f:
            json.dump(evidence, f, indent=2)

        # 4. Generate RFC draft (RFC_draft.md)
        rfc_content = f"""# RFC - Candidate Representation: {hypothesis.name}

## 1. Summary
Proposed representation plugin `{hypothesis.name}` compiled via CRP Research Subsystem.
- **Hypothesis:** {hypothesis.description}
- **Target Workload:** `{hypothesis.target_workload}`
- **Compiler Strategy:** `{ir_data.get("strategy")}`
- **Strategy Parameters:** {json.dumps(ir_data.get("parameters"))}

## 2. Benchmark Evidence
| Metric | Baseline | Candidate | Improvement / Delta |
|---|---|---|---|
| Memory | {record.baseline_metrics.memory_bytes} B | {record.candidate_metrics.memory_bytes} B | {((record.baseline_metrics.memory_bytes - record.candidate_metrics.memory_bytes) / record.baseline_metrics.memory_bytes * 100) if record.baseline_metrics.memory_bytes > 0 else 0:.1f}% saved |
| Latency | {record.baseline_metrics.latency_ms:.2f} ms | {record.candidate_metrics.latency_ms:.2f} ms | {(record.baseline_metrics.latency_ms - record.candidate_metrics.latency_ms):.2f} ms |
| Accuracy Loss | {record.baseline_metrics.accuracy_loss:.4f} | {record.candidate_metrics.accuracy_loss:.4f} | - |

- **Reconstruction Accuracy Loss:** {record.candidate_metrics.accuracy_loss:.4f}
- **Reward Score:** {record.reward_score:.4f}

## 3. Proposal Status
- [ ] Staged for review
- [ ] Promote into CRP core plugin registry
"""
        with open(os.path.join(bundle_dir, "RFC_draft.md"), "w") as f:
            f.write(rfc_content)

        # 5. Generate ADR draft (ADR_draft.md)
        adr_content = f"""# ADR Draft - Implement {hypothesis.name} representation plugin

## Status
Proposed (Candidate Bundle: `{exp_id}`)

## Context
Evaluations of synthetic and embedding search workloads in the Experience DB show optimization opportunities. The hypothesis is described as:
"{hypothesis.description}"

This candidate uses strategy `{ir_data.get("strategy")}` configured with parameters:
{json.dumps(ir_data.get("parameters"), indent=2)}

## Decision
Promote the compiled `{hypothesis.name}` representation plugin into the main CRP plugins registry. This change must be committed manually by a human developer.

## Consequences
- Reduces target footprint to {record.candidate_metrics.memory_bytes} bytes.
- Latency overhead of {record.candidate_metrics.latency_ms:.2f} ms.
- Preserves accuracy requirements (measured loss of {record.candidate_metrics.accuracy_loss:.4f}).
"""
        with open(os.path.join(bundle_dir, "ADR_draft.md"), "w") as f:
            f.write(adr_content)

        return bundle_dir

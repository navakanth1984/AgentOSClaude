from typing import List, Dict, Any, Protocol
from dataclasses import dataclass

@dataclass
class Hypothesis:
    id: str
    name: str
    description: str
    baseline_run_id: str  # Run record ID to compare against
    plugin_ir: str       # Declarative JSON IR string matching IR_SPEC.md
    target_workload: str  # Target workload class to test against
    metadata: Dict[str, Any]

class HypothesisGenerator(Protocol):
    def generate_hypotheses(self, db_path: str, ledger_path: str) -> List[Hypothesis]:
        """Propose candidate hypotheses based on SQLite Experience DB and past ledger logs."""
        ...

class HeuristicHypothesisGenerator:
    """Standard heuristic-based generator proposing declarative IR configs."""
    
    def generate_hypotheses(self, db_path: str, ledger_path: str) -> List[Hypothesis]:
        # Simple heuristic generator proposing standard block quantization configurations
        # based on past performance bottlenecks.
        ir_sample = """{
            "ir_version": "1.0.0",
            "ir_abi": 1,
            "name": "BlockQuantizedInt8",
            "strategy": "quantization.block.v1",
            "parameters": {
                "block_size": 32,
                "quantization_bits": 8,
                "symmetric": false
            },
            "objective": {
                "primary": "memory",
                "secondary": "latency",
                "constraints": {
                    "max_accuracy_loss": 0.05,
                    "max_latency_ms": 5.0
                }
            }
        }"""
        
        hypotheses = [
            Hypothesis(
                id="HYP-001",
                name="BlockQuantizedInt8",
                description="Use group-based quantization bounds to minimize quantization error.",
                baseline_run_id="latest",
                plugin_ir=ir_sample,
                target_workload="SyntheticTensorWorkload",
                metadata={"heuristic": "block_quantization"}
            )
        ]
        return hypotheses

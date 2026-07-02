import sqlite3
import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from crp_runtime.policy import Constraints, Profile
from crp_runtime.workloads import WorkloadSpec
from research.hypothesis import Hypothesis
from research.compiler import (
    IRCompiler,
    CompilerError,
    ParserError,
    SchemaError,
    CanonicalizationError,
    SemanticError,
    TemplateError,
    ASTError
)
from research.sandbox import IsolatedSandboxEvaluator, SandboxMetricResult

@dataclass
class BaselineMetrics:
    run_id: str
    workload_name: str
    memory_bytes: int
    latency_ms: float
    accuracy_loss: float

@dataclass
class ExperimentResultRecord:
    hypothesis_id: str
    version: str
    baseline_run_id: str
    baseline_metrics: BaselineMetrics
    candidate_metrics: SandboxMetricResult
    passed_constraints: bool
    reward_score: float
    rejection_reason: str = ""

class ExperimentScheduler:
    """Schedules, versions, and runs experiments comparing candidate plugins against defined baselines."""
    
    def __init__(self, db_path: str, evaluator=None):
        self.db_path = db_path
        self.compiler = IRCompiler()
        self.evaluator = evaluator or IsolatedSandboxEvaluator()

    def _get_baseline_from_db(self, workload_name: str, baseline_run_id: str) -> Optional[BaselineMetrics]:
        """Queries the SQLite Experience DB to retrieve baseline execution metrics."""
        if not os.path.exists(self.db_path):
            return None
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Retrieve baseline based on run ID or latest run matching target workload
            if baseline_run_id == "latest":
                cursor.execute(
                    """
                    SELECT r.run_id, w.workload_class, b.memory_bytes, b.latency_ms, b.quality_score 
                    FROM runs r
                    JOIN benchmarks b ON r.run_id = b.run_id
                    JOIN workloads w ON b.workload_id = w.workload_class
                    WHERE w.workload_class = ? OR w.model = ?
                    ORDER BY r.timestamp DESC LIMIT 1
                    """, (workload_name, workload_name)
                )
            else:
                cursor.execute(
                    """
                    SELECT r.run_id, w.workload_class, b.memory_bytes, b.latency_ms, b.quality_score 
                    FROM runs r
                    JOIN benchmarks b ON r.run_id = b.run_id
                    JOIN workloads w ON b.workload_id = w.workload_class
                    WHERE r.run_id = ?
                    """, (baseline_run_id,)
                )
                
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return BaselineMetrics(
                    run_id=row[0],
                    workload_name=row[1],
                    memory_bytes=int(row[2]),
                    latency_ms=float(row[3]),
                    accuracy_loss=1.0 - float(row[4])  # quality score vs accuracy loss mapping
                )
        except Exception:
            pass
        return None

    def run_experiment(
        self,
        hypothesis: Hypothesis,
        constraints: Constraints,
        profile: Profile,
        workload_spec: WorkloadSpec
    ) -> ExperimentResultRecord:
        """Executes a full hypothesis run, compiling the plugin, running the sandbox, and comparing it to the baseline."""
        
        # 1. Retrieve baseline
        baseline = self._get_baseline_from_db(hypothesis.target_workload, hypothesis.baseline_run_id)
        if not baseline:
            # Fallback mock baseline if database is empty or not yet initialized
            baseline = BaselineMetrics(
                run_id="default_dense_baseline",
                workload_name=hypothesis.target_workload,
                memory_bytes=4096,  # 4KB synthetic baseline
                latency_ms=1.5,
                accuracy_loss=0.0
            )

        # 2. Compile IR to Plugin
        try:
            artifact = self.compiler.compile_ir(hypothesis.plugin_ir)
            class_name = json.loads(artifact.canonical_ir)["name"]
        except CompilerError as e:
            if isinstance(e, ParserError):
                code = "IR:PAR_001"
            elif isinstance(e, SchemaError):
                code = "IR:SCH_002"
            elif isinstance(e, CanonicalizationError):
                code = "IR:CAN_003"
            elif isinstance(e, SemanticError):
                code = "IR:SEM_004"
            elif isinstance(e, TemplateError):
                code = "IR:TMP_005"
            elif isinstance(e, ASTError):
                code = "IR:AST_006"
            else:
                code = "IR:GEN_000"

            return ExperimentResultRecord(
                hypothesis_id=hypothesis.id,
                version="1.0.0",
                baseline_run_id=baseline.run_id,
                baseline_metrics=baseline,
                candidate_metrics=SandboxMetricResult(0, 0.0, 0.0, 0.0, False, f"{code}: {e}"),
                passed_constraints=False,
                reward_score=-999.0,
                rejection_reason=f"Compilation failure: {code} - {e}"
            )

        # 3. Isolated subprocess evaluation (exec confined to worker)
        cand_metrics = self.evaluator.evaluate(
            plugin_source=artifact.plugin_source,
            class_name=class_name,
            spec=workload_spec,
        )
        if not cand_metrics.success:
            return ExperimentResultRecord(
                hypothesis_id=hypothesis.id,
                version="1.0.0",
                baseline_run_id=baseline.run_id,
                baseline_metrics=baseline,
                candidate_metrics=cand_metrics,
                passed_constraints=False,
                reward_score=-999.0,
                rejection_reason=f"Execution failure: {cand_metrics.error_message}"
            )

        # 4. Hard constraints evaluation
        rejection_reason = ""
        passed = True
        
        if cand_metrics.memory_bytes > constraints.max_memory_bytes:
            passed = False
            rejection_reason = f"Memory budget exceeded: {cand_metrics.memory_bytes} > {constraints.max_memory_bytes}"
        elif cand_metrics.accuracy_loss > constraints.max_accuracy_loss:
            passed = False
            rejection_reason = f"Accuracy loss budget exceeded: {cand_metrics.accuracy_loss:.4f} > {constraints.max_accuracy_loss:.4f}"
        elif cand_metrics.latency_ms > constraints.max_latency_ms:
            passed = False
            rejection_reason = f"Latency budget exceeded: {cand_metrics.latency_ms:.2f} ms > {constraints.max_latency_ms:.2f} ms"

        # 5. Multi-objective scoring
        if passed:
            memory_saved = max(0, baseline.memory_bytes - cand_metrics.memory_bytes)
            latency_gain = max(0.0, baseline.latency_ms - cand_metrics.latency_ms)
            reward_score = (profile.alpha_memory * memory_saved) + (profile.beta_latency * latency_gain) - (profile.gamma_accuracy * cand_metrics.accuracy_loss * memory_saved)
        else:
            reward_score = -1.0

        return ExperimentResultRecord(
            hypothesis_id=hypothesis.id,
            version="1.0.0",
            baseline_run_id=baseline.run_id,
            baseline_metrics=baseline,
            candidate_metrics=cand_metrics,
            passed_constraints=passed,
            reward_score=reward_score,
            rejection_reason=rejection_reason
        )

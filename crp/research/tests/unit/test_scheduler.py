"""Unit tests for the ExperimentScheduler and ExperimentRegistry."""

import json
import os
import tempfile

from crp_runtime.policy import Constraints, Profile
from crp_runtime.workloads import WorkloadSpec
from research.hypothesis import HeuristicHypothesisGenerator
from research.registry import ExperimentRegistry
from research.scheduler import ExperimentScheduler


def test_scheduler_and_registry():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "experience.db")
        ledger_path = os.path.join(tmpdir, "ledger.json")
        experiments_root = os.path.join(tmpdir, "experiments")

        generator = HeuristicHypothesisGenerator()
        hypotheses = generator.generate_hypotheses(db_path, ledger_path)
        assert len(hypotheses) > 0

        hyp = hypotheses[0]
        scheduler = ExperimentScheduler(db_path)
        registry = ExperimentRegistry(ledger_path, experiments_root)

        constraints = Constraints(max_memory_bytes=10000, max_accuracy_loss=0.5, max_latency_ms=10.0)
        profile = Profile(alpha_memory=1.0, beta_latency=1.0, gamma_accuracy=0.1)
        workload_spec = WorkloadSpec(name="synthetic_tensor", params={"rows": 10, "cols": 10, "rank": 3}, seed=42)

        record = scheduler.run_experiment(hyp, constraints, profile, workload_spec)
        assert record.hypothesis_id == hyp.id

        # Log to ledger
        registry.log_to_ledger(record, hyp)
        assert os.path.exists(ledger_path)
        with open(ledger_path, "r") as f:
            log_line = json.loads(f.readline())
            assert log_line["hypothesis_id"] == hyp.id

        # Register and bundle (if constraints pass)
        if record.passed_constraints:
            bundle_dir = registry.register_and_bundle(record, hyp)
            assert os.path.exists(bundle_dir)
            assert os.path.exists(os.path.join(bundle_dir, "plugin.py"))
            assert os.path.exists(os.path.join(bundle_dir, "summary.json"))
            assert os.path.exists(os.path.join(bundle_dir, "RFC_draft.md"))
            assert os.path.exists(os.path.join(bundle_dir, "ADR_draft.md"))

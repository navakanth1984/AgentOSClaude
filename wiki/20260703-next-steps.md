# Next Steps – CRP Evolutionary Research Platform (2026‑07‑03)

**Context**: Implemented the optional research subsystem (`crp/research/`) on top of Cognitive Runtime Platform (CRP). The platform proposes, evaluates, and compiles candidates via a constrained Python AST/DSL, running isolated evaluations against replay workloads, pre-filtering on hard constraints, and outputting self-contained Experiment Bundles for human review.

## Immediate Action Items
1. **Design and Implement Additional Hypothesis Generators**
   - Implement statistical generators analyzing variance and sparsity trends in the Experience DB.
   - Build a pluggable interface for LLM-based generators (e.g., using Ollama or Gemini API) that reads ledger records and suggests candidate quantization block configurations.
2. **Strengthen Sandbox Isolation**
   - Move sandbox execution from simple dynamic loading in the same process/namespace to isolated processes using `multiprocessing` or clean subprocesses.
   - Enforce memory and CPU constraints in the sandbox using cgroups (Linux) or Job Objects (Windows) to capture execution limits reliably.
3. **Pluggable Baseline Definitions**
   - Allow configuration of custom baseline references per experiment instead of defaulting to `DensePlugin` or the latest matching workload run.
4. **Human Review Dashboard**
   - Build a simple dashboard/CLI tool to review outstanding Experiment Bundles under `crp/experiments/`, display comparisons between candidate and baseline metrics, and automate git staging upon human approval.

## Examination Pointers
- **Hypothesis Definition & Interfaces:** [hypothesis.py](file:///c:/Users/navka/navakanth001/crp/research/hypothesis.py)
- **AST / DSL Compiler:** [compiler.py](file:///c:/Users/navka/navakanth001/crp/research/compiler.py)
- **Sandbox Evaluation Engine:** [sandbox.py](file:///c:/Users/navka/navakanth001/crp/research/sandbox.py)
- **Scheduler & Baseline Metrics:** [scheduler.py](file:///c:/Users/navka/navakanth001/crp/research/scheduler.py)
- **Ledger Journal & Recommendation Bundles:** [registry.py](file:///c:/Users/navka/navakanth001/crp/research/registry.py)
- **Subsystem Unit Tests:** [test_research.py](file:///c:/Users/navka/navakanth001/crp/research/tests/test_research.py)

---
*Prepared for the next agent to continue the work.*

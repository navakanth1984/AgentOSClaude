# EXP-002: N-Model Scaling

## Decision Authority

This experiment is authorized to change:
- ✅ Default production max_models
- ✅ Recommended configuration profiles
- ✅ Benchmark baseline

This experiment is NOT authorized to change:
- Debate execution mode
- Planner/ExecutionGraph architecture
- Aggregation algorithm
- Provider routing

## Evidence Snapshot

Experiment: EXP-002
Question: N-Model Scaling
Benchmark: prompts_v1
Benchmark Version: Execution Benchmark Framework v1.0

Configuration
- Aggregation: Standard
- Models Evaluated: N=2, N=3, N=4
- Runs: 40

Artifacts
- config.json
- report.json
- raw_manifests/

Git SHA: [TO_BE_FILLED]

## Evidence Quality

Reproducible:
Yes

Randomization:
seed=42

Provider Conditions:
OpenRouter with observed rate-limit backoffs

Decision Confidence:
[ High | Medium | Low ]

Reason:
[ TO BE FILLED ]

## Question
Does increasing the number of participating models materially improve answer quality enough to justify the latency and cost?

## Hypothesis
N=3 is the best trade-off between latency, consensus, and cost.

## Configuration
- Benchmark: prompts_v1
- Aggregation: Standard
- Models: 2, 3, 4
- Git SHA: [TO_BE_FILLED]

## Results

| Metric               | N=2 | N=3 | N=4 | Best |
| -------------------- | --: | --: | --: | :--: |
| P50 Latency          | 14.9s | 15.8s |     |      |
| P95 Latency          | 20.1s | 26.6s |     |      |
| Avg Consensus        | 0.87 | 0.81 |     |      |
| Objective Consensus  | 0.88 | 0.88 |     |      |
| Subjective Consensus | 0.79 | 0.49 |     |      |
| Estimated Cost       | $0.0005 | $0.0013 |     |      |
| Estimated Tokens     | 272 | ~700 |     |      |
| Success Rate         | 100% | 100% |     |      |

## Interpretation

> **Interpretation Note**
> Consensus is not normalized for team size. Higher consensus at lower N is expected and should not be interpreted as higher answer quality by itself. Production decisions should weigh latency, cost, objective consensus, and qualitative inspection together.

## Marginal Gains

| Transition | Objective Consensus Δ | Latency Δ | Cost Δ | ROI | Worth It? |
|------------|----------------------:|----------:|-------:|----:|:---------:|
| 2 -> 3     |                       |           |        |     |           |
| 3 -> 4     |                       |           |        |     |           |

*(ROI: High = Significant objective improvement for modest latency/cost; Medium = Moderate improvement with noticeable overhead; Low = Marginal improvement relative to overhead; Negative = Additional overhead without measurable benefit)*

## Pareto Frontier

| Configuration | Pareto Optimal | Dominated By | Reason |
|---------------|:--------------:|--------------|--------|
| N=2 | ? | N=3? | Lowest latency/cost |
| N=3 | ? | None | Balanced quality/latency |
| N=4 | ? | N=3? | Highest quality? |

## Decision
[ Adopt | Retain | Investigate ]

## Rationale

N=2 rejected because ...

N=3 selected because ...

N=4 rejected because ...

## Outcome
[ Adopt | Retain | Investigate ]

## Production Impact

Configuration Changed:
- max_models = [ TO BE DECIDED ]

Affected Components:
- MixtureExecutor
- Dashboard defaults
- ExecutionRequest

Migration Required:
No

Backward Compatible:
Yes

---
## Governance

Status:
Accepted

Supersedes:
None

Superseded By:
—

This decision remains in force until superseded by a future ADR supported by a completed EXP.

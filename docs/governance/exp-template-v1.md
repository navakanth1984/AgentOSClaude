# Experiment 01: Fast vs Standard Aggregation

## Question
Can Fast aggregation reduce latency enough to justify becoming the default execution mode?

## Hypothesis
Fast reduces P95 latency by >= 30% while reducing consensus by <= 5% compared to the Standard baseline.

## Configuration
- Benchmark: prompts_v1
- Models: 3
- Aggregation: Fast vs Standard
- Git SHA: [TO_BE_FILLED]

## Results

| Metric | Standard | Fast | Δ | Target | Result |
|--------|---------:|-----:|--:|--------|--------|
| P50 Latency | ~15.8s | ~12.9s | -18% | Lower | ✅ Pass |
| P95 Latency | ~26.6s | ~22.9s | -14% | ≥30% lower | ❌ Fail |
| Avg Consensus | ~0.81 | ~0.76 | -6% | ≤5% drop | ❌ Fail |
| Objective Consensus | 0.88 | 0.83 | -0.05 | Stable | ❌ Fail |
| Subjective Consensus | 0.49 | 0.55 | +0.06 | Stable | ✅ Pass |
| Success Rate | 100% | 100% | - | 100% | ✅ Pass |
| Estimated Cost | $0.0013 | $0.0013 | - | Lower/Equal | ✅ Pass |

## Decision
⚖️ **Keep Standard as the default**

## Rationale
Fast aggregation did reduce latency (P50 down by 18%), but the P95 reduction (-14%) fell short of the ≥30% target required to justify the switch. More importantly, we observed a 6% drop in average consensus (missing our ≤5% tolerance), largely driven by a decline in Objective tasks. 

Given that the latency improvements are modest at the 95th percentile and come at the cost of objective accuracy, Standard remains the safer default for the core execution engine.

## Follow-up
- Keep `aggregation="standard"` as the default in production.
- Consider exposing Fast specifically for low-stakes conversational interactions where latency is more critical than rigorous consensus.
- Proceed to Experiment 2 (N-Model Scaling) using the Standard aggregation baseline.

---
date: 2026-04-11
tags: [ai-automation, self-improvement, agent-loops, prompt-engineering, karpathy]
project: "AI-Automation"
source: "Andrej Karpathy - AutoResearch open-source project"
---

# AutoResearch — Karpathy's Self-Improving AI Loop

## Key Idea
An AI agent that autonomously runs experiments to improve itself. It keeps changes that improve a metric and discards ones that don't — recursive self-improvement without human intervention.

## Architecture (Three-File Structure)

| File | Role | Can Agent Modify? |
|---|---|---|
| `program.md` | Goal, rules, constraints defined by human | No |
| `train.py` | The thing being optimized (code, prompt, config) | **Yes — only this** |
| `prepare.py` | Scoring metric + evaluation script | **Never — prevents cheating** |

## Three Conditions for Success

1. **Clear objective metric** — one number, one direction (e.g., Sharpe ratio, latency ms, conversion rate)
2. **Fully automated evaluation** — no human in the loop, must be fast enough to run hundreds of times
3. **Strict file constraints** — agent touches exactly one file; fixed time budget per experiment so tests are comparable

## How the Loop Works

```
formulate hypothesis
  → modify train.py
  → run evaluation (prepare.py)
  → improvement? → git commit ✓
  → regression?  → git reset, try again ✗
  → repeat
```

## Real-World Use Cases

- **Trading** — tweak buy/sell rules on historical data, score by Sharpe ratio
- **Marketing** — automated A/B testing on emails/ads, score by conversions
- **Prompt Engineering** — test system instructions, phrasing, complexity levels
- **Codebases** — make code faster; score by benchmark time
- **Model fine-tuning** — optimize open-source models for local devices

## Why the Design Works (The "Why")

- `prepare.py` immutability solves the alignment problem: the agent can't redefine "success"
- Single-file constraint bounds the search space so the loop converges
- LLM generates hypotheses → semi-open-ended search + metric keeps it honest
- Different from hyperparameter tuners: no need to pre-define search space

## Gotcha
"Fully automated evaluation" is harder than it sounds. Most real metrics involve humans, live APIs, or databases — which breaks the loop. Best targets: speed, math scores, file outputs, API response quality via LLM-judge.

## Tutorial Steps (Website Load Time Example)
1. Clone AutoResearch repo → open in Cursor or Claude Code
2. Build baseline app + write benchmarking script (e.g., Puppeteer)
3. Write custom `program.md` with your specific objective
4. Command agent: run baseline, record results, begin autonomous loop
5. Agent: hypothesize → modify → evaluate → commit or reset

## Action / Next Steps
- [ ] Try a prompt optimization loop using Claude API as the evaluator
- [ ] Build `prepare.py` for a task I already have (e.g., vault capture quality scoring)
- [ ] Review Karpathy's original `program.md` for structure inspiration
- [ ] Link to: [[Claude Prompt Engineering]], [[AI Agent Workflows]]

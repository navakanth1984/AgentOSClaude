---
date: 2026-04-11
tags: [ai-agent-loop, karpathy, autoresearch]
project: "AI-Automation"
source: "AutoResearch by Karpathy uses an AI agent loop to self-improve code."
---

# AutoResearch by Karpathy

## Key Idea
AutoResearch by Karpathy is a system that uses an AI agent loop to continuously improve its own code.

## Details
* The system consists of three files: program.md, train.py, and prepare.py.
* Program.md defines the goal of the agent's improvements.
* Train.py is the only file the agent can modify or "touch".
* Prepare.py contains the scoring metric used to evaluate the agent's performance and must never be modified.

## Action / Next Steps
- [ ] Investigate how AutoResearch by Karpathy handles cases where the agent proposes changes that lead to regression, and how it adapts its strategy in such situations.
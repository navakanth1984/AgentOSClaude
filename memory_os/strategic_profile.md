# Strategic Profile (Bucket 3)

*This is a mutable markdown file representing the current real-time strategy, focus, and decisions for the active Super Skill. The AI reads this file at the start of every session to align its context.*

## Current Objective
Optimizing AI model usage economics with a dynamic routing system that selects the most cost-efficient model per task complexity tier.

## Active Focus
- Implementing the model-router skill for automatic complexity classification and model selection.
- Tracking routing decisions and corrections to self-improve selection accuracy over time.
- Secondary: Continuing DAAVA cinematic production using Visual DNA pipeline.

## Key Architectural Decisions
- **Foundation:** Karpathy principles enforced via `karpathy_mandates.md`.
- **Memory OS:** Tri-layered system established (Session, Long-Term, Strategic).
- **Model Routing:** 5-tier system (Ultra-Budget → Frontier) with ULCOP v2.1 priority stack.
- **Cost Optimization:** Prompt caching + batch API + output optimization + context pruning.
- **Eval Loop:** Locked evaluator pattern from Agentic Engineering — routing quality scorer separate from optimizer.
- **Data/Connectors:** OpenRouter configured for multi-model API access. Pinecone and Firecrawl available.
- **Refinement Loop:** Self-improving routing corrections logged to `memory_os/long_term_knowledge/model-routing-corrections.md`.

## Default Model Routing
| Task Type | Default Model |
|:---|:---|
| Simple edits, formatting | Gemini 2.5 Flash-Lite |
| General coding, scripts | Gemini 2.5 Flash / DeepSeek V3 |
| Multi-file refactoring | Claude Sonnet 4.6 / Gemini 2.5 Pro |
| Architecture, novel design | Claude Opus 4.6 (Thinking) |
| Research, exploration | Parallel Flash subagents |

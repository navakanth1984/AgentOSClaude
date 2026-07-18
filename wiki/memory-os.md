# Memory OS
> The persistent memory, governance, and preference layer for all agents in the workspace.

## Overview
Memory OS is the centralized system that stores and manages the knowledge, preferences, and operational history of the agentic framework. It is designed to provide agents with both long-term, foundational knowledge and short-term, session-specific context. It also contains the core protocols and checklists that govern agent behavior.

## Key Components

### Memory Stores
- **long_term_knowledge/**: A repository for durable, foundational knowledge and lessons learned. This is where "settled" information that rarely changes is stored.
- **taste_library/**: A collection of approved patterns, aesthetic preferences, and high-quality examples that guide the subjective output of agents.
- **session_memory/**: Contains ephemeral, per-session data, including handoff files for passing context between agent sessions.

### Governance & Protocols
- **north-star-protocol.md**: Defines the highest-level guiding principles and objectives for the entire system.
- **strategic_profile.md**: Outlines the user's strategic goals and preferences.
- **session-start-checklist.md**: A mandatory checklist that agents must run at the beginning of each session to ensure alignment and context.
- **automation-tier-classifier.md**: A framework for classifying the complexity and required oversight for different automated tasks.
- **context-quality-check.md**: A set of rules for evaluating the quality and relevance of context provided to agents.

### Operational Data
- **model-usage-log.json**: A structured log of all model API calls, used for tracking costs and efficiency.
- **gcp_credit_usage.json**: A log for tracking Google Cloud Platform credit usage.

## Connections
- This system is the implementation of the memory concepts outlined in [Knowledge Base Protocol](knowledge-base-protocol.md).
- The checklists and protocols within Memory OS are referenced in agent-specific instructions like [CLAUDE.md](CLAUDE.md) and [.antigravity.md](.antigravity.md).

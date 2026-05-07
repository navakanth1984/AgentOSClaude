# SKILL: Agentic Engineering (Software 3.0 Discipline)

## Description
Architecture, constraints, and operational guidelines for building autonomous AI optimization loops. In Software 3.0, the context window is the lever, the eval metric is the compass, and the human is the director.

## The Paradigm Shift
- **Software 1.0**: Write explicit code (Bottleneck: Engineering hours)
- **Software 2.0**: Train neural networks (Bottleneck: Data and compute)
- **Software 3.0**: Prompt AI; context window is the lever (Bottleneck: Human taste and metric definition)

Agentic engineering raises the ceiling—elite engineers use autonomous agents to accelerate without sacrificing security, correctness, or code quality.

## The AutoResearch Loop
A framework for recursive, self-improving AI experiments.
- **Human defines**: `program.md` (goals, rules, constraints)
- **Agent modifies**: `train.py` (code / prompts / copy)
- **Human locks**: `prepare.py` (eval script — **NEVER** agent-accessible)

### The Three Sacred Files
1. **program.md**: The contract. Goals, rules, constraints, and success metric definition.
2. **train.py**: The only file the agent can modify (code, prompts, strategy).
3. **prepare.py**: The locked oracle. The evaluation script. Treat like production secrets.

## The Six Operational Guidelines
1. **Operate Exclusively in Verifiable Domains**: Success must be a single scalar number (e.g., Latency, F1 score, conversion rate).
2. **Enforce Strict Time-Boxing**: Every experiment must run for the same time budget to ensure quality wins over runtime.
3. **Prepare for Jagged Intelligence**: Agents spike in logic but fail silently in "brittle" domains (e.g., spatial logic, identity mapping).
4. **Treat Agents as Brilliant, Flaw-Prone Interns**: They memorize APIs but lack common sense. Human owns architecture and identifiers.
5. **Aggressively Monitor Code Quality and Bloat**: Agents optimize for metrics, not elegance. Human review is mandatory after a "win."
6. **Build Agent-Native Infrastructure**: Use sensors (logs, APIs) and actuators (CLIs, IaC) instead of human-centric UIs.

## The BIT Framework (Self-Improving Pipelines)
**Build → Integrate → Tune**
- **Build**: Agent executes task; human reviews output.
- **Integrate**: Session close; agent captures learnings into helper skill.
- **Tune**: Monthly/Project-level; agent proposes improvements; human approves.

## Quick Architecture Checklist
- [ ] Is the success metric a single scalar number?
- [ ] Is the eval script (`prepare.py`) locked and inaccessible to the agent?
- [ ] Is the agent restricted to exactly one target file (`train.py`)?
- [ ] Is every experiment time-boxed to the same budget?
- [ ] Have you reviewed for jagged-intelligence failure modes?
- [ ] Do you own the system architecture and identifier mapping?
- [ ] Is there a human review step after each successful loop run?

## Integration with Other Skills
- **karpathy-coding-guidelines**: Run bloat audit after successful loops.
- **context-engineering**: Use CDLC to manage the agent's prompts/skills.
- **hyperframes**: Original home of the BIT framework.

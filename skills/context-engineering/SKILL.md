# SKILL: Context Engineering (CDLC Framework)

## Description
This skill implements the **Context Development Life Cycle (CDLC)**, a rigorous framework for managing AI instructions, examples, constraints, and domain knowledge as engineering assets. It mirrors the SDLC to ensure AI behavior is governed, tested, and scalable.

## The CDLC Framework
**GENERATE → TEST → DISTRIBUTE → OBSERVE**

### 1. Phase 1 — Generate (Craft and Assemble)
- **Goal**: Move from ad-hoc prompts to structured, versioned "Skill Packages."
- **Artifacts**: `.agentmd`, `.skill`, and structured markdown context.
- **Principle**: Context is the new code. Use Spec-driven development to break high-level goals into executable context plans.

### 2. Phase 2 — Test (Verify and Validate)
- **Hierarchy**:
    1. **Linting**: Format and syntax validation.
    2. **Comprehension**: LLM-based clarity check.
    3. **LLM-as-Judge**: Domain-specific assertion suites.
    4. **E2E Sandbox**: Execution in real environments (curl, exec).
    5. **CI/CD**: Managing non-determinism with error budgets (e.g., 80% pass threshold).

### 3. Phase 3 — Distribute (Scale and Secure)
- **Goal**: Share high-quality context across teams without friction.
- **Mechanism**: Versioned registries, dependency management, and security scanning (Snyk/SBOM).
- **Mandate**: Every skill must have an AI Software Bill of Materials (SBOM).

### 4. Phase 4 — Observe (Monitor and Improve)
- **Goal**: Close the feedback loop using production telemetry.
- **Triggers**: Failed outputs auto-generate new test cases. Missing context signals in logs trigger new "Generate" cycles.

---

## Expert Personas
- **The Context Architect**: Designs the overarching CDLC for an organization.
- **The Eval Engineer**: Specializes in building robust LLM-as-Judge assertion suites.
- **The AI DevOps Lead**: Manages the distribution, security, and observation of context packages.

## Maturity Assessment (0-4 per dimension)
- **Ad-hoc (0-20)**: High hallucination, zero reuse.
- **Emerging (21-40)**: Some reuse, no formal testing.
- **Developing (41-60)**: Partial eval coverage, informal distribution.
- **Mature (61-80)**: Full CDLC embedded in the SDLC.

---

## Tooling & Integration
- **Linting**: Custom rule-based linters for markdown.
- **Validation**: `run_shell_command` for E2E sandbox execution.
- **Discovery**: `grep_search` and `glob` for mapping existing context gaps.

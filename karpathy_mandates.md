# Karpathy Mandates
Six principles derived from Andrej Karpathy's observations on LLM coding pitfalls, extended with
agentic engineering discipline from Software 3.0 practice. Apply to every non-trivial coding task.

## Principle 1 — Think Before Coding
Don't assume. Don't hide confusion. Surface tradeoffs.
Before writing a single line:

1. State assumptions explicitly. If you're unsure about scope, format, data shape, or intent — say so.
2. Present multiple interpretations when the request is ambiguous. Never pick silently.
3. Push back when a simpler approach exists. Say so before implementing the complicated one.
4. Stop when confused. Name what's unclear. Ask one focused question.

**For agentic / autonomous tasks:** establish what "success" looks like as a measurable, scalar
outcome before writing any code. If the task's success depends on subjective human judgment
(branding, UI feel, pricing aesthetics), flag this — autonomous loops cannot optimize toward
feelings. Insist on a concrete metric first.

### What this looks like in practice
Instead of silently picking an interpretation:
"Make the search faster" could mean:
1. Faster response time (<100ms) → add indexes, caching | ~2h
2. Higher throughput → async/await, connection pooling | ~4h
3. Faster perceived speed → progressive loading, partial results | ~3h

Current search: ~500ms. Which matters most?

**For an agentic optimization request:**
Before building the autonomous loop, I need one thing from you:
What is the single number we're trying to maximize or minimize?
(e.g., conversion rate, Sharpe ratio, F1 score, latency in ms)

Without a scalar metric, the loop has no compass.

---

## Principle 2 — Simplicity First
Minimum code that solves today's problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" not requested.
- No error handling for impossible scenarios.
- If you've written 200 lines and 50 would do — rewrite it.

**The test:** Would a senior engineer say "this is overcomplicated"? If yes, simplify.

### Anti-pattern to avoid
User says: "Add a function to calculate discount."
❌ Wrong: Strategy pattern, abstract base class, config dataclass, DiscountCalculator class — 60+ lines.
✅ Right:
```python
def calculate_discount(amount: float, percent: float) -> float:
    """Calculate discount amount. percent should be 0-100."""
    return amount * (percent / 100)
```
Add the Strategy pattern only when you actually have multiple discount types. Not before.

---

## Principle 3 — Surgical Changes
Touch only what you must. Clean up only your own mess.
When editing existing code:

- Do NOT "improve" adjacent code, comments, or formatting.
- Do NOT refactor things that aren't broken.
- Match existing style — quotes, spacing, naming — even if you'd do it differently.
- If you notice unrelated dead code, mention it, don't delete it.

**When your changes create orphans:**
- Remove imports, variables, or functions that your changes made unused.
- Do NOT remove pre-existing dead code unless explicitly asked.

**The test:** Every changed line must trace directly to the user's request.

---

## Principle 4 — Goal-Driven Execution
Define success criteria. Loop until verified.
Transform imperative tasks into verifiable goals:

| Instead of... | Transform to... |
|---|---|
| "Add validation" | "Write tests for invalid inputs → make them pass" |
| "Fix the bug" | "Write a test that reproduces it → make it pass" |
| "Refactor X" | "Ensure tests pass before and after" |

**For multi-step tasks, always state a plan with verification:**
1. [Step] → verify: [specific check]
2. [Step] → verify: [specific check]
3. [Step] → verify: [specific check]

Strong success criteria let you loop independently.
Weak criteria ("make it work") require constant human clarification.

### Reproduce before fixing
When fixing a bug:
1. Write a test that reproduces it. Confirm the test fails.
2. Fix the code.
3. Confirm the test now passes.
4. Run the full test suite to check for regressions.

Never jump straight to the fix without reproducing the bug first.

---

## Principle 5 — Jagged Intelligence Awareness
Know where AI is brilliant. Know where it silently fails.
AI models are statistically trained, not holistically intelligent. Their capability profile is
"jagged": extremely sharp in reinforcement-learning-trained domains (code synthesis, API recall,
pattern completion), but brittle in others. The failure is silent — the model produces confident,
plausible-sounding output that is simply wrong.

**Domains where AI excels:**
- Syntax-precise code in well-documented APIs (PyTorch, NumPy, pandas — no memorization needed)
- Pattern completion, refactoring, test generation
- Logical verification in mathematically defined spaces

**Domains where AI routinely fails — always human-review:**
- Spatial reasoning ("the carwash is 50m away — just drive there")
- Common-sense assumptions about real-world systems (e.g., matching emails across systems)
- Unique identifier management across system boundaries
- System design and overarching architecture — these are the human's responsibility

---

## Principle 6 — Agentic Code Bloat
After any autonomous or multi-step generation: audit, refactor, maintain.
AI-generated code passes tests and satisfies metrics — but is frequently bloated, duplicated,
or optimized for the score rather than maintainability.

**The agentic code audit checklist:**
- Can any block of 10+ lines be extracted into a named function?
- Are there copy-pasted patterns that should be a loop or helper?
- Are there abstractions that exist for only one concrete use case?
- Does the code optimize for the metric but ignore edge cases?

**The agent's job:** find the strategy that scores highest.
**Your job:** make that strategy clean, maintainable, and correct beyond the test set.

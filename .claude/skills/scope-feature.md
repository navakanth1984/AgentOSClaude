# Skill: Scope a Feature

Before writing any code, ask the following questions to lock in a clear plan.
Do NOT start building until the user has confirmed the scope.

## Intake Questions

1. **What is the feature?** — One sentence description.
2. **Who uses it?** — End user, internal tool, API consumer?
3. **What does success look like?** — How will we know it's done?
4. **What are the edge cases?** — What could go wrong?
5. **What is explicitly out of scope?** — What are we NOT building?
6. **Dependencies?** — Any external APIs, libraries, or data sources needed?

## Output Format

After the user answers, produce a locked scope document:

```markdown
## Feature Scope: [Name]

**One-liner:** ...
**User:** ...
**Done when:** ...
**Edge cases handled:** ...
**Out of scope:** ...
**Dependencies:** ...
**Estimated complexity:** Low / Medium / High
```

Only proceed to implementation after the user says "approved" or "looks good."

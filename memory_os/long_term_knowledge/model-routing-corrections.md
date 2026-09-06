# Model Routing Corrections Log

*This file accumulates routing corrections over time. The model-router skill reads this 
to improve its classification accuracy.*

## Format

Each entry records a routing decision that was wrong (over-powered or under-powered):

```
### YYYY-MM-DD — [Task Description]
- **Routed to:** [Model]
- **Should have been:** [Model]
- **Reason:** [Why the routing was wrong]
- **Signal missed:** [What signal should have triggered better routing]
```

---

## Corrections

### 2026-06-12 — Initial Setup
- **Note:** Model router skill installed. No corrections yet.
- **Baseline models:** Gemini 2.5 Flash (default), Claude Opus 4.6 (frontier)

---

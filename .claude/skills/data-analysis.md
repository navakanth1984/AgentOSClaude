# Skill: Data Analysis

Use this playbook whenever the user drops a file into `raw/` and asks for analysis.

## Steps

1. **Identify the file type** — CSV, Excel, PDF, JSON
2. **Load and inspect** — Show shape, column names, data types, null counts
3. **Ask the key question** — "What decision are you trying to make with this data?"
4. **Produce the analysis:**
   - Summary statistics
   - Key trends or anomalies
   - Visualizations (if environment supports it)
   - Plain-English findings (3-5 bullet points)
5. **Save output** to `output/YYYY-MM-DD-analysis-[filename].md`
6. **Update memory** — Append a one-liner to `memory/tasks.md`

## Output Format

```markdown
## Analysis: [filename]
**Date:** YYYY-MM-DD
**Question:** ...
**Key Findings:**
- ...
**Recommendation:**
...
```

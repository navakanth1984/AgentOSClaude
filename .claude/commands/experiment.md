Create a new experiment note in Obsidian and add it to the health dashboard.

Vault path: C:\Users\navka\OneDrive\Documents\Obsidian Vault\
Experiments folder: 01-Projects/AI-Automation/Experiments/

## What to do with: $ARGUMENTS

1. Parse the user's input to extract:
   - Experiment name
   - Hypothesis (what you predict will happen)
   - Protocol (exact steps, timing, frequency)
   - Metrics to track (what to measure, scale)
   - Duration (default: 30 days)
   - Project link (Health, Focus, Fitness, etc.)

2. Create the experiment file at: 01-Projects/AI-Automation/Experiments/YYYY-MM-DD-[name].md

3. Use this exact frontmatter and structure:

---
date: YYYY-MM-DD
status: in-progress
type: experiment
project: Health
tags: [experiment, health, in-progress]
duration_days: 30
start_date: YYYY-MM-DD
end_date: YYYY-MM-DD (start + duration)
---

# Experiment: [Name]

## Hypothesis
[What you predict will happen if you follow the protocol]

## Protocol
- **What:** [exact action]
- **When:** [time of day]
- **Frequency:** [daily/3x week/etc]
- **Duration:** 30 days

## Success Criteria
- [ ] [measurable outcome — e.g., "Wake within 30 min of target 80% of days"]

## Metrics
| Date | [Metric 1] | [Metric 2] | Notes |
|------|-----------|-----------|-------|
| YYYY-MM-DD | | | |

## Observations
<!-- Morning check-in appends here daily -->

## Results
<!-- Fill after experiment ends -->

4. Confirm to user: file created at [path], will appear in morning check-in tomorrow.

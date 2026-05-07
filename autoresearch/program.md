# AutoResearch — Vault Capture Prompt Optimizer

## Goal
Find the best system prompt for converting raw inputs (URLs, rough notes, brain dumps, transcripts) into structured Obsidian vault notes that follow Navakanth's capture format.

## What "Best" Means
A high-scoring note:
- Has correct YAML frontmatter (date, tags, project, source)
- Has a clear title using `#`
- Has a Key Idea section and a Details section
- Has at least one actionable checkbox `- [ ]`
- Uses tags relevant to the actual content
- Uses tags that already exist in the vault (consistency = better linking)
- Is concise — between 150 and 400 words
- Feels like something worth keeping, not generic filler

## Scoring Breakdown (100 pts total)
- Structure: 40 pts — correct frontmatter, sections, checkbox
- Length: 20 pts — 150-400 words
- Tag relevance: 10 pts — tags match the topic
- Tag consistency: 10 pts — tags reuse existing vault tags
- Quality: 20 pts — LLM judge on insight, specificity, actionability

## Rules for the Agent
1. You may ONLY modify `train.py`
2. Never touch `evaluate.py` — it contains the scoring logic
3. Never touch `test_inputs.json` — it contains the fixed test cases
4. Each experiment must produce output within 30 seconds
5. Try variations in: persona, structure instructions, output format, length constraints, tone, examples

## The Capture Format the Prompt Must Produce
```
---
date: YYYY-MM-DD
tags: [tag1, tag2]
project: "Project Name"
source: "URL or description"
---

# Title

## Key Idea
...

## Details
...

## Action / Next Steps
- [ ] ...
```

## Ideas to Try
- Add a worked example in the prompt (few-shot)
- Instruct the model to infer tags from content
- Vary persona: "knowledge archivist", "research assistant", "second brain"
- Experiment with explicit word count limits
- Try instructing structured thinking before output (chain of thought)
- Test different section names or ordering

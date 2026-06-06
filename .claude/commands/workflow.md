# /workflow

Spin up a multi-agent parallel workflow for large tasks.

## Usage
```
/workflow <task description>
```

## Steps

1. **Decompose the task** into N independent sub-tasks (aim for 3-10)
2. **Assign each sub-task to a sub-agent role:**
   - Researcher — gathers data, searches web
   - Builder — writes code or content
   - Reviewer — checks output for errors
   - Deployer — ships the result
3. **Run sub-agents in parallel** — open separate Claude Code panels or use `--dangerously-skip-permissions` in headless mode
4. **Aggregate results** — collect outputs into `output/workflow-YYYY-MM-DD/`
5. **Final review** — main agent reviews and integrates
6. **Save summary** to `memory/YYYY-MM-DD-workflow-[task].md`

## Context Management

- Each sub-agent gets its own 1M token context
- Main agent stays lean — only receives final outputs
- If any sub-agent exceeds 50% context, it should compact before continuing

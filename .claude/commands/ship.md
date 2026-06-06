# /ship

Summarize everything built or changed in this session, commit it, and push to the remote branch.

## Steps

1. Run `git diff --stat HEAD` to list changed files
2. Summarize changes in plain English (what was built, why it matters)
3. Stage all changes: `git add -A`
4. Commit with a descriptive message
5. Push: `git push -u origin <current-branch>`
6. Update `memory/tasks.md` — mark completed items as done
7. Append a one-liner to the CLAUDE.md change log

## Output

Print a summary like:
```
Shipped: [N] files changed
Branch: [branch-name]
Summary: [what was built]
Next: [what's left]
```

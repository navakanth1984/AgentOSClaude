# SYNC CONTRACT — cinematic-pipeline

**This folder is the single source of truth.**

Path (canonical):
`C:\Users\navka\navakanth001\.agents\skills\cinematic-pipeline\`

Claude Code reads this exact folder through a Windows **directory junction**:
`C:\Users\navka\.claude\skills\cinematic-pipeline`  →  (junction)  →  this folder.

Because it is a junction (not a copy), any edit made here is *instantly* visible
to Claude Code, and vice-versa. There is nothing to "copy" or "push".

## Rules for Antigravity (and any agent editing this skill)

1. **Edit in place.** Modify files in THIS `.agents/skills/cinematic-pipeline/`
   folder directly. Do not create a parallel copy elsewhere.
2. **Never move, rename, or delete this folder.** Doing so breaks the junction
   on the Claude side (`~/.claude/skills/cinematic-pipeline` would dangle).
   If the folder must move, the junction has to be recreated (see below).
3. **Don't delete-and-recreate the whole directory** as a "clean rebuild."
   Replace files individually. (Deleting the dir orphans the junction.)
4. **After ANY change to `dsl_compiler.py`, `dsl/presets.json`, or
   `dsl/templates.json`, run the self-test before considering the work done:**
   ```
   python dsl_compiler.py --test
   ```
   It must end with `[OK] Self-test passed successfully.` (0 errors).
5. **Keep `SKILL.md` Stage 05 in sync with the compiler.** If you add a
   backend, pass, or validation rule, update the Stage 05 description.

## If the junction ever breaks (folder moved, or recreated)

Recreate it from PowerShell (no admin needed — junctions don't require it):
```powershell
$dst = "$env:USERPROFILE\.claude\skills\cinematic-pipeline"
$src = "$env:USERPROFILE\navakanth001\.agents\skills\cinematic-pipeline"
if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
New-Item -ItemType Junction -Path $dst -Target $src | Out-Null
```

## Verify the link is healthy
```powershell
Get-Item "$env:USERPROFILE\.claude\skills\cinematic-pipeline" |
  Select-Object FullName, LinkType, Target
```
`LinkType` must read `Junction` and `Target` must point back to the `.agents` path above.

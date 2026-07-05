# Storage Management — C: ↔ E: Strategy

> **One-line summary:** C: drive (460 GB total, ~59 GB free) is managed by deleting regeneratable deps and mirroring heavy/inactive folders to E:\navakanth001\ via symlinks, keeping all paths intact.

---

## The Problem

`C:\Users\navka\navakanth001` accumulated ~400 GB over time. Primary offenders:

| Category | Typical size | Safe to delete? |
|----------|-------------|-----------------|
| `node_modules/` (per project) | 200 MB – 2 GB each | Yes — `npm install` regenerates |
| Python `venv/` / `.venv/` | 60 MB – 640 MB each | Yes — `pip install -r requirements.txt` |
| `__pycache__/` dirs | Small individually, large in bulk | Yes — Python auto-regenerates |
| Media/video output folders | 500 MB – 1 GB | Move to E:, not delete |
| SDK installs (Flutter etc.) | 1.5 – 2 GB | Move to E: + symlink |
| Benchmark / pipeline output | 500 MB – 1 GB | Move to E: |

---

## E:\ Mirror Architecture

`E:\navakanth001\` is the external SSD mirror of `C:\Users\navka\navakanth001\`. Same subfolder names, same structure — seamless full migration if ever needed.

```
E:\navakanth001\
  flutter_sdk\        ← 1,705 MB  (SDK, symlinked from C:)
  dead_loop_trailer\  ← 701 MB   (video output, symlinked)
  capcut_pipeline\    ← 502 MB   (pipeline output, symlinked)
  corpus_output_bench\ ← 1,086 MB (benchmark output, symlinked)
  graphify-out\       ← 643 MB   (build output, symlinked)
```

### Symlink Rule

After moving a folder to E:, create a directory symlink at the original C: path so every script, VS Code extension, and PATH entry keeps working:

```powershell
# Run as Administrator
Remove-Item "C:\Users\navka\navakanth001\<folder>" -Recurse -Force
New-Item -ItemType SymbolicLink `
  -Path "C:\Users\navka\navakanth001\<folder>" `
  -Target "E:\navakanth001\<folder>"
```

> Symlink creation requires **elevated PowerShell** (Run as Administrator) or Windows Developer Mode enabled.

---

## 2026-07-01 Cleanup Run — Results

### What was deleted (regeneratable, ~8 GB)

- **75 `node_modules` directories** — 7.1 GB total (openclaw 1.89 GB, open-design 1.56 GB, my-fabric-app 649 MB, geminicli001 563 MB, nth-dimension-react 450 MB, rayfin-todo-app 362 MB, remotion-video 342 MB, and more)
- **5 Python venvs** — 953 MB total (root venv 638 MB, 2× build-your-own-openclaw, ClawGlove, kqlbridge)
- **464 `__pycache__` directories** — ~200 MB

### What was moved to E:\navakanth001\ (~4.64 GB)

All 5 verified file-count-matched before C: removal:

| Folder | Files | Size |
|--------|-------|------|
| `flutter_sdk` | 20,524 | 1,705 MB |
| `corpus_output_bench` | 1,953 | 1,086 MB |
| `dead_loop_trailer` | 76 | 701 MB |
| `graphify-out` | 27,369 | 643 MB |
| `capcut_pipeline` | 63 | 502 MB |

**Total freed from C: ≈ 13 GB**

### Pending (requires Admin PowerShell)

```powershell
$base = "C:\Users\navka\navakanth001"
$ext  = "E:\navakanth001"
$folders = @("flutter_sdk","dead_loop_trailer","capcut_pipeline","corpus_output_bench","graphify-out")
foreach ($f in $folders) {
    Remove-Item "$base\$f" -Recurse -Force
    New-Item -ItemType SymbolicLink -Path "$base\$f" -Target "$ext\$f" | Out-Null
    Write-Output "✓ $f symlinked"
}
```

---

## Ongoing Maintenance Checklist

Run these periodically to prevent accumulation:

```powershell
# 1. Nuke all node_modules across the tree (~monthly or before any big move)
Get-ChildItem "C:\Users\navka\navakanth001" -Recurse -Directory -Filter "node_modules" `
  -ErrorAction SilentlyContinue `
  | Where-Object { $_.FullName -notmatch "\\node_modules\\.+" } `
  | Remove-Item -Recurse -Force

# 2. Nuke all __pycache__
Get-ChildItem "C:\Users\navka\navakanth001" -Recurse -Directory -Filter "__pycache__" `
  -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

# 3. Prune stale git worktrees (up to 2.5 GB)
git -C "C:\Users\navka\navakanth001" worktree list
git -C "C:\Users\navka\navakanth001" worktree prune

# 4. Check disk free
Get-PSDrive C, E | Select-Object Name, @{N='Free(GB)';E={[math]::Round($_.Free/1GB,2)}}
```

---

## Robocopy — Safe Cross-Drive Transfer

`Move-Item` times out on large cross-drive copies. Use robocopy instead:

```powershell
& "C:\Windows\System32\Robocopy.exe" "C:\source\folder" "E:\navakanth001\folder" /E /COPY:DAT /R:1 /W:1 /NP
# Exit code 0 = nothing to copy; 1 = files copied; 3 = copied + extras. All are success.
# Exit code 8+ = errors.
```

Verify completion by comparing file counts before deleting C: source:

```powershell
(Get-ChildItem "C:\path" -Recurse).Count  # must equal E: count before deleting
```

---

## What to Keep on C: (Active Work)

- `openclaw/` — active project
- `agent_os/` — core Agent OS
- `obsidian-vault/` — keep local, vault paths are absolute
- `memory_os/` — session memory, must stay local
- `.git/` — never move git internals

## Note: `E:\nth-absolute-cinema\` is a separate pattern, not part of this mirror

This page covers `E:\navakanth001\` — a **mirror** of `C:\Users\navka\navakanth001\`
subfolders via symlinks (same relative structure, files moved for space only).

[Nth Absolute Cinema](nth-absolute-cinema.md) lives at `E:\nth-absolute-cinema\` — its
**own top-level root**, not mirrored from C:, no symlink back. That project's whole
point is portability (copy the SSD to another machine and run), so it deliberately
does not follow the C:↔E: symlink pattern above. Don't conflate the two E: layouts.

## Related Pages

- [Agent OS](agent-os.md)
- [Memory OS](memory-os.md)
- [Code Development Lifecycle](development-lifecycle.md)
- [Nth Absolute Cinema](nth-absolute-cinema.md)

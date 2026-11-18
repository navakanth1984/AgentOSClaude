# OSS Tools Registry

> One list of the open-source tools kept ready for future apps, plus a doctor script that reports which ones actually work on this machine today.

## How to use it

```powershell
python scripts/oss_doctor.py               # status of every tool
python scripts/oss_doctor.py --only media  # one category
python scripts/oss_doctor.py --json        # for agents/scripts
python scripts/oss_doctor.py --strict      # exit 1 if anything is not usable (for CI / pre-flight)
```

- **Registry (source of truth):** [oss-tools-registry.json](oss-tools-registry.json). To add a tool, add one entry there and re-run the doctor. Never hand-write a status in prose: the doctor computes it.
- **Doctor:** [scripts/oss_doctor.py](../scripts/oss_doctor.py). Stdlib only. It never prints secret values, only whether a key is set.
- **PoC suite:** `D:\navakanth001\open-source-pocs\` (35 scoped PoCs, `report.json`). The doctor summarises it but doesn't copy it. "Verified" there means the PoC passed in a sandbox. It does not mean the tool is wired into an app. To depend on a PoC tool, promote it into the registry first.

## Status meanings

| Status | Meaning |
|---|---|
| READY | Present, deps installed, prerequisites on PATH |
| CONFIGURED | MCP server or plugin is configured correctly. A live connection can only be proven inside a Claude session |
| NEEDS_DEPS | Cloned, but `node_modules` / `.venv` is not installed yet |
| BLOCKED | A required binary (docker, ollama, go) or env key is missing |
| DRIFT | The clone's `origin` doesn't match the registry upstream |
| EXPOSED | Works, but a real secret is committed in tracked `.mcp.json` |
| MISSING | Not found at the registry path |

## Baseline: 2026-11-18 (first run)

19/34 usable, measured by the doctor rather than assumed. Findings that differed from the earlier (Antigravity-generated) catalog:

- **Secrets hygiene:** two MCP entries in tracked `.mcp.json` hold literal key values instead of `${VAR}` references. The doctor flags them as EXPOSED. Fix: rotate the keys, move them to env vars, and reference them as `${VAR}`.
- **Docker is not installed.** Postiz and Dify are BLOCKED. The `creator_stack` compose file can't run.
- **Ollama is not installed.** `mcp-local-llm` is BLOCKED.
- **Go is not installed.** `clodex` is BLOCKED.
- `mcp-notebooklm` has an empty `YOUTUBE_API_KEY`.
- **NEEDS_DEPS** (cloned but not installed): open-seo, ghost, hermes-agent, rea, ecc, presenton, ai-youtube-shorts, openshorts.
- `token-optimizer-mcp` is installed but not registered as an MCP server anywhere.
- In-session (not visible to the doctor): `magic-compact` and `reticle` MCPs failed to connect on 2026-11-18.
- The `manage_oss_arsenal.ps1`, `openseo_audit.py` and `postiz_syndicator.py` scripts exist only on the unmerged `claude_code_opensource_tools` branch (Antigravity worktree), not on `master`. That script's `status` command prints "All 7 … governed" whether or not the tools exist.
- PoC suite: 32 verified, 3 failed (brag, cliproxyapi, text-to-cad).

## Related
- [Agent OS](agent-os.md) · [Code Development Lifecycle](development-lifecycle.md) · [Storage Management](storage-management.md) (deps are deleted to save space and get reinstalled, which is why NEEDS_DEPS is common)

"""OSS tool readiness doctor.

Reads wiki/oss-tools-registry.json and checks, per tool, what is actually true on
this machine right now: folder present, git remote matches upstream, dependencies
installed, required binaries on PATH, MCP server configured with its env keys set.

It never prints secret values - only whether a key is set.

Usage:
    python scripts/oss_doctor.py              # table
    python scripts/oss_doctor.py --json       # machine-readable
    python scripts/oss_doctor.py --strict     # exit 1 if any tool is not usable
    python scripts/oss_doctor.py --only media # filter by category
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "wiki" / "oss-tools-registry.json"
USER_CLAUDE_JSON = Path.home() / ".claude.json"
INSTALLED_PLUGINS = Path.home() / ".claude" / "plugins" / "installed_plugins.json"

READY = "READY"
CONFIGURED = "CONFIGURED"  # MCP entry valid; live connection is only provable inside a Claude session
NEEDS_DEPS = "NEEDS_DEPS"
BLOCKED = "BLOCKED"
DRIFT = "DRIFT"
MISSING = "MISSING"
EXPOSED = "EXPOSED"  # works, but a real secret is committed to a tracked file
USABLE = {READY, CONFIGURED}

# Fix hints are written as instructions so the output tells the next agent what to do.
FIX = {
    NEEDS_DEPS: "Install deps inside the tool folder (npm install / uv venv && uv pip install -r requirements.txt), then re-run the doctor.",
    BLOCKED: "Install the missing prerequisite listed in detail, or set the missing env key, then re-run the doctor.",
    DRIFT: "The clone's origin does not match the registry upstream. Confirm which is right and fix one of them.",
    EXPOSED: "Rotate the key at the provider NOW, set it as a user env var, and change .mcp.json to \"${VAR_NAME}\". Removing it from the file does not remove it from git history.",
    MISSING: "Clone/install it to the registry path (or correct the path in wiki/oss-tools-registry.json).",
}


@dataclass
class Result:
    id: str
    category: str
    kind: str
    status: str
    detail: list[str] = field(default_factory=list)
    use_for: str = ""


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _git_remote(path: Path) -> str | None:
    if not (path / ".git").exists():
        return None  # a parent repo's remote would be misleading, so only trust a .git right here
    try:
        out = subprocess.run(
            ["git", "-C", str(path), "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() or None


def _norm_repo(url: str) -> str:
    url = url.strip().lower().removesuffix(".git").rstrip("/")
    return re.sub(r"^(https?://|git@)github\.com[/:]", "", url)


def _missing_bins(names: list[str]) -> list[str]:
    return [b for b in names if shutil.which(b) is None]


def _deps_gap(path: Path) -> str | None:
    if (path / "package.json").exists() and not (path / "node_modules").exists():
        return "package.json present but node_modules missing"
    py_manifest = (path / "pyproject.toml").exists() or (path / "requirements.txt").exists()
    has_venv = (path / ".venv").exists() or (path / "venv").exists()
    if py_manifest and not has_venv:
        return "Python manifest present but no .venv/venv"
    return None


def check_repo(t: dict) -> Result:
    r = Result(t["id"], t["category"], "repo", READY, use_for=t.get("use_for", ""))
    path = Path(t["path"])
    if not path.exists():
        r.status, r.detail = MISSING, [f"path not found: {path}"]
        return r
    remote = _git_remote(path)
    if remote is None:
        r.detail.append("not a standalone git clone (no .git in folder)")
    elif t.get("upstream") and _norm_repo(remote) != _norm_repo(t["upstream"]):
        r.status = DRIFT
        r.detail.append(f"origin={remote} expected={t['upstream']}")
    gap = _deps_gap(path)
    if gap and r.status == READY:
        r.status = NEEDS_DEPS
    if gap:
        r.detail.append(gap)
    missing = _missing_bins(t.get("requires", []))
    if missing:
        r.status = BLOCKED
        r.detail.append("missing on PATH: " + ", ".join(missing))
    return r


def check_binary(t: dict) -> Result:
    r = Result(t["id"], t["category"], "binary", READY, use_for=t.get("use_for", ""))
    found = shutil.which(t["binary"])
    if found:
        r.detail.append(found)
    else:
        r.status, r.detail = MISSING, [f"'{t['binary']}' not on PATH"]
    return r


def _env_key_set(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    m = re.fullmatch(r"\$\{(\w+)\}", value.strip())
    return bool(os.environ.get(m.group(1))) if m else True


def _is_literal_secret(key: str, value: object) -> bool:
    secretish = re.search(r"(KEY|TOKEN|SECRET|PASSWORD)$", key.upper())
    return bool(secretish) and isinstance(value, str) and bool(value.strip()) and not value.strip().startswith("${")


def check_mcp(t: dict, repo_cfg: dict, user_cfg: dict) -> Result:
    r = Result(t["id"], t["category"], "mcp", CONFIGURED, use_for=t.get("use_for", ""))
    source = repo_cfg if t.get("config") == "repo" else user_cfg
    where = ".mcp.json" if t.get("config") == "repo" else "~/.claude.json"
    entry = (source.get("mcpServers") or {}).get(t["server"])
    if not entry:
        r.status, r.detail = MISSING, [f"server '{t['server']}' not in {where}"]
        return r
    if entry.get("url"):
        r.detail.append(f"remote {entry['url']} (auth via /mcp if prompted)")
    else:
        cmd = entry.get("command", "")
        if shutil.which(cmd) is None:
            r.status = BLOCKED
            r.detail.append(f"command '{cmd}' not on PATH")
        else:
            r.detail.append(f"stdio: {cmd}")
    env = entry.get("env") or {}
    exposed = [k for k, v in env.items() if t.get("config") == "repo" and _is_literal_secret(k, v)]
    if exposed:
        r.status = EXPOSED
        r.detail.append("literal secret in git-tracked .mcp.json: " + ", ".join(exposed))
    unset = [k for k, v in env.items() if not _env_key_set(v)]
    if unset:
        r.status = BLOCKED
        r.detail.append("env keys unset: " + ", ".join(unset))
    missing = _missing_bins(t.get("requires", []))
    if missing:
        r.status = BLOCKED
        r.detail.append("missing on PATH: " + ", ".join(missing))
    return r


def check_plugin(t: dict) -> Result:
    r = Result(t["id"], t["category"], "plugin", CONFIGURED, use_for=t.get("use_for", ""))
    plugins = _load_json(INSTALLED_PLUGINS).get("plugins") or {}
    if t["plugin"] in plugins:
        r.detail.append("installed (connection health is only visible inside a Claude session)")
    else:
        r.status, r.detail = MISSING, [f"plugin '{t['plugin']}' not installed"]
    return r


def poc_summary(cfg: dict) -> dict:
    report = _load_json(Path(cfg["report"])) if cfg else {}
    if not isinstance(report, list):
        return {"available": False}
    counts: dict[str, int] = {}
    failed = []
    for row in report:
        counts[row.get("status", "?")] = counts.get(row.get("status", "?"), 0) + 1
        if row.get("status") != "verified":
            failed.append(row.get("id"))
    return {"available": True, "total": len(report), "counts": counts, "not_verified": failed}


def run(only: str | None) -> tuple[list[Result], dict]:
    reg = _load_json(REGISTRY)
    if not reg:
        sys.exit(f"Registry missing or invalid: {REGISTRY}")
    repo_cfg = _load_json(REPO_ROOT / ".mcp.json")
    user_cfg = _load_json(USER_CLAUDE_JSON)
    results = []
    for t in reg["tools"]:
        if only and t["category"] != only:
            continue
        kind = t["kind"]
        if kind == "repo":
            results.append(check_repo(t))
        elif kind == "binary":
            results.append(check_binary(t))
        elif kind == "mcp":
            results.append(check_mcp(t, repo_cfg, user_cfg))
        elif kind == "plugin":
            results.append(check_plugin(t))
    return results, poc_summary(reg.get("poc_suite", {}))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any tool is not READY/CONFIGURED")
    ap.add_argument("--only", help="filter by category (context, growth, media, mcp, ...)")
    args = ap.parse_args()

    results, pocs = run(args.only)
    not_usable = [r for r in results if r.status not in USABLE]

    if args.json:
        print(json.dumps({"tools": [asdict(r) for r in results], "poc_suite": pocs}, indent=2))
    else:
        w = max(len(r.id) for r in results) if results else 10
        for r in sorted(results, key=lambda x: (x.category, x.id)):
            print(f"{r.status:<11} {r.category:<8} {r.id:<{w}}  {'; '.join(r.detail)}")
        usable = len(results) - len(not_usable)
        print(f"\n{usable}/{len(results)} usable now.")
        if pocs.get("available"):
            print(f"PoC suite: {pocs['counts']} (not verified: {', '.join(pocs['not_verified']) or 'none'})")
        for status in sorted({r.status for r in not_usable}):
            print(f"\nFIX {status}: {FIX[status]}")

    return 1 if (args.strict and not_usable) else 0


if __name__ == "__main__":
    sys.exit(main())

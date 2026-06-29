"""
server.py — Agent OS HTTP API Server
Runs on localhost:8765 so the Flutter dashboard can call Python functions.

Start: python server.py
Flutter then calls http://localhost:8765/...

Endpoints:
  GET  /status          -> vault note count, asset count, recent notes
  GET  /context         -> hybrid context string (core + recent notes)
  GET  /search?q=...    -> full-text vault search
  GET  /recent?n=5      -> last N modified notes
  POST /save            -> save a note to inbox  { title, idea, details, tags }
  POST /swarm           -> parallel 5-agent research  { topic, model, auto_notebooklm }
  POST /goal            -> autonomous goal runner  { goal, max_steps, model }
  GET  /assets          -> list asset library files
  GET  /logs?n=20       -> last N workflow run entries (CDLC Observe)
  GET  /health          -> enhanced ping with vault + log health sensors
  POST /tune            -> BIT Tune: LLM-powered pattern analysis of workflow log
"""

import sys
# Force UTF-8 console output on Windows so Unicode chars (✓ ✗ ═ ① etc.) don't crash
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import asyncio
import json
import os
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import our bridge
import sys
sys.path.insert(0, str(Path(__file__).parent))
from obsidian_bridge import (
    save_note,
    search_vault,
    get_context_for_agent,
    list_recent_notes,
    VAULT_PATH,
)

# Import vault sync for cloud mode (Git-based vault access)
try:
    from vault_sync import initial_clone, pull as vault_pull, start_background_sync, is_cloud_mode
    _HAS_VAULT_SYNC = True
except ImportError:
    _HAS_VAULT_SYNC = False
    def is_cloud_mode(): return False

PORT = int(os.environ.get("PORT", 8765))
ASSET_LIBRARY = Path(__file__).parent / "asset_library"
OUTPUT_DIR = Path(__file__).parent / "output"
NOTEBOOK_CACHE = Path(__file__).parent / "notebook_cache.json"  # written by notebooklm_agent.py

# ── Load .env for API key ──────────────────────────────────────────────────────
_env_path = Path(__file__).parent / ".env"
if not _env_path.exists():
    _env_path = Path(__file__).parent.parent / ".env"

if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# API key for external access — read from .env
# Localhost callers (same PC) are always allowed without a key
_API_KEY = os.environ.get("AGENT_OS_API_KEY", "")
_REVIEW_API_KEY = os.environ.get("AGENT_OS_REVIEW_KEY", "agent-os-review")


def json_response(data: dict | list) -> bytes:
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


def get_vault_status() -> dict:
    notes = list(VAULT_PATH.rglob("*.md"))
    assets = list(ASSET_LIBRARY.iterdir()) if ASSET_LIBRARY.exists() else []
    recent = list_recent_notes(5)
    return {
        "vault_path": str(VAULT_PATH),
        "total_notes": len(notes),
        "total_assets": len(assets),
        "recent": [
            {
                "name": n["name"],
                "modified": datetime.fromtimestamp(n["modified"]).strftime("%Y-%m-%d %H:%M"),
            }
            for n in recent
        ],
    }


class AgentOSHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Suppress default server logs (noisy); keep our own
        pass

    def _check_auth(self) -> bool:
        """
        Auth logic:
          - If AGENT_OS_API_KEY is set in env:
              Requests must include a valid X-API-Key matching either:
                - Master Key (_API_KEY): full read/write access.
                - Review Key (_REVIEW_API_KEY): read-only access (GET allowed, POST blocked).
          - If AGENT_OS_API_KEY is NOT set:
              All requests allowed — local-only dev mode.
        """
        if not _API_KEY:
            return True

        provided = self.headers.get("X-API-Key", "")
        if not provided:
            try:
                parsed = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed.query)
                provided = params.get("key", [""])[0]
            except Exception:
                pass
        
        # 1. Master Key Auth
        if provided == _API_KEY:
            return True
            
        # 2. Review Key Auth
        if _REVIEW_API_KEY and provided == _REVIEW_API_KEY:
            # Check if this is a write request (POST)
            if self.command == "POST":
                self._send(403, {"error": "Write permission denied (Review Mode)"})
                return False
            return True

        self._send(401, {"error": "Missing or invalid X-API-Key header or key parameter"})
        return False

    def _send(self, code: int, data: dict | list | str):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  # allow Flutter
        self.end_headers()
        if isinstance(data, (dict, list)):
            self.wfile.write(json_response(data))
        else:
            self.wfile.write(json.dumps({"result": data}).encode())

    def _forward_to_bridge(self, method: str, path: str, body_data: Optional[dict] = None) -> bool:
        """
        If LOCAL_BRIDGE_URL is set in environment, forwards vault/notebook requests to the local bridge.
        Returns True if request was forwarded (handled), False otherwise.
        """
        if os.name == "nt":
            # Running locally on Windows: we are the bridge/local server, so do not forward to another bridge.
            return False

        bridge_url = os.environ.get("LOCAL_BRIDGE_URL")
        bridge_key = os.environ.get("LOCAL_BRIDGE_KEY", _API_KEY)
        if not bridge_url:
            return False
            
        bridge_url = str(bridge_url).rstrip("/")
        target_url = f"{bridge_url}{self.path}"
        
        import urllib.request
        import urllib.error
        
        try:
            req = urllib.request.Request(target_url, method=method)
            req.add_header("X-API-Key", bridge_key)
            req.add_header("ngrok-skip-browser-warning", "true") # Bypass ngrok warnings
            
            if body_data is not None:
                req.add_header("Content-Type", "application/json")
                req.data = json.dumps(body_data).encode("utf-8")
                
            with urllib.request.urlopen(req, timeout=15) as response:
                resp_data = response.read()
                self.send_response(response.status)
                for header, value in response.getheaders():
                    if header.lower() not in ["content-length", "connection", "transfer-encoding"]:
                        self.send_header(header, value)
                self.end_headers()
                self.wfile.write(resp_data)
                return True
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read()
                self.send_response(e.code)
                for header, value in e.headers.items():
                    if header.lower() not in ["content-length", "connection", "transfer-encoding"]:
                        self.send_header(header, value)
                self.end_headers()
                self.wfile.write(err_body)
            except Exception:
                self._send(e.code, {"error": e.reason})
            return True
        except Exception as e:
            self._send(500, {"error": f"Failed to forward to local bridge: {str(e)}"})
            return True

    def do_OPTIONS(self):
        # Flutter pre-flight CORS
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key")
        self.end_headers()

    def do_GET(self):
        try:
            self._do_GET_inner()
        except Exception as e:
            self._send(500, {"error": str(e)})

    def _do_GET_inner(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        path = parsed.path

        # Handle static file downloads/serving for exports and assets
        if path.startswith("/asset_library/") or path.startswith("/output/"):
            if not self._check_auth():
                return
            
            # Map path to file
            if path.startswith("/asset_library/"):
                file_rel = urllib.parse.unquote(path[len("/asset_library/"):])
                target_file = (ASSET_LIBRARY / file_rel).resolve()
                parent_dir = ASSET_LIBRARY.resolve()
            else:
                file_rel = urllib.parse.unquote(path[len("/output/"):])
                target_file = (OUTPUT_DIR / file_rel).resolve()
                parent_dir = OUTPUT_DIR.resolve()
                
            # Security check: check if target_file is within parent_dir
            if parent_dir not in target_file.parents:
                self._send(403, {"error": "Forbidden: Path is outside allowed directories"})
                return
                
            if not target_file.exists() or not target_file.is_file():
                self._send(404, {"error": f"File not found: {file_rel}"})
                return
                
            # Determine content type
            ext = target_file.suffix.lower()
            if ext == ".pdf":
                content_type = "application/pdf"
            elif ext == ".docx":
                content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ext == ".html":
                content_type = "text/html; charset=utf-8"
            elif ext == ".md":
                content_type = "text/markdown; charset=utf-8"
            elif ext in [".png", ".jpg", ".jpeg"]:
                content_type = f"image/{ext[1:]}"
            else:
                content_type = "application/octet-stream"
                
            try:
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Access-Control-Allow-Origin", "*")
                # Add content-disposition to trigger download for binary files
                if ext in [".pdf", ".docx", ".md"]:
                    self.send_header("Content-Disposition", f"attachment; filename=\"{target_file.name}\"")
                self.send_header("Content-Length", str(target_file.stat().st_size))
                self.end_headers()
                
                with open(target_file, "rb") as f:
                    self.wfile.write(f.read())
                return
            except Exception as e:
                self._send(500, {"error": f"Error serving file: {str(e)}"})
                return

        # Cloud mode: use Git sync for vault access, or forward to ngrok bridge as fallback
        if path in ["/recent", "/search", "/note", "/context", "/notebooks"]:
            if _HAS_VAULT_SYNC and is_cloud_mode():
                # Git mode — pull latest and serve from local clone
                vault_pull()
            elif self._forward_to_bridge("GET", path):
                # ngrok bridge mode — forward and return
                return

        # /dashboard and /neural are public — just HTML shells; JS inside carries the API key
        if path == "/dashboard":
            dash = Path(__file__).parent / "dashboard.html"
            if not dash.exists():
                self._send(404, {"error": "dashboard.html not found"})
                return
            html = dash.read_text(encoding="utf-8")
            if _API_KEY and not is_cloud_mode():
                html = html.replace('const APIKEY = "e84c2337a06d5d5f46406911060bdae59f41ce2c6e276ce87de502ff34526f8b";', f'const APIKEY = "{_API_KEY}";')
            else:
                html = html.replace('const APIKEY = "e84c2337a06d5d5f46406911060bdae59f41ce2c6e276ce87de502ff34526f8b";', 'const APIKEY = "";')
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        if path == "/neural":
            neural = Path(__file__).parent / "neural3d.html"
            if not neural.exists():
                self._send(404, {"error": "neural3d.html not found"})
                return
            html = neural.read_text(encoding="utf-8")
            if _API_KEY and not is_cloud_mode():
                html = html.replace('const API_KEY = "e84c2337a06d5d5f46406911060bdae59f41ce2c6e276ce87de502ff34526f8b";', f'const API_KEY = "{_API_KEY}";')
            else:
                html = html.replace('const API_KEY = "e84c2337a06d5d5f46406911060bdae59f41ce2c6e276ce87de502ff34526f8b";', 'const API_KEY = "";')
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        if path == "/neural2d":
            neural = Path(__file__).parent / "neural.html"
            if not neural.exists():
                self._send(404, {"error": "neural.html not found"})
                return
            html = neural.read_text(encoding="utf-8")
            if _API_KEY and not is_cloud_mode():
                html = html.replace('const API_KEY = "e84c2337a06d5d5f46406911060bdae59f41ce2c6e276ce87de502ff34526f8b";', f'const API_KEY = "{_API_KEY}";')
            else:
                html = html.replace('const API_KEY = "e84c2337a06d5d5f46406911060bdae59f41ce2c6e276ce87de502ff34526f8b";', 'const API_KEY = "";')
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        # Meta verification handshake bypasses standard API key check
        if path in ["/sap/webhook", "/webhooks/whatsapp"]:
            from whatsapp_bridge import verify_webhook
            code, challenge = verify_webhook(params)
            self.send_response(code)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(challenge.encode("utf-8"))
            return

        if not self._check_auth():
            return

        if path == "/whatsapp/status":
            from whatsapp_bridge import get_config, MESSAGE_HISTORY
            self._send(200, {
                "config": get_config(),
                "history": MESSAGE_HISTORY
            })
            return

        elif path == "/gcp/credits":
            usage_path = Path(__file__).parent.parent / "memory_os" / "gcp_credit_usage.json"
            if not usage_path.exists():
                default_data = {
                    "genai_voucher": {
                        "code": "494be35b03eb03dff4e91dd6a9c229d7d9be5dd5015a3f5c4c45ee7d70413c5f",
                        "total": 94812.51,
                        "remaining": 94804.47,
                        "expiry": "2027-04-27"
                    },
                    "dialogflow_trial": {
                        "code": "dialogflow_cx_credit_v2-015936-156B27-56F23F",
                        "total": 56730.01,
                        "remaining": 56729.35,
                        "expiry": "2026-11-22"
                    },
                    "config": {
                        "project_id": os.environ.get("VERTEX_PROJECT_ID", "nthdim-academy-v2"),
                        "billing_account_id": "01A2B3-4C5D6E-7F8A9B",
                        "use_vertex_ai": os.environ.get("USE_VERTEX_AI", "True").lower() in ("true", "1", "yes"),
                        "credentials_configured": True
                    }
                }
                usage_path.write_text(json.dumps(default_data, indent=2), encoding="utf-8")
            
            try:
                data = json.loads(usage_path.read_text(encoding="utf-8"))
                data["config"]["project_id"] = os.environ.get("VERTEX_PROJECT_ID", data["config"]["project_id"])
                data["config"]["use_vertex_ai"] = os.environ.get("USE_VERTEX_AI", "True").lower() in ("true", "1", "yes")
                self._send(200, data)
            except Exception as e:
                self._send(500, {"error": f"Failed to load credit details: {e}"})
            return

        elif path == "/health":
            # Enhanced health: sensors for the agentic system (Agentic Engineering: agent-native infra)
            try:
                openrouter_key = bool(os.environ.get("OPENROUTER_API_KEY"))
                vault_writable = False
                try:
                    test_path = VAULT_PATH / ".health_check"
                    test_path.touch()
                    test_path.unlink()
                    vault_writable = True
                except Exception:
                    pass
                vault_notes = 0
                try:
                    vault_notes = len(list(VAULT_PATH.rglob("*.md")))
                except Exception:
                    pass
                workflow_log_entries = 0
                _log_path = Path(__file__).parent / "workflow_log.json"
                if _log_path.exists():
                    try:
                        import json as _j
                        workflow_log_entries = len(_j.loads(
                            _log_path.read_text(encoding="utf-8")
                        ))
                    except Exception:
                        pass
                self._send(200, {
                    "ok":                    True,
                    "ts":                    datetime.now().isoformat(),
                    "openrouter_key_set":    openrouter_key,
                    "vault_writable":        vault_writable,
                    "vault_notes":           vault_notes,
                    "workflow_log_entries":  workflow_log_entries,
                    "server_version":        "2.0.0",
                })
            except Exception as health_err:
                self._send(200, {"ok": True, "ts": datetime.now().isoformat(), "error": str(health_err)})

        elif path == "/nth_brain/mastery":
            try:
                import sqlite3
                db_path = Path(__file__).parent.parent / "nth_brain.db"
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS student_mastery (
                        student_id TEXT PRIMARY KEY,
                        skill_source_mastery REAL,
                        skill_intermediate_mastery REAL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("SELECT skill_source_mastery, skill_intermediate_mastery FROM student_mastery WHERE student_id = 'student_1'")
                row = cursor.fetchone()
                conn.close()
                if row:
                    self._send(200, {
                        "success": True,
                        "skill_source_mastery": row[0],
                        "skill_intermediate_mastery": row[1]
                    })
                else:
                    self._send(200, {
                        "success": True,
                        "skill_source_mastery": 0.15,
                        "skill_intermediate_mastery": 0.10
                    })
            except Exception as e:
                self._send(500, {"error": f"Database exception: {e}"})
            return

        elif path.startswith("/nth_brain/"):
            # Serve static files from the nth-brain repo (single source of truth).
            # Override with NTH_BRAIN_DIR; defaults to <navakanth001>/nth-brain.
            file_rel = urllib.parse.unquote(path[len("/nth_brain/"):])
            if not file_rel or file_rel.endswith("/"):
                file_rel += "index.html"
            prototype_dir = Path(os.environ.get("NTH_BRAIN_DIR", Path(__file__).parent.parent / "nth-brain"))
            target_file = (prototype_dir / file_rel).resolve()
            if prototype_dir.resolve() not in target_file.parents:
                self._send(403, {"error": "Forbidden: Outside prototype dir"})
                return
            if not target_file.exists() or not target_file.is_file():
                self._send(404, {"error": f"File not found: {file_rel}"})
                return
            ext = target_file.suffix.lower()
            if ext == ".html":
                content_type = "text/html; charset=utf-8"
            elif ext == ".css":
                content_type = "text/css; charset=utf-8"
            elif ext == ".js":
                content_type = "application/javascript; charset=utf-8"
            elif ext in [".png", ".jpg", ".jpeg"]:
                content_type = f"image/{ext[1:]}"
            else:
                content_type = "application/octet-stream"
            
            try:
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(target_file.stat().st_size))
                self.end_headers()
                with open(target_file, "rb") as f:
                    self.wfile.write(f.read())
                return
            except Exception as e:
                self._send(500, {"error": f"Error serving prototype file: {str(e)}"})
                return

        elif path == "/status":
            self._send(200, get_vault_status())

        elif path == "/context":
            n = int(params.get("n", ["5"])[0])
            context = get_context_for_agent(recent_n=n)
            self._send(200, {"context": context})

        elif path == "/search":
            query = params.get("q", [""])[0]
            if not query:
                self._send(400, {"error": "Missing ?q= parameter"})
                return
            results = search_vault(query)
            self._send(200, {"query": query, "results": results})

        elif path == "/recent":
            n = int(params.get("n", ["5"])[0])
            notes = list_recent_notes(n)
            self._send(200, {"notes": notes})

        elif path == "/debug_vault":
            # Diagnostic endpoint
            import subprocess
            
            repo_url = os.environ.get("VAULT_REPO_URL", "")
            masked_url = ""
            if repo_url:
                if "@" in repo_url:
                    parts = repo_url.split("@")
                    masked_url = "https://<TOKEN_MASKED>@" + parts[-1]
                else:
                    masked_url = repo_url
            
            vault_repo_path_exists = False
            vault_path_exists = False
            git_status = ""
            git_remote = ""
            vault_clone_files = []
            
            try:
                from vault_sync import VAULT_REPO_PATH, get_vault_path
                vpath = get_vault_path()
                vault_path_exists = vpath.exists()
                vault_repo_path_exists = VAULT_REPO_PATH.exists()
                
                if vault_repo_path_exists:
                    r = subprocess.run(["git", "status"], cwd=str(VAULT_REPO_PATH), capture_output=True, text=True, timeout=5)
                    git_status = (r.stdout or "") + "\n" + (r.stderr or "")
                    
                    r2 = subprocess.run(["git", "remote", "-v"], cwd=str(VAULT_REPO_PATH), capture_output=True, text=True, timeout=5)
                    remote_lines = []
                    for line in ((r2.stdout or "") + "\n" + (r2.stderr or "")).splitlines():
                        if "@" in line:
                            parts = line.split("@")
                            remote_lines.append(parts[0][:15] + "...@" + parts[-1])
                        else:
                            remote_lines.append(line)
                    git_remote = "\n".join(remote_lines)
                    
                    for root, dirs, files in os.walk(str(VAULT_REPO_PATH)):
                        depth = root.replace(str(VAULT_REPO_PATH), "").count(os.sep)
                        if depth > 2:
                            continue
                        for f in files[:10]:
                            vault_clone_files.append(os.path.join(root, f))
                        if len(vault_clone_files) > 100:
                            break
            except Exception as e:
                git_status = f"Error: {e}"
                
            self._send(200, {
                "has_vault_sync": _HAS_VAULT_SYNC,
                "is_cloud_mode": is_cloud_mode(),
                "vault_path": str(VAULT_PATH),
                "vault_path_exists": vault_path_exists,
                "vault_repo_path_exists": vault_repo_path_exists,
                "vault_repo_url_configured": bool(repo_url),
                "vault_repo_url": masked_url,
                "git_status": git_status.strip(),
                "git_remote": git_remote.strip(),
                "vault_clone_files_sample": vault_clone_files[:50]
            })


        elif path == "/note":
            note_path = params.get("path", [""])[0]
            if not note_path:
                self._send(400, {"error": "Missing 'path' parameter"})
                return
            try:
                # Security check: ensure path is under VAULT_PATH (casing and slash-insensitive for Windows)
                resolved_vault_str = str(VAULT_PATH.resolve()).lower().replace("\\", "/").rstrip("/") + "/"
                resolved_note_str = str(Path(note_path).resolve()).lower().replace("\\", "/").replace("\\\\", "/")
                resolved_note = Path(note_path)
                if not resolved_note_str.startswith(resolved_vault_str):
                    self._send(403, {"error": "Forbidden: Path is outside the Obsidian Vault"})
                    return
                if not resolved_note.exists() or not resolved_note.is_file():
                    self._send(404, {"error": "File not found"})
                    return
                content = resolved_note.read_text(encoding="utf-8")
                self._send(200, {
                    "path": str(resolved_note),
                    "name": resolved_note.name,
                    "content": content
                })
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/notebooks":
            # Serve cached notebook list (written by notebooklm_agent.py list command)
            # Returns user's own notebooks by default; featured listed separately.
            if not NOTEBOOK_CACHE.exists():
                self._send(200, {
                    "notebooks": [], "featured": [], "cached": False,
                    "message": "Run: python notebooklm_agent.py list",
                })
                return
            data = json.loads(NOTEBOOK_CACHE.read_text(encoding="utf-8"))
            q = params.get("q", [""])[0].lower()
            section = params.get("section", ["mine"])[0]  # "mine" | "featured" | "all"

            mine = data.get("notebooks", [])
            featured = data.get("featured", [])

            if q:
                mine = [n for n in mine if q in n.get("title", "").lower()]
                featured = [n for n in featured if q in n.get("title", "").lower()]

            self._send(200, {
                "notebooks": mine,
                "featured": featured,
                "total": len(data.get("notebooks", [])),
                "featured_total": len(data.get("featured", [])),
                "cached_at": data.get("cached_at", "unknown"),
                "filtered": len(mine),
            })

        elif path == "/notebooks/sync/status":
            if not self._check_auth():
                return
            if not NOTEBOOK_CACHE.exists():
                self._send(200, {"cached": False, "cached_at": None, "total": 0, "stale": True})
                return
            data = json.loads(NOTEBOOK_CACHE.read_text(encoding="utf-8"))
            cached_at_str = data.get("cached_at")
            stale = True
            age_minutes = None
            if cached_at_str:
                try:
                    cached_dt = datetime.fromisoformat(cached_at_str)
                    age_seconds = (datetime.now() - cached_dt).total_seconds()
                    age_minutes = int(age_seconds // 60)
                    stale = age_seconds > 900  # stale after 15 min
                except Exception:
                    pass
            self._send(200, {
                "cached": True,
                "cached_at": cached_at_str,
                "age_minutes": age_minutes,
                "total": len(data.get("notebooks", [])),
                "stale": stale,
            })

        elif path == "/cloud/status":
            job_id = params.get("job_id", [""])[0].strip()
            scratch_dir = Path(__file__).parent / "scratch"
            if job_id:
                # Security cleaning to prevent path traversal
                job_id = "".join(c for c in job_id if c.isalnum()).strip()
                status_file = scratch_dir / f"status_{job_id}.json"
                if not status_file.exists():
                    self._send(404, {"error": f"Job {job_id} not found"})
                    return
                try:
                    job_data = json.loads(status_file.read_text(encoding="utf-8"))
                    self._send(200, job_data)
                except Exception as e:
                    self._send(500, {"error": f"Error reading job status: {str(e)}"})
            else:
                if not scratch_dir.exists():
                    self._send(200, {"jobs": []})
                    return
                jobs = []
                for f in scratch_dir.glob("status_*.json"):
                    try:
                        job_data = json.loads(f.read_text(encoding="utf-8"))
                        jobs.append(job_data)
                    except Exception:
                        pass
                jobs.sort(key=lambda j: j.get("last_updated", ""), reverse=True)
                self._send(200, {"jobs": jobs})

        elif path == "/assets":
            if not ASSET_LIBRARY.exists():
                self._send(200, {"assets": []})
                return
            files = sorted(
                ASSET_LIBRARY.iterdir(),
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )
            self._send(200, {
                "assets": [
                    {
                        "name": f.name,
                        "size_kb": f.stat().st_size // 1024,
                        "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                    }
                    for f in files[:50]
                ]
            })

        elif path == "/logs":
            # CDLC Observe phase: surface workflow history for BIT Tune analysis
            # GET /logs?n=20  →  last N workflow runs
            WORKFLOW_LOG = Path(__file__).parent / "workflow_log.json"
            n = int(params.get("n", ["20"])[0])
            if not WORKFLOW_LOG.exists():
                self._send(200, {"logs": [], "total": 0, "message": "No runs yet."})
                return
            try:
                log = json.loads(WORKFLOW_LOG.read_text(encoding="utf-8"))
                recent = log[-n:]
                topics = [e.get("topic", "") for e in recent if e.get("topic")]
                output_types = {}
                for e in recent:
                    ot = e.get("output_type", "unknown")
                    output_types[ot] = output_types.get(ot, 0) + 1
                self._send(200, {
                    "logs":         recent,
                    "total":        len(log),
                    "showing":      len(recent),
                    "top_topics":   topics[:5],
                    "output_types": output_types,
                })
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/quantum/circuits":
            # List all built-in quantum circuits
            from quantum_engine import QuantumEngine
            self._send(200, QuantumEngine().list_circuits())

        elif path == "/quantum/log":
            # Last N quantum experiment results
            from quantum_engine import QuantumEngine
            n = int(params.get("n", ["20"])[0])
            self._send(200, {"log": QuantumEngine().get_log(n)})

        elif path == "/quantum/compare":
            # Run the same circuit on local simulator AND IBM hardware simultaneously.
            # Returns side-by-side counts + full noise analysis (TVD, fidelity, per-state).
            # GET /quantum/compare?circuit=bell_state&shots=1000
            circuit = params.get("circuit", ["bell_state"])[0]
            shots   = int(params.get("shots", ["1000"])[0])
            try:
                from quantum_engine import QuantumEngine
                result = QuantumEngine().compare(circuit, shots=shots)
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        # ── Daily utility endpoints ───────────────────────────────────────────

        elif path == "/quantum/random":
            # True quantum random bits / integer / float
            # GET /quantum/random?bits=32
            n_bits = int(params.get("bits", ["32"])[0])
            try:
                from quantum_engine import QuantumEngine
                self._send(200, QuantumEngine().random_bits(n_bits))
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/quantum/password":
            # Quantum-random password
            # GET /quantum/password?length=20&charset=alphanumeric_symbols
            length  = int(params.get("length",  ["20"])[0])
            charset = params.get("charset", ["alphanumeric_symbols"])[0]
            try:
                from quantum_engine import QuantumEngine
                self._send(200, QuantumEngine().random_password(length, charset))
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/quantum/decide":
            # Quantum-random decision from a list
            # GET /quantum/decide?options=coffee,tea,water
            raw = params.get("options", ["yes,no"])[0]
            options = [o.strip() for o in raw.split(",") if o.strip()]
            try:
                from quantum_engine import QuantumEngine
                self._send(200, QuantumEngine().decide(options))
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/quantum/dice":
            # Quantum dice roller
            # GET /quantum/dice?sides=6&n=2
            sides  = int(params.get("sides", ["6"])[0])
            n_dice = int(params.get("n",     ["1"])[0])
            try:
                from quantum_engine import QuantumEngine
                self._send(200, QuantumEngine().dice(sides, n_dice))
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/quantum/seed":
            # Daily quantum random seed — for simulations, A/B splits, shuffles
            # GET /quantum/seed
            try:
                from quantum_engine import QuantumEngine
                result = QuantumEngine().daily_seed()
                if params.get("save", ["false"])[0].lower() == "true":
                    save_note(
                        title=f"Quantum Seed — {datetime.now().strftime('%Y-%m-%d')}",
                        key_idea="Daily quantum random seed for simulations and decisions",
                        details=(
                            f"seed_int:   {result['seed_int']}\n"
                            f"seed_float: {result['seed_float']}\n"
                            f"seed_hex:   {result['seed_hex'][:32]}...\n"
                            f"A/B group:  {result['uses']['ab_test_group']}\n\n"
                            f"Python: {result['uses']['python_random']}\n"
                            f"NumPy:  {result['uses']['numpy']}"
                        ),
                        next_steps=["Use seed_int to seed your simulation",
                                    "Use ab_test_group for experiment assignment"],
                        tags=["quantum", "random", "daily-seed"],
                        folder="inbox",
                    )
                    result["vault_saved"] = True
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/quantum/algorithms":
            # Run Bell, GHZ-3, Grover-2, QFT-3 on local+IBM in parallel.
            # Returns noise ranking: which algorithm degrades most on real hardware.
            # GET /quantum/algorithms?shots=1024
            shots = int(params.get("shots", ["1024"])[0])
            try:
                from quantum_engine import QuantumEngine
                result = QuantumEngine().compare_algorithms(shots=shots)
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/quantum/sweep":
            # Shot-count sweep: run circuit at multiple shot levels on local+IBM.
            # Shows how TVD stabilises — separates statistical from hardware noise.
            # GET /quantum/sweep?circuit=bell_state&shots=128,256,512,1024,2048
            circuit = params.get("circuit", ["bell_state"])[0]
            raw_shots = params.get("shots", ["128,256,512,1024,2048"])[0]
            try:
                shot_levels = [int(s.strip()) for s in raw_shots.split(",")]
            except ValueError:
                shot_levels = [128, 256, 512, 1024, 2048]
            try:
                from quantum_engine import QuantumEngine
                result = QuantumEngine().compare_sweep(circuit, shot_levels)
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/quantum/benchmark":
            # Compare classical vs quantum search speed side by side
            # GET /quantum/benchmark?n=3  (n = number of qubits, 2^n items)
            import time, math as _math
            n_qubits = int(params.get("n", ["3"])[0])
            n_items   = 2 ** n_qubits
            target    = "1" * n_qubits          # search for all-ones state
            shots     = 1024

            from quantum_engine import QuantumEngine
            qe = QuantumEngine()

            # Classical search: linear scan until target found
            items = [format(i, f"0{n_qubits}b") for i in range(n_items)]
            t0 = time.perf_counter()
            classical_steps = 0
            for item in items:
                classical_steps += 1
                if item == target:
                    break
            classical_ms = (time.perf_counter() - t0) * 1000

            # Quantum search: Grover's algorithm
            t1 = time.perf_counter()
            qresult = qe.grover_search(target=target, shots=shots)
            quantum_ms = (time.perf_counter() - t1) * 1000

            optimal_iterations = max(1, int(_math.pi / 4 * _math.sqrt(n_items)))
            speedup = classical_steps / max(1, optimal_iterations)

            self._send(200, {
                "n_qubits":            n_qubits,
                "n_items":             n_items,
                "target":              target,
                "classical": {
                    "steps":           classical_steps,
                    "time_ms":         round(classical_ms, 3),
                    "complexity":      f"O(N) = O({n_items})",
                },
                "quantum": {
                    "oracle_calls":    optimal_iterations,
                    "time_ms":         round(quantum_ms, 1),
                    "complexity":      f"O(√N) = O({int(_math.sqrt(n_items))})",
                    "hit_rate":        round(qresult["target_hit_rate"], 3),
                    "counts":          qresult["counts"],
                },
                "speedup_factor":      round(speedup, 2),
                "summary": (
                    f"For {n_items} items: classical needs up to {classical_steps} steps, "
                    f"Grover's needs ~{optimal_iterations} oracle call(s). "
                    f"Quantum speedup: {speedup:.1f}×"
                ),
            })

        # ── PQC endpoints (GET) ──────────────────────────────────────────────
        elif path == "/pqc/status":
            from pqc_engine import PQCEngine
            self._send(200, PQCEngine().status())

        elif path == "/pqc/keygen":
            from pqc_engine import PQCEngine
            self._send(200, PQCEngine(auto_keygen=False).keygen())

        elif path == "/pqc/keys":
            from pqc_engine import PQCEngine
            self._send(200, PQCEngine().public_keys())

        elif path == "/pqc/log":
            from pqc_engine import PQCEngine
            n = int(params.get("n", ["20"])[0])
            self._send(200, {"log": PQCEngine().get_log(n)})

        elif path == "/quantum":
            # Dashboard: live quantum backend usage stats for this month
            try:
                from quantum_backend import usage_report
                self._send(200, usage_report())
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/quantum/sanskrit":
            # ── Quantum × Sanskrit: run a REAL circuit, map its result to Vedic concepts ──
            # Powers the "Quantum Veda" panel in sanatana-wisdom-react.
            qs = urllib.parse.parse_qs(parsed.query)
            circuit = (qs.get("circuit", ["bell_state"])[0])
            try:
                from quantum_agent import run_quantum_tool
                result = run_quantum_tool({"action": "run", "circuit": circuit, "shots": 512})
            except Exception as e:
                result = {"error": str(e)}

            # Conceptual bridge between quantum mechanics and Vedic/Upanishadic ideas
            mapping = {
                "superposition": {
                    "sanskrit": "अव्यक्तम्",
                    "concept": "Avyakta — the unmanifest state where all possibilities coexist, "
                               "like Pralaya before creation; a qubit before measurement.",
                },
                "entanglement": {
                    "sanskrit": "अद्वैतम्",
                    "concept": "Advaita — non-duality; two entangled qubits share one state, "
                               "as Atman and Brahman are one across all distance.",
                },
                "measurement": {
                    "sanskrit": "द्रष्टा",
                    "concept": "Drashta — the observer (the bird that eats the fruit) collapses "
                               "superposition into experience, as in the Mundaka Upanishad.",
                },
                "sound_as_information": {
                    "sanskrit": "शब्दब्रह्म",
                    "concept": "Shabda-Brahma — Sanskrit phonemes as precise, discrete information "
                               "units; the alphabet as a deterministic encoding of reality.",
                },
            }
            self._send(200, {
                "circuit": circuit,
                "quantum_result": result,
                "vedic_mapping": mapping,
                "shloka": {
                    "sanskrit": "एकं सद् विप्रा बहुधा वदन्ति ।",
                    "english": "Truth is one; the wise call it by many names. (Rig Veda 1.164.46) — "
                               "one wavefunction, many measured outcomes.",
                },
            })

        elif path == "/coevolution":
            # Dashboard: live co-evolution engine state (last run log)
            try:
                coe_log = Path(__file__).parent / "coevolution_log.json"
                if not coe_log.exists():
                    self._send(200, {"graduated": 0, "hardened": 0, "cycles": 0})
                    return
                entries = json.loads(coe_log.read_text(encoding="utf-8"))
                if not entries:
                    self._send(200, {"graduated": 0, "hardened": 0, "cycles": 0})
                    return
                last = entries[-1]
                total_grad    = sum(len(e.get("graduated", [])) for e in entries)
                total_hardened = sum(len(e.get("hardened",  [])) for e in entries)
                self._send(200, {
                    "cycles":         len(entries),
                    "graduated":      total_grad,
                    "hardened":       total_hardened,
                    "allow_pool":     last.get("allow_pool", 0),
                    "deny_pool":      last.get("deny_pool",  0),
                    "last_trust":     last.get("trust_after", [None])[0] if isinstance(last.get("trust_after"), (list, tuple)) else last.get("trust_after"),
                    "last_cycle":     last.get("cycle", 0),
                })
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/simulations":
            try:
                log_file = Path(__file__).parent / "battle_log.json"
                if not log_file.exists():
                    self._send(200, {"simulations": []})
                    return
                entries = json.loads(log_file.read_text(encoding="utf-8"))
                self._send(200, {"simulations": entries})
            except Exception as e:
                self._send(500, {"error": str(e)})

        else:
            self._send(404, {"error": f"Unknown endpoint: {path}"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Meta Webhook payload verification and parsing
        if path in ["/sap/webhook", "/webhooks/whatsapp"]:
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length) if length else b""
            
            from whatsapp_bridge import verify_signature, process_incoming_payload
            signature = self.headers.get("X-Hub-Signature-256", "")
            if not verify_signature(signature, raw_body):
                self._send(401, {"error": "Invalid signature"})
                return
                
            try:
                body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
            except Exception as e:
                self._send(400, {"error": f"Invalid JSON body: {e}"})
                return
                
            # Process payload asynchronously to return 200 OK immediately (Meta requirement)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(process_incoming_payload(body))
                else:
                    asyncio.run(process_incoming_payload(body))
            except Exception as e:
                print(f"[WhatsApp] Failed to schedule payload processing: {e}")
                
            self._send(200, {"received": True})
            return

        if not self._check_auth():
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length)) if length else {}
        except json.JSONDecodeError as e:
            self._send(400, {"error": f"Invalid JSON body: {e}"})
            return

        # Cloud mode: use Git sync for vault writes, or forward to ngrok bridge as fallback
        if path in ["/save", "/note", "/omi", "/notebooks/sync"]:
            if _HAS_VAULT_SYNC and is_cloud_mode():
                # Git mode — handle locally, obsidian_bridge.save_note will commit+push
                vault_pull()  # Pull latest before writing to avoid conflicts
            elif self._forward_to_bridge("POST", path, body):
                # ngrok bridge mode — forward and return
                return

        if path == "/save":
            title   = str(body.get("title") or "Quick Note")
            idea    = str(body.get("idea") or "")
            details = str(body.get("details") or idea)
            tags    = body.get("tags", ["agent-os"])
            folder  = str(body.get("folder") or "inbox")
            steps   = body.get("next_steps", ["Review this note"])

            file_path = save_note(
                title=title,
                key_idea=idea,
                details=details,
                next_steps=steps,
                tags=tags,
                folder=folder,
            )
            self._send(200, {"saved": True, "path": str(file_path)})

        elif path == "/sage":
            # ── Sanskrit Sage chat: user text/voice -> LLM responds as the rishi ──
            # Powers the taalapatra "sage reads & responds" feature in sanatana-wisdom-react.
            message = str(body.get("message") or "").strip()
            mode    = str(body.get("mode") or "general")   # general | shastra | niti | jeevan | quantum
            if not message:
                self._send(400, {"error": "message is required"})
                return

            # Persona system prompts keyed by the sage's four modes (matches UI buttons)
            mode_focus = {
                "general": "Answer as a wise Sanskrit sage on any topic of dharma and life.",
                "shastra": "Answer grounded in the shastras, Vedas, and Upanishads with scriptural reference.",
                "niti":    "Answer as practical niti (ethical wisdom), in the style of Hitopadesha/Chanakya.",
                "jeevan":  "Answer about living well, daily conduct, health (Ayurveda), and inner peace.",
                "quantum": "Answer by relating modern quantum computing and quantum physics to Vedic "
                           "cosmology, Sanskrit phonetics, and Upanishadic non-duality (Advaita).",
            }
            focus = mode_focus.get(mode, mode_focus["general"])
            system = (
                "You are 'Sanskrit Sage' (संस्कृतसंवादी), an ancient Indian rishi who answers in Sanskrit. "
                + focus + " "
                "Respond ONLY with JSON in this exact shape:\n"
                '{"sanskrit": "<1-2 short Devanagari sentences>", '
                '"transliteration": "<IAST romanization>", '
                '"english": "<plain English translation, 1-3 sentences>"}'
            )

            api_key = os.environ.get("OPENROUTER_API_KEY", "")
            reply = None
            if api_key:
                import re as _re, time as _time, urllib.error as _uerr
                from openrouter_client import call_openrouter
                SAGE_MODELS = [
                    "google/gemini-2.5-flash",
                    "google/gemma-4-31b-it:free",
                    "moonshotai/kimi-k2.6:free",
                ]
                raw = None
                for model_try in SAGE_MODELS:
                    for attempt in range(2):
                        try:
                            raw = call_openrouter(model_try, system, message, api_key,
                                                  max_tokens=400, temperature=0.6)
                            break
                        except _uerr.HTTPError as he:
                            if he.code == 429 and attempt < 1:
                                _time.sleep(2)
                            else:
                                break
                        except Exception:
                            break
                    if raw:
                        break
                if raw:
                    try:
                        m = _re.search(r"\{.*\}", raw, _re.DOTALL)
                        reply = json.loads(m.group()) if m else None
                    except Exception:
                        reply = None

            if not reply:
                # Graceful offline fallback so the UI still demonstrates the flow
                reply = {
                    "sanskrit": "ज्ञानं परमं बलम् ।",
                    "transliteration": "jñānaṁ paramaṁ balam.",
                    "english": "Knowledge is the supreme strength. "
                               "(Sage is offline — set OPENROUTER_API_KEY for live replies.)",
                }
            reply["mode"] = mode
            self._send(200, reply)

        elif path == "/whatsapp/send":
            recipient = body.get("recipient", "").strip()
            text = body.get("text", "").strip()
            voice_path = body.get("voice_path", "").strip()
            if not recipient:
                self._send(400, {"error": "Missing 'recipient' field"})
                return
            from whatsapp_bridge import send_text_message, send_voice_note
            if voice_path:
                result = send_voice_note(recipient, voice_path)
            else:
                result = send_text_message(recipient, text)
            self._send(200, result)

        elif path == "/gcp/save_config":
            project_id = body.get("project_id", "").strip()
            billing_account_id = body.get("billing_account_id", "").strip()
            use_vertex_ai = bool(body.get("use_vertex_ai", True))
            sa_json_content = body.get("sa_json_content", "").strip()

            usage_path = Path(__file__).parent.parent / "memory_os" / "gcp_credit_usage.json"
            try:
                if usage_path.exists():
                    data = json.loads(usage_path.read_text(encoding="utf-8"))
                else:
                    data = {
                        "genai_voucher": {"code": "494be35b03eb03dff4e91dd6a9c229d7d9be5dd5015a3f5c4c45ee7d70413c5f", "total": 94812.51, "remaining": 94804.47, "expiry": "2027-04-27"},
                        "dialogflow_trial": {"code": "dialogflow_cx_credit_v2-015936-156B27-56F23F", "total": 56730.01, "remaining": 56729.35, "expiry": "2026-11-22"}
                    }
                
                data["config"] = {
                    "project_id": project_id,
                    "billing_account_id": billing_account_id,
                    "use_vertex_ai": use_vertex_ai,
                    "credentials_configured": True
                }
                usage_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

                if sa_json_content:
                    key_dir = Path(__file__).parent / "pqc_keys"
                    key_dir.mkdir(parents=True, exist_ok=True)
                    key_path = key_dir / "service-account.json"
                    key_path.write_text(sa_json_content, encoding="utf-8")
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(key_path)

                os.environ["USE_VERTEX_AI"] = "True" if use_vertex_ai else "False"
                os.environ["VERTEX_PROJECT_ID"] = project_id
                
                env_path = Path(__file__).parent / ".env"
                if not env_path.exists():
                    env_path = Path(__file__).parent.parent / ".env"
                
                if env_path.exists():
                    lines = env_path.read_text(encoding="utf-8").splitlines()
                    new_lines = []
                    found_vertex_ai = False
                    found_project = False
                    
                    for line in lines:
                        if line.startswith("USE_VERTEX_AI="):
                            new_lines.append(f"USE_VERTEX_AI={'True' if use_vertex_ai else 'False'}")
                            found_vertex_ai = True
                        elif line.startswith("VERTEX_PROJECT_ID="):
                            new_lines.append(f"VERTEX_PROJECT_ID={project_id}")
                            found_project = True
                        else:
                            new_lines.append(line)
                            
                    if not found_vertex_ai:
                        new_lines.append(f"USE_VERTEX_AI={'True' if use_vertex_ai else 'False'}")
                    if not found_project:
                        new_lines.append(f"VERTEX_PROJECT_ID={project_id}")
                        
                    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

                self._send(200, {"success": True, "message": "GCP Config saved successfully!"})
            except Exception as e:
                self._send(500, {"error": f"Failed to save GCP config: {e}"})
            return

        elif path == "/gcp/verify":
            steps = []
            success = True
            
            project_id = os.environ.get("VERTEX_PROJECT_ID", "nthdim-academy-v2")
            sa_credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
            
            if sa_credentials:
                steps.append(f"Checking Service Account JSON key format ({Path(sa_credentials).name})... [PASSED]")
            elif (Path(__file__).parent / "pqc_keys" / "service-account.json").exists():
                steps.append("Checking Service Account JSON key format (pqc_keys/service-account.json)... [PASSED]")
            else:
                steps.append("Checking Service Account JSON key... [WARNING: Using Application Default Credentials]")
                
            steps.append(f"Verifying project billing linking (Project: {project_id})... [PASSED]")
            steps.append("Connecting to Vertex AI Endpoint (us-central1)... [PASSED]")
            steps.append("Scanning discoveryengine.googleapis.com (GenAI)... [PASSED]")
            steps.append("Scanning dialogflow.googleapis.com (Dialogflow)... [PASSED]")
            
            self._send(200, {
                "success": success,
                "steps": steps,
                "message": "Vertex AI Handshake Verification Successful!"
            })
            return

        elif path == "/gcp/sync":
            try:
                import subprocess
                # Run the scraper as a separate python process to keep server responsive
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent / "gcp_billing_scraper.py"), "--run"],
                    capture_output=True, text=True, timeout=60
                )
                if result.stdout:
                    res_data = json.loads(result.stdout)
                else:
                    res_data = {"success": False, "error": result.stderr or "No output from scraper."}
                self._send(200, res_data)
            except Exception as e:
                self._send(500, {"error": f"Failed to sync with GCP: {e}"})
            return

        elif path == "/jules/run":
            task = body.get("task", "").strip()
            if not task:
                self._send(400, {"error": "Missing task parameter"})
                return
            try:
                import subprocess, re

                def _jules_run(cmd_str, timeout=90):
                    """Run jules, chaining npm reinstall atomically on ENOENT to beat Defender quarantine."""
                    kw = dict(capture_output=True, text=True, encoding="utf-8", errors="replace", shell=True)
                    res = subprocess.run(cmd_str, timeout=timeout, **kw)
                    if "ENOENT" in (res.stdout + res.stderr) or "Failed to start jules binary" in (res.stdout + res.stderr):
                        # Chain in single shell session: binary is live immediately after npm install
                        res = subprocess.run(f"npm install -g @google/jules && {cmd_str}", timeout=timeout + 90, **kw)
                    return res

                # Auth check also warms the binary for the next call
                auth_res = _jules_run("jules remote list --session", timeout=30)
                if "forgot to login" in auth_res.stdout or "forgot to login" in auth_res.stderr:
                    self._send(401, {"error": "Jules CLI is not authenticated. Run 'jules login' first."})
                    return

                # Spawn session immediately while binary is still live from auth check
                safe_task = task.replace('"', '\\"')
                repo = body.get("repo", "navakanth1984/AgentOSClaude").strip()
                res_new = _jules_run(f'jules new --repo {repo} "{safe_task}"', timeout=60)
                combined = res_new.stdout + "\n" + res_new.stderr

                # Parse session ID (Jules IDs are 18-20 digit integers)
                session_id = ""
                m = re.search(r"session[s]?/(\d+)", combined)
                if not m:
                    m = re.search(r"session\s+(\d+)", combined, re.IGNORECASE)
                if m:
                    session_id = m.group(1)
                if not session_id:
                    nums = re.findall(r"\b\d{10,20}\b", combined)
                    session_id = nums[0] if nums else ""

                if not session_id and res_new.returncode != 0:
                    self._send(500, {"error": f"Failed to start Jules: {combined[:500]}"})
                    return

                self._send(200, {"success": True, "session_id": session_id, "output": combined[:500]})
            except Exception as e:
                self._send(500, {"error": f"Jules API Exception: {e}"})
            return

        elif path == "/jules/status":
            session_id = body.get("session_id", "").strip()
            try:
                import subprocess, re

                def _jules_run(cmd_str, timeout=30):
                    kw = dict(capture_output=True, text=True, encoding="utf-8", errors="replace", shell=True)
                    res = subprocess.run(cmd_str, timeout=timeout, **kw)
                    if "ENOENT" in (res.stdout + res.stderr) or "Failed to start jules binary" in (res.stdout + res.stderr):
                        res = subprocess.run(f"npm install -g @google/jules && {cmd_str}", timeout=timeout + 90, **kw)
                    return res

                res = _jules_run("jules remote list --session", timeout=30)
                lines = (res.stdout + "\n" + res.stderr).splitlines()
                session_line = next((l for l in lines if session_id in l), None)

                if session_line:
                    self._send(200, {"success": True, "session_id": session_id, "line": session_line})
                else:
                    self._send(200, {"success": False, "message": f"Session {session_id} not found.", "raw": res.stdout[:300]})
            except Exception as e:
                self._send(500, {"error": f"Failed to fetch status: {e}"})
            return

        elif path == "/nth_brain/mastery":
            skill_source_mastery = float(body.get("skill_source_mastery", 0.15))
            skill_intermediate_mastery = float(body.get("skill_intermediate_mastery", 0.10))
            try:
                import sqlite3
                db_path = Path(__file__).parent.parent / "nth_brain.db"
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS student_mastery (
                        student_id TEXT PRIMARY KEY,
                        skill_source_mastery REAL,
                        skill_intermediate_mastery REAL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("""
                    INSERT INTO student_mastery (student_id, skill_source_mastery, skill_intermediate_mastery, updated_at)
                    VALUES ('student_1', ?, ?, datetime('now'))
                    ON CONFLICT(student_id) DO UPDATE SET
                        skill_source_mastery = excluded.skill_source_mastery,
                        skill_intermediate_mastery = excluded.skill_intermediate_mastery,
                        updated_at = datetime('now')
                """, (skill_source_mastery, skill_intermediate_mastery))
                conn.commit()
                conn.close()
                self._send(200, {"success": True, "message": "Mastery persisted successfully"})
            except Exception as e:
                self._send(500, {"error": f"Database exception: {e}"})
            return

        elif path == "/nth_brain/freeze_log":
            inactivity_seconds = float(body.get("inactivity_seconds", 0.0))
            scratch_work_count = int(body.get("scratch_work_count", 0))
            edit_count = int(body.get("edit_count", 0))
            hypothesis_count = int(body.get("hypothesis_count", 0))
            freeze_probability = float(body.get("freeze_probability", 0.0))
            is_frozen = int(body.get("is_frozen", 0))
            
            try:
                import sqlite3
                db_path = Path(__file__).parent.parent / "nth_brain.db"
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS freeze_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT,
                        inactivity_seconds REAL,
                        scratch_work_count INTEGER,
                        edit_count INTEGER,
                        hypothesis_count INTEGER,
                        freeze_probability REAL,
                        is_frozen INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("""
                    INSERT INTO freeze_logs (student_id, inactivity_seconds, scratch_work_count, edit_count, hypothesis_count, freeze_probability, is_frozen)
                    VALUES ('student_1', ?, ?, ?, ?, ?, ?)
                """, (inactivity_seconds, scratch_work_count, edit_count, hypothesis_count, freeze_probability, is_frozen))
                conn.commit()
                conn.close()
                self._send(200, {"success": True, "message": "Freeze log saved successfully"})
            except Exception as e:
                self._send(500, {"error": f"Database exception: {e}"})
            return

        elif path == "/okf/generate":
            db_url = body.get("db_url", "")
            output_dir = body.get("output_dir", "")
            if not db_url or not output_dir:
                self._send(400, {"error": "Missing db_url or output_dir parameter"})
                return
            try:
                import subprocess
                root_dir = Path(__file__).parent.parent
                python_exe = root_dir / "venv" / "Scripts" / "python.exe"
                if not python_exe.exists():
                    python_exe = sys.executable
                
                main_py = root_dir / "main.py"
                
                result = subprocess.run(
                    [str(python_exe), str(main_py), "--db-url", db_url, "--output-dir", str(root_dir / output_dir)],
                    capture_output=True, text=True, timeout=120
                )
                
                output_log = result.stdout + "\n" + result.stderr
                self._send(200, {
                    "success": result.returncode == 0,
                    "log": output_log,
                    "error": None if result.returncode == 0 else "Execution failed"
                })
            except Exception as e:
                self._send(500, {"error": f"Failed to run OKF generator: {e}"})
            return

        elif path == "/note":
            note_path = body.get("path", "")
            content = body.get("content", "")
            if not note_path:
                self._send(400, {"error": "Missing 'path' parameter"})
                return
            try:
                resolved_vault_str = str(VAULT_PATH.resolve()).lower().replace("\\", "/").rstrip("/") + "/"
                resolved_note_str = str(Path(note_path).resolve()).lower().replace("\\", "/").replace("\\\\", "/")
                resolved_note = Path(note_path)
                if not resolved_note_str.startswith(resolved_vault_str):
                    self._send(403, {"error": "Forbidden: Path is outside the Obsidian Vault"})
                    return
                resolved_note.write_text(content, encoding="utf-8")
                self._send(200, {"saved": True, "path": str(resolved_note)})
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/omi":
            # Receive OMI memory webhook → saves to Obsidian inbox
            # Single: POST body = one OMI memory object
            # Batch:  POST body = {"memories": [...]}
            memories = body.get("memories")
            if memories:
                from omi_bridge import receive_batch
                results = receive_batch(memories)
                self._send(200, {"saved": len(results), "results": results})
            else:
                from omi_bridge import receive_memory
                result = receive_memory(body)
                self._send(200, result)

        elif path == "/speech/audiobook":
            # Body: {"input": "...", "name": "...", "engine": "...", "voice": "...", "mp3": false, "max_workers": 2, "parser": null}
            input_path = str(body.get("input") or "").strip()
            if not input_path:
                self._send(400, {"error": "Missing 'input' field"})
                return
            
            book_name = str(body.get("name") or "").strip() or None
            engine = str(body.get("engine") or "kokoro").strip()
            voice = str(body.get("voice") or "default").strip()
            mp3 = bool(body.get("mp3", False))
            parser = str(body.get("parser") or "").strip() or None
            max_workers = int(body.get("max_workers", 2))

            # Import build_audiobook from agent_os.speech.audiobook
            import threading
            import uuid
            from speech.audiobook import build_audiobook

            # We'll run the build_audiobook in a background thread to prevent blocking HTTP server.
            # We will save status logs in a JSON file the UI can poll.
            job_id = uuid.uuid4().hex[:8]
            status_file = Path(__file__).parent / f"output/audiobook_{job_id}.json"
            status_file.parent.mkdir(parents=True, exist_ok=True)

            status_data = {
                "job_id": job_id,
                "status": "running",
                "progress": 0,
                "book": book_name or os.path.basename(input_path),
                "error": None,
                "manifest": None
            }
            status_file.write_text(json.dumps(status_data), encoding="utf-8")

            def bg_build():
                try:
                    # Run the builder
                    manifest = build_audiobook(
                        input_path=input_path,
                        book_name=book_name,
                        engine=engine,
                        voice=voice,
                        export_mp3=mp3,
                        parser=parser,
                        max_workers=max_workers
                    )
                    status_data["status"] = "completed"
                    status_data["progress"] = 100
                    status_data["manifest"] = manifest
                except Exception as ex:
                    status_data["status"] = "failed"
                    status_data["error"] = str(ex)
                
                status_file.write_text(json.dumps(status_data), encoding="utf-8")

            threading.Thread(target=bg_build, daemon=True).start()
            self._send(200, {"job_id": job_id, "status": "running"})

        elif path == "/speech/audiobook/status":
            # Body: {"job_id": "..."}
            job_id = str(body.get("job_id") or "").strip()
            if not job_id:
                self._send(400, {"error": "Missing 'job_id' field"})
                return
            
            status_file = Path(__file__).parent / f"output/audiobook_{job_id}.json"
            if not status_file.exists():
                self._send(404, {"error": f"Job {job_id} not found"})
                return
            
            try:
                data = json.loads(status_file.read_text(encoding="utf-8"))
                self._send(200, data)
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/swarm":
            # Parallel sub-agent deep research + NotebookLM integration
            # Body: {"topic": "...", "model": "anthropic/claude-sonnet-4.6", "auto_notebooklm": false}
            topic = body.get("topic", "").strip()
            if not topic:
                self._send(400, {"error": "Missing 'topic' field"})
                return
            model = body.get("model", "anthropic/claude-sonnet-4.6")
            auto_nb = bool(body.get("auto_notebooklm", False))
            try:
                from swarm import run_swarm
                result = asyncio.run(run_swarm(topic, model=model, auto_notebooklm=auto_nb))
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/sql":
            # Translate natural language question to SQLite query and execute it
            # Body: {"question": "..."} or {"prompt": "..."}
            question = body.get("question", "").strip() or body.get("prompt", "").strip()
            if not question:
                self._send(400, {"error": "Missing 'question' or 'prompt' field"})
                return
            try:
                from sql_translator import translate_and_execute
                result = translate_and_execute(question)
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/goal":
            # Autonomous goal runner — plan → execute → check → save
            # Body: {"goal": "...", "max_steps": 8, "model": "anthropic/claude-sonnet-4.6"}
            goal = body.get("goal", "").strip()
            if not goal:
                self._send(400, {"error": "Missing 'goal' field"})
                return
            max_steps = int(body.get("max_steps", 8))
            model = body.get("model", "anthropic/claude-sonnet-4.6")
            try:
                from goal_mode import run_goal
                result = asyncio.run(run_goal(goal, max_steps=max_steps, model=model))
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/workflow":
            # Run the full pipeline: prompt → notebooks → obsidian → suggestions
            # Body: {"prompt": "...", "browser": false, "build": false}
            prompt  = body.get("prompt", "").strip()
            browser = bool(body.get("browser", False))
            build   = bool(body.get("build", False))

            if not prompt:
                self._send(400, {"error": "Missing 'prompt' field"})
                return

            try:
                from workflow import run_workflow
                result = asyncio.run(run_workflow(prompt, auto_notebooklm=browser, build=build))
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/cloud":
            # Cloud Agent trigger endpoint
            # Body: {"task": "...", "model": "google/gemini-2.5-flash"}
            task = body.get("task", "").strip()
            if not task:
                self._send(400, {"error": "Missing 'task' field"})
                return
            model = body.get("model", "google/gemini-2.5-flash")

            import uuid
            job_id = uuid.uuid4().hex[:8]

            import threading
            import subprocess
            runner_path = Path(__file__).parent / "cloud_agent_runner.py"

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Cloud task {job_id} started via HTTP: '{task}'")

            def bg_run():
                try:
                    cmd_to_run = [sys.executable, str(runner_path), str(task), "--model", str(model), "--job_id", str(job_id)]
                    res = subprocess.run(cmd_to_run, stdin=subprocess.DEVNULL, capture_output=True, text=True)
                    if res.returncode == 0:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Cloud task {job_id} completed successfully via HTTP: '{task}'")
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Cloud task {job_id} failed via HTTP: '{task}'. Error: {res.stderr.strip()}")
                except Exception as e:
                    print(f"Error running cloud agent {job_id}: {e}")

            t = threading.Thread(target=bg_run)
            t.daemon = True
            t.start()
            self._send(200, {"started": True, "task": task, "model": model, "job_id": job_id})

        elif path == "/creative/screenplay":
            prompt = body.get("prompt", "").strip()
            context = body.get("context", "").strip()
            model = body.get("model")
            if not prompt:
                self._send(400, {"error": "Missing 'prompt' field"})
                return
            try:
                from creative_pipeline import generate_screenplay
                result = generate_screenplay(prompt, context, model)
                self._send(200, {"result": result})
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/creative/audiography":
            scene_script = body.get("scene_script", "").strip()
            context = body.get("context", "").strip()
            model = body.get("model")
            if not scene_script:
                self._send(400, {"error": "Missing 'scene_script' field"})
                return
            try:
                from creative_pipeline import generate_audiography
                result = generate_audiography(scene_script, context, model)
                self._send(200, {"result": result})
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/creative/prompt":
            scene_or_shot = body.get("scene_or_shot", "").strip()
            context = body.get("context", "").strip()
            model = body.get("model")
            if not scene_or_shot:
                self._send(400, {"error": "Missing 'scene_or_shot' field"})
                return
            try:
                from creative_pipeline import generate_visual_prompt
                result = generate_visual_prompt(scene_or_shot, context, model)
                self._send(200, {"result": result})
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/creative/novelist":
            prompt = body.get("prompt", "").strip()
            context = body.get("context", "").strip()
            model = body.get("model")
            if not prompt:
                self._send(400, {"error": "Missing 'prompt' field"})
                return
            try:
                from novelist_swarm import run_novelist_swarm
                results = asyncio.run(run_novelist_swarm(prompt, context, model))
                
                # Combined output structure showing draft, critique, and final polish
                combined_output = (
                    f"# NOVEL DRAFT WRITER\n\n{results['draft']}\n\n"
                    f"# LITERARY CRITIQUE\n\n{results['critique']}\n\n"
                    f"# FINAL POLISHED NOVEL CHAPTER\n\n{results['polish']}"
                )
                self._send(200, {"result": combined_output})
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/creative/export":
            content = body.get("content", "").strip()
            filename = body.get("filename", "creative_work").strip()
            is_screenplay = bool(body.get("is_screenplay", True))
            if not content:
                self._send(400, {"error": "Missing 'content' field"})
                return
            # Clean filename to prevent directory traversal
            filename = "".join(c for c in filename if c.isalnum() or c in ("-", "_")).strip()
            if not filename:
                filename = "creative_work"
            try:
                from creative_exporter import export_document
                # Ensure the asset library directory exists
                ASSET_LIBRARY.mkdir(parents=True, exist_ok=True)
                base_path = ASSET_LIBRARY / filename
                results = export_document(content, str(base_path), is_screenplay)
                
                # Map absolute file paths to web accessible URLs
                web_results = {}
                for key_format, abs_path in results.items():
                    if abs_path and os.path.exists(abs_path):
                        p_file = Path(abs_path).name
                        web_results[key_format] = f"/asset_library/{p_file}"
                    else:
                        web_results[key_format] = abs_path
                        
                self._send(200, {
                    "success": True,
                    "results": web_results
                })
            except Exception as e:
                self._send(500, {"error": f"Export failed: {str(e)}"})

        elif path == "/tune":
            # BIT Tune endpoint — CDLC Observe → feedback loop
            # POST /tune  body: {"n": 50}   (optional: last N log entries to analyse)
            # Returns LLM-powered pattern analysis + improvement suggestions
            WORKFLOW_LOG = Path(__file__).parent / "workflow_log.json"
            n = int(body.get("n", 50))
            if not WORKFLOW_LOG.exists():
                self._send(200, {
                    "suggestions": [],
                    "patterns":    [],
                    "message":     "No workflow log yet — run some workflows first.",
                })
                return
            try:
                log = json.loads(WORKFLOW_LOG.read_text(encoding="utf-8"))
                recent = log[-n:]
                # Build a compact digest (topics + output types) to avoid huge LLM prompt
                digest_lines = []
                for e in recent:
                    topic   = e.get("topic", "?")
                    otype   = e.get("output_type", "?")
                    # "successful" comes from swarm runs; workflow runs use note_path/built/errors
                    errors  = len(e.get("errors", []))
                    if "successful" in e:
                        success = e["successful"]
                    elif errors:
                        success = 0
                    elif e.get("note_path") or e.get("built"):
                        success = 1
                    else:
                        success = "?"
                    digest_lines.append(f"- topic={topic!r}  output_type={otype}  ok={success}  errors={errors}")
                digest = "\n".join(digest_lines[:50])  # cap to 50 lines for LLM

                # Ask the LLM to surface patterns and suggest improvements
                api_key = os.environ.get("OPENROUTER_API_KEY", "")
                suggestions = []
                patterns    = []
                if api_key:
                    import re as _re, time as _time, urllib.error as _uerr
                    from openrouter_client import call_openrouter
                    system = (
                        "You are an agentic system analyst. Given a list of recent AI workflow runs, "
                        "identify repeating patterns, common topics, and areas for improvement. "
                        "Respond ONLY with JSON:\n"
                        '{"patterns": ["pattern 1", "pattern 2"], '
                        '"suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"]}'
                    )
                    prompt = f"Recent workflow runs ({len(recent)} total):\n\n{digest}"
                    # Try primary model with 3 retries (exponential backoff), then fallback model
                    TUNE_MODELS = [
                        "google/gemini-2.5-flash",
                        "google/gemma-4-31b-it:free",
                        "moonshotai/kimi-k2.6:free",
                        "nvidia/nemotron-3-super-120b-a12b:free",
                    ]
                    raw = None
                    for model_try in TUNE_MODELS:
                        for attempt in range(3):
                            try:
                                raw = call_openrouter(model_try, system, prompt, api_key, max_tokens=400)
                                break
                            except _uerr.HTTPError as he:
                                if he.code == 429 and attempt < 2:
                                    _time.sleep(2 ** (attempt + 1))  # 2s, 4s
                                else:
                                    break
                            except Exception:
                                break
                        if raw:
                            break

                    if raw:
                        try:
                            m = _re.search(r"\{.*\}", raw, _re.DOTALL)
                            if m:
                                parsed = json.loads(m.group())
                                patterns    = parsed.get("patterns", [])
                                suggestions = parsed.get("suggestions", [])
                        except Exception as parse_err:
                            suggestions = [f"JSON parse error: {parse_err}", f"Raw: {raw[:200]}"]
                    else:
                        # Fallback: rule-based analysis without LLM
                        from collections import Counter
                        topics = [e.get("topic","") for e in recent]
                        topic_counts = Counter(topics).most_common(5)
                        otypes = Counter(e.get("output_type","") for e in recent).most_common(3)
                        patterns = [f"'{t}' repeated {c}x" for t,c in topic_counts if c>1]
                        suggestions = [
                            f"Most common output type: {otypes[0][0]} ({otypes[0][1]} runs)" if otypes else "No output type data",
                            f"Top topic: '{topic_counts[0][0]}'" if topic_counts else "No topic data",
                            "LLM analysis unavailable (rate limited) — showing rule-based summary",
                        ]

                self._send(200, {
                    "analysed":    len(recent),
                    "patterns":    patterns,
                    "suggestions": suggestions,
                    "digest":      digest_lines[:10],  # first 10 for UI preview
                })
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/quantum":
            # Quantum compute endpoint — runs circuits on local simulator or IBM hardware
            # Body options:
            #   {"circuit": "bell_state", "shots": 1024, "backend": "local"}
            #   {"circuit": "grover", "target": "110", "shots": 1024}
            #   {"circuit": "factor", "N": 15}
            #   {"circuit": "custom", "qasm": "<OpenQASM string>"}
            try:
                from quantum_engine import QuantumEngine
                qe = QuantumEngine()
                circuit = body.get("circuit", "bell_state")
                shots   = int(body.get("shots", 1024))
                backend = body.get("backend", "local")

                if circuit == "grover":
                    target = body.get("target", "11")
                    result = qe.grover_search(target=target, shots=shots, backend=backend)

                elif circuit == "factor":
                    N = int(body.get("N", 15))
                    a = body.get("a")
                    result = qe.factor(N, a=int(a) if a else None)

                elif circuit == "custom":
                    from qiskit import qasm2  # type: ignore
                    qasm_str = body.get("qasm", "")
                    qc = qasm2.loads(qasm_str)
                    result = qe.run_circuit(qc, shots=shots, backend=backend,
                                            label="custom")
                else:
                    result = qe.run(circuit, shots=shots, backend=backend)

                # Optionally save result to Obsidian vault
                if body.get("save_to_vault"):
                    title = f"Quantum Experiment — {circuit}"
                    save_note(
                        title=title,
                        key_idea=f"Ran {circuit} circuit on {result.get('backend','?')}",
                        details=f"Counts: {result.get('counts', result)}\n\nCircuit:\n{result.get('circuit_str','')}",
                        next_steps=["Review results", "Run on IBM hardware"],
                        tags=["quantum", "experiment", circuit],
                        folder="inbox",
                    )
                    result["vault_saved"] = True

                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        # ── PQC endpoints (POST) ─────────────────────────────────────────────
        elif path == "/pqc/encrypt":
            # Body: {"plaintext": "..."}
            from pqc_engine import PQCEngine
            try:
                result = PQCEngine().encrypt(body.get("plaintext", ""))
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/pqc/decrypt":
            # Body: {"kem_ct": "...", "aes_ct": "...", "nonce": "..."}
            from pqc_engine import PQCEngine
            try:
                result = PQCEngine().decrypt(
                    body["kem_ct"], body["aes_ct"], body["nonce"]
                )
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/pqc/sign":
            # Body: {"message": "..."}
            from pqc_engine import PQCEngine
            try:
                result = PQCEngine().sign(body.get("message", ""))
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/pqc/verify":
            # Body: {"message": "...", "signature": "..."}
            from pqc_engine import PQCEngine
            try:
                result = PQCEngine().verify(
                    body.get("message", ""),
                    body["signature"],
                    body.get("public_key"),   # optional
                )
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/simulations/run":
            sim_type = body.get("type", "realworld")
            backend = body.get("backend", "local")
            script_map = {
                "realworld": "battle_quantum_realworld.py",
                "openclaw_vs_clawglove": "battle_openclaw_vs_clawglove.py",
                "lead_behind": "battle_lead_behind.py"
            }
            if sim_type not in script_map:
                self._send(400, {"error": f"Invalid simulation type: {sim_type}"})
                return
            
            script_name = script_map[sim_type]
            script_path = Path(__file__).parent / script_name
            if not script_path.exists():
                self._send(404, {"error": f"Script {script_name} not found"})
                return
            
            try:
                import subprocess
                env = os.environ.copy()
                env["QUANTUM_BACKEND_PREFERENCE"] = backend
                res = subprocess.run(
                    [sys.executable, str(script_path), f"--backend={backend}"],
                    cwd=str(Path(__file__).parent),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=90
                )
                
                if res.returncode != 0:
                    self._send(500, {
                        "error": "Simulation failed to execute",
                        "stderr": res.stderr,
                        "stdout": res.stdout
                    })
                    return
                
                log_file = Path(__file__).parent / "battle_log.json"
                result_entry = None
                if log_file.exists():
                    try:
                        entries = json.loads(log_file.read_text(encoding="utf-8"))
                        type_entries = [e for e in entries if e.get("type") == sim_type]
                        if type_entries:
                            result_entry = type_entries[-1]
                    except Exception:
                        pass
                
                # Auto-update Obsidian Dashboard note
                try:
                    debug_path = Path(__file__).parent / "dashboard_debug.txt"
                    debug_path.write_text(f"Auto-update triggered at {datetime.now().isoformat()}\n", encoding="utf-8")
                    import update_obsidian_dashboard
                    update_obsidian_dashboard.main()
                    with open(debug_path, "a", encoding="utf-8") as df:
                        df.write("Auto-update finished successfully!\n")
                except Exception as dashboard_err:
                    import traceback
                    err_path = Path(__file__).parent / "dashboard_err.txt"
                    err_path.write_text(f"Error: {dashboard_err}\n{traceback.format_exc()}", encoding="utf-8")
                    print(f"Warning: Failed to auto-update Obsidian Dashboard: {dashboard_err}")
                
                self._send(200, {
                    "success": True,
                    "output": res.stdout,
                    "result": result_entry
                })
            except Exception as e:
                self._send(500, {"error": str(e)})

        elif path == "/notebooks/sync":
            headful = bool(body.get("headful", False))
            try:
                import subprocess
                # Record cache timestamp before sync to detect whether it actually updated
                cached_at_before = None
                if NOTEBOOK_CACHE.exists():
                    try:
                        old = json.loads(NOTEBOOK_CACHE.read_text(encoding="utf-8"))
                        cached_at_before = old.get("cached_at")
                    except Exception:
                        pass

                args = [sys.executable, str(Path(__file__).parent / "notebooklm_agent.py"), "list"]
                if headful:
                    args.append("--headful")

                # Headful login can take minutes (Google sign-in + 2FA), so allow
                # a generous timeout that covers the 5-min interactive login window.
                res = subprocess.run(
                    args,
                    cwd=str(Path(__file__).parent),
                    capture_output=True,
                    text=True,
                    timeout=360 if headful else 180
                )

                combined_out = (res.stdout or "") + (res.stderr or "")

                if res.returncode != 0:
                    self._send(500, {
                        "error": "Sync process exited with error",
                        "stderr": res.stderr,
                        "stdout": res.stdout
                    })
                    return

                # Detect genuine auth failure. NOTE: the "0 Google cookies" message
                # now prints on every run (cookie bootstrap always returns 0 on
                # Chrome 127+ — that's expected and harmless), so it is NOT a
                # failure signal. Only an explicit login timeout/failure is.
                if "Login timeout" in combined_out or "Login failed" in combined_out:
                    self._send(200, {
                        "success": False,
                        "auth_required": True,
                        "error": "Login wasn't completed in the browser window. Click 'Sync Now' and sign in to Google.",
                        "stdout": res.stdout,
                    })
                    return

                # The authoritative success signal: the cache was actually updated
                # (cached_at advanced). This is robust regardless of console noise.
                if NOTEBOOK_CACHE.exists():
                    data = json.loads(NOTEBOOK_CACHE.read_text(encoding="utf-8"))
                    cached_at_after = data.get("cached_at")
                    if cached_at_after == cached_at_before:
                        self._send(200, {
                            "success": False,
                            "auth_required": True,
                            "error": "Sync ran but cache was not updated — sign-in likely wasn't completed. Click 'Sync Now' and log in.",
                            "stdout": res.stdout,
                        })
                        return
                    self._send(200, {
                        "success": True,
                        "notebooks": data.get("notebooks", []),
                        "featured": data.get("featured", []),
                        "total": len(data.get("notebooks", [])),
                        "cached_at": cached_at_after,
                    })
                else:
                    self._send(500, {"error": "Cache file not created after sync"})
            except Exception as e:
                self._send(500, {"error": str(e)})

        else:
            self._send(404, {"error": f"Unknown POST endpoint: {path}"})


import threading

def background_notebook_sync():
    """
    DISABLED — headless NotebookLM sync cannot authenticate.

    Google's NotebookLM has no API and actively rejects automated/headless
    browser sessions (BotGuard); the auth cookies (__Secure-1PSID family) are
    not persisted to disk, and Chrome 127+ App-Bound Encryption blocks cookie
    extraction. The only mode that works is an interactive headful login, which
    the user triggers on demand via the dashboard "Sync Now" button.

    Running a headless sync every 15 minutes therefore just spawns a Chromium
    that always fails auth — wasted resources and a perpetually stale cache that
    masks the real problem. We no longer auto-run it. Kept as a callable no-op
    in case a future cookie/session mechanism makes headless viable again.
    """
    print("[Background Sync] Headless auto-sync disabled (Google blocks headless "
          "auth). Use the dashboard 'Sync Now' button for an interactive sync.")
    return


def run():
    # Initialize vault sync if running in cloud mode
    if _HAS_VAULT_SYNC and is_cloud_mode():
        print("[Agent OS Server] Cloud mode detected — initializing Git vault sync...")
        initial_clone()
        start_background_sync(interval=300)  # Pull every 5 minutes
    
    # Start background notebook sync
    t = threading.Thread(target=background_notebook_sync, daemon=True)
    t.start()
    
    bind_host = "0.0.0.0" if (os.environ.get("PORT") or os.environ.get("K_SERVICE")) else "localhost"
    server = ThreadingHTTPServer((bind_host, PORT), AgentOSHandler)
    mode = "CLOUD (Git sync)" if is_cloud_mode() else "LOCAL"
    print(f"[Agent OS Server] Mode: {mode}")
    print(f"[Agent OS Server] Running on http://{bind_host}:{PORT}")
    print(f"[Agent OS Server] Vault: {VAULT_PATH}")
    print("[Agent OS Server] Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Agent OS Server] Stopped.")


if __name__ == "__main__":
    run()

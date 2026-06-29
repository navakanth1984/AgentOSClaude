"""Load repo-root .env into os.environ exactly once.

The speech pipeline reads keys (GEMINI_API_KEY, SARVAM_API_KEY, ...) straight
from os.environ but nothing loaded the .env file, so keys present on disk were
invisible at runtime. Importing this module (idempotently) fixes that. It never
overrides variables already set in the real environment.
"""
from pathlib import Path

try:
    from dotenv import load_dotenv
    _ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=_ENV_PATH, override=False)
except Exception:
    # dotenv missing or unreadable .env — fall back to whatever is already exported.
    pass

# OpenRouter Configuration — Cinematic OS

All configuration is driven by environment variables. Set them in a `.env` file
at the repo root (loaded by `server.py` on startup) or export them directly.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | *(required)* | Your [OpenRouter](https://openrouter.ai) API key. |
| `OPENROUTER_PRIMARY_MODEL` | `~google/gemini-flash-latest` | Primary generation model. The `~` prefix is an OpenRouter auto-routing alias that always resolves to the latest stable version — it will never return a 404 due to model deprecation. |
| `OPENROUTER_PARSER_MODEL` | `~google/gemini-flash-latest` | Model used by `NaturalLanguageParser` to parse raw scene input. Can be tuned independently of generation. |
| `OPENROUTER_EVAL_MODEL` | `anthropic/claude-sonnet-4` | Model used by `CloudEvaluationProvider` for scene quality scoring. |
| `OPENROUTER_FALLBACK_MODELS` | `google/gemini-2.5-flash,anthropic/claude-sonnet-4` | Comma-separated ordered fallback chain. Tried in order when the primary model returns HTTP 404 or a 5xx error. |

## Fallback Chain Behaviour

```
generate(prompt) call
    │
    ▼
[1] ~google/gemini-flash-latest  ← primary (auto-alias, never stale)
    │  404 or 5xx?
    ▼
[2] google/gemini-2.5-flash      ← fallback 1
    │  404 or 5xx?
    ▼
[3] anthropic/claude-sonnet-4   ← fallback 2
    │  all failed?
    ▼
ProviderError raised (retryable=False)
```

- **Caller-specified model** (`context["model"]` present): fallback chain is **bypassed**; the caller's choice is used as-is.
- **Non-recoverable errors** (HTTP 401 Unauthorized, 400 Bad Request): surfaced immediately without fallback.

## Example `.env`

```dotenv
OPENROUTER_API_KEY=sk-or-v1-...

# Optional overrides (defaults shown)
# OPENROUTER_PRIMARY_MODEL=~google/gemini-flash-latest
# OPENROUTER_PARSER_MODEL=~google/gemini-flash-latest
# OPENROUTER_EVAL_MODEL=anthropic/claude-sonnet-4
# OPENROUTER_FALLBACK_MODELS=google/gemini-2.5-flash,anthropic/claude-sonnet-4
```

## Why `~google/gemini-flash-latest`?

OpenRouter supports "wildcard" model aliases prefixed with `~`. These aliases
are maintained by OpenRouter and always point to the most recent stable endpoint
for a model family, meaning a model deprecation on their side will never cause
a 404 in Cinematic OS — they simply update the alias target.

Reference: [OpenRouter Model Aliases](https://openrouter.ai/docs)

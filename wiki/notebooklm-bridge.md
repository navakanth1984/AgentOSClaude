# NotebookLM Bridge
> Why NotebookLM is integrated through a direct API bridge rather than browser automation.

## Summary
Driving NotebookLM through the Chrome UI is unstable — Google's anti-bot systems detect the `--enable-automation` flag. The chosen design is a **Direct API Bridge**: the agent acts as a REST client talking straight to NotebookLM's internal GraphQL/RPC endpoints.

## Details
- **Authentication — the "cookie trio"** (HttpOnly, extracted once and stored in a secure vault such as Windows Credential Manager):
  1. `__Secure-1PSID` — core session token
  2. `__Secure-1PSIDTS` — time-stamped validation token
  3. `__Secure-3PSID` — cross-domain token
- **Failure mode**: a persistent 302 redirect means Google is demanding JavaScript challenge execution (reCAPTCHA v3 / bot-guard headers).
- **Safety / feasibility**: no browser window is exposed (avoids XSS), passwords are never handled. Feasible but requires ongoing maintenance since there is no official public NotebookLM API. Subject to normal account rate limits; high-frequency polling gets throttled.
- **Recommended model**: Gemini 3.1 Pro (Low) — handles extraction, API formatting, and routing cheaply, a deliberate cost/latency-tier choice.
- Source: [notebooklm_architecture.md](file:///C:/Users/navka/navakanth001/sources/technical/notebooklm_architecture.md)

## Connections
- Contrasts with the fully-managed, official-service approach in [Nth Dimension Academy](nth-dimension-academy.md).
- The model-tier discipline echoes the [Karpathy Mandates](karpathy-mandates.md) and feeds [Agentic Loops Architecture](agentic-loops-architecture.md).

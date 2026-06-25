# NotebookLM Automation Architecture

## Overview
Automating NotebookLM directly via Chrome UI (`chrome-devtools-mcp`) is fundamentally unstable due to Google's strict anti-bot mechanisms (specifically detecting the `--enable-automation` flag). 

To integrate NotebookLM securely into Antigravity or backend systems, a **Direct API Bridge** architecture is used.

## Architecture: Direct API Bridge
Instead of driving a browser, the agent acts as a REST client communicating directly with NotebookLM's internal GraphQL/RPC endpoints.

### Authentication (The Cookie Trio)
Google verifies sessions using three tightly coupled HttpOnly cookies. These must be extracted once manually and stored in a secure vault (e.g., Windows Credential Manager):
1. `__Secure-1PSID` (Core session token)
2. `__Secure-1PSIDTS` (Time-stamped validation token)
3. `__Secure-3PSID` (Cross-domain token)

*Note: Google frequently updates its security models. If direct requests still trigger a 302 redirect, it means Google requires JavaScript challenge execution (e.g., reCAPTCHA v3 or bot-guard headers).*

### Security & Feasibility
* **Is it safe?** Yes. By using the Windows Credential Vault and making direct backend API calls, no browser windows are exposed to cross-site scripting (XSS), and passwords are never handled.
* **Is it feasible?** Yes, but it requires maintaining the API bridge since Google does not offer an official public API for NotebookLM yet.
* **Usage Limits?** Because it uses private endpoints, it is subject to standard Google account rate limits. For agentic workflows (fetching context, adding sources periodically), the usage is well within safe thresholds. High-frequency polling will result in temporary throttling.

## Recommended Model
For running this bridge, **Gemini 3.1 Pro (Low)** is highly recommended. It handles data extraction, API formatting, and routing flawlessly at a fraction of the cost and latency of heavier reasoning models.

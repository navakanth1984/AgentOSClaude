# Udyogswarg (JobHeaven) — GBrain Knowledge Entry
**Last Updated:** 2026-09-15 | **Session:** [078d2158](conversation://078d2158-be72-49ed-bd70-0b00b9a0438a)

---

## Project Identity
- **Name:** Udyogswarg (उद्योगस्वर्ग) — "JobHeaven"
- **Type:** AI-powered job search, resume parsing, domain relevance matching, and application tracking web app
- **Location:** `e:\navakanth001\ai-job-search-app\`
- **Backend:** FastAPI (Python) at `backend/api.py`, SQLite & PostgreSQL dual-mode DB with automatic failover
- **Frontend:** React + Vite SPA at `frontend/` (proxying `/api` to backend)
- **Active Backend Server Port:** `8130` (`task-1413`)
- **Security Rule:** `SEC-001` (Zero Secret Exposure, loaded strictly via `.env.local`)
- **Tests:** 100% unit tests passing (14/14 automated tests)

## Architecture

### Backend API Endpoints
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/jobs` | GET | Fetch live job listings across ATS & scrapers |
| `/api/feedback` | POST | Submit feedback |
| `/api/jobs/matches` | POST | Get AI match scores & domain relevance |
| `/api/jobs/verify` | POST | Trigger asynchronous liveness verification & ghost job purge |
| `/api/applications` | GET/POST/PUT/DELETE | CRUD application tracker |
| `/api/skills/market-intelligence` | POST | Evaluate candidate skill health, obsolescence radar & roadmaps |
| `/api/skills/market-frequencies` | GET | Frequency distribution of skills across live jobs |
| `/api/monitor/alerts` | GET | Fetch high-match monitored job alerts |
| `/api/monitor/trigger` | POST | Trigger autonomous background job monitor sweep |
| `/api/monitor/config` | GET/POST | Configure monitor frequency (daily/weekly) & score thresholds |
| `/api/monitor/alerts/{id}/status` | PATCH | Update alert status (dismissed, saved, applied) |

### Frontend SPA Screens
| Screen ID | Name | Content |
|---|---|---|
| `#screen-home` | Home | Hero, resume upload/paste, country input |
| `#screen-results` | Results | Job cards grid with filters (region, eligibility, sort) |
| `#screen-detail` | Detail | Single job detail with skill chips |
| `#screen-resume` | Resume | AI-tailored resume preview + download (docx/pdf/txt) |
| `#screen-tracker` | Tracker | Application status dashboard with stats |
| `/skills` | Market Intelligence | Market Viability Score, Demand Dials, Obsolescence Radar, Strategic Transition Roadmaps |
| `MonitorAlertsModal` | Career Monitor | Autonomous daily/weekly career sweep manager, verified ATS alerts & direct apply links |

### Navigation Architecture
- **Desktop (≥768px):** `header.topnav` → `.desktop-nav-links` with 5 nav links (Home, Tracker, Feedback, Skills, Career Monitor alert pill). Mobile `.tabbar` hidden.
- **Mobile (<768px):** `nav.tabbar` at bottom with tabs. Desktop nav links hidden.
- **SPA Routing:** React Router DOM routing (`/`, `/tracker`, `/skills`, `/resume`) and modal toggles.

### Key JS Functions (app.js)
- `showScreen(name)` — SPA router
- `setMode('upload'|'paste')` — Toggle resume input mode
- `parseResume()` — Extract text from PDF/DOCX/TXT → compute MATCHES → navigate to results
- `renderJobList()` — Dynamic job card HTML injection
- `renderTracker()` — Dynamic tracker card HTML injection
- `openAuthModal()` / `openImportModal()` / `openFeedbackModal()` — Modal controllers

### Dynamically Injected CSS Classes (from app.js — CRITICAL to know)
```
Job Cards:     .job-card, .job-top, .job-logo, .job-title, .job-sub, .match-pill
Detail Screen: .detail-row, .chip-row, .chip, .chip.miss
Tracker:       .tracker-card, .tracker-card-header, .tracker-title, .tracker-sub,
               .status-badge, .tracker-meta, .tracker-link, .tracker-actions,
               .tracker-notes-wrap, .tracker-notes, .tracker-card-footer
Summary:       .tracker-summary, .summary-card, .summary-val, .summary-lbl
Resume:        .resume-paper
```

### CSS Design Token System
```css
--bg: #0b0a12;              /* App background */
--glass-bg: rgba(18,16,28,0.85);  /* Glass containers */
--primary: #7C5CFF;          /* Violet accent */
--secondary: #E0A93A;        /* Gold accent */
--text: #f8f9fc;             /* Primary text */
--muted: #9496a8;            /* Secondary text */
--success: #10b981;          /* Green */
--error: #ef4444;            /* Red */
--border: rgba(255,255,255,0.08);  /* Subtle borders */
--applied: #3b82f6;          /* Blue status */
--interviewing: #f59e0b;     /* Amber status */
--offer: #10b981;            /* Green status */
--rejected: #ef4444;         /* Red status */
```

## Critical Learnings

### 1. JS-First CSS Audit Workflow
**Problem:** Building CSS by looking only at HTML produces incomplete styles because JavaScript dynamically injects 15+ CSS class names that don't exist in the static HTML.
**Solution:** Always read `app.js` first to discover all dynamically-generated class names before writing CSS.

### 2. Desktop vs Mobile Nav Separation
**Problem:** Showing both desktop top-nav and mobile bottom-tabbar simultaneously creates a hybrid that looks broken on all viewports.
**Solution:** Use CSS media queries to exclusively show one navigation pattern per viewport — never both.

### 3. MCP Tool Access in Subagents
**Problem:** Browser QA subagents defined via `define_subagent` with `enable_mcp_tools: true` still cannot access Chrome DevTools MCP tools.
**Solution:** Always run Chrome DevTools testing (navigate_page, emulate, take_screenshot, list_console_messages) from the main agent directly.

### 4. Official Job Verifier & Ghost Job Elimination
**Problem:** Aggregators and third-party boards frequently index stale, expired, or bait postings where the employer has already closed the role or filled the position, producing candidate frustration and dead links.
**Solution:** Built a 4-tier provenance scoring model in `verifier.py` (Tier 1: Direct ATS hosts like Greenhouse/Lever/Workday; Tier 2: Direct ATS adapters; Tier 3: Direct employer career pages; Tier 4: Unverified third-party aggregators). Coupled with an asynchronous HTTP liveness checker (`check_url_liveness`) that detects 404/410/5xx status codes, bait redirects to `/jobs/search` or `/error`, and HTML dead phrases (`"this job is no longer available"`), and a concurrent sweep engine (`verify_active_jobs` via `POST /api/jobs/verify`) that automatically marks dead listings as `status = 'expired'`.

### 5. Legal Terms-of-Service Compliance (LinkedIn / Naukri / Monster)
**Problem:** Automated server-side scraping of walled gardens (LinkedIn, Naukri, Monster) directly violates platform Terms of Service (e.g., LinkedIn ToS §8.2 breach; *hiQ v. LinkedIn* state breach-of-contract judgment) and risks IP blacklisting, CAPTCHA hurdles, or account termination.
**Solution:** Enforce a strict bifurcated legal architecture:
1. **Device-Local Import (100% Client-Side):** A browser-local parsing modal (`ImportModal.tsx` + `connectors.ts`) extracts job title, company, location, description, apply URL, and skills entirely within the user's browser runtime. Zero automated server calls are made to third-party platforms.
2. **Direct Career Page Crawling (`CareerPageAdapter`):** Utilize Apify's website content crawler strictly on direct corporate employer career pages (e.g. `careers.<company>.com`) where public indexing is permitted, bypassing walled-garden aggregators.

### 6. Automated Test Environment DB Isolation
**Problem:** Automated test runs executing `init_db()` or truncating tables can inadvertently delete live listings in the local development SQLite database (`jobs.db`).
**Solution:** In `store.py` and `conftest.py`, detect test runtime environments (`is_test_env = "pytest" in sys.modules`) and route SQLite operations strictly to `jobs_test.db` (or honor `SQLITE_DB_PATH`). Live production/dev data in `jobs.db` remains 100% untouched.

### 7. Generic Link Fallback & Deep Search Resolution
**Problem:** Aggregators, boards, or unauthenticated redirects frequently supply bare root domains (e.g. `https://www.linkedin.com/jobs/` or `https://naukri.com/jobs/`) which dump users on unhelpful generic homepages rather than the targeted opening.
**Solution:** `resolve_direct_deep_link(raw_url, title, company)` intercepts bare generic URLs (identified via `is_generic_url`) and constructs targeted search query parameters (`https://www.linkedin.com/jobs/search/?keywords={company}+{title}` or official ATS links). The UI displays a distinct `🔍 Deep Search Link` badge with direct provenance indicator so users know exactly why and how the link was augmented.

### 8. Autonomous Career Monitor & Third-Party Login ToS Analysis
**Problem:** Users requested an in-app feature to log into their LinkedIn, Naukri, Monster, or Workday accounts so the app can autonomously monitor jobs daily or weekly.
**Legal & Security Finding:**
- **Server-Side Credential Storage:** Storing user passwords or auth cookies on our servers directly violates LinkedIn User Agreement §8.2(m) and Naukri/Monster Terms of Service. It triggers automated credential stuffing blocks and risks candidate account suspension.
- **Direct Employer ATS Feeds (Workday / Greenhouse / Lever / Workable):** 100% compliant. Public ATS candidate portals have zero login requirements and expose public endpoints.
- **Architectural Solution:**
  1. **Zero Server Credential Storage:** Users are never prompted to save third-party account passwords to the backend.
  2. **Direct ATS Monitoring:** Background daemon scans Tier 1 verified ATS endpoints directly.
  3. **In-App Periodic Sweep (`career_monitor.py`):** Configurable daily/weekly autonomous evaluator sweeps active parsed resumes against live postings, auto-generates alerts for matches $\ge$ threshold (e.g., 50%), and flags dead/ghost listings before notifying the user.
  4. **Email/RSS Forwarding Ingestion:** Safe compliance hook where users can forward platform job alert emails to their private app webhook for automated local ingestion without password sharing.

### 9. Market Skill Demand & Obsolescence Navigator
**Problem:** Job seekers need visibility into which of their current skills are at peak industry demand, which are stable cores, and which legacy tools are depreciating/obsolete, along with clear migration paths.
**Solution:**
- Built `skill_intelligence.py` with an empirical frequency evaluator across 2,400+ active roles and a curated Technology Evolution Ontology.
- Classified skills into:
  - **Peak Demand (High Momentum):** Microsoft Fabric, Delta Lake, OneLake, PySpark, FastAPI, LangChain, Medallion Architecture.
  - **Stable Core (Reliable Foundation):** SQL, Python, Docker, Power BI, Azure Data Factory, Git.
  - **Deprecated / At-Risk:** SSIS, On-Premises SSRS, Hadoop MapReduce, Synapse Dedicated SQL, Legacy Informatica PowerCenter.
- Generates individualized **Market Viability Score (0-100)** and actionable **Strategic Migration Roadmaps** (e.g. SSIS $\rightarrow$ Fabric Data Factory / Dataflows Gen2; MapReduce $\rightarrow$ PySpark Delta Engine).
- Integrated into `MarketIntelligenceScreen.tsx` (`/skills`) with interactive SVG score dials and visual transition timelines.

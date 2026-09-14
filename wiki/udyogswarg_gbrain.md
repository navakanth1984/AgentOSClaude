# Udyogswarg (JobHeaven) — GBrain Knowledge Entry
**Last Updated:** 2026-09-14 | **Session:** [078d2158](conversation://078d2158-be72-49ed-bd70-0b00b9a0438a)

---

## Project Identity
- **Name:** Udyogswarg (उद्योगस्वर्ग) — "JobHeaven"
- **Type:** AI-powered job search, resume parsing, domain relevance matching, and application tracking web app
- **Location:** `e:\navakanth001\ai-job-search-app\`
- **Backend:** FastAPI (Python) at `backend/api.py`, SQLite & PostgreSQL dual-mode DB with automatic failover
- **Frontend:** React + Vite SPA at `frontend/` (proxying `/api` to backend)
- **Active Backend Server Port:** `8130` (`task-1413`)
- **Security Rule:** `SEC-001` (Zero Secret Exposure, loaded strictly via `.env.local`)
- **Tests:** 100% unit tests passing

## Architecture

### Backend API Endpoints
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/jobs` | GET | Fetch live job listings across ATS & scrapers |
| `/api/feedback` | POST | Submit feedback |
| `/api/jobs/matches` | POST | Get AI match scores & domain relevance |
| `/api/applications` | GET/POST/PUT/DELETE | CRUD application tracker |

### Frontend SPA Screens
| Screen ID | Name | Content |
|---|---|---|
| `#screen-home` | Home | Hero, resume upload/paste, country input |
| `#screen-results` | Results | Job cards grid with filters (region, eligibility, sort) |
| `#screen-detail` | Detail | Single job detail with skill chips |
| `#screen-resume` | Resume | AI-tailored resume preview + download (docx/pdf/txt) |
| `#screen-tracker` | Tracker | Application status dashboard with stats |

### Navigation Architecture
- **Desktop (≥768px):** `header.topnav` → `.desktop-nav-links` with 4 nav buttons. Mobile `.tabbar` hidden.
- **Mobile (<768px):** `nav.tabbar` at bottom with 5 tabs. Desktop nav links hidden.
- **SPA Routing:** `showScreen(name)` toggles `.screen.active` class.

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

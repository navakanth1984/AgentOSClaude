# Nth Dimension Academy — Conversational AI
> Architecture for a teaching-assistant agent on the Nth Dimension Academy site, built on Google Cloud RAG.

## Summary
A production conversational agent that answers student questions on DP-600, DP-700, DP-750, DP-800, and Agent OS. The design deliberately avoids custom Python backends, leaning on managed Google Cloud services funded by existing credits.

## Details
- **Brain — Vertex AI Search (GenAI App Builder)**: Obsidian course folders are uploaded into a Vertex AI Data Store, which auto-chunks, embeds, and retrieves — an enterprise RAG layer rather than a hand-rolled script.
# Nth Dimension Academy — Conversational AI
> Architecture for a teaching-assistant agent on the Nth Dimension Academy site, built on Google Cloud RAG.

## Summary
A production conversational agent that answers student questions on DP-600, DP-700, DP-750, DP-800, and Agent OS. The design deliberately avoids custom Python backends, leaning on managed Google Cloud services funded by existing credits.

## Details
- **Brain — Vertex AI Search (GenAI App Builder)**: Obsidian course folders are uploaded into a Vertex AI Data Store, which auto-chunks, embeds, and retrieves — an enterprise RAG layer rather than a hand-rolled script.
- **Engine — Dialogflow CX**: a "Data Store Agent" (generative fallback) linked to the Vertex store; handles sessions, conversational memory, and safety filters with no backend code.
- **Interface — Dialogflow Messenger**: a prebuilt HTML/JS web component embedded in the site, with built-in microphone speech-to-text (no separate speech API key needed).
- **Roadmap**: (1) aggregate course Markdown from the vault → GCS bucket; (2) create the Vertex Data Store over that bucket; (3) configure the Dialogflow CX agent persona + link; (4) inject the Messenger snippet into the site.
- Cost is covered by GenAI App Builder and Dialogflow CX credits.
- Source: [nth_dimension_architecture.md](file:///C:/Users/navka/navakanth001/sources/technical/nth_dimension_architecture.md)

## Engagement & Telemetry Framework (v1.0)
A vendor-agnostic client-side architecture that monitors active user attention, calculates learning index scores, and batches events for resilient delivery:
- **Observation Engine (`engagement-framework.js`)**: Runs intersection observers over defined `data-section` modules, captures interactive CTA clicks (using event delegation), and applies the Page Visibility API to pause dwell-timers when tabs are hidden.
- **Curiosity Index**: Computes a weighted attention rating (Active Dwell Time: 35%, Max Scroll Depth: 30%, Interaction Clicks: 20%, Section Entries: 15%) and maps milestones (e.g. "Master Explorer"). Saves state in versioned `sessionStorage` (`nth_learning_hud_v1`).
- **Telemetry Adapter (`analytics-adapter.js`)**: Subscribes to Custom DOM Events (`academy:sectionVisited`, `academy:milestoneUnlocked`, `academy:curiosityChanged`). Accumulates and flushes events every 4 seconds (with direct bypasses for milestone conversions) to GA4 (`gtag`) and Vercel Analytics. Automatically enriches payloads with page path, viewport width, and network connection type context.
- **Performance Observing & Delivery (`performance-observer.js`)**: Uses browser APIs to trace runtime paint/load signals (FCP, LCP, CLS, INP) and dispatches performance telemetry. Complemented by AVIF/WebP image generation pipelines (reducing asset weight by 89%-96%) and lazy-loading / video poster configurations for layout protection.
- **HUD Audit Mode**: Gated behind `?hud=true` or `?debug=true` query parameters to preserve a pristine layout for visitors while allowing visual owner diagnostics.

## Analytics Intelligence Platform (v1.0 Roadmap)
Transitions telemetry from collection to decision-making using a Medallion Architecture:
- **Bronze (Raw Lake)**: Direct GA4 BigQuery export table stream (e.g., `events_YYYYMMDD`).
- **Silver (Cleaned/Normalized)**: Standardized timestamp schemas, flattened parameter keys, and unified session blocks (e.g., `session_events`, `performance_metrics`, `engagement_events`).
- **Gold (Semantic Layer)**: Direct fact/dim models for simple dashboard query execution (e.g., `fact_learning_sessions`, `fact_performance`, `dim_device`, `dim_connection`).
- **Key Dashboards**:
  - **Executive**: Learning engagement rates, CTAs CTR, and course completions.
  - **Product**: Visual learner funnel mapping drop-off %, LCP, and curiosity transitions.
  - **Engineering**: Real-user Core Web Vitals distributions, slow resource audit records, and adapter queue status.

## OpenSEO, GEO & Interactive Lead Generation Platform (v2.0)

**Status**: Verified 2026-09-19 | Production Live on https://nthdimensionacademy.com | Git Commit `b8cbffc` on `main`

A production-grade SEO, Generative Engine Optimization (GEO), and multi-channel lead acquisition engine built into the React 19 / Vite 8 digital academy portal:

### Architectural Components
1. **Semantic Pre-rendering Engine (`index.html`)**:
   - Injects 5,691 characters of semantic HTML inside `<div id="root">` prior to client-side bundle execution.
   - Eliminates SPA crawl blackout for non-JS web crawlers (`is-agentic` score increased from 51/100 to 96/100).
   - Achieves 0.00 Cumulative Layout Shift (CLS) as React 19 seamlessly replaces the pre-rendered shell with the 3D WebGL particle cosmos.
2. **Edge Content Negotiation (`middleware.js` & `vercel.json`)**:
   - Intercepts requests bearing `Accept: text/markdown` and delivers clean, high-density markdown in 59ms (1.42 KB).
   - Avoids passing 1.5MB React bundles to LLM query engines.
3. **Machine-Readable Knowledge Protocols (`public/llms.txt` & `public/llms-full.txt`)**:
   - Machine-readable specification outlining exact syllabus details, prerequisites, and "When to use this" routing criteria for Perplexity, ChatGPT-User, and ClaudeBot.
4. **Structured Data Authority (`Schema.org`)**:
   - Homepage: `@graph` JSON-LD linking `EducationalOrganization` (Nth Dimension Academy), `Person` (MCT Navakanth Reddy Dumpa), and 5 `Course` entries with syllabus URLs.
   - Atlases: Dedicated `Course` JSON-LD embedded across all 5 Learning Atlases.
5. **Interactive 2-Minute Certification Matcher (`CertificationMatcherModal.jsx`)**:
   - 3-step diagnostic matching student skillset to DP-600, DP-700, DP-750, DP-800, or AI-103.
   - Immediate 1-click WhatsApp handoff to MCT Navakanth Reddy (`+91 6304980314`) with prefilled course tokens.
   - Serverless lead capture handler (`api/leads.js`) with resilient fallback logging.
6. **Learning Atlas Modernization & Layering Rectification**:
   - Replaced disabled "Coming Soon" buttons across all 5 Learning Atlases (`dp600-atlas`, `dp700-atlas`, `dp750-atlas`, `dp800-atlas`, `ai103-atlas`) with active `🎯 2-Min Matcher` and `⚡ 1-on-1 MCT Call` buttons.
   - Added Lead Magnet cards (*"Accelerate Your [COURSE] Certification Journey"*) above each atlas footer.
   - Rectified iframe trap: Added persistent top control header in `App.jsx` (`← Return to Academy Portal`, `🎯 2-Min Matcher`, `💬 WhatsApp MCT`, `✕`) and elevated modal z-indices to `z-[10001]` to ensure clean layering over `z-[9999]` iframe.
7. **High-Trust Static Anchor Pages**:
   - `/about/`, `/contact/`, `/privacy/`, and `/terms/` deployed as standalone static HTML routes.

### Verified
- **Production HTTP 200**: Verified live on `https://nthdimensionacademy.com/`, `/robots.txt`, `/llms.txt`, `/about`, and `/dp600-atlas` via `read_url_content` and Node.js fetch telemetry.
- **Edge Markdown Latency**: Measured 59ms TTFB on `Accept: text/markdown` requests.
- **Browser DevTools Verification**: Visual validation across desktop and mobile viewports via `chrome-devtools-mcp` with zero layout shift; captured `live_production_homepage.png`, `live_production_hero_ctas.png`, and `live_production_modal_open.png`.
- **Production Build**: Clean `npm run build` with 0 errors (Vite 8, 2,728 modules transformed).

### Known Gaps
- **Trailing Slash 308 Normalization**: Vercel normalizes paths without trailing slashes (e.g., `/dp600-atlas/` 308 redirects to `/dp600-atlas`). Internal links should standardize on non-trailing slashes to eliminate redundant 20ms redirect hops.
- **Atlas File Weight**: Atlas HTML files (`dp600-atlas/index.html`, etc.) are ~1.39MB due to inlined base64 images; extracting base64 assets to compressed WebP files in `public/assets/` will reduce initial atlas payload by ~70%.

## Connections
- The site itself is an active project at the repo root: [nthdimensionacademy/](file:///c:/Users/navka/navakanth001/nthdimensionacademy/) and [nth-dimension-react/](file:///c:/Users/navka/navakanth001/nth-dimension-react/).
- Course content overlaps [Microsoft Fabric (DP-700)](fabric-dp700.md).
- Shares the RAG-over-Markdown approach with [OKF Bundle Generator](okf-bundle-generator.md); contrasts with the unofficial-API approach in [NotebookLM Bridge](notebooklm-bridge.md).

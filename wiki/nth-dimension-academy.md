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

## Connections
- The site itself is an active project at the repo root: [nthdimensionacademy/](file:///c:/Users/navka/navakanth001/nthdimensionacademy/) and [nth-dimension-react/](file:///c:/Users/navka/navakanth001/nth-dimension-react/).
- Course content overlaps [Microsoft Fabric (DP-700)](fabric-dp700.md).
- Shares the RAG-over-Markdown approach with [OKF Bundle Generator](okf-bundle-generator.md); contrasts with the unofficial-API approach in [NotebookLM Bridge](notebooklm-bridge.md).

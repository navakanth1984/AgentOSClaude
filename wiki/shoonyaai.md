# ShoonyaAI

## Current Status (2026-09-17)

**Status:** Live on Vercel Production (`https://shoonyaai.vercel.app`); zero login friction; resilient multi-sheet Excel ingestion, cloud-to-cloud pull (Google Drive/Sheets & OneDrive/SharePoint), W3C live disk sync, tabular auto-healing, and interactive 3D spatial topologies (Pillars, Spheres, Ribbon, Pyramids, Globe) fully verified.

### Verified

- **Tabular Auto-Healing Engine (`sanitizeTabularMatrix`)**: Eliminates column header errors (`Use 1-80 unique, nonempty column headers`) across Google Sheets exports and delimited CSV files. Automatically skips single-cell title banners on row 0, trims trailing blank columns, auto-names empty headers (`column_${i+1}`), deduplicates column names (`Amount`, `Amount_2`), truncates headers >100 chars, bounds to 80 columns, and normalizes jagged rows.
- **Resilient Multi-Sheet & Formula Excel Ingestion**: Automatically detects populated worksheets in multi-tab workbooks (e.g. `Milk Data Maintanance.xlsx`), selects the primary data sheet (`MilkData`), and extracts cell formulas (`=C2*45`), rich text, ISO dates, and hyperlinks into clean DuckDB primitives.
- **Cloud-to-Cloud Pull & Direct Streaming**:
  - **Microsoft OneDrive / SharePoint**: Upgraded `normalizeCloudUrl()` to convert `:r:` redirect paths to `:g:` guest paths and append `download=1`, resolving HTTP 401 Unauthorized without requiring OAuth credentials.
  - **Google Drive / Sheets**: Normalizes all drive/sheet links to `/export?format=csv` or direct download, intercepts large-file virus scan confirmation pages (`confirm=t`), and rejects HTML auth barriers before CSV parsing.
- **W3C Local Live Disk Sync**: Uses browser File System Access API (`window.showOpenFilePicker`) to link local files from desktop; users click "Sync from Disk" to refresh live analytical models instantly without re-uploading.
- **Three.js 3D Pyramids & Responsive HUD**: Re-architected HUD into a two-row responsive layout, docking the 2D Spatial Radar mini-map (`bottom-28 right-4`) with an interactive collapse toggle, eliminating DOM click interception on the Pyramids button. Optimized materials to emissive `MeshStandardMaterial` for 60 FPS performance without WebGL framebuffer warnings.
- **Open-Source OCR Integration Blueprint**: Validated zero-API-cost open-source stack: Tesseract.js (client-side WASM worker for images/receipts), Mozilla PDF.js (vector extract + canvas raster fallback for scanned PDFs), JSZip/DOMParser (pure XML/HTML parsing for EPUB books), and Mammoth.js (DOCX).
- **Clean Domain & Zero Login**: Deployment alias permanently configured at `https://shoonyaai.vercel.app`. Vercel preview deployment protection disabled via CLI (`vercel project protection disable shoonyaai --sso`), removing authentication/password prompt so users access the app frictionlessly.
- **Serverless Ephemeral Storage Resilience**: Resolved multi-container `Dataset or run was not found` (HTTP 404) cache misses on ephemeral serverless microVMs (`/tmp`). Implemented client-assisted re-hydration fallback in `backend/workspace.ts` and `src/components/DataWorkspace.tsx`, plus an in-memory fallback layer in `backend/storage.ts`.
- **Extensive Sources Regression Suite**: 100% pass rate across all source scenarios (CSV standard/ragged, TSV, JSON, Base64 XLSX, REST with pagination, SSRF guardrails, DuckDB analytical execution, and Excel provenance export).

### Known Gaps

- Azure CLI is not authenticated in the isolated CLI profile. No Azure staging resources or signed mobile release binaries exist yet.
- Production acceptance still requires the gates in [Production readiness gate](../shoonyaai/docs/PRODUCTION_READINESS_GATE.md), including real Entra identity, managed PostgreSQL (`CONTROL_DATABASE_URL`), Blob/Key Vault, staging smoke, and mobile-device evidence.

The execution handoff for Antigravity is [ShoonyaAI Antigravity handoff (2026-09-16)](shoonyaai-antigravity-handoff-2026-09-16.md).

Local repository: `G:\navakanth001\shoonyaai`. Upstream: https://github.com/navakanth1984/shoonyaai.
Live URL: https://shoonyaai.vercel.app

The original app supplied simulated architect, engineer, analyst, security, and admin screens. The 2026-09-13 implementation adds a real prompt workspace over CSV/XLSX and bounded PostgreSQL snapshots, a strict plan compiler, isolated DuckDB calculations, persisted results, Excel provenance, touch-controlled Three.js results, and Capacitor Android/iOS projects.

Durable implementation and tool decisions: [Autonomous workspace](../shoonyaai/docs/AUTONOMOUS_WORKSPACE.md). Original premise review and 80 proposed use cases: [Validation and use cases](../shoonyaai/docs/AI_NATIVE_ETL_VALIDATION_AND_USE_CASES.md). Code graph: `shoonyaai/.graphify/GRAPH_REPORT.md`; Swift grammar was unavailable during extraction, so iOS source coverage is incomplete.

Boundaries: this is a single-workspace analytical pilot. Role-labelled execution stages do not establish autonomous cloud administration or production pipeline deployment. Live provider/database checks require configured services. Native project generation does not establish signed release/device readiness. See [AI-native ETL framework](ai_native_etl_and_analytics_gbrain.md).

2026-09-14 continuation: exact JSON numeric text is preserved across file and REST import; pagination rejects cross-origin custom credentials; upload limits and HTTP parser errors are shared by the app and tests. Node 24 in-process testing resolves the worker-permission blocker: 22 tests now pass, including production security headers/readiness, OIDC signature validation, and connector-broker fail-closed behavior; 18 synthetic connector probes and 4 targeted mutations also pass. The development tenant adapter now proves two bearer-token organizations cannot enumerate or retrieve each other's datasets, runs, or exports; tenant mode also disables the global PostgreSQL URL fallback. Production now has an OIDC JWT verifier, durable PostgreSQL control-store adapter, opaque connector `secretRef` broker contract, strict origin/security headers, Vercel entrypoint/configuration, and a production readiness gate. Fresh browser/device QA, external broker deployment, durable migration, and Vercel environment configuration remain open. The current scope and next delivery sequence are recorded in [Whole product readiness](../shoonyaai/docs/WHOLE_PRODUCT_READINESS_REVIEW.md). Graph extraction was refreshed; Swift grammar remains unavailable and semantic labeling is still pending.

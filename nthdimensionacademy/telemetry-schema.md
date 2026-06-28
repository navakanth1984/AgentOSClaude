# Telemetry Schema Specification (v1.0.0)

This document serves as the formal contract between client-side telemetry instrumentation (React and Vanilla DOM layers) and the downstream analytics adapters, transformations, and dashboards.

---

## 1. Global Context Parameter Enrichment
Every custom DOM event dispatched by the telemetry adapter is automatically enriched with the following environment variables:

| Parameter Name | Data Type | Source | Description |
| :--- | :--- | :--- | :--- |
| `page_path` | String | `window.location.pathname` | The active relative URL path. |
| `viewport_width` | Integer | `window.innerWidth` | Responsive viewport breakpoint locator. |
| `connection_type` | String | `navigator.connection.effectiveType` | Client network speed indicator (e.g., `4g`, `3g`, `slow-2g`). |
| `timestamp` | ISO String | `new Date().toISOString()` | Execution-level UTC timestamp. |

---

## 2. Event Schemas

### A. `academy:sectionVisited`
Fired when a user enters a defined content container.

- **Trigger Source**: Intersection Observer (20% top, 60% bottom margins).
- **Event Properties (`detail`)**:
  - `section` (String): The conformed name of the section (from the `data-section` attribute in the DOM, e.g., `Core Expertise`, `Curriculum Map`).

---

### B. `academy:performanceMetric`
Fired when the browser records Web Vitals paint or latency timings.

- **Trigger Source**: Performance Observer APIs (`paint`, `largest-contentful-paint`, `layout-shift`, `first-input`).
- **Event Properties (`detail`)**:
  - `metric` (String): Metric key (`FCP`, `LCP`, `CLS`, `INP`).
  - `value` (Float): Measured timing in milliseconds (except CLS, which is a score coefficient).
  - `rating` (String): Evaluation status (`GOOD`, `NEEDS IMPROVEMENT`, `POOR`).

---

### C. `academy:curiosityChanged`
Fired when the student's Curiosity Index updates.

- **Trigger Source**: Score recalculation engine (triggered by idle-aware timer, clicks, scroll, and sections).
- **Event Properties (`detail`)**:
  - `index` (Integer): The composite calculated Curiosity Index (`0 - 100`).
  - `rank` (String): Explorer title matching the score (e.g., `Apprentice Explorer`, `Dimension Weaver`, `Cosmic Architect`).

---

### D. `academy:milestoneUnlocked`
Fired when the Curiosity Index reaches one of the pre-configured threshold checkpoints.

- **Trigger Source**: Milestone logic loop.
- **Event Properties (`detail`)**:
  - `milestone` (String): Label of the unlocked milestone (e.g., `Timeline unlocked`, `Hidden quote discovered`).
  - `description` (String): Short contextual description of the unlock event.

---

## 3. Session State Storage Schema
Client-side session memory is stored in `sessionStorage` under the key `nth_learning_hud_v1` with the following structure:

```json
{
  "version": 1,
  "timeOnPage": 182,
  "maxScrollDepth": 84,
  "clickCount": 4,
  "visitedSections": ["Academy Ascent", "About MCT", "Core Expertise"],
  "unlockedMilestones": ["Timeline unlocked", "Hidden quote discovered"]
}
```

# MVCT MRP Core: Implementation Charter

> **Active Implementation Charter (Execution Mode).** Adopted 2026-07-11. Specifies operational constraints and targets for shipping, measuring, and evolving the product.

---

# 1. Objective & Mission

Build MVCT into a production-ready, adaptive learning platform for children and lifelong learners. Success is measured by working software, measurable telemetry, automated validation, user engagement, and learning outcomes.

## Operating Principles
- **Architecture is frozen:** Implementation is fluid.
- **Evidence overrides assumptions:** Telemetry overrides opinions.
- **Behavior overrides surveys:** Every improvement must be measurable.
- **Action over documentation:** Never expand architecture when implementation is the bottleneck.

---

# 2. Parallel Implementation Streams

### Stream A: Engineering Intelligence
- **Focus:** `EngineeringEvent` pipelines, `EngineeringProjector` (E2), Confidence Engine, Watch Runner validation reports, and automated PR generation structures.

### Stream B: Product Intelligence
- **Focus:** Passive `InteractionEvent` collection (clicks, scroll depth, hesitation, dwell time, abandonment, viewports, and performance metrics) without third-party analytics trackers. Journey Graphs and Component Fitness projections.

### Stream C: Learning Intelligence
- **Focus:** BKT calculations, cohort isolation, paced spaced-retrieval scheduling, and simulation tests without violating the frozen research protocol.

### Stream D: Platform
- **Focus:** Provisioning Azure Dev, Staging, and Production environments (Azure Front Door, App Service / Container Apps, Azure PostgreSQL, Redis, Application Insights, Key Vault, Blob Storage, Power BI).

### Stream E: Experience Engineering
- **Focus:** Redesigning Web, PWA, React Native, Android, and iOS client experiences under strict Playwright, Visual Regression, Accessibility, Performance, and Synthetic Learner stress-testing verification.

---

# 3. Performance Targets

- **Page Load:** < 2 seconds
- **Interaction Latency:** < 100 milliseconds
- **API p95:** < 250 milliseconds
- **Crash-free Session Rate:** > 99.9%
- **Accessibility:** WCAG AA Compliant
- **Capabilities:** Mobile-first, responsive, offline-capable.

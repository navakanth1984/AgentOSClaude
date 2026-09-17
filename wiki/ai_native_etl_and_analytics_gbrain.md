# AI-Native ETL & Analytics (`AetherData` / `ShoonyaAI`) — Canonical KB

**Status**: Verified 2026-09-17 (ShoonyaAI live analytical web platform on Vercel at `https://shoonyaai.vercel.app`; resilient multi-sheet Excel ingestion, sanitizeTabularMatrix auto-healing, cloud pulls for Google Drive/OneDrive, W3C live disk sync, and 3D spatial visualizer verified); Verified 2026-09-16 (ShoonyaAI live analytical web platform verified on Vercel at `https://shoonyaai.vercel.app`; 11/11 source scenarios passed; serverless ephemeral container re-hydration operational; zero-login access configured; 3D spatial Three.js scene verified); Verified 2026-09-10 (AetherStudio product layer; Apify + unstructured sources live; 205 tests). Superseded: 2026-08-29 platform architecture retained only as history in §7.

**Read `wiki/log.md` for the dated execution record; it outranks this file where
they disagree.**

---

## 1. System Identity

`aetherdata-spike/` is a **spike, not a product.** It was scoped as an open-source
AI-native ETL + analytics + visualization framework and narrowed, after review, to
a single question: *can quality be made a property of records rather than of
tables, and can it be enforced on the consumer's query?*

The durable return on the project is **five measured findings** (§3), not the code.

Published records:
- Findings: https://claude.ai/code/artifact/c831bde1-38c6-40ba-9f71-c87201c352df
- Prototype surface: https://claude.ai/code/artifact/0e54bc1a-c77b-4d8f-a346-fd0fc77ca08a
- Panel review: https://claude.ai/code/artifact/7c09c249-7198-4003-9597-f2190a4a5f01

---

## 2. What exists on disk

| Module | What it does |
| :--- | :--- |
| `connect.py` | Sniffs encoding and format rather than trusting the extension |
| `store.py` | DuckDB store; per-record `_provenance` / `_confidence` / `_conformance` / `_quarantine` |
| `gate.py` | 4-rung ladder: **scope → bind → shadow → contract**, sandboxed |
| `scope.py` | Static least-privilege check over the SQL syntax tree (sqlglot) |
| `propagate.py` | The confidence algebra — **imported by its own tests and nothing else** |
| `participants.py` | Escalation chain; exhausted chain BLOCKS; autonomy is measured |
| `router.py` / `access.py` | Tier routing (which engine) and access-path routing (scan vs seek) |

### `poc/` — the working pipeline (added 2026-09-10)

Composes with existing open source rather than reimplementing it, per the
landscape finding that this category is formally *semantic operators*.

| Module | What it does |
| :--- | :--- |
| `sources.py` | Live Hacker News connector. One feed, three modalities: structured (score/comments/age), unstructured (title), real-time (`/v0/newstories` with `StreamState` dedup) |
| `operators.py` | `Engine`: `sql` (DuckDB) vs `sem_filter`/`sem_map` (LOTUS), plus the cost `Meter` and a semantic result cache |
| `planner.py` | 4 prebuilt use cases; free-form question → model-generated plan → **whitelist validation**, reusing `aetherdata.scope` |
| `triggers.py` | Deterministic rules → `Event`s carrying their own evidence and a named action |
| `run.py`, `export_run.py` | Executor + CLI + capture for the dashboard |


### `aether_studio/` -- the product layer (added 2026-09-10, later the same day)

**What it is.** Requirement in, insight dashboard out. `py -m aether_studio --source <file|sqlite|postgres://|https://json> --require "<what you want to learn>" --out dash.html`, or `py -m aether_studio serve` for a browser UI (port 8766 in the shared `launch.json`). Built on the reusable parts of the spike and POC: `aetherdata.scope` (AST scope rung), `aetherdata.propagate` (now **wired**, see below), `aetherdata.connect` (sniffing loader), `poc.operators.Engine` (DuckDB + LOTUS + meter).

| Module | What it does |
| :--- | :--- |
| `catalog.py` | Connects file / sqlite / postgres (row-capped) / JSON URL into one DuckDB; sanitises column names at the edge (reserved words suffixed); creates a `<table>__trusted` view per table |
| `profile.py` | Column kinds (id, entity, bool, numeric, datetime, categorical, constant, text); per-row `_confidence` / `_quarantine` / `_record_key`; **entity descent via `propagate_entity`** on `*_id` parent columns past 30% quarantine |
| `planner.py` | Model planner (Gemini, JSON questions) and deterministic `auto_plan`; **validator**: scope rung + **literal-grounding rung** (every string literal compared to a categorical column must occur in it) + banned words + single statement. Refused questions are kept with the reason |
| `execute.py` | Runs every accepted SQL **twice** (all rows, then the `__trusted` view via AST table rewrite) and reports the max relative delta; `Quality` aggregated over the contributing rows |
| `narrate.py` | Model narrator fed the result tables and the SQL, never raw rows; **claim validator** drops any sentence whose numbers are not in the results. Deterministic fallback narrator obeys the same rule |
| `viz.py` | Chart chosen by result shape (kpi/bar/line/scatter/table), inline SVG, theme tokens; every panel carries the trust line, the delta, the SQL |
| `app.py`, `ui.html` | CLI and stdlib HTTP server + single-page UI |

**Apify connector (added 2026-09-10, second pass).** `apify://dataset/<id>`, `apify://run/<runId>` (resolves the run's default dataset, refuses non-SUCCEEDED runs), `apify://actor/<user/name>[?input=<urlencoded json>]` (starts the actor, waits up to 300 s, takes its dataset). Token from `APIFY_API_KEY` via `load_env`, sent as a Bearer header, never in a URL or note. Items paged 1,000 at a time, capped at 50,000 with a note. Nested list/dict cells are serialised to JSON strings at the edge.

*Verified 2026-09-10 (live, real credits):* `apify://actor/apify/rag-web-browser?input=...` started run `P8hsJcfX2bU7cXfTf` (SUCCEEDED, dataset `MSwBtewfJYchTqoK4`, 8 items); `apify://run/P8hsJcfX2bU7cXfTf` then produced a dashboard: 5/5 model questions accepted, 66 flattened columns, 2 of 8 rows quarantined by the relative-sparse rule, narrative validated, meter $0.000676 / 4,386 tokens. `py -m pytest -q` -> `190 passed in 26.03s`.

**Unstructured and semi-structured inputs (added 2026-09-10, third pass).** `.txt/.md/.log` load as rows: logs one row per line with `ts_raw`/`level`/`message` parsed by regex when present, prose one row per paragraph with `heading`/`chars`/`words`. A directory loads every supported file, unioned by kind (`<dir>_records`, `<dir>_text`) with `source_file`, skips noted. JSON envelopes (`{"items": [...]}`) are unwrapped; nested objects are flattened to dot-joined columns; lists are serialised; placeholder strings (`—`, `N/A`, `null`, `?`...) become nulls at the edge. The semantic step truncates each cell to 1,500 characters and may target only a column of kind `text`.

*Verified 2026-09-10 (live):* the semantic pre-step ran for the first time on the 40 cached HN titles: closed set of 8 themes, 6 used, 5/5 questions accepted, narrative validated, $0.000660. On the Apify markdown pages the first attempt classified a constant column (defect 15); after the text-only rung the model chose a SQL keyword CASE on the title instead of a semantic step and reported 7 of 8 pages as 'other' -- honest, and a plan-quality limit, not a validator failure. A 16th defect from that run: the claim validator dropped a true sentence quoting an unrounded average (14 decimals); numbers are now compared at 3 decimals. `py -m pytest -q` -> `205 passed`; `tests/test_unstructured.py` holds 15 tests over varying-key JSONL, BOM/placeholder/multi-line CSV, logs, markdown, directories, injection-looking values, prompt privacy, closed-set mapping, truncation, partial failure, and three real workspace files.

*Defects found only by messy data, fixed with tests:* (10) nested JSON objects were not flattened -- `user` became a JSON string instead of `user_name`, `user_id`. (11) an `{"items": [...]}` envelope loaded as one row. (12) a literal containing `;` was refused as "multiple statements" -- the AST already counts statements. (13) **privacy hole**: on a small table every column has few distinct values, so a paragraph column was classified categorical and its sample values reached the planner prompt; categorical now requires repeats, and samples are capped at 40 chars. (14) LOTUS stats are cumulative and were assigned to the meter with `=`, erasing planner spend when a `sem_map` ran; deltas are now added. (15) the model put the semantic step on a constant categorical column (`searchresult_resulttype` = ORGANIC) and reported one page type; semantic steps are now text-only by validation.

*Defects found by that run, fixed with tests:* (8) `json_normalize` leaves lists in cells; `nunique()` raised `unhashable type: list` on the first real item -- serialised at the edge. (9) Claim validator dropped a true sentence because the model wrote `4684956.0` and the table rendered `4684956` -- numbers are now normalised before lookup.

**Verified 2026-09-10**
- **186 tests pass** -- `py -m pytest -q` read in full: `186 passed in 23.54s` (163 -> 186; +19 studio, +4 scope table-function cases).
- **Live end-to-end with real inference** -- `py -m aether_studio ...` on `product_analytics.jsonl` + `azure_quantum_experiments.csv`: 6/6 questions answered, narrative `model:gemini/gemini-2.5-flash-lite (validated)`, meter **$0.000544 / 3,132 tokens**, 86% of ops deterministic. Output file `aetherstudio_dashboard.html` inspected; zero `1970` axis labels.
- **Browser UI** -- served through the Browser pane at `http://localhost:8766`; sources and requirement submitted through the form; dashboard rendered in the iframe with model planner and validated narrative (screenshots taken in session).
- **Entity descent is wired** -- `profile.stamp_quality` calls `aetherdata.propagate.propagate_entity`; `tests/test_studio.py::test_profile_kinds_and_quality_rules` asserts a clean-looking row is quarantined by inheritance; `test_entity_descent_is_idempotent_on_restamp` asserts a second pass is a no-op.
- **Packaged** -- `pyproject.toml` with `[project.scripts] aether-studio`, `README.md` with a quickstart.

**Defects the harness caught during the build (all fixed, all with tests)**
1. `aetherdata.scope` let `FROM read_csv('x.csv')` through: a function-valued `Table` has an empty `.name` so the table loop skipped it, and `ReadCSV.name` returns the file literal so the function denylist missed it. Fixed both; 4 adversarial cases added to `tests/test_scope.py`.
2. Model wrote `WHERE status_ != 'SUCCEEDED'` against a column whose only value is `JobStatus.SUCCEEDED` -> three successes reported as failures, narrated as fact. **Literal-grounding rung** added; the question is now refused with the real values in the message.
3. Planner and narrator bypassed LOTUS so the meter printed `$0.000000 / 0 tokens` for two real calls. `Engine.account_completion` added; flips to UNMETERED when usage cannot be read.
4. Flat ">50% null => sparse" rule quarantined 98.3% of event-style JSON (union of per-event schemas). Rule is now **relative**: past 50% null *and* 25 points past the table median row.
5. My own deterministic narrator computed "34% of the total shown" -- its own validator dropped the sentence. Derived shares removed; the no-arithmetic rule applies to the fallback narrator too.
6. Trust line printed the algebra min-completeness as "27% coverage" while 0 rows were quarantined. Coverage (usable/total) and lowest-row completeness are now reported separately.
7. Line chart x-axis showed 1970: DuckDB returns `datetime64[us]`, renderer assumed ns. Unit normalised; test pins the axis year to the data.

**Third-party stack (all verified live):** `lotus-ai` 1.2.4 (Stanford semantic
operators), `litellm`, `gemini/gemini-2.5-flash-lite`, `duckdb`, `pandas`.
Inference is real and paid, not mocked.

Dashboard: https://claude.ai/code/artifact/cbd377bb-150f-47c5-a4a4-27af6857c90a

Benchmarks: `bench_access.py`, `bench_zonemap.py`, `bench_calibration.py`, `demo.py`.

### Verified
- **123 tests pass** — verified 2026-09-10 by reading `py -m pytest` output in
  full: `123 passed in 16.08s`. (118 on 2026-08-31; +5 replay tests.)
- **Replaying the pipeline is now a no-op** — verified 2026-09-10 by
  `tests/test_replay.py`, which runs the whole pipeline twice and diffs state.
  Before the fix a replay **tripled** the data (1,029 → 3,087 rows). Records now
  carry `record_key`, an identity *derived* from provenance
  (`source_uri#record_index`) rather than generated from an arrival counter.
  `demo.py` produces byte-identical numbers to before the fix, so it is
  behaviour-preserving on first run and correct on replay.
  **Note for anyone adding a smoke test here:** the session-count metric passed
  throughout the broken period, because `COUNT DISTINCT` is insensitive to
  duplicates. Row counts, coverage and every denominator were wrong. Do not use
  a distinct-count as the canary.
- **Lineage descent converges in one pass** — verified 2026-09-10; a second pass
  quarantines 0 rows, so propagation has a defined end rather than cascading.
- **The demo runs end to end on real data** — `py demo.py` against
  `mvct-mrp-core/product_analytics.jsonl` (1,029 real records).
- **`propagate.py` is unwired** — verified by `grep -rln propagate --include=*.py`:
  matches only `__init__.py`, itself, its tests, and three bench scripts. No
  pipeline imports it.
- **Not packaged** — verified by `ls pyproject.toml setup.py`: neither exists.

---

## 3. The five findings (the actual output)

Each measured on real data; commands given so they can be re-run.

1. **Record-level quality is insufficient without entity propagation.**
   1,029 telemetry records. 680 of 711 `CardCompleted` events carried no
   suspicious field of their own but belonged to a flagged session. Accuracy
   98.7% → **74.2%**; mean reaction 1,094 ms → **14,116 ms** (12.9×).
   *Verified by* `py demo.py`, `py export_facts.py`.

2. **A pipeline's confidence in itself points the wrong way.** Correlating each
   trust signal against known error: coverage **+0.74**, conformance **+0.74**,
   externally-labelled audit **−0.93**. Both self-computed signals are highest
   when the answer is most wrong. Structural, not a tuning problem: a detector
   that finds nothing drops nothing and therefore looks perfect.
   **A system cannot measure its own undetected errors from inside itself.**
   *Verified by* `py bench_calibration.py`.

3. **The published index-selectivity threshold is ~80× too permissive.** Guidance
   says ~0.1% of rows; measured knee on 2M rows is **0.0010–0.0015%**. Wrong in
   the expensive direction — routes a scan to a seek at 25× cost.
   *Verified by* `py bench_access.py 2000000`.

4. **Sort/zone-map benefit scales with table size — and is rented, not owned.**
   Noise at 2M rows (2–3×); **13.7× / 15.8×** at 20M. A four-distinct-value
   column prunes with neither sorting nor indexing (1.0× both). A table has
   **one** physical order — indexes are additive, ordering is exclusive.

   **Never quote the speedup unqualified.** Maintenance cost depends entirely on
   whether the sort key correlates with arrival order. Measured on an 8M-row
   sorted base, appending 20% more rows:

   | | append-only (key grows) | late-arriving (key lands mid-table) |
   | :--- | :--- | :--- |
   | query vs sorted | **1.10×** — effectively free | **4.39×** — most of the benefit eaten |

   Restoring order costs a full re-sort: 9.6M rows in 5,920 ms = **3.70 µs per
   ingested row**, paid whether or not anyone queries. Time-series pipelines
   sorting by event time are in the free case; anything sorting by an id, or
   backfilling, is renting.
   *Verified by* `py bench_zonemap.py 20000000`, `py bench_compaction.py 8000000 200000 8`.

5b. **Model choice inside the semantic tier matters as much as the tier split.**
   The first real data point for the long-unmeasured tier hypothesis, measured on
   the POC's live workload: `gemini-2.5-flash` billed **$2.02 per 1M tokens**;
   `gemini-2.5-flash-lite` billed **$0.11 per 1M** for *correct results on the
   same task* — **~18× cheaper**. Choosing the cheap model within the paid tier
   is a larger lever than several percentage points of deterministic share.
   Per-run deterministic share measured at 100% / 33% / 50% across three real
   use cases, total spend under a tenth of a cent.
   *Verified by* `py -m poc.run <use-case>`, cost read from
   `lm.stats.physical_usage`.

6. **Correctness checking is not authority checking.** A query selecting
   `customer_ssn` for a revenue task passes parse, bind, shadow execution and the
   contract. Only AST scope checking catches it, and it must run before
   execution. This is the shape of prompt injection against a data agent.
   *Verified by* `tests/test_scope.py`, 12-case adversarial corpus.

---

## 4. Architecture invariants (things a newcomer cannot infer from the code)

- **The gate is a ladder of declared strengths, not a boolean.** Rungs 2–4 answer
  "is this correct"; rung 1 answers "is this in scope". A result must be reported
  with the rung it reached. **"Verified" must never come to mean "bound
  successfully."**
- **`scope=None` skips rung 1** — deliberately, not by oversight. Absence of a
  declared scope means authority was not checked.
- **The shadow DuckDB is sealed before untrusted SQL runs**, and the fixture runs
  *before* the seal. `lock_configuration=true` must be applied last — without it
  the untrusted SQL can turn the sandbox off from inside.
- **An exhausted escalation chain BLOCKS.** Silence is never consent.
- **`confidence` and `audit` are separate and must stay separate** (see finding 2).
  `trustworthy` is never true without an audit, however high the confidence.
- **Quarantine marks, never deletes** — which is *illegal under GDPR* and must be
  fixed with crypto-shredding before any real personal data touches this.

---

## 5. Prior art — settled 2026-08-31

The proposed research contribution was an algebra for propagating confidence.
Four reviewers asked for a prior-art check; it was deferred four times. Resolved:

**Provenance Semirings** — Green, Karvounarakis & Tannen, PODS 2007
(https://web.cs.ucdavis.edu/~green/papers/pods07.pdf) — is the general framework
for propagating annotations through relational algebra.

| Operation | Verdict |
| :--- | :--- |
| Join = min of contributors | **Prior art** — the access-control semiring `A = ({P < C < S < T < 0}, min, max, 0, P)` |
| Quarantine absorbs | **Prior art** — that semiring's annihilator `0` |
| Aggregate = min × coverage | Known-hard gap; the framework covers only positive RA and an aggregate's provenance cannot be a plain semiring value |
| Entity descent | Outside the framework — not a query operation at all |

**Use verbatim: the mechanism is not new; the granularity and the enforcement
point are.** Never claim invention of the join rule.

---

## 6. Known Gaps

- ~~`propagate.py` is not wired into the pipeline.~~ **Closed 2026-09-10**: `aether_studio.profile.stamp_quality` runs entity descent through `propagate_entity`, and `aether_studio.execute` aggregates row `Quality` per answer. The Phase A shape (file -> typed table -> gate -> propagated quality -> trusted view -> `pip install` -> quickstart) now exists as AetherStudio. Still open from Phase A: no `_gold` contract promotion; `_conformance` is not populated.
- **AetherStudio quality rules are generic and shallow.** Duplicate, relative-sparse, and entity descent only. The spike finding 1 came from a *semantic* rule (robot sessions identified by `browserInfo`) that no generic profiler can derive; on the same telemetry AetherStudio quarantines 0 rows. Real datasets with real defects will show deltas; this one no longer does.
- **The literal-grounding rung covers `=`, `!=`, `IN` only.** `LIKE`, `ILIKE`, `BETWEEN` on categorical columns are not grounded.
- **Accuracy is still unmeasured**, now for three model outputs: the plan, any semantic classification, and the narrative. The claim validator guarantees every *number* is real; it cannot guarantee the *sentence* is true (e.g. "peak" vs "only value"). No labelled set exists.
- **Apify actor form starts a paid run every time.** There is no dedup of identical inputs; use `apify://run/<id>` to re-read a finished run. The 300 s wait is a hard ceiling; longer actors fail closed with the run status.
- **The Postgres connector is row-capped at 50,000** and notes it; aggregates over larger tables are over a prefix. Pushdown is not implemented.
- ~~Semantic pre-step not exercised live.~~ **Closed 2026-09-10.** Open instead: the **category set is chosen by the model** and is generic (HN titles landed 25 of 40 in "Technology"); no measurement of label accuracy exists. PDFs are not loadable (no `pypdf` installed); `.docx` likewise.
- **74.2% is a floor, not a truth.** It holds only if every robot session
  self-identified in `browserInfo`. By finding 2 that cannot be known from inside.
  The real figure is unknown and lower.
- **The tier split (~90% deterministic) remains unmeasured.** No analytical SQL
  corpus existed on this machine — a workspace-wide `find` returned only Prisma
  migration DDL.
- **Sensitive data reaches the model before any gate rung runs.** Scope checking
  guards the generated query; it cannot guard the sample rows sent to write it.
  This was the security reviewer's #2 blocker and is unaddressed.
- **No authorization decision point.** Contract ownership answers *who to consult*,
  not *who may read*. No row-level security, no masking, no separation of duties —
  a self-owned column self-approves.
- **All timings are machine-local**, from one laptop. Volumes above 1,029 records
  are real record shapes replicated, not real volume.
- **No user was ever consulted.** The five "specialists" were research agents.
  The named target — an analytics engineer on a dbt team — has not been spoken to.
- **The post-compaction residual (1.48×) is not isolated.** By that point the
  table is 1.20× larger and the two effects were not separated. Treat it as an
  upper bound on residual disorder, not a measurement of it.

- **The POC's accuracy is entirely unmeasured.** No labelled set exists. The very
  first semantic probe wrongly excluded an AI-safety story from the AI category,
  so false negatives are known to occur at an unknown rate. **This is the single
  biggest gap in the POC** and the obvious next task.
- **The POC is a demo, not a benchmark.** 40 rows per run. Concurrency, sustained
  provider failure, and cost at volume are untested.
- **No POC run is audited.** Trigger evidence is real; nothing independent
  confirms the semantic filter was right. Finding 2 applies to the POC's own
  output.

### Closed 2026-09-10
- ~~Ordering's maintenance cost is unmeasured~~ — measured; see finding 4.
- ~~Replay idempotency is untested beyond one stage~~ — tested pipeline-wide and
  fixed; see §2.
- ~~`propagate.py` is not wired into the pipeline~~ — **still true of
  `propagate.py` specifically**, but the POC demonstrates the end-to-end shape
  the reviewed Phase A called for, on live data, with real operators.
- ~~The tier split is entirely unmeasured~~ — **partially** closed; see finding
  5b. Measured on a 40-row live workload, not on a production corpus.

---

## 7. History — the rejected scope (retained, not current)

Recorded 2026-08-29: a six-layer platform (ingestion, transformation, quality,
governance, permissions, analytics) on ODCS v3.1.0 + Arrow Flight SQL + DuckDB +
LanceDB + MCP, counter-positioned against Datris.ai (AGPL) and TextQL.

**Rejected 2026-08-30** by five independent reviewers who reached the same
conclusion from different disciplines: five of the six subsystems have mature
Apache/MIT incumbents; build one narrow library that composes into dbt / Dagster /
DuckDB instead. Of five claimed differentiators, one survived — and it turned out
to be partly prior art (§5).

Two corrections to that day's research, both already applied:
- **`Pretensor` does not exist.** Recorded as verified on 2026-08-29; two
  independent searches found no such project. A document-level "Verified" header
  concealed a fabricated entity — **verification is per-claim, not per-document.**
- Star counts and funding figures in that entry were second-hand; those
  re-checked against primary sources on 2026-08-29 held (Alkera AI, Datris.ai,
  TextQL, LanceDB, ODCS v3.1.0).

**Process lesson.** The narrowing was accepted and then quietly ignored: the work
that followed was a router, benchmarks, a sandbox and a scope checker, while the
differentiated component stayed unwired. Momentum reads as progress. Drift from an
agreed plan should be surfaced rather than waited for.

---

## 8. ShoonyaAI Web & Cloud Analytical Engine (Added 2026-09-16)

**Repository:** `G:\navakanth001\shoonyaai`  
**Live Endpoint:** `https://shoonyaai.vercel.app`  
**Architecture:** React 19 + TypeScript + Vite + DuckDB-Wasm / DuckDB Node + Three.js 3D Spatial + Vercel Serverless Functions.

### 8.1 Serverless Ephemeral Container Resilience Pattern
In serverless deployments (AWS Lambda / Vercel Functions), serverless instances are stateless and ephemeral. Sequential HTTP operations—such as `POST /api/workspace/datasets` (upload/sniffing) followed by `POST /api/workspace/runs` (DuckDB plan compilation & analytical execution)—frequently route to different container microVMs. Writing datasets only to `/tmp` in Container A produces an `ENOENT` cache miss (HTTP 404) in Container B.

**Solution Architecture (Client-Assisted Re-hydration):**
1. **Payload Augmentation:** The client caches the active dataset payload (`content`, `format`, `name`) in React memory.
2. **Fallback Re-hydration:** `POST /api/workspace/runs` and `POST /api/workspace/runs/:id/excel` accept optional source content. If `/tmp` or the module-scope in-memory cache experiences a cache miss, the serverless handler automatically re-parses and re-hydrates the dataset in `<5ms`.
3. **State Reconciliation:** React client state merges optimistic sources and runs rather than wholesale replacement during background polling `refresh()` loops.

### 8.2 Verified Capabilities (11/11 Test Suite)
- **Multi-Source Ingestion:** CSV (standard + UTF-8 BOM + ragged rows), TSV, JSON array of objects, and Base64 XLSX.
- **REST Connector:** Real HTTP fetching with pagination and rigid SSRF protection (rejection of `127.0.0.1`, `localhost`, and AWS/cloud metadata `169.254.169.254`).
- **PostgreSQL Connector:** Fail-closed network probing and credential hygiene.
- **Analytical Engine:** DuckDB aggregation and filtering with sub-second execution.
- **3D Spatial Visualizer:** Three.js procedural column generation, multi-axis rotation, interactive timeline slider, and color-coded categoricals.
- **Excel Provenance Export:** OpenXML binary `.xlsx` generation containing raw results and an immutable `Provenance` audit sheet.
- **Frictionless Public Pilot:** Disabled Vercel preview deployment protection (`--sso`), removing authentication/password hurdles for seamless evaluation.

### 8.3 Known Gaps & Next Steps
- Production Azure infrastructure (PostgreSQL Flexible Server, Key Vault, Entra OIDC) is not yet provisioned.
- Persistent analytical storage currently uses serverless re-hydration; production migration requires `CONTROL_DATABASE_URL` attachment.
- Mobile native binaries (Capacitor iOS/Android) require signed provisioning profiles.

### 8.4 Tabular Auto-Healing Engine (`sanitizeTabularMatrix`) (Added 2026-09-17)
Real-world operational spreadsheets (Google Sheets, POS systems, manual milk collection logs) violate pure relational database constraints. They contain:
1. **Title Banners in Row 0**: A single non-empty cell with merged metadata (e.g. `['Monthly Milk Procurement', '', '', '']`), with real headers on Row 1.
2. **Trailing Blank Columns**: Trailing commas or formula padding (e.g. `['Date', 'Vendor', 'Liters', '', '']`).
3. **Blank & Duplicate Column Headers**: Missing cell headers in the middle or duplicate names (e.g. `['Date', '', 'Amount', 'Amount']`).

**The Solution (`sanitizeTabularMatrix`)**:
- **Banner Detection**: Detects when Row 0 has only 1 populated cell while Row 1 has $\ge 2$ populated cells, cleanly discarding the banner and promoting Row 1 to headers.
- **Effective Width Boundary**: Scans all rows to find the rightmost index containing actual data, trimming away trailing empty columns.
- **Auto-Naming & Deduplication**: Assigns `column_${i+1}` to empty headers, deduplicates names (`Amount`, `Amount_2`), and truncates names exceeding 100 characters.
- **Row Normalization**: Tolerates trailing commas in rows without throwing `"A row has more cells than the header"`.

### 8.5 Cloud-to-Cloud Pull & Live Disk Sync Connectors
- **Microsoft OneDrive / SharePoint Direct Streaming**: Probes and resolves `1drv.ms` shortlinks, converts `:r:` redirect paths to `:g:` guest paths, replaces `view.aspx` with `download.aspx`, and appends `download=1`. Streams binary files directly without triggering OAuth 401 Unauthorized errors when "Anyone with the link can edit/view" is enabled.
- **Google Drive / Google Sheets Normalization**: Routes Google Sheets to `/export?format=csv`, handles Drive file IDs (`drive.google.com/uc?export=download&id=...`), intercepts large-file virus scan confirmation screens (`confirm=t`), and rejects HTML sign-in/SSO pages before parsing.
- **W3C Live Disk Sync**: Leverages browser File System Access API (`window.showOpenFilePicker`) so local desktop files retain persistent file handles for 1-click live syncing.

### 8.6 Open-Source OCR Ingestion Architecture
Evaluated and standardized legitimate, open-source, zero-API-cost tools for document and image ingestion into DuckDB:
1. **Tesseract.js (Apache-2.0)**: In-browser WASM + Web Worker engine for scanned receipts and images (PNG, JPG, TIFF, WebP). 100% private, zero cloud infrastructure cost.
2. **Mozilla PDF.js (Apache-2.0)**: Hybrid dual-tier extractor: directly streams vector text from digital PDFs with zero latency, falling back to canvas rasterization + Tesseract.js for flat scanned PDFs.
3. **JSZip + DOMParser (MIT)**: Zero-OCR extraction for EPUB publications (which are standard ZIP containers of XHTML/HTML).
4. **Mammoth.js (BSD-2)**: Converts Word (`.docx`) tables and content to clean tabular data.
Extracted tables feed directly into `sanitizeTabularMatrix()` $\rightarrow$ `profile()` $\rightarrow$ DuckDB analytical engine.


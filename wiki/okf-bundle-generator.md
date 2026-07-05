# OKF Bundle Generator
> A completed Python tool that turns a database schema into a linked Markdown knowledge bundle.

## Summary
The OKF (Open Knowledge Format) Bundle Generator reads a database, asks an LLM to describe each table in plain English, and writes one Markdown file per table — YAML frontmatter plus a human-readable body — with relative links expressing the foreign-key graph. The implementation is marked **completed**.

## Details
- **Pattern**: each concept (a database table) becomes a single `.md` file with `type`, `title`, `tags`, and `timestamp` frontmatter — the same one-file-per-concept idea this wiki itself uses.
- **Pipeline (four modules)**:
  - `extractor.py` — SQLAlchemy inspects SQLite/PostgreSQL, pulls table names, columns, types, and foreign keys into a graph dict.
  - `enricher.py` — Google GenAI SDK prompts an LLM to write each table's description and to format relationships as relative Markdown links (e.g. `[Users](../tables/users.md)`).
  - `writer.py` — composes YAML frontmatter + body and writes to `{output_dir}/tables/{table_name}.md`.
  - `main.py` — orchestrator; takes `--db-url` and `--output-dir`, loops every table through enrich → write.
- **Live code** lives outside the wiki at the repo root: `okf_generator/`, `main.py`, `setup.sh`, with output in `okf_output/`.
- Source: [okf-implementation-plan.md](file:///C:/Users/navka/navakanth001/sources/technical/okf-implementation-plan.md)

## Best Practices & Guidelines
- **Metadata vs. Body**: Keep YAML metadata minimal but strongly typed (`type` is required; `title`, `description`, `resource_link`, `tags`, `timestamp` are recommended) for routing. The Markdown body contains human-readable rules or formulas.
- **Progressive Disclosure**: Use an `index.md` file in directories as a table of contents. This allows AI agents to read the index first and dynamically decide which specific documents to pull into context, saving token windows.
- **When to Use OKF (Stable vs. Dynamic)**: OKF is designed to capture **stable expertise** (definitions, rules, "hard-won" context changing less than once a month). It is **not** a replacement for live data pipelines (e.g., live inventory or current pricing) which should be accessed via APIs.

## Real-World Validation (2026-07-05)
- First production run: pointed the generator at `crp/experience.db` (the frozen CRP Phase 0 Experience DB — see [Cognitive Runtime Platform](cognitive-runtime-platform.md)), a genuinely stable schema and thus a clean fit for OKF's scope.
- Command: `.venv/Scripts/python.exe main.py --db-url "sqlite:///crp/experience.db" --output-dir "okf_crp_bundle"` (requires `GEMINI_API_KEY` from repo-root `.env`).
- Result: `okf_crp_bundle/` with `index.md` + 4 table pages (`events`, `rejections`, `runs`, `scores`). Enrichment quality confirmed good — accurate column descriptions, correct relative FK links (e.g. `events` → `runs`).
- Reproducibility gaps found and fixed: `okf_generator/requirements.txt` was missing (sqlalchemy, google-genai, pyyaml never pinned anywhere); `main.py` used the deprecated `datetime.utcnow()`, switched to `datetime.now(timezone.utc)`. Both shipped via [PR #30](https://github.com/navakanth1984/AgentOSClaude/pull/30), merged into `master`.
- Candidate next domains (real stable-schema databases inventoried in this workspace): `nth_brain.db`, `ClawGlove/provenance_ledger.db`. Transient/test databases (job queues, test fixtures) are explicitly out of scope per the stable-vs-dynamic guideline above.

## Connections
- The link-graph-of-Markdown idea is the same principle behind [Agentic Loops Architecture](agentic-loops-architecture.md) and this knowledge base.
- LLM-enrichment-of-structured-data mirrors the RAG ingestion in [Nth Dimension Academy](nth-dimension-academy.md).
- **Pattern reused beyond databases (2026-07-06)**: the metadata/body split + progressive-disclosure guidelines above were applied outside OKF's original database scope to document [Design Extraction Workflow](design-extraction-workflow.md) — a reusable AI-tool practice, not a DB table. Confirms these guidelines generalize to any piece of "stable expertise" worth capturing once and shared across sessions/tools, not just schema-derived content.

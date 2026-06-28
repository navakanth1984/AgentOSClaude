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

## Connections
- The link-graph-of-Markdown idea is the same principle behind [Agentic Loops Architecture](agentic-loops-architecture.md) and this knowledge base.
- LLM-enrichment-of-structured-data mirrors the RAG ingestion in [Nth Dimension Academy](nth-dimension-academy.md).

# Implementation Plan: OKF Bundle Generator (COMPLETED ✅)

## Context
You are tasked with building a Python automation script that generates an Open Knowledge Format (OKF) bundle from a database schema. OKF is a standard where each concept (e.g., a database table) is represented as a single Markdown file containing YAML frontmatter and plain text body content.

## Architecture
Create a Python module with the following file structure:
- `requirements.txt` ✅
- `main.py` (Orchestrator) ✅
- `okf_generator/` ✅
  - `__init__.py` ✅
  - `extractor.py` (Pulls schema from SQLite/PostgreSQL) ✅
  - `enricher.py` (Uses an LLM via the Google GenAI SDK to write descriptions) ✅
  - `writer.py` (Handles YAML frontmatter and writes the `.md` files) ✅

## Phase 1: Dependency Setup [DONE ✅]
- [x] Create `requirements.txt` including `pyyaml`, `google-genai`, and `sqlalchemy`.
- [x] Write a shell script `setup.sh` to create a virtual environment and install dependencies.

## Phase 2: The Extractor (`extractor.py`) [DONE ✅]
- [x] Create a function `get_schema_metadata(db_url)`.
- [x] Use SQLAlchemy to inspect the database.
- [x] Extract all table names, column names, data types, and explicit foreign key relationships.
- [x] Return a dictionary representing the graph of the database.

## Phase 3: The LLM Enricher (`enricher.py`) [DONE ✅]
- [x] Create a function `generate_markdown_content(table_name, columns, foreign_keys)`.
- [x] Use the `google-genai` SDK.
- [x] Prompt the LLM to write a clear, human-readable Markdown description of the table's purpose based on its column names.
- [x] **Crucial:** Instruct the LLM to format the relationships section using relative markdown links to other OKF files (e.g., "Links to [Users](../tables/users.md)").

## Phase 4: The Writer (`writer.py`) [DONE ✅]
- [x] Create a function `write_okf_file(output_dir, table_data, md_content)`.
- [x] Generate the YAML frontmatter containing:
  - `type: Table`
  - `title: {Table Name}`
  - `tags: [database, auto-generated]`
  - `timestamp: {current_date}`
- [x] Concatenate the YAML frontmatter (enclosed in `---`) with the LLM-generated Markdown content.
- [x] Write the file to `{output_dir}/tables/{table_name}.md`.

## Phase 5: The Orchestrator (`main.py`) [DONE ✅]
- [x] Tie the modules together.
- [x] Accept CLI arguments for `--db-url` and `--output-dir`.
- [x] Iterate through every table found by the extractor, pass it to the enricher, and write it via the writer.
- [x] Create an `index.md` file at the root of the output directory linking to all generated table files.

## Execution Rules for Antigravity
- [x] Stop and ask for my Google GenAI API key when you reach Phase 3. Do not hardcode a mock key.
- [x] Write modular code with docstrings.
- [x] Check off each phase as you complete it.

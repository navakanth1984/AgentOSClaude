"""
OKF Bundle Generator Orchestrator.
Coordinates the database extractor, LLM enricher, and file writer.
"""

import os
import argparse
from datetime import datetime
from okf_generator.extractor import get_schema_metadata
from okf_generator.enricher import generate_markdown_content
from okf_generator.writer import write_okf_file

def load_env():
    """Manually parse .env to load GEMINI_API_KEY if not in environment."""
    if not os.environ.get("GEMINI_API_KEY") and os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        if key.strip() == "GEMINI_API_KEY":
                            os.environ["GEMINI_API_KEY"] = val.strip()
                            break
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")

def main():
    load_env()
    parser = argparse.ArgumentParser(description="Generate an OKF bundle from a database schema.")
    parser.add_argument("--db-url", required=True, help="Database connection URL (e.g. sqlite:///db.sqlite)")
    parser.add_argument("--output-dir", required=True, help="Directory to write the OKF bundle to")
    parser.add_argument("--api-key", default=None, help="Google GenAI API Key (optional, defaults to GEMINI_API_KEY environment variable)")

    args = parser.parse_args()

    # 1. Pull schema from database using extractor
    print(f"Extracting schema metadata from: {args.db_url}")
    try:
        metadata = get_schema_metadata(args.db_url)
    except Exception as e:
        print(f"Error inspecting database: {e}")
        return

    tables = metadata.get("tables", {})
    if not tables:
        print("No tables found in the database. Exiting.")
        return

    print(f"Found {len(tables)} tables: {', '.join(tables.keys())}")
    print("Generating OKF files...")

    # Ensure output root directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    generated_tables = []

    # Iterate through tables, enrich, and write
    for table_name, table_schema in tables.items():
        print(f"  -> Processing table: {table_name}")
        columns = table_schema["columns"]
        foreign_keys = table_schema["foreign_keys"]

        # 2. Enrich columns and relations with LLM
        try:
            md_content = generate_markdown_content(
                table_name=table_name,
                columns=columns,
                foreign_keys=foreign_keys,
                api_key=args.api_key
            )
        except Exception as e:
            print(f"     [!] LLM Enrichment failed for {table_name}: {e}")
            print("         Falling back to schema-only Markdown description.")
            # Fallback schema presentation
            columns_fallback = "\n".join([f"- {c['name']} ({c['type']})" for c in columns])
            md_content = f"### Schema Description\n\nAuto-generated schema fallback for `{table_name}`. LLM enrichment failed: {e}\n\n**Columns:**\n{columns_fallback}"

        # 3. Write via the writer
        table_data = {"name": table_name}
        try:
            file_path = write_okf_file(args.output_dir, table_data, md_content)
            print(f"     [+] Wrote: {file_path}")
            generated_tables.append(table_name)
        except Exception as e:
            print(f"     [!] Failed to write OKF file for {table_name}: {e}")

    # 4. Create an index.md linking to all generated files
    index_path = os.path.join(args.output_dir, "index.md")
    current_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    index_content = f"""# OKF Bundle Schema Index

**Generated on:** {current_date}
**Source Database:** `{args.db_url}`

## Tables
"""
    for tbl in sorted(generated_tables):
        index_content += f"- [{tbl}](./tables/{tbl}.md)\n"

    try:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)
        print(f"[+] Successfully generated index file at: {index_path}")
    except Exception as e:
        print(f"[!] Failed to write index file: {e}")

    print("OKF Bundle generation complete!")

if __name__ == "__main__":
    main()

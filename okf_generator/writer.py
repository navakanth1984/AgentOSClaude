"""
Writer module for OKF Bundle Generator.
Formats YAML frontmatter and writes OKF Markdown files.
"""

import os
import yaml
from datetime import datetime

def write_okf_file(output_dir: str, table_data: dict, md_content: str) -> str:
    """
    Generates YAML frontmatter, prepends it to markdown content,
    and writes the output to {output_dir}/tables/{table_name}.md.

    Args:
        output_dir (str): Root of the output directory.
        table_data (dict): Table metadata (must contain 'name').
        md_content (str): Human-readable markdown text describing the table.

    Returns:
        str: The file path where the OKF file was written.
    """
    table_name = table_data["name"]
    tables_dir = os.path.join(output_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)

    # Prepare YAML frontmatter
    frontmatter = {
        "type": "Table",
        "title": table_name,
        "tags": ["database", "auto-generated"],
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    # Generate YAML block
    yaml_block = yaml.dump(frontmatter, sort_keys=False, default_flow_style=False)

    # Concatenate frontmatter with the content
    full_content = f"---\n{yaml_block}---\n\n# {table_name}\n\n{md_content}\n"

    # Write file
    file_path = os.path.join(tables_dir, f"{table_name}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_content)

    return file_path

"""
Enricher module for OKF Bundle Generator.
Uses Google GenAI SDK (Gemini) to generate description documentation for tables.
"""

import os
from google import genai

def generate_markdown_content(table_name: str, columns: list, foreign_keys: list, api_key: str | None = None) -> str:
    """
    Prompts Gemini to generate a clear, human-readable Markdown description
    of the table's purpose and fields, linking relationships relatively.

    Args:
        table_name (str): The name of the table.
        columns (list): Column metadata.
        foreign_keys (list): Foreign key relationship metadata.
        api_key (str, optional): Google GenAI API key. If not provided,
            the Client SDK will look up the GEMINI_API_KEY environment variable.

    Returns:
        str: Generated markdown text.
    """
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        # Client will automatically read GEMINI_API_KEY from environment
        client = genai.Client()

    # Formulate a structured text representation of the schema
    columns_str = "\n".join([
        f"- {col['name']} ({col['type']})" + (" (Primary Key)" if col['primary_key'] else "") + (" (Nullable)" if col['nullable'] else " (Not Null)")
        for col in columns
    ])

    if foreign_keys:
        fkeys_str = "\n".join([
            f"- {', '.join(fk['constrained_columns'])} references {fk['referred_table']}({', '.join(fk['referred_columns'])})"
            for fk in foreign_keys
        ])
    else:
        fkeys_str = "None"

    prompt = f"""
You are an expert database documentation writer. Generate a clear, professional, and human-readable Markdown description of a database table's purpose and structure based on its schema.

Table Name: {table_name}

Columns:
{columns_str}

Foreign Key Relationships:
{fkeys_str}

Please generate the documentation using the following structure:
1. A brief overview describing the purpose of this table (what concept or entity it represents).
2. A detailed explanation of key columns.
3. A "Relationships" section.
   CRUCIAL REQUIREMENT: For each relationship (foreign key or logical connection), you MUST format it as a relative markdown link to other OKF files. Use the format: `[Table Name](../tables/target_table_name.md)`.
   Example: "This table links to [Users](../tables/users.md) via `user_id`."

Do NOT include any YAML frontmatter or main title header (like `# {table_name}`) in the output. Just return the markdown body content starting with the overview description.
"""

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )

    return response.text.strip()

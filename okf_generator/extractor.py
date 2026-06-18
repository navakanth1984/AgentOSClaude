"""
Extractor module for OKF Bundle Generator.
Extracts schema metadata from SQLite or PostgreSQL databases using SQLAlchemy.
"""

from sqlalchemy import create_engine, inspect

def get_schema_metadata(db_url: str) -> dict:
    """
    Connects to a database and extracts all table schemas, column metadata,
    and foreign key relationships.

    Args:
        db_url (str): The database connection URL (e.g. sqlite:///test.db or postgresql://...)

    Returns:
        dict: A dictionary mapping table names to their columns and foreign keys.
            Format:
            {
                "tables": {
                    "table_name": {
                        "columns": [
                            {"name": "col_name", "type": "VARCHAR", "primary_key": True, "nullable": False},
                            ...
                        ],
                        "foreign_keys": [
                            {
                                "constrained_columns": ["col_name"],
                                "referred_table": "other_table",
                                "referred_columns": ["id"]
                            },
                            ...
                        ]
                    }
                }
            }
    """
    engine = create_engine(db_url)
    inspector = inspect(engine)
    
    schema_metadata = {"tables": {}}
    
    # Get all table names
    table_names = inspector.get_table_names()
    
    for table_name in table_names:
        # Extract columns
        columns = []
        for col in inspector.get_columns(table_name):
            columns.append({
                "name": col["name"],
                "type": str(col["type"]),
                "primary_key": bool(col.get("primary_key", False)),
                "nullable": bool(col.get("nullable", True))
            })
            
        # Extract foreign key relationships
        foreign_keys = []
        for fk in inspector.get_foreign_keys(table_name):
            foreign_keys.append({
                "constrained_columns": fk["constrained_columns"],
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"]
            })
            
        schema_metadata["tables"][table_name] = {
            "columns": columns,
            "foreign_keys": foreign_keys
        }
        
    return schema_metadata

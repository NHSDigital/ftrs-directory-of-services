"""
This script is used to load the schema to the database.

Local Usage:
    python -m pipeline.schema --schema-path <path_to_schema> --db-uri <db_uri> [--drop] [--schema-name <schema_name>]
"""

import logging
from pathlib import Path

from sqlalchemy import Connection, text

from pipeline.common import get_db_engine


def _load_schema_file(schema_path: str) -> str:
    """
    Load the schema file and return the content
    """
    schema_path = Path(schema_path).resolve()
    if not schema_path.is_file():
        err_msg = f"Schema file not found: {schema_path}"
        raise ValueError(err_msg)

    logging.info(f"Loading schema from {schema_path}")
    return schema_path.read_text()


def _drop_schema(
    conn: Connection, schema_name: str, bypass_input: bool = False
) -> None:
    """
    Drop the schema from the database
    """
    logging.info(f"Dropping the schema: {schema_name}")
    if not bypass_input:
        logging.info(
            "Are you sure you want to do this? This will drop the existing schema and all the data it contains."
        )
        user_response = input("Type 'yes' to continue: ")
        if user_response != "yes":
            logging.warning("Aborting the schema load")
            raise SystemExit(1)

    conn.execute(text(f'DROP SCHEMA "{schema_name}" CASCADE'))
    conn.commit()

    logging.info("Schema dropped successfully")


def load_schema(
    schema_path: str,
    db_uri: str,
    drop: bool = False,
    drop_schema_name: str = "Core",
) -> None:
    """
    Load the schema from a file and execute it in the database
    """
    content = _load_schema_file(schema_path)
    engine = get_db_engine(db_uri)

    with engine.connect() as conn:
        if drop:
            _drop_schema(conn, schema_name=drop_schema_name)

        logging.info("Executing the schema")
        conn.execute(text(content))
        conn.commit()

    logging.info("Schema loaded successfully")


def main(args: list[str] | None = None) -> None:
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Load schema to the database")
    parser.add_argument(
        "--db-uri", type=str, required=True, help="URI to connect to the database"
    )
    parser.add_argument(
        "--schema-path", type=str, required=True, help="Path to the schema file"
    )
    parser.add_argument(
        "--drop", action="store_true", help="Drop the existing schema before loading"
    )
    parser.add_argument(
        "--drop-schema-name",
        type=str,
        default="Core",
        help="Name of the schema to drop",
    )

    args = parser.parse_args(args)
    load_schema(args.schema_path, args.db_uri, args.drop, args.drop_schema_name)

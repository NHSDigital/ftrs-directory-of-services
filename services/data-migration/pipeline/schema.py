"""
This script is used to load the schema to the database.

Local Usage:
    python -m pipeline.schema --schema-path <path_to_schema> --db-uri <db_uri> [--drop] [--schema-name <schema_name>]
"""

import logging
from pathlib import Path

from pipeline.common import get_db_connection


def load_schema(
    schema_path: str,
    db_uri: str,
    drop: bool = False,
    drop_schema_name: str = "Core",
) -> None:
    """
    Load the schema from a file and execute it in the database
    """
    schema_path = Path(schema_path).resolve()
    if not schema_path.is_file():
        err_msg = "Schema file not found: {schema_path}"
        raise ValueError(err_msg)

    logging.info(f"Loading schema from {schema_path}")
    content = schema_path.read_text()

    if drop:
        logging.info(
            f"Drop flag is set. The following schema will be dropped: {drop_schema_name}"
        )
        logging.info(
            "Are you sure you want to do this? This will drop the existing schema and all the data it contains."
        )
        user_response = input("Type 'yes' to continue: ")
        if user_response != "yes":
            logging.warning("Aborting the schema load")
            return

    conn = get_db_connection(db_uri)
    with conn.cursor() as cur:
        if drop:
            logging.info(f"Dropping the schema: {drop_schema_name}")
            cur.execute(f'DROP SCHEMA "{drop_schema_name}" CASCADE')
            conn.commit()

        logging.info("Executing the schema")
        cur.execute(content)
        conn.commit()

    conn.close()
    logging.info("Schema loaded successfully")


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Load schema to the database")
    parser.add_argument("--db-uri", type=str, help="URI to connect to the database")
    parser.add_argument("--schema-path", type=str, help="Path to the schema file")
    parser.add_argument(
        "--drop", action="store_true", help="Drop the existing schema before loading"
    )
    parser.add_argument(
        "--drop-schema-name",
        type=str,
        default="Core",
        help="Name of the schema to drop",
    )

    args = parser.parse_args()
    load_schema(args.schema_path, args.db_uri, args.drop, args.drop_schema_name)

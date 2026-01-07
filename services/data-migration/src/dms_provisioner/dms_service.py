import re
from pathlib import Path
from typing import List

import chevron
from ftrs_common.logger import Logger
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

LOGGER = Logger.get(service="DMS-Lambda-handler")
TEMPLATE_DIR = Path(__file__).parent / "templates"
SCHEMA_FILE = TEMPLATE_DIR / "pathwaysdos_schema.sql"
RELATED_TABLES = ["serviceendpoints"]
INDEXES_TABLES = [
    "services",
    "servicetypes",
    "serviceendpoints",
    "servicedayopenings",
    "servicedayopeningtimes",
    "servicesgsds",
    "servicedispositions",
    "servicespecifiedopeningdates",
    "servicespecifiedopeningtimes",
]


def create_dms_user(engine: Engine, rds_username: str, rds_password: str) -> None:
    """
    Create a DMS user in the target RDS instance
    """
    dms_user_template = (TEMPLATE_DIR / "create_dms_user.mustache").read_text()

    command = chevron.render(
        dms_user_template,
        {"rds_username": rds_username, "rds_password": rds_password},
    )

    with engine.connect() as conn:
        conn.execute(text(command))
        conn.commit()

    LOGGER.info("DMS user created")


def create_services_trigger(
    engine: Engine,
    lambda_arn: str,
    aws_region: str,
) -> None:
    """
    Create RDS trigger for services table to invoke Lambda on data changes
    """
    dms_template = (TEMPLATE_DIR / "services_trigger.mustache").read_text()
    command = chevron.render(
        dms_template,
        {
            "table_name": "services",
            "lambda_arn": lambda_arn,
            "aws_region": aws_region,
        },
    )
    with engine.connect() as connection:
        connection.execute(text(command))
        connection.commit()

    LOGGER.info("DB trigger for services table created successfully.")


def create_service_related_table_trigger(
    engine: Engine,
    lambda_arn: str,
    aws_region: str,
    table_name: str,
) -> None:
    """
    Create RDS trigger for related service tables to invoke Lambda on data changes
    """
    dms_template = (TEMPLATE_DIR / "service_related_trigger.mustache").read_text()
    command = chevron.render(
        dms_template,
        {
            "table_name": table_name,
            "lambda_arn": lambda_arn,
            "aws_region": aws_region,
        },
    )
    with engine.connect() as connection:
        connection.execute(text(command))
        connection.commit()

    LOGGER.info(f"DB trigger for {table_name} table created successfully.")


def create_rds_triggers(
    engine: Engine,
    lambda_arn: str,
    aws_region: str,
) -> None:
    """
    Create RDS trigger for replica database to invoke Lambda on data changes
    """
    create_services_trigger(
        engine=engine,
        lambda_arn=lambda_arn,
        aws_region=aws_region,
    )

    for table in RELATED_TABLES:
        create_service_related_table_trigger(
            engine=engine,
            lambda_arn=lambda_arn,
            aws_region=aws_region,
            table_name=table,
        )


def extract_indexes_from_sql_file(sql_file_path: Path = SCHEMA_FILE) -> List[str]:
    """
    Extract CREATE INDEX statements from a SQL schema file.
    Returns a list of CREATE INDEX statements.
    """
    if not sql_file_path.exists():
        raise FileNotFoundError(f"Schema file not found: {sql_file_path}")

    content = sql_file_path.read_text()

    # Regex to match CREATE INDEX and CREATE UNIQUE INDEX statements
    # Matches multi-line statements ending with semicolon
    index_pattern = re.compile(
        r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+[^;]+;",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    indexes = index_pattern.findall(content)

    # Clean up whitespace and normalize
    cleaned_indexes = []
    for idx in indexes:
        # Normalize whitespace
        cleaned = " ".join(idx.split())
        # Add IF NOT EXISTS if not present
        if "IF NOT EXISTS" not in cleaned.upper():
            cleaned = cleaned.replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS", 1)
            cleaned = cleaned.replace(
                "CREATE UNIQUE INDEX", "CREATE UNIQUE INDEX IF NOT EXISTS", 1
            )
        cleaned_indexes.append(cleaned)

    LOGGER.info(
        f"Extracted {len(cleaned_indexes)} index statements from {sql_file_path}"
    )
    return cleaned_indexes


def _extract_index_name(stmt: str) -> str:
    """
    Extract index name from CREATE INDEX statement.
    """
    # Match index name after CREATE [UNIQUE] INDEX [IF NOT EXISTS]
    match = re.search(
        r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)",
        stmt,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def _index_exists(engine: Engine, index_name: str, schema: str = "pathwaysdos") -> bool:
    """
    Check if an index already exists in the database.
    """
    query = text("""
        SELECT 1 FROM pg_indexes
        WHERE schemaname = :schema AND indexname = :index_name
        LIMIT 1
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"schema": schema, "index_name": index_name})
        return result.fetchone() is not None


def create_indexes_from_sql_file(
    engine: Engine,
    sql_file_path: Path = SCHEMA_FILE,
    tables: List[str] = None,
) -> None:
    """
    Extract indexes from SQL schema file and create them in the database.
    Optionally filter by table names. Only creates indexes that don't already exist.
    """
    if tables is None:
        tables = INDEXES_TABLES

    indexes = extract_indexes_from_sql_file(sql_file_path)

    if tables:
        # Filter indexes to only include those for specified tables
        filtered_indexes = []
        for idx in indexes:
            for table in tables:
                if (
                    f"ON {table}" in idx.lower()
                    or f"on pathwaysdos.{table}" in idx.lower()
                ):
                    filtered_indexes.append(idx)
                    break
        indexes = filtered_indexes

    created_count = 0
    skipped_count = 0
    failed_count = 0

    for stmt in indexes:
        index_name = _extract_index_name(stmt)

        if index_name and _index_exists(engine, index_name):
            LOGGER.debug(f"Index already exists, skipping: {index_name}")
            skipped_count += 1
            continue

        try:
            with engine.connect() as connection:
                connection.execute(text(stmt))
                connection.commit()
            LOGGER.debug(f"Created index: {stmt[:80]}...")
            created_count += 1
        except SQLAlchemyError as e:
            LOGGER.warning(f"Failed to create index: {str(e)}")
            failed_count += 1

    LOGGER.info(
        f"Index creation complete: {created_count} created, {skipped_count} skipped, {failed_count} failed"
    )

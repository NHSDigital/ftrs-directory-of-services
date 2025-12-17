from pathlib import Path
from typing import Dict, List, Optional

import chevron
from ftrs_common.logger import Logger
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

LOGGER = Logger.get(service="DMS-Lambda-handler")
TEMPLATE_DIR = Path(__file__).parent / "templates"
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


def get_indexes_for_tables(
    engine: Engine, schema_name: str, table_names: Optional[List[str]] = None
) -> Dict[str, List[str]]:
    if table_names is None:
        table_names = INDEXES_TABLES

    if not table_names:
        LOGGER.warning("No table names provided to get indexes for.")
        return {}

    indexes = {}
    query = text("""
                SELECT tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = :schema_name
                AND tablename = ANY (:table_names)
                ORDER BY tablename, indexname
                """)

    with engine.connect() as connection:
        # PostgreSQL requires special handling for array parameters
        result = connection.execute(
            query, {"schema_name": schema_name, "table_names": table_names}
        )

        for row in result:
            table = row.tablename
            index = row.indexname

            if table not in indexes:
                indexes[table] = []

            # Skip primary key indexes (they already exist)
            if not index.endswith("_pkey") and not index.endswith("_pk"):
                indexes[table].append({"name": index, "definition": row.indexdef})

    LOGGER.info(f"Retrieved indexes for {len(indexes)} tables.")
    return indexes


def create_indexes_for_tables(
    engine: Engine,
    indexes: Dict[str, List[Dict[str, str]]],
    schema_name: str,
    skip_existing: bool = True,
) -> Dict[str, List[str]]:
    created_indexes = {}
    skipped_indexes = {}

    try:
        with (
            engine.begin() as connection
        ):  # Use begin() for automatic transaction management
            for table_name, index_list in indexes.items():
                created_indexes[table_name] = []
                skipped_indexes[table_name] = []

                for index_info in index_list:
                    index_name = index_info["name"]
                    index_def = index_info["definition"]
                    # Build CREATE INDEX statement
                    if skip_existing:
                        create_stmt = f"""
                                    DO $$
                                    BEGIN
                                        IF NOT EXISTS (
                                            SELECT 1
                                            FROM pg_indexes
                                            WHERE schemaname = '{schema_name}'
                                            AND tablename = '{table_name}'
                                            AND indexname = '{index_name}'
                                        ) THEN
                                            EXECUTE '{index_def.replace("'", "''")}';
                                        END IF;
                                    END $$;
                                    """
                    else:
                        create_stmt = index_def
                    try:
                        connection.execute(text(create_stmt))
                        created_indexes[table_name].append(index_name)
                        LOGGER.debug(
                            f"Created index {index_name} on {schema_name}.{table_name}"
                        )

                    except SQLAlchemyError as e:
                        if "already exists" in str(e) or "duplicate key" in str(e):
                            skipped_indexes[table_name].append(index_name)
                            LOGGER.debug(
                                f"Index {index_name} already exists on {table_name}"
                            )
                        else:
                            LOGGER.warning(
                                f"Failed to create index {index_name} on {table_name}: {str(e)}"
                            )

            LOGGER.info(
                f"Index creation completed. Created: {sum(len(v) for v in created_indexes.values())}, "
                f"Skipped: {sum(len(v) for v in skipped_indexes.values())}"
            )
    except SQLAlchemyError:
        LOGGER.exception("Error creating indexes")
        raise

import pytest
import boto3
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Generator
from loguru import logger

from sqlalchemy import text, MetaData
from testcontainers.postgres import PostgresContainer
from testcontainers.localstack import LocalStackContainer
from sqlmodel import create_engine, SQLModel, Session
from ftrs_data_layer.domain import legacy
from utilities.common.legacy_dos_rds_tables import LEGACY_DOS_TABLES
from utilities.common.rds_data import gp_service
from utilities.common.dynamoDB_tables import dynamodb_tables




# Session-scoped containers (keep these as session-scoped for efficiency)
@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """PostgreSQL container for testing."""
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def localstack_container() -> Generator[LocalStackContainer, None, None]:
    """LocalStack container with DynamoDB for testing."""
    with LocalStackContainer(image="localstack/localstack:3.0") as localstack:
        yield localstack


def _get_source_db_config() -> dict:
    return {
        "host": os.getenv("SOURCE_DB_HOST", "localhost"),
        "port": os.getenv("SOURCE_DB_PORT", "5432"),
        "database": os.getenv("SOURCE_DB_NAME", "pathwaysdos"),
        "username": os.getenv("SOURCE_DB_USER", "postgres"),
        "password": os.getenv("SOURCE_DB_PASSWORD", "password"),
    }


def _dump_schema_and_data(
    source_config: dict, schema_file: str, data_file: str
) -> None:
    """Dump database schema and data for selected tables using pg_dump."""

    # First dump the schema only
    schema_cmd = [
        "pg_dump",
        f"--host={source_config['host']}",
        f"--port={source_config['port']}",
        f"--username={source_config['username']}",
        f"--dbname={source_config['database']}",
        "--schema-only",
        "--no-privileges",
        "--no-owner",
        "--no-security-labels",
        "--no-tablespaces",
        "--schema=pathwaysdos",
        f"--file={schema_file}",
    ]

    # Then dump data for specific tables only
    table_args = []
    for table in LEGACY_DOS_TABLES:
        table_args.extend(["--table", f"pathwaysdos.{table}"])

    data_cmd = [
        "pg_dump",
        f"--host={source_config['host']}",
        f"--port={source_config['port']}",
        f"--username={source_config['username']}",
        f"--dbname={source_config['database']}",
        "--data-only",
        "--disable-triggers",
        "--no-privileges",
        "--no-owner",
        "--no-security-labels",
        "--no-tablespaces",
        f"--file={data_file}",
    ] + table_args

    env = os.environ.copy()
    env["PGPASSWORD"] = source_config["password"]

    logger.info(f"Dumping schema to: {schema_file}")
    schema_result = subprocess.run(schema_cmd, env=env, capture_output=True, text=True)

    if schema_result.returncode != 0:
        raise RuntimeError(f"Schema dump failed: {schema_result.stderr}")

    logger.info(f"Dumping data for tables: {', '.join(LEGACY_DOS_TABLES)}")
    data_result = subprocess.run(data_cmd, env=env, capture_output=True, text=True)

    if data_result.returncode != 0:
        raise RuntimeError(f"Data dump failed: {data_result.stderr}")

    logger.info("Schema and data dump completed successfully")


def _load_schema_and_data(
    container_config: dict, schema_file: str, data_file: str
) -> None:
    """Load schema and data into the test container."""

    # Load schema first
    schema_cmd = [
        "psql",
        f"--host={container_config['host']}",
        f"--port={container_config['port']}",
        f"--username={container_config['username']}",
        f"--dbname={container_config['database']}",
        f"--file={schema_file}",
    ]

    # Then load data
    data_cmd = [
        "psql",
        f"--host={container_config['host']}",
        f"--port={container_config['port']}",
        f"--username={container_config['username']}",
        f"--dbname={container_config['database']}",
        f"--file={data_file}",
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = container_config["password"]

    logger.info("Loading schema into test container")
    schema_result = subprocess.run(schema_cmd, env=env, capture_output=True, text=True)

    if schema_result.returncode != 0:
        logger.warning(f"Schema load had warnings: {schema_result.stderr}")

    logger.info("Loading data into test container")
    data_result = subprocess.run(data_cmd, env=env, capture_output=True, text=True)

    if data_result.returncode != 0:
        logger.warning(f"Data load had warnings: {data_result.stderr}")

    logger.info("Schema and data loaded successfully")


def _init_database(engine):
    """Initialize database with schema and tables."""
    # First, clean up any existing database to ensure we start fresh
    _cleanup_database(engine)

    with engine.connect() as conn:
        # Create schema first
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS pathwaysdos"))
        conn.commit()

    # Create tables with the proper metadata that includes the schema
    # The legacy models have schema="pathwaysdos" in their metadata
    legacy.LegacyDoSModel.metadata.create_all(engine)


def _init_database_with_migration(postgres_container: PostgresContainer):
    """Initialize database with schema and data from source database."""
    # Get container connection details
    connection_string = postgres_container.get_connection_url()
    engine = create_engine(connection_string, echo=False)

    # First, clean up any existing database to ensure we start fresh
    _cleanup_database(engine)

    # Get source database configuration
    source_config = _get_source_db_config()

    # Parse connection URL to get individual components for psql commands
    from urllib.parse import urlparse

    parsed = urlparse(connection_string)

    container_config = {
        "host": parsed.hostname,
        "port": str(parsed.port),
        "database": parsed.path.lstrip("/"),
        "username": parsed.username,
        "password": parsed.password,
    }

    # Create temporary files for schema and data dumps
    with (
        tempfile.NamedTemporaryFile(
            mode="w", suffix=".sql", delete=False
        ) as schema_file,
        tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as data_file,
    ):
        schema_path = schema_file.name
        data_path = data_file.name

    try:
        # Dump schema and data from source
        _dump_schema_and_data(source_config, schema_path, data_path)

        # Load schema and data into test container
        _load_schema_and_data(container_config, schema_path, data_path)

    finally:
        # Clean up temporary files
        try:
            Path(schema_path).unlink(missing_ok=True)
            Path(data_path).unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary files: {e}")


def _cleanup_database(engine):
    """Clean up a database by dropping all tables and schema."""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'pathwaysdos'"
                )
            )
            schema_exists = result.fetchone() is not None

            if schema_exists:
                # Drop all tables in the schema
                conn.execute(text("DROP SCHEMA IF EXISTS pathwaysdos CASCADE"))
                conn.commit()
                logger.info("Database schema 'pathwaysdos' dropped successfully")
            else:
                logger.info(
                    "Database schema 'pathwaysdos' does not exist, no cleanup needed"
                )

            # Also check for any tables in public schema (just to be thorough)
            result = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                )
            )
            tables = [row[0] for row in result]

            if tables:
                logger.info(f"Dropping {len(tables)} tables from 'public' schema")
                for table in tables:
                    conn.execute(
                        text(f'DROP TABLE IF EXISTS "public"."{table}" CASCADE')
                    )
                conn.commit()

    except Exception as e:
        # Log error but don't fail the test
        logger.error(f"Warning: Failed to cleanup database: {e}")


@pytest.fixture(name="dos_db", scope="function")
def fixture_dos_db(
    postgres_container: PostgresContainer,
) -> Generator[Session, None, None]:
    """
    DoS database fixture for BDD tests.
    Creates a clean database session with all tables for each test.
    """
    connection_string = postgres_container.get_connection_url()
    engine = create_engine(connection_string, echo=False)

    try:
        # Initialize a database with schema
        _init_database(engine)

        # Create a session
        session = Session(engine)
        _seed_gp_organisations(session)

        yield session

    finally:
        # Cleanup: close session and cleanup database
        if "session" in locals():
            session.close()

        # Clean up the database
        _cleanup_database(engine)

        # Dispose of the engine to close all connections
        engine.dispose()


# New fixture for tests that need migrated data
@pytest.fixture(name="dos_db_with_migration", scope="function")
def fixture_dos_db_with_migration(
    postgres_container: PostgresContainer,
) -> Generator[Session, None, None]:
    """
    DoS database fixture with migrated data from a source database.
    Creates a database session with schema and data loaded from source DB.
    """
    connection_string = postgres_container.get_connection_url()
    engine = create_engine(connection_string, echo=False)

    try:
        logger.info("Initializing database with schema and data from source DB")
        _init_database_with_migration(postgres_container)

        # Create a session
        session = Session(engine)
        yield session

    finally:
        # Cleanup: close session and cleanup database
        if "session" in locals():
            session.close()

        # Clean up the database
        _cleanup_database(engine)

        # Dispose of the engine to close all connections
        engine.dispose()


@pytest.fixture(name="dynamodb", scope="function")
def fixture_dynamodb(
    localstack_container: LocalStackContainer,
) -> Generator[dict, None, None]:
    """
    DynamoDB fixture for BDD tests.
    Provides both client and resource with pre-created tables for each test.
    """
    endpoint_url = localstack_container.get_url()

    client = boto3.client(
        "dynamodb",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )

    resource = boto3.resource(
        "dynamodb",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )

    try:
        # Create tables
        _create_dynamodb_tables(client)

        yield {"client": client, "resource": resource, "endpoint_url": endpoint_url}

    finally:
        # Cleanup: Delete all tables
        _cleanup_dynamodb_tables(client)


def _seed_gp_organisations(session: Session) -> None:
    """Seed the database with GP organisations for testing."""
    for org in gp_service:
        session.add(org)

    session.commit()


def _create_dynamodb_tables(client) -> None:
    """Create DynamoDB tables for testing."""
    for table_config in dynamodb_tables:
        try:
            client.create_table(**table_config)
            waiter = client.get_waiter("table_exists")
            waiter.wait(TableName=table_config["TableName"])
        except client.exceptions.ResourceInUseException:
            pass  # Table already exists


def _cleanup_dynamodb_tables(client) -> None:
    """Clean up DynamoDB tables after testing."""
    try:
        # List and delete all tables
        response = client.list_tables()
        for table_name in response.get("TableNames", []):
            try:
                client.delete_table(TableName=table_name)
                waiter = client.get_waiter("table_not_exists")
                waiter.wait(TableName=table_name)
            except Exception as e:
                # Log error but continue with other tables
                logger.error(f"Warning: Failed to delete table {table_name}: {e}")
    except Exception as e:
        # Log error but don't fail the test
        print(f"Warning: Failed to cleanup DynamoDB tables: {e}")


# Step definition helpers
@pytest.fixture(scope="function")  # Also change this to function scope
def dos_search_context():
    """Context for storing test data during BDD scenarios."""
    return {}

@pytest.fixture(scope="session")
def project_root_folder_path() -> str:
    return str(Path(os.path.abspath(__file__)).parent.parent)

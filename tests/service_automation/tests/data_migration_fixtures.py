"""Pytest fixtures for data migration testing."""

import os
from typing import Any, Dict, Generator
from mypy_boto3_dynamodb import DynamoDBClient, DynamoDBServiceResource
import boto3
import pytest
from loguru import logger
from sqlalchemy import text
from sqlalchemy import create_engine
from testcontainers.localstack import LocalStackContainer
from testcontainers.postgres import PostgresContainer

from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from utilities.common.constants import (
    ENV_ENVIRONMENT,
    ENV_WORKSPACE,
)
from utilities.common.dynamoDB_tables import get_dynamodb_tables
from utilities.common.data_migration.migration_helper import MigrationHelper
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def boto3_session() -> Generator[boto3.Session, None, None]:
    """Boto3 session for testing."""
    session = boto3.Session()
    yield session


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


@pytest.fixture(scope="session")
def dynamodb_client(localstack_container: LocalStackContainer) -> DynamoDBClient:
    """Boto3 DynamoDB client for testing."""
    endpoint_url = localstack_container.get_url()
    client = boto3.client(
        "dynamodb",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )

    return client


@pytest.fixture(scope="session")
def dynamodb_resource(
    localstack_container: LocalStackContainer,
) -> DynamoDBServiceResource:
    """Boto3 DynamoDB resource for testing."""
    endpoint_url = localstack_container.get_url()
    resource = boto3.resource(
        "dynamodb",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )

    return resource


# def _get_source_db_config() -> Dict[str, str]:
#     """Get source database configuration from environment variables."""
#     return {
#         "host": os.getenv(ENV_SOURCE_DB_HOST),
#         "port": os.getenv(ENV_SOURCE_DB_PORT),
#         "database": os.getenv(ENV_SOURCE_DB_NAME),
#         "username": os.getenv(ENV_SOURCE_DB_USER),
#         "password": os.getenv(ENV_SOURCE_DB_PASSWORD),
#     }


# def _dump_schema_and_data(
#     source_config: Dict[str, str], schema_file: str, data_file: str
# ) -> None:
#     """Dump database schema and data for selected tables using pg_dump."""

#     # First dump the schema only
#     schema_cmd = [
#         "pg_dump",
#         f"--host={source_config['host']}",
#         f"--port={source_config['port']}",
#         f"--username={source_config['username']}",
#         f"--dbname={source_config['database']}",
#         "--schema-only",
#         "--no-privileges",
#         "--no-owner",
#         "--no-security-labels",
#         "--no-tablespaces",
#         "--schema=pathwaysdos",
#         # "-T pathwaysdos.z2*",
#         # "-T ",
#         f"--file={schema_file}",
#     ]

#     # Then dump data for specific tables only
#     table_args = []
#     for table in LEGACY_DOS_TABLES:
#         table_args.extend(["--table", f"pathwaysdos.{table}"])

#     data_cmd = [
#         "pg_dump",
#         f"--host={source_config['host']}",
#         f"--port={source_config['port']}",
#         f"--username={source_config['username']}",
#         f"--dbname={source_config['database']}",
#         "--data-only",
#         "--disable-triggers",
#         "--no-privileges",
#         "--no-owner",
#         "--no-security-labels",
#         "--no-tablespaces",
#         f"--file={data_file}",
#     ] + table_args

#     env = os.environ.copy()
#     env["PGPASSWORD"] = source_config["password"]

#     logger.info(f"Dumping schema to: {schema_file}")
#     schema_result = subprocess.run(schema_cmd, env=env, capture_output=True, text=True)

#     if schema_result.returncode != 0:
#         raise RuntimeError(f"Schema dump failed: {schema_result.stderr}")

#     logger.info(f"Dumping data for tables: {', '.join(LEGACY_DOS_TABLES)}")
#     data_result = subprocess.run(data_cmd, env=env, capture_output=True, text=True)

#     if data_result.returncode != 0:
#         raise RuntimeError(f"Data dump failed: {data_result.stderr}")

#     logger.info("Schema and data dump completed successfully")


# def _load_schema_and_data(
#     container_config: Dict[str, str], schema_file: str, data_file: str
# ) -> None:
#     """Load schema and data into the test container."""

#     # Load schema first
#     schema_cmd = [
#         "psql",
#         f"--host={container_config['host']}",
#         f"--port={container_config['port']}",
#         f"--username={container_config['username']}",
#         f"--dbname={container_config['database']}",
#         f"--file={schema_file}",
#     ]

#     # Then load data
#     data_cmd = [
#         "psql",
#         f"--host={container_config['host']}",
#         f"--port={container_config['port']}",
#         f"--username={container_config['username']}",
#         f"--dbname={container_config['database']}",
#         f"--file={data_file}",
#     ]

#     env = os.environ.copy()
#     env["PGPASSWORD"] = container_config["password"]

#     logger.info("Loading schema into test container")
#     schema_result = subprocess.run(schema_cmd, env=env, capture_output=True, text=True)

#     if schema_result.returncode != 0:
#         logger.warning(f"Schema load had warnings: {schema_result.stderr}")

#     logger.info("Loading data into test container")
#     data_result = subprocess.run(data_cmd, env=env, capture_output=True, text=True)

#     if data_result.returncode != 0:
#         logger.warning(f"Data load had warnings: {data_result.stderr}")

#     logger.info("Schema and data loaded successfully")

S3_DEV_MIGRATION_STORE_BUCKET = "ftrs-dos-dev-data-migration-pipeline-store"
S3_INTEGRATION_TEST_DATA_PATH = "test-data/integration-tests/"


# def _init_database(
#     postgres_container: PostgresContainer,
#     boto3_session: boto3.Session,
# ) -> None:
#     """
#     Initialize database with schema and metadata from source database.
#     """


# Get container connection details
# connection_string = postgres_container.get_connection_url()
# engine = create_engine(connection_string, echo=False)

# First, clean up any existing database to ensure we start fresh
# _cleanup_database(engine)

# Get source database configuration
# source_config = _get_source_db_config()

# Parse connection URL to get individual components for psql commands
# parsed = urlparse(connection_string)

# container_config = {
#     "host": parsed.hostname,
#     "port": str(parsed.port),
#     "database": parsed.path.lstrip("/"),
#     "username": parsed.username,
#     "password": parsed.password,
# }

# Create temporary files for schema and data dumps
# with (
#     tempfile.NamedTemporaryFile(
#         mode="w", suffix=".sql", delete=False
#     ) as schema_file,
#     tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as data_file,
# ):
#     schema_path = schema_file.name
#     data_path = data_file.name

# try:
#     # Dump schema and data from source
#     _dump_schema_and_data(source_config, schema_path, data_path)

#     # Load schema and data into test container
#     _load_schema_and_data(container_config, schema_path, data_path)

# finally:
#     # Clean up temporary files
#     try:
#         Path(schema_path).unlink(missing_ok=True)
#         Path(data_path).unlink(missing_ok=True)
#     except Exception as e:
#         logger.warning(f"Failed to clean up temporary files: {e}")


# def _cleanup_database(engine) -> None:
# """Clean up a database by dropping all tables and schema."""
# try:
#     with engine.connect() as conn:
#         result = conn.execute(
#             text(
#                 "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'pathwaysdos'"
#             )
#         )
#         schema_exists = result.fetchone() is not None

#         if schema_exists:
#             # Drop all tables in the schema
#             conn.execute(text("DROP SCHEMA IF EXISTS pathwaysdos CASCADE"))
#             conn.commit()
#             logger.info("Database schema 'pathwaysdos' dropped successfully")
#         else:
#             logger.info(
#                 "Database schema 'pathwaysdos' does not exist, no cleanup needed"
#             )

#         # Also check for any tables in public schema (just to be thorough)
#         result = conn.execute(
#             text(
#                 "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
#             )
#         )
#         tables = [row[0] for row in result]

#         if tables:
#             logger.info(f"Dropping {len(tables)} tables from 'public' schema")
#             for table in tables:
#                 conn.execute(
#                     text(f'DROP TABLE IF EXISTS "public"."{table}" CASCADE')
#                 )
#             conn.commit()
#             logger.debug(f"Dropped {len(tables)} tables from public schema")

# except Exception as e:
#     # Log error but don't fail the test
#     logger.error(f"Warning: Failed to cleanup database: {e}")


# def _seed_gp_organisations(session: Session) -> None:
#     """Seed the database with GP organisations for testing."""
#     for org in gp_service:
#         session.add(org)
#     session.commit()


def _create_dynamodb_tables(dynamodb_client: DynamoDBClient) -> None:
    """
    Create DynamoDB tables for testing using environment-based configuration.

    Tables follow pattern: {PROJECT_NAME}-{ENVIRONMENT}-database-{resource}-{WORKSPACE}

    Args:
        client: Boto3 DynamoDB client

    Raises:
        Exception: If table creation fails
    """
    table_configs = get_dynamodb_tables()
    logger.debug(f"Creating {len(table_configs)} DynamoDB tables")

    for config in table_configs:
        table_name = config["TableName"]
        try:
            dynamodb_client.create_table(**config)
            waiter = dynamodb_client.get_waiter("table_exists")
            waiter.wait(TableName=table_name)
            logger.debug(f"Created table: {table_name}")
        except dynamodb_client.exceptions.ResourceInUseException:
            logger.debug(f"Table {table_name} already exists")
        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            raise

    logger.debug("DynamoDB tables ready")


def _cleanup_dynamodb_tables(client: DynamoDBClient) -> None:
    """
    Clean up DynamoDB tables after testing.

    Args:
        client: Boto3 DynamoDB client
    """
    try:
        response = client.list_tables()
        table_names = response.get("TableNames", [])

        for table_name in table_names:
            try:
                client.delete_table(TableName=table_name)
                waiter = client.get_waiter("table_not_exists")
                waiter.wait(TableName=table_name)
                logger.debug(f"Deleted DynamoDB table: {table_name}")
            except Exception as e:
                logger.error(f"Failed to delete table {table_name}: {e}")
    except Exception as e:
        logger.error(f"DynamoDB cleanup failed: {e}")


def _get_s3_sql_file(boto3_session: boto3.Session, file_name: str) -> str:
    """
    Get the full path to a test SQL file stored in S3.

    Args:
        file_name: Name of the SQL file
    Returns:
        Full path to the SQL file
    """
    s3_client = boto3_session.client("s3")
    sql_obj = s3_client.get_object(
        Bucket=S3_DEV_MIGRATION_STORE_BUCKET,
        Key=f"{S3_INTEGRATION_TEST_DATA_PATH}{file_name}",
    )
    return sql_obj["Body"].read().decode("utf-8")


@pytest.fixture(scope="session")
def dos_sql_statements(boto3_session: boto3.Session) -> list[str]:
    schema = _get_s3_sql_file(boto3_session, "schema.sql")
    metadata = _get_s3_sql_file(boto3_session, "metadata.sql")
    clinical = _get_s3_sql_file(boto3_session, "clinical.sql")

    return [schema, metadata, clinical]


@pytest.fixture(name="dos_db", scope="function")
def fixture_dos_db(
    dos_sql_statements: list[str],
    postgres_container: PostgresContainer,
) -> Generator[Session, None, None]:
    """
    DoS database fixture for BDD tests with clean schema for each test.

    Args:
        postgres_container: PostgreSQL container fixture

    Yields:
        Database session with initialized schema
    """
    connection_string = postgres_container.get_connection_url()
    engine = create_engine(connection_string, echo=False)

    with Session(engine) as db_session:
        for sql_statement in dos_sql_statements:
            _execute_sql_statement(db_session, sql_statement)

        yield db_session
        _cleanup_pathwaysdos_schema(db_session)

    engine.dispose()


def _execute_sql_statement(
    db_session: Session,
    sql_statement: str,
) -> None:
    """
    Execute a SQL statement using the provided database session.

    Args:
        db_session: Database session
        sql_statement: SQL statement to execute
    """
    db_session.execute(text(sql_statement))
    db_session.commit()


def _cleanup_pathwaysdos_schema(db_session: Session) -> None:
    """
    Clean up the pathwaysdos schema after testing.
    """
    db_session.execute(text("DROP SCHEMA IF EXISTS pathwaysdos CASCADE"))
    db_session.commit()


@pytest.fixture(name="dynamodb", scope="function")
def fixture_dynamodb(
    localstack_container: LocalStackContainer,
) -> Generator[Dict[str, Any], None, None]:
    """
    DynamoDB fixture with pre-created tables for each test.

    Tables follow pattern: {PROJECT_NAME}-{ENVIRONMENT}-database-{resource}-{WORKSPACE}

    Args:
        localstack_container: LocalStack container fixture

    Yields:
        Dictionary with client, resource, and endpoint_url
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

    _create_dynamodb_tables(client)

    try:
        yield {"client": client, "resource": resource, "endpoint_url": endpoint_url}
    finally:
        _cleanup_dynamodb_tables(client)


@pytest.fixture(scope="function")
def model_repos_local(
    dynamodb,
) -> dict[str, AttributeLevelRepository[Organisation | Location | HealthcareService]]:
    def prep_local_repo(table_name, model_cls, dynamodb):
        model_repo = get_service_repository(model_cls, table_name)
        model_repo.resource = dynamodb[
            "resource"
        ]  # fake credentials aligned with localstack set in the injected dynamodb client
        model_repo.table = dynamodb["resource"].Table(table_name)
        return model_repo

    return {
        "organisation": prep_local_repo("organisation", Organisation, dynamodb),
        "location": prep_local_repo("location", Location, dynamodb),
        "healthcare-service": prep_local_repo(
            "healthcare-service", HealthcareService, dynamodb
        ),
    }


@pytest.fixture(scope="function")
def migration_helper(
    postgres_container: PostgresContainer,
    dynamodb: Dict[str, Any],
) -> MigrationHelper:
    """
    Migration helper configured for test environment.

    Args:
        postgres_container: PostgreSQL container fixture
        dynamodb: DynamoDB fixture with pre-created tables

    Returns:
        Configured MigrationHelper instance

    Raises:
        AssertionError: If required DynamoDB configuration is missing
    """
    db_uri = postgres_container.get_connection_url()

    if "endpoint_url" not in dynamodb:
        raise AssertionError(
            "DynamoDB fixture must provide endpoint_url. "
            "Ensure fixture_dynamodb is correctly configured."
        )

    dynamodb_endpoint = dynamodb["endpoint_url"]

    environment = os.getenv(ENV_ENVIRONMENT)
    workspace = os.getenv(ENV_WORKSPACE)

    logger.debug(
        f"Creating MigrationHelper with environment={environment}, workspace={workspace}"
    )

    return MigrationHelper(
        db_uri=db_uri,
        dynamodb_endpoint=dynamodb_endpoint,
        environment=environment,
        workspace=workspace,
    )


@pytest.fixture(scope="function")
def migration_context(dos_db: Session) -> Dict[str, Any]:
    """
    Context to store migration test data across BDD steps.

    Structure:
        service_id (int|None): ID of service being migrated (None = full sync)
        result (MigrationRunResult|None): Result from migration execution
        service_data (dict): Service attributes from Gherkin table
        service_name (str): Human-readable name for test service
        sqs_event (dict): SQS event data for event-based migrations
        sqs_service_ids (list[int]): Service IDs extracted from SQS event
        sqs_service_id (int|None): Primary service ID from SQS event
        mock_logger (MockLogger|None): MockLogger instance with captured logs
        db_session (Session): Active database session for DoS

    Args:
        dos_db: DoS database session fixture

    Returns:
        Dictionary context for storing test state
    """
    return {
        "service_id": None,  # None indicates full sync migration
        "result": None,
        "service_data": {},
        "service_name": "",
        "sqs_event": {},
        "sqs_service_ids": [],
        "sqs_service_id": None,
        "mock_logger": None,
        "db_session": dos_db,
        "state": None,
    }

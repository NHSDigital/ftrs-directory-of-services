"""Pytest fixtures for data migration testing."""
<<<<<<< HEAD
=======

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator
from urllib.parse import urlparse
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))

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
from utilities.data_migration.dos_db_utils import get_test_data_script

from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
<<<<<<< HEAD
from utilities.common.constants import (
    ENV_ENVIRONMENT,
    ENV_WORKSPACE,
    S3_DEV_MIGRATION_STORE_BUCKET,
    S3_INTEGRATION_TEST_DATA_PATH,
)
from utilities.common.dynamoDB_tables import get_dynamodb_tables
from utilities.common.data_migration.migration_helper import MigrationHelper
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def boto3_session() -> Generator[boto3.Session, None, None]:
    """Boto3 session for testing."""
    session = boto3.Session()
    yield session
=======
from utilities.common.constants import ENV_ENVIRONMENT, ENV_WORKSPACE
from utilities.common.dynamoDB_tables import get_dynamodb_tables
from utilities.data_migration.migration_helper import MigrationHelper
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))


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


<<<<<<< HEAD
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


def _create_dynamodb_tables(dynamodb_client: DynamoDBClient) -> None:
=======
def _create_dynamodb_tables(client: Any) -> None:
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))
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


<<<<<<< HEAD
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
=======
@pytest.fixture(scope="session")
def dos_db_setup_scripts() -> list[str]:
    schema_sql = get_test_data_script("schema.sql")
    metadata_sql = get_test_data_script("metadata.sql")
    clinical_sql = get_test_data_script("clinical.sql")
    return [schema_sql, metadata_sql, clinical_sql]
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))


@pytest.fixture(name="dos_db", scope="function")
def fixture_dos_db(
    dos_sql_statements: list[str],
    postgres_container: PostgresContainer,
<<<<<<< HEAD
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
=======
    dos_db_setup_scripts: list[str],
) -> Generator[Session, None, None]:
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))
    """
    Execute a SQL statement using the provided database session.

    Args:
        db_session: Database session
        sql_statement: SQL statement to execute
    """
    db_session.execute(text(sql_statement))
    db_session.commit()

<<<<<<< HEAD

def _cleanup_pathwaysdos_schema(db_session: Session) -> None:
    """
    Clean up the pathwaysdos schema after testing.
    """
    db_session.execute(text("DROP SCHEMA IF EXISTS pathwaysdos CASCADE"))
    db_session.commit()
=======
    try:
        logger.debug("Initializing database with migrated data")

        session = Session(engine)

        for script in dos_db_setup_scripts:
            if script.strip():
                session.exec(text(script))
        session.commit()

        yield session

        session.exec(text("DROP SCHEMA IF EXISTS pathwaysdos CASCADE"))
        session.commit()

    finally:
        if "session" in locals():
            session.close()

        engine.dispose()
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))


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
<<<<<<< HEAD
        db_session (Session): Active database session for DoS
=======
        migration_state (dict|None): State record from DynamoDB state table
        db_session (Session): Active database session
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))

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
<<<<<<< HEAD
        "db_session": dos_db,
        "state": None,
=======
        "migration_state": None,
        "db_session": dos_db,
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))
    }

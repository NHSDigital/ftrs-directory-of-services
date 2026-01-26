"""Pytest fixtures for data migration testing."""

import os
from typing import Any, Dict, Generator

import boto3
import pytest
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from loguru import logger
from sqlalchemy import Engine, text
from sqlmodel import Session, create_engine
from testcontainers.localstack import LocalStackContainer
from testcontainers.postgres import PostgresContainer
from utilities.common.constants import ENV_ENVIRONMENT, ENV_WORKSPACE
from utilities.common.dynamoDB_tables import get_dynamodb_tables
from utilities.data_migration.dos_db_utils import get_test_data_script
from utilities.data_migration.migration_helper import MigrationHelper


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


def _create_dynamodb_tables(client: Any) -> None:
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
            client.create_table(**config)
            waiter = client.get_waiter("table_exists")
            waiter.wait(TableName=table_name)
            logger.debug(f"Created table: {table_name}")
        except client.exceptions.ResourceInUseException:
            logger.debug(f"Table {table_name} already exists")
        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            raise

    logger.debug("DynamoDB tables ready")


def _cleanup_dynamodb_tables(client: Any) -> None:
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


@pytest.fixture(scope="session")
def dos_db_setup_scripts() -> list[str]:
    schema_sql = get_test_data_script("schema.sql")
    metadata_sql = get_test_data_script("metadata.sql")
    clinical_sql = get_test_data_script("clinical.sql")
    return [schema_sql, metadata_sql, clinical_sql]


@pytest.fixture(scope="session")
def dos_db_engine(postgres_container: PostgresContainer) -> create_engine:
    """
    DoS database engine with schema and initial data setup.

    Args:
        postgres_container: PostgreSQL container fixture

    Returns:
        SQLAlchemy engine connected to the DoS database
    """
    connection_string = postgres_container.get_connection_url()
    engine = create_engine(connection_string, echo=False)
    yield engine
    engine.dispose()


@pytest.fixture(name="dos_db")
def fixture_dos_db(
    dos_db_engine: Engine,
    dos_db_setup_scripts: list[str],
) -> Generator[Session, None, None]:
    """
    DoS database fixture with migrated data from source database.

    Args:
        postgres_container: PostgreSQL container fixture

    Yields:
        Database session with schema and data from source DB
    """

    try:
        logger.debug("Initializing database with migrated data")
        session = Session(dos_db_engine)

        for script in dos_db_setup_scripts:
            session.exec(text(script))
        session.commit()

        yield session

    finally:
        session.exec(text("DROP SCHEMA IF EXISTS pathwaysdos CASCADE"))
        session.commit()
        session.close()


@pytest.fixture(name="dynamodb")
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

    try:
        _create_dynamodb_tables(client)
        yield {"client": client, "resource": resource, "endpoint_url": endpoint_url}
    finally:
        _cleanup_dynamodb_tables(client)


@pytest.fixture
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


@pytest.fixture
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


@pytest.fixture
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
        migration_state (dict|None): State record from DynamoDB state table
        db_session (Session): Active database session

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
        "migration_state": None,
        "db_session": dos_db,
    }

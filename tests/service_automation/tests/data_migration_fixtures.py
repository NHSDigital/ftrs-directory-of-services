import pytest
import boto3
from typing import Generator, Any

from sqlalchemy import text, MetaData
from testcontainers.postgres import PostgresContainer
from testcontainers.localstack import LocalStackContainer
from sqlmodel import create_engine, SQLModel, Session
from ftrs_data_layer.domain import legacy


# Session-scoped containers (keep these as session-scoped for efficiency)
@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """PostgreSQL container for testing."""
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def localstack_container() -> Generator[LocalStackContainer, None, None]:
    """LocalStack container with DynamoDB for testing."""
    with LocalStackContainer(
        image="localstack/localstack:3.0"
    ) as localstack:
        yield localstack


def _init_database(engine):
    """Initialize database with schema and tables."""
    with engine.connect() as conn:
        # Create schema first
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS pathwaysdos"))
        conn.commit()

    # Create tables with the proper metadata that includes the schema
    # The legacy models have schema="pathwaysdos" in their metadata
    legacy.LegacyDoSModel.metadata.create_all(engine)


def _cleanup_database(engine):
    """Clean up database by dropping all tables and schema."""
    try:
        with engine.connect() as conn:
            # Drop all tables in the schema
            conn.execute(text("DROP SCHEMA IF EXISTS pathwaysdos CASCADE"))
            conn.commit()
    except Exception as e:
        # Log error but don't fail the test
        print(f"Warning: Failed to cleanup database: {e}")


# Change scope to "function" to create new DB connection for each test
@pytest.fixture(name="dos_db", scope="function")
def fixture_dos_db(postgres_container: PostgresContainer) -> Generator[Session, None, None]:
    """
    DoS database fixture for BDD tests.
    Creates a clean database session with all tables for each test.
    """
    connection_string = postgres_container.get_connection_url()
    engine = create_engine(connection_string, echo=False)

    try:
        # Initialize database with schema
        _init_database(engine)

        # Create a session
        session = Session(engine)
        _seed_gp_organisations(session)

        yield session

    finally:
        # Cleanup: close session and cleanup database
        if 'session' in locals():
            session.close()

        # Clean up the database
        _cleanup_database(engine)

        # Dispose of the engine to close all connections
        engine.dispose()


# Change scope to "function" to create new DynamoDB for each test
@pytest.fixture(name="dynamodb", scope="function")
def fixture_dynamodb(localstack_container: LocalStackContainer) -> Generator[dict, None, None]:
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
        region_name="eu-west-2"
    )

    resource = boto3.resource(
        "dynamodb",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2"
    )

    try:
        # Create tables
        _create_dynamodb_tables(client)

        yield {
            "client": client,
            "resource": resource,
            "endpoint_url": endpoint_url
        }

    finally:
        # Cleanup: Delete all tables
        _cleanup_dynamodb_tables(client)


def _seed_gp_organisations(session: Session) -> None:
    """Seed database with GP organisation test data."""
    gp_organisations = [
        legacy.Service(
            id=1,
            uid="service-1",  # Add required uid field
            name="Greenway Medical Centre",
            typeid=1,  # Add required typeid field
            openallhours=False,
            restricttoreferrals=False,
            postcode="SW1A 1AA",
            address="123 Medical Street",
            town="London",
            web="https://greenwaymedical.nhs.uk",
            email="enquiries@greenwaymedical.nhs.uk",
            publicphone="020 7946 0958",
        ),
        legacy.Service(
            id=2,
            uid="service-2",  # Add required uid field
            name="Riverside Health Centre",
            typeid=1,  # Add required typeid field
            openallhours=False,
            restricttoreferrals=False,
            postcode="M1 1AA",
            address="456 River Road",
            town="Manchester",
            web="https://riversidehealth.nhs.uk",
            email="reception@riversidehealth.nhs.uk",
            publicphone="0161 496 0123",
        ),
        legacy.Service(
            id=3,
            uid="service-3",  # Add required uid field
            name="Hillside Surgery",
            typeid=1,  # Add required typeid field
            openallhours=False,
            restricttoreferrals=False,
            postcode="B1 1AA",
            address="789 Hill Avenue",
            town="Birmingham",
            web="https://hillsidesurgery.nhs.uk",
            email="admin@hillsidesurgery.nhs.uk",
            publicphone="0121 496 0789",
        )
    ]

    for org in gp_organisations:
        session.add(org)

    session.commit()


def _create_dynamodb_tables(client) -> None:
    """Create DynamoDB tables for testing."""
    tables = [
        {
            "TableName": "organisation",
            "KeySchema": [
                {"AttributeName": "id", "KeyType": "HASH"}
            ],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"}
            ],
            "BillingMode": "PAY_PER_REQUEST"
        },
        {
            "TableName": "location",
            "KeySchema": [
                {"AttributeName": "id", "KeyType": "HASH"}
            ],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"}
            ],
            "BillingMode": "PAY_PER_REQUEST"
        },
        {
            "TableName": "healthcare-service",
            "KeySchema": [
                {"AttributeName": "id", "KeyType": "HASH"}
            ],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"}
            ],
            "BillingMode": "PAY_PER_REQUEST"
        }
    ]

    for table_config in tables:
        try:
            client.create_table(**table_config)
            waiter = client.get_waiter('table_exists')
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
                waiter = client.get_waiter('table_not_exists')
                waiter.wait(TableName=table_name)
            except Exception as e:
                # Log error but continue with other tables
                print(f"Warning: Failed to delete table {table_name}: {e}")
    except Exception as e:
        # Log error but don't fail the test
        print(f"Warning: Failed to cleanup DynamoDB tables: {e}")


# Step definition helpers
@pytest.fixture(scope="function")  # Also change this to function scope
def gp_search_context():
    """Context for storing test data during BDD scenarios."""
    return {}

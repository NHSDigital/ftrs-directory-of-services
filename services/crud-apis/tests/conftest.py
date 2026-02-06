"""Pytest configuration for CRUD APIs integration tests.

This module provides fixtures for running integration tests against
real DynamoDB tables using LocalStack testcontainers.

Usage:
    Run all tests (unit + integration):
        pytest

    Run only unit tests (no Docker required):
        pytest -m "not integration"

    Run only integration tests:
        pytest -m integration
"""

import os
from typing import Any, Generator

import pytest

# Set environment variables before importing fixtures
os.environ.setdefault("PROJECT_NAME", "ftrs-dos")
os.environ.setdefault("ENVIRONMENT", "local")
os.environ.setdefault("WORKSPACE", "test")
os.environ.setdefault("ENDPOINT_URL", "http://localhost:4566")
os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-2")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")

# Import shared fixtures from ftrs_common.testing
from ftrs_common.testing.dynamodb_fixtures import (
    create_dynamodb_tables,
    dynamodb_client,
    dynamodb_resource,
    localstack_container,
    make_local_repository,
    truncate_dynamodb_table,
)
from ftrs_common.testing.table_config import (
    get_dynamodb_table_configs,
    get_table_name,
)

# Re-export session-scoped fixtures for pytest discovery
localstack_container = localstack_container
dynamodb_client = dynamodb_client
dynamodb_resource = dynamodb_resource


@pytest.fixture(scope="session")
def dynamodb_tables_for_crud(
    dynamodb_client: Any,
    dynamodb_resource: Any,
    localstack_container: Any,
) -> Generator[dict[str, Any], None, None]:
    """
    Session-scoped DynamoDB tables for CRUD API integration tests.

    Creates only the core entity tables (org, location, healthcare-service)
    since CRUD APIs don't need triage-code or data-migration-state tables.

    Yields:
        Dictionary with client, resource, endpoint_url, and table configuration
    """
    # Only create core tables for CRUD APIs
    table_configs = get_dynamodb_table_configs(
        include_core=True,
        include_triage_code=False,
        include_data_migration_state=False,
        project_name=os.getenv("PROJECT_NAME"),
        environment=os.getenv("ENVIRONMENT"),
        workspace=os.getenv("WORKSPACE"),
    )

    table_names = create_dynamodb_tables(dynamodb_client, table_configs)
    endpoint_url = localstack_container.get_url()

    yield {
        "client": dynamodb_client,
        "resource": dynamodb_resource,
        "endpoint_url": endpoint_url,
        "table_names": table_names,
        "table_configs": table_configs,
    }


@pytest.fixture
def clean_tables(
    dynamodb_tables_for_crud: dict[str, Any],
) -> Generator[dict[str, Any], None, None]:
    """
    Fixture that truncates all tables before each test.

    Use this when tests need a clean slate.

    Yields:
        The dynamodb_tables_for_crud dict
    """
    client = dynamodb_tables_for_crud["client"]
    resource = dynamodb_tables_for_crud["resource"]

    # Truncate all tables before the test
    for table_name in dynamodb_tables_for_crud["table_names"]:
        truncate_dynamodb_table(client, resource, table_name)

    yield dynamodb_tables_for_crud


@pytest.fixture
def organisation_repository(
    dynamodb_tables_for_crud: dict[str, Any],
) -> Any:
    """
    Organisation repository connected to LocalStack DynamoDB.

    Returns:
        AttributeLevelRepository[Organisation] instance
    """
    from ftrs_data_layer.domain import Organisation

    table_name = get_table_name(
        "organisation",
        project_name=os.getenv("PROJECT_NAME"),
        environment=os.getenv("ENVIRONMENT"),
        workspace=os.getenv("WORKSPACE"),
    )

    return make_local_repository(
        table_name=table_name,
        model_cls=Organisation,
        dynamodb_resource=dynamodb_tables_for_crud["resource"],
        endpoint_url=dynamodb_tables_for_crud["endpoint_url"],
    )


@pytest.fixture
def location_repository(
    dynamodb_tables_for_crud: dict[str, Any],
) -> Any:
    """
    Location repository connected to LocalStack DynamoDB.

    Returns:
        AttributeLevelRepository[Location] instance
    """
    from ftrs_data_layer.domain import Location

    table_name = get_table_name(
        "location",
        project_name=os.getenv("PROJECT_NAME"),
        environment=os.getenv("ENVIRONMENT"),
        workspace=os.getenv("WORKSPACE"),
    )

    return make_local_repository(
        table_name=table_name,
        model_cls=Location,
        dynamodb_resource=dynamodb_tables_for_crud["resource"],
        endpoint_url=dynamodb_tables_for_crud["endpoint_url"],
    )


@pytest.fixture
def healthcare_service_repository(
    dynamodb_tables_for_crud: dict[str, Any],
) -> Any:
    """
    HealthcareService repository connected to LocalStack DynamoDB.

    Returns:
        AttributeLevelRepository[HealthcareService] instance
    """
    from ftrs_data_layer.domain import HealthcareService

    table_name = get_table_name(
        "healthcare-service",
        project_name=os.getenv("PROJECT_NAME"),
        environment=os.getenv("ENVIRONMENT"),
        workspace=os.getenv("WORKSPACE"),
    )

    return make_local_repository(
        table_name=table_name,
        model_cls=HealthcareService,
        dynamodb_resource=dynamodb_tables_for_crud["resource"],
        endpoint_url=dynamodb_tables_for_crud["endpoint_url"],
    )

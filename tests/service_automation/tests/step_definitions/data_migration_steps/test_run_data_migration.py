"""BDD step definitions for running single service migration."""
import os
from typing import Any, Dict

import pytest
from loguru import logger
from pytest_bdd import given, parsers, scenarios, then, when
from sqlalchemy import text
from sqlmodel import Session

from utilities.common.db_helper import delete_service_if_exists, verify_service_exists
from utilities.common.gherkin_helper import parse_gherkin_table
from utilities.common.migration_helper import MigrationHelper

scenarios("../../tests/features/data_migration_features/run_data_migration.feature")


@given("the test environment is configured")
def test_environment_configured(
    migration_helper: MigrationHelper, dynamodb: Dict[str, Any]
) -> None:
    """
    Verify test environment is properly configured.

    Args:
        migration_helper: Helper for running migrations
        dynamodb: DynamoDB test fixture with client and endpoint

    Raises:
        AssertionError: If environment is not properly configured
        pytest.fail: If DynamoDB is not accessible
    """
    logger.info(
        "Testing environment configuration",
        extra={
            "dynamodb_endpoint": dynamodb.get("endpoint_url"),
            "environment": os.getenv("ENVIRONMENT", "not set"),
            "workspace": os.getenv("WORKSPACE", "not set"),
        },
    )

    try:
        response = dynamodb["client"].list_tables()
        table_names = response.get("TableNames", [])
        logger.info(f"Found {len(table_names)} DynamoDB tables")
        assert "TableNames" in response, "DynamoDB should be accessible"
    except Exception as e:
        pytest.fail(f"Failed to access DynamoDB: {e}")

    assert migration_helper is not None, "Migration helper should be configured"
    assert migration_helper.db_uri is not None, "Database URI should be set"
    assert (
        migration_helper.dynamodb_endpoint is not None
    ), "DynamoDB endpoint should be set"

    logger.info("Environment configuration verified")


@given("the DoS database has test data")
def dos_database_has_test_data(dos_db_with_migration: Session) -> None:
    """
    Verify DoS database is accessible and has tables.

    Args:
        dos_db_with_migration: Database session with migrated schema

    Raises:
        AssertionError: If database is not accessible or tables don't exist
    """
    result = dos_db_with_migration.exec(
        text("SELECT COUNT(*) FROM pathwaysdos.services")
    )
    count = result.fetchone()[0]
    assert count >= 0, "Should be able to query services table"
    logger.info(f"DoS database ready with {count} services")


@given("DynamoDB tables are ready")
def dynamodb_tables_ready(dynamodb: Dict[str, Any]) -> None:
    """
    Verify DynamoDB tables exist and are accessible.

    Args:
        dynamodb: DynamoDB test fixture with client

    Raises:
        AssertionError: If required tables don't exist
        pytest.fail: If tables are missing
    """
    client = dynamodb["client"]
    response = client.list_tables()
    table_names = response.get("TableNames", [])

    logger.debug(f"Found {len(table_names)} tables in DynamoDB")

    project_name = os.getenv("PROJECT_NAME", "ftrs-dos")
    environment = os.getenv("ENVIRONMENT", "dev")
    workspace = os.getenv("WORKSPACE", "test")

    expected_resources = ["organisation", "location", "healthcare-service"]
    expected_tables = [
        f"{project_name}-{environment}-database-{resource}-{workspace}"
        for resource in expected_resources
    ]

    missing_tables = [table for table in expected_tables if table not in table_names]

    if missing_tables:
        pytest.fail(
            f"Missing required DynamoDB tables: {', '.join(missing_tables)}\n"
            f"Found tables: {', '.join(table_names)}\n"
            f"Expected pattern: {project_name}-{environment}-database-{{resource}}-{workspace}"
        )

    logger.info("All required DynamoDB tables are ready")


@given(
    parsers.parse(
        "a '{entity_type}' exists called '{entity_name}' in DoS with attributes:"
    ),
    target_fixture="service_created",
)
def create_service_with_attributes(
    dos_db_with_migration: Session,
    migration_context: Dict[str, Any],
    entity_type: str,
    entity_name: str,
    datatable: list[list[str]],
) -> Dict[str, Any]:
    """
    Create a service in DoS database with attributes from Gherkin table.

    Args:
        dos_db_with_migration: Database session with migrated schema
        migration_context: Test context for storing state across steps
        entity_type: Type of entity being created (e.g., 'Service')
        entity_name: Human-readable name for the test entity
        datatable: Gherkin table data as list of lists [[key, value], ...]

    Returns:
        Dictionary of parsed service attributes

    Raises:
        AssertionError: If required fields are missing
        pytest.fail: If database operation fails
    """
    attributes = parse_gherkin_table(datatable)

    required_fields = ["id", "typeid", "statusid"]
    missing = [f for f in required_fields if f not in attributes]
    if missing:
        pytest.fail(f"Missing required fields: {', '.join(missing)}")

    service_id = attributes["id"]
    migration_context["service_data"] = attributes
    migration_context["service_name"] = entity_name
    migration_context["service_id"] = service_id

    try:
        delete_service_if_exists(dos_db_with_migration, service_id)

        columns = list(attributes.keys())
        placeholders = [f":{col}" for col in columns]

        insert_sql = text(
            f"""
            INSERT INTO pathwaysdos.services ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            """
        )

        dos_db_with_migration.exec(insert_sql.bindparams(**attributes))
        dos_db_with_migration.commit()

        result = verify_service_exists(dos_db_with_migration, service_id)

        if not result:
            pytest.fail(f"Failed to verify inserted service with ID {service_id}")

        logger.info(
            "Created test service",
            extra={"service_id": service_id, "type_id": result[1]},
        )

    except Exception as e:
        dos_db_with_migration.rollback()
        pytest.fail(f"Database operation failed: {e}")

    return attributes


@when(parsers.parse("a single service migration is run for ID '{service_id:d}'"))
def run_single_service_migration(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
    service_id: int,
) -> None:
    """
    Execute migration for a single service.

    Args:
        migration_helper: Helper for running migrations
        migration_context: Test context dictionary
        service_id: Service ID to migrate
    """
    result = migration_helper.run_single_service_migration(service_id)
    migration_context["result"] = result
    migration_context["service_id"] = service_id


@when("a full service migration is run")
def run_full_service_migration(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
) -> None:
    """
    Execute full service migration.

    Args:
        migration_helper: Helper for running migrations
        migration_context: Test context dictionary
    """
    result = migration_helper.run_full_service_migration()
    migration_context["result"] = result


@then("the migration process should complete successfully")
def verify_migration_success(migration_context: Dict[str, Any]) -> None:
    """
    Verify the migration completed successfully.

    Args:
        migration_context: Test context dictionary

    Raises:
        AssertionError: If migration failed
    """
    result = migration_context["result"]

    assert result is not None, "Migration result should exist"
    assert result.success, f"Migration should succeed. Error: {result.error}"


@then(
    parsers.parse(
        "the metrics should be "
        "{total:d} total, "
        "{supported:d} supported, "
        "{unsupported:d} unsupported, "
        "{transformed:d} transformed, "
        "{migrated:d} migrated, "
        "{skipped:d} skipped and "
        "{errors:d} errors"
    )
)
def verify_migration_metrics_inline(
    migration_context: Dict[str, Any],
    total: int,
    supported: int,
    unsupported: int,
    transformed: int,
    migrated: int,
    skipped: int,
    errors: int,
) -> None:
    """
    Verify migration metrics match expected values.

    Args:
        migration_context: Test context dictionary
        total: Expected total_records count
        supported: Expected supported_records count
        unsupported: Expected unsupported_records count
        transformed: Expected transformed_records count
        migrated: Expected migrated_records count
        skipped: Expected skipped_records count
        errors: Expected errors count

    Raises:
        AssertionError: If any metric doesn't match expected value
    """
    result = migration_context["result"]

    assert result is not None, "Migration result should exist"
    assert result.metrics is not None, "Migration metrics should exist"

    metrics = result.metrics
    service_id = migration_context.get("service_id")
    service_data = migration_context.get("service_data", {})

    assert metrics.total_records == total, (
        f"Total records mismatch for service {service_id}: "
        f"expected {total}, got {metrics.total_records}"
    )

    assert metrics.supported_records == supported, (
        f"Supported records mismatch for service {service_id}:\n"
        f"  Expected: {supported}\n"
        f"  Got: {metrics.supported_records}\n"
        f"  Type ID: {service_data.get('typeid')}\n"
        f"  ODS Code: {service_data.get('odscode')}\n"
        f"  Status: {service_data.get('statusid')}"
    )

    assert metrics.unsupported_records == unsupported, (
        f"Unsupported records mismatch: expected {unsupported}, "
        f"got {metrics.unsupported_records}"
    )

    assert metrics.transformed_records == transformed, (
        f"Transformed records mismatch: expected {transformed}, "
        f"got {metrics.transformed_records}"
    )

    assert metrics.migrated_records == migrated, (
        f"Migrated records mismatch: expected {migrated}, "
        f"got {metrics.migrated_records}"
    )

    assert metrics.skipped_records == skipped, (
        f"Skipped records mismatch: expected {skipped}, "
        f"got {metrics.skipped_records}"
    )

    assert metrics.errors == errors, (
        f"Errors mismatch: expected {errors}, got {metrics.errors}"
    )

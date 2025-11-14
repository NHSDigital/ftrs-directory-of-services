"""Shared step definitions for data migration BDD tests."""
import json
import os
from typing import Any, Dict, List

import pytest
from loguru import logger
from sqlalchemy import text
from sqlmodel import Session

from utilities.common.db_helper import delete_service_if_exists, verify_service_exists
from utilities.common.gherkin_helper import parse_gherkin_table
from utilities.common.log_helper import (
    get_mock_logger_from_context,
    verify_service_not_migrated_log,
    verify_service_skipped_log,
    verify_transformation_log,
    verify_transformer_selected_log,
)
from utilities.common.migration_helper import MigrationHelper

# ============================================================
# Type Aliases
# ============================================================

ServiceAttributes = Dict[str, Any]
MigrationContext = Dict[str, Any]
DynamoDBFixture = Dict[str, Any]
GherkinTable = List[List[str]]
SQSEvent = Dict[str, Any]

# ============================================================
# Constants
# ============================================================

# DynamoDB fixture keys
DYNAMODB_CLIENT = "client"
DYNAMODB_RESOURCE = "resource"
DYNAMODB_ENDPOINT = "endpoint_url"

# Environment variable keys
ENV_PROJECT_NAME = "PROJECT_NAME"
ENV_ENVIRONMENT = "ENVIRONMENT"
ENV_WORKSPACE = "WORKSPACE"

# Default values
DEFAULT_PROJECT_NAME = "ftrs-dos"
DEFAULT_ENVIRONMENT = "dev"
DEFAULT_WORKSPACE = "test"

# Database constants
PATHWAYSDOS_SCHEMA = "pathwaysdos"
SERVICES_TABLE = f"{PATHWAYSDOS_SCHEMA}.services"

# Required service fields
REQUIRED_SERVICE_FIELDS = ["id", "typeid", "statusid"]

# Expected DynamoDB resource types
EXPECTED_DYNAMODB_RESOURCES = ["organisation", "location", "healthcare-service"]


# ============================================================
# Helper Functions
# ============================================================


def _get_expected_dynamodb_table_names() -> List[str]:
    """
    Get expected DynamoDB table names based on environment configuration.

    Returns:
        List of expected table names following pattern:
        {PROJECT_NAME}-{ENVIRONMENT}-database-{resource}-{WORKSPACE}
    """
    project_name = os.getenv(ENV_PROJECT_NAME, DEFAULT_PROJECT_NAME)
    environment = os.getenv(ENV_ENVIRONMENT, DEFAULT_ENVIRONMENT)
    workspace = os.getenv(ENV_WORKSPACE, DEFAULT_WORKSPACE)

    return [
        f"{project_name}-{environment}-database-{resource}-{workspace}"
        for resource in EXPECTED_DYNAMODB_RESOURCES
    ]


def _get_migration_type_description(migration_context: MigrationContext) -> str:
    """
    Get human-readable description of migration type from context.

    Args:
        migration_context: Test context dictionary

    Returns:
        Description string (e.g., "full sync", "service 300000", "SQS event for service 12345")
    """
    service_id = migration_context.get("service_id")
    sqs_service_id = migration_context.get("sqs_service_id")
    sqs_event = migration_context.get("sqs_event", {})

    if sqs_event:
        is_empty_event = len(sqs_event) == 0
        record_count = len(sqs_event.get("Records", []))

        if is_empty_event:
            return "empty event"
        elif sqs_service_id:
            return f"SQS event for service {sqs_service_id}"
        else:
            return f"SQS event with {record_count} record(s)"
    elif service_id is None:
        return "full sync"
    else:
        return f"service {service_id}"


def _parse_sqs_event(docstring: str) -> SQSEvent:
    """
    Parse SQS event JSON from Gherkin docstring.

    Args:
        docstring: JSON string from Gherkin step

    Returns:
        Parsed event dictionary

    Raises:
        pytest.fail: If JSON is invalid
    """
    try:
        return json.loads(docstring)
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON in event docstring: {e}")


def _extract_service_ids_from_sqs_event(event: SQSEvent) -> List[int]:
    """
    Extract service IDs from SQS event records.

    Args:
        event: SQS event dictionary

    Returns:
        List of service IDs found in event records
    """
    service_ids = []

    if event.get("Records"):
        for record in event["Records"]:
            body = record.get("body", "{}")
            try:
                body_json = json.loads(body)
                if "record_id" in body_json:
                    service_ids.append(body_json["record_id"])
            except json.JSONDecodeError:
                logger.warning(f"Could not parse record body: {body}")

    return service_ids


def _validate_service_attributes(attributes: ServiceAttributes) -> None:
    """
    Validate that service attributes contain all required fields.

    Args:
        attributes: Service attributes dictionary

    Raises:
        pytest.fail: If required fields are missing
    """
    missing = [f for f in REQUIRED_SERVICE_FIELDS if f not in attributes]
    if missing:
        pytest.fail(f"Missing required fields: {', '.join(missing)}")


def _assert_metric_matches(
    actual: int,
    expected: int,
    metric_name: str,
    migration_type: str,
    additional_context: str = "",
) -> None:
    """
    Assert that a metric value matches expected value.

    Args:
        actual: Actual metric value
        expected: Expected metric value
        metric_name: Name of the metric being checked
        migration_type: Description of migration type
        additional_context: Optional additional context for error message

    Raises:
        AssertionError: If values don't match
    """
    error_parts = [
        f"{metric_name.capitalize()} mismatch for {migration_type}:",
        f"  Expected: {expected}",
        f"  Got: {actual}",
    ]

    if additional_context:
        error_parts.append(f"  {additional_context}")

    assert actual == expected, "\n".join(error_parts)


# ============================================================
# Background Setup Steps
# ============================================================


def run_test_environment_configured(
    migration_helper: MigrationHelper, dynamodb: DynamoDBFixture
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
    try:
        response = dynamodb[DYNAMODB_CLIENT].list_tables()
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


def run_dos_database_has_test_data(dos_db_with_migration: Session) -> None:
    """
    Verify DoS database is accessible and has tables.

    Args:
        dos_db_with_migration: Database session with migrated schema

    Raises:
        AssertionError: If database is not accessible or tables don't exist
    """
    result = dos_db_with_migration.exec(text(f"SELECT COUNT(*) FROM {SERVICES_TABLE}"))
    count = result.fetchone()[0]
    assert count >= 0, "Should be able to query services table"
    logger.info(f"DoS database ready with {count} services")


def run_dynamodb_tables_ready(dynamodb: DynamoDBFixture) -> None:
    """
    Verify DynamoDB tables exist and are accessible.

    Args:
        dynamodb: DynamoDB test fixture with client

    Raises:
        AssertionError: If required tables don't exist
        pytest.fail: If tables are missing
    """
    client = dynamodb[DYNAMODB_CLIENT]
    response = client.list_tables()
    table_names = response.get("TableNames", [])

    logger.debug(f"Found {len(table_names)} tables in DynamoDB")

    expected_tables = _get_expected_dynamodb_table_names()
    missing_tables = [table for table in expected_tables if table not in table_names]

    if missing_tables:
        project_name = os.getenv(ENV_PROJECT_NAME, DEFAULT_PROJECT_NAME)
        environment = os.getenv(ENV_ENVIRONMENT, DEFAULT_ENVIRONMENT)
        workspace = os.getenv(ENV_WORKSPACE, DEFAULT_WORKSPACE)

        pytest.fail(
            f"Missing required DynamoDB tables: {', '.join(missing_tables)}\n"
            f"Found tables: {', '.join(table_names)}\n"
            f"Expected pattern: {project_name}-{environment}-database-{{resource}}-{workspace}"
        )

    logger.info("All required DynamoDB tables are ready")


# ============================================================
# Common Steps
# ============================================================


def run_create_service_with_attributes(
    dos_db_with_migration: Session,
    migration_context: MigrationContext,
    entity_type: str,
    entity_name: str,
    datatable: GherkinTable,
) -> ServiceAttributes:
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
    _validate_service_attributes(attributes)

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
            INSERT INTO {SERVICES_TABLE} ({', '.join(columns)})
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


def run_full_service_migration(
    migration_helper: MigrationHelper,
    migration_context: MigrationContext,
) -> None:
    """
    Execute full service migration and capture output.

    Args:
        migration_helper: Helper for running migrations
        migration_context: Test context dictionary
    """
    result = migration_helper.run_full_service_migration()

    migration_context["result"] = result
    migration_context["mock_logger"] = result.mock_logger

    logger.info(
        "Full service migration completed",
        extra={
            "success": result.success,
            "total_records": result.metrics.total_records if result.metrics else 0,
        },
    )


def run_single_service_migration(
    migration_helper: MigrationHelper,
    migration_context: MigrationContext,
    service_id: int,
) -> None:
    """
    Execute migration for a single service and capture output.

    Args:
        migration_helper: Helper for running migrations
        migration_context: Test context dictionary
        service_id: Service ID to migrate
    """
    result = migration_helper.run_single_service_migration(service_id)

    migration_context["result"] = result
    migration_context["mock_logger"] = result.mock_logger
    migration_context["service_id"] = service_id


def run_verify_migration_metrics_inline(
    migration_context: MigrationContext,
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
    migration_type = _get_migration_type_description(migration_context)

    # Build additional context for supported records assertion
    if service_id is None:
        # Full sync migration
        supported_context = "(All existing services in database)"
    else:
        # Single service migration
        supported_context = (
            f"Type ID: {service_data.get('typeid')}, "
            f"ODS Code: {service_data.get('odscode')}, "
            f"Status: {service_data.get('statusid')}"
        )

    # Verify all metrics
    _assert_metric_matches(
        metrics.total_records, total, "total records", migration_type
    )
    _assert_metric_matches(
        metrics.supported_records,
        supported,
        "supported records",
        migration_type,
        supported_context,
    )
    _assert_metric_matches(
        metrics.unsupported_records, unsupported, "unsupported records", migration_type
    )
    _assert_metric_matches(
        metrics.transformed_records, transformed, "transformed records", migration_type
    )
    _assert_metric_matches(
        metrics.migrated_records, migrated, "migrated records", migration_type
    )
    _assert_metric_matches(
        metrics.skipped_records, skipped, "skipped records", migration_type
    )
    _assert_metric_matches(metrics.errors, errors, "errors", migration_type)

    logger.info(
        f"Verified metrics for {migration_type}",
        extra={
            "total": total,
            "supported": supported,
            "unsupported": unsupported,
            "transformed": transformed,
            "migrated": migrated,
            "skipped": skipped,
            "errors": errors,
            "is_full_sync": service_id is None,
        },
    )


def run_verify_transformation_output(
    migration_context: MigrationContext,
    service_id: int,
    org_count: int,
    location_count: int,
    service_count: int,
) -> None:
    """
    Verify that a service was transformed into the expected number of resources.

    Validates DM_ETL_007 log reference from DataMigrationLogBase.

    Args:
        migration_context: Test context dictionary with mock_logger
        service_id: Service ID that was transformed
        org_count: Expected number of organisations created
        location_count: Expected number of locations created
        service_count: Expected number of healthcare services created

    Raises:
        AssertionError: If transformation log not found or counts don't match
    """
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_transformation_log(
        mock_logger=mock_logger,
        service_id=service_id,
        organisation_count=org_count,
        location_count=location_count,
        healthcare_service_count=service_count,
    )

    logger.info(
        f"Verified transformation output for service {service_id}",
        extra={
            "organisation_count": org_count,
            "location_count": location_count,
            "healthcare_service_count": service_count,
        },
    )


def run_verify_service_not_migrated(
    migration_context: MigrationContext,
    service_id: int,
    expected_reason: str,
) -> None:
    """
    Verify that a service was not migrated with the expected reason.

    Validates DM_ETL_004 log reference from DataMigrationLogBase.

    Args:
        migration_context: Test context dictionary with mock_logger
        service_id: Service ID that was not migrated
        expected_reason: Expected reason for not migrating

    Raises:
        AssertionError: If migration failure log not found or wrong reason
    """
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_service_not_migrated_log(
        mock_logger=mock_logger,
        service_id=service_id,
        expected_reason=expected_reason,
    )

    logger.info(
        f"Verified service {service_id} was not migrated",
        extra={"reason": expected_reason},
    )


def run_verify_service_skipped(
    migration_context: MigrationContext,
    service_id: int,
    expected_reason: str,
) -> None:
    """
    Verify that a service was skipped with the expected reason.

    Validates DM_ETL_005 log reference from DataMigrationLogBase.

    Args:
        migration_context: Test context dictionary with mock_logger
        service_id: Service ID that was skipped
        expected_reason: Expected reason for skipping

    Raises:
        AssertionError: If service skip log not found or wrong reason
    """
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_service_skipped_log(
        mock_logger=mock_logger,
        service_id=service_id,
        expected_reason=expected_reason,
    )

    logger.info(
        f"Verified service {service_id} was skipped",
        extra={"reason": expected_reason},
    )

def run_verify_transformer_selected(
    migration_context: MigrationContext,
    transformer_name: str,
    service_id: int,
) -> None:
    """
    Verify the correct transformer was selected for the service.

    Validates DM_ETL_003 log reference from DataMigrationLogBase.

    Args:
        migration_context: Test context dictionary with mock_logger
        transformer_name: Expected transformer name (e.g., 'GPPracticeTransformer')
        service_id: Service ID that was migrated

    Raises:
        AssertionError: If transformer selection log not found or wrong transformer
    """
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_transformer_selected_log(
        mock_logger=mock_logger,
        transformer_name=transformer_name,
        service_id=service_id,
    )

    logger.info(
        f"Verified transformer selection for service {service_id}",
        extra={"transformer_name": transformer_name},
    )

# ============================================================
# Common SQS Steps
# ============================================================


def run_sqs_event_migration(
    migration_helper: MigrationHelper,
    migration_context: MigrationContext,
    docstring: str,
) -> Dict[str, Any]:
    """
    Execute migration with SQS event and capture output.

    Args:
        migration_helper: Helper for running migrations
        migration_context: Test context dictionary
        docstring: JSON event string from Gherkin docstring

    Returns:
        Dictionary containing event processing result

    Raises:
        pytest.fail: If event JSON is invalid
    """
    event = _parse_sqs_event(docstring)
    service_ids = _extract_service_ids_from_sqs_event(event)

    logger.debug(
        "Processing SQS event",
        extra={
            "record_count": len(event.get("Records", [])),
            "is_empty": len(event) == 0,
            "service_ids": service_ids,
        },
    )

    result = migration_helper.run_sqs_event_migration(event)

    migration_context["result"] = result
    migration_context["mock_logger"] = result.mock_logger
    migration_context["sqs_event"] = event
    migration_context["sqs_service_ids"] = service_ids
    migration_context["sqs_service_id"] = service_ids[0] if service_ids else None

    logger.info(
        "SQS event migration completed",
        extra={
            "success": result.success,
            "migrated_records": (
                result.metrics.migrated_records if result.metrics else 0
            ),
            "is_empty_event": len(event) == 0,
            "service_ids": service_ids,
        },
    )

    return {"event": event, "result": result}


def run_verify_sqs_event_metrics(
    migration_context: MigrationContext,
    total: int,
    supported: int,
    unsupported: int,
    transformed: int,
    migrated: int,
    skipped: int,
    errors: int,
) -> None:
    """
    Verify SQS event migration metrics match expected values.

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
    result = migration_context.get("result")
    logger.info("Verifying SQS results", extra={"result": result})

    assert result is not None, "Migration result should exist"
    assert result.metrics is not None, "Migration metrics should exist"

    metrics = result.metrics
    migration_type = _get_migration_type_description(migration_context)

    # Verify all metrics using helper function
    _assert_metric_matches(
        metrics.total_records, total, "total records", migration_type
    )
    _assert_metric_matches(
        metrics.supported_records, supported, "supported records", migration_type
    )
    _assert_metric_matches(
        metrics.unsupported_records, unsupported, "unsupported records", migration_type
    )
    _assert_metric_matches(
        metrics.transformed_records, transformed, "transformed records", migration_type
    )
    _assert_metric_matches(
        metrics.migrated_records, migrated, "migrated records", migration_type
    )
    _assert_metric_matches(
        metrics.skipped_records, skipped, "skipped records", migration_type
    )
    _assert_metric_matches(metrics.errors, errors, "errors", migration_type)

    sqs_event = migration_context.get("sqs_event", {})
    service_id = migration_context.get("sqs_service_id")

    logger.info(
        f"Verified SQS event metrics for {migration_type}",
        extra={
            "total": total,
            "supported": supported,
            "unsupported": unsupported,
            "transformed": transformed,
            "migrated": migrated,
            "skipped": skipped,
            "errors": errors,
            "is_empty_event": len(sqs_event) == 0,
            "service_id": service_id,
        },
    )

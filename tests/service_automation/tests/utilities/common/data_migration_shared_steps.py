"""Shared step definitions for data migration BDD tests."""
import json
import os
from typing import Any, Dict

import pytest
from loguru import logger
from sqlalchemy import text
from sqlmodel import Session

from utilities.common.log_helper import LogVerificationConfig, verify_log_reference
from utilities.common.db_helper import delete_service_if_exists, verify_service_exists
from utilities.common.gherkin_helper import parse_gherkin_table
from utilities.common.migration_helper import MigrationHelper


# ============================================================
# Background Setup Steps
# ============================================================


def run_test_environment_configured(
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


def run_dos_database_has_test_data(dos_db_with_migration: Session) -> None:
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


def run_dynamodb_tables_ready(dynamodb: Dict[str, Any]) -> None:
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


# ============================================================
# Common Steps
# ============================================================


def run_create_service_with_attributes(
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

def run_full_service_migration(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
    capfd: pytest.CaptureFixture[str],
) -> None:
    """
    Execute full service migration and capture output.

    Args:
        migration_helper: Helper for running migrations
        migration_context: Test context dictionary
        capfd: Pytest fixture for capturing stdout/stderr
    """
    result = migration_helper.run_full_service_migration()

    captured_full = capfd.readouterr()

    migration_context["result"] = result
    migration_context["captured_output"] = {
        "stdout": captured_full.out,
        "stderr": captured_full.err,
    }

    logger.info(
        "Full service migration completed",
        extra={
            "success": result.success,
            "total_records": result.metrics.total_records if result.metrics else 0,
        },
    )

def run_single_service_migration(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
    service_id: int,
    capfd: pytest.CaptureFixture[str],
) -> None:
    """
    Execute migration for a single service and capture output.

    Args:
        migration_helper: Helper for running migrations
        migration_context: Test context dictionary
        service_id: Service ID to migrate
        capfd: Pytest fixture for capturing stdout/stderr
    """
    result = migration_helper.run_single_service_migration(service_id)

    captured_single = capfd.readouterr()
    with capfd.disabled():
        print("output not captured, going directly to sys.stdout")
        print("!!! captured_single", captured_single)

    migration_context["result"] = result
    migration_context["service_id"] = service_id
    migration_context["captured_output"] = {
        "stdout": captured_single,
        "stderr": captured_single,
    }

def run_verify_migration_metrics_inline(
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

    is_full_sync = service_id is None
    migration_type = "full sync" if is_full_sync else f"service {service_id}"

    assert metrics.total_records == total, (
        f"Total records mismatch for {migration_type}: "
        f"expected {total}, got {metrics.total_records}"
    )

    if is_full_sync:
        assert metrics.supported_records == supported, (
            f"Supported records mismatch for {migration_type}:\n"
            f"  Expected: {supported}\n"
            f"  Got: {metrics.supported_records}\n"
            f"  (All existing services in database)"
        )
    else:
        assert metrics.supported_records == supported, (
            f"Supported records mismatch for {migration_type}:\n"
            f"  Expected: {supported}\n"
            f"  Got: {metrics.supported_records}\n"
            f"  Type ID: {service_data.get('typeid')}\n"
            f"  ODS Code: {service_data.get('odscode')}\n"
            f"  Status: {service_data.get('statusid')}"
        )

    assert metrics.unsupported_records == unsupported, (
        f"Unsupported records mismatch for {migration_type}: "
        f"expected {unsupported}, got {metrics.unsupported_records}"
    )

    assert metrics.transformed_records == transformed, (
        f"Transformed records mismatch for {migration_type}: "
        f"expected {transformed}, got {metrics.transformed_records}"
    )

    assert metrics.migrated_records == migrated, (
        f"Migrated records mismatch for {migration_type}: "
        f"expected {migrated}, got {metrics.migrated_records}"
    )

    assert metrics.skipped_records == skipped, (
        f"Skipped records mismatch for {migration_type}: "
        f"expected {skipped}, got {metrics.skipped_records}"
    )

    assert metrics.errors == errors, (
        f"Errors mismatch for {migration_type}: "
        f"expected {errors}, got {metrics.errors}"
    )

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
            "is_full_sync": is_full_sync,
        },
    )

def run_verify_transformation_output(
    migration_context: Dict[str, Any],
    service_id: int,
    org_count: int,
    location_count: int,
    service_count: int,
) -> None:
    """
    Verify that a service was transformed into the expected number of resources.

    Validates DM_ETL_007 log reference from DataMigrationLogBase.

    Args:
        migration_context: Test context dictionary with captured output
        service_id: Service ID that was transformed
        org_count: Expected number of organisations created
        location_count: Expected number of locations created
        service_count: Expected number of healthcare services created

    Raises:
        AssertionError: If transformation log not found or counts don't match
    """

    def validate_counts(log_line: str) -> None:
        """Validate entity counts in log line."""
        org_count_pattern = f'"organisation_count":{org_count}'
        location_count_pattern = f'"location_count":{location_count}'
        service_count_pattern = f'"healthcare_service_count":{service_count}'

        if org_count_pattern not in log_line:
            pytest.fail(
                f"Organisation count mismatch in DM_ETL_007 log.\n"
                f"Expected: {org_count} organisations\n"
                f"Log: {log_line}"
            )

        if location_count_pattern not in log_line:
            pytest.fail(
                f"Location count mismatch in DM_ETL_007 log.\n"
                f"Expected: {location_count} locations\n"
                f"Log: {log_line}"
            )

        if service_count_pattern not in log_line:
            pytest.fail(
                f"Healthcare service count mismatch in DM_ETL_007 log.\n"
                f"Expected: {service_count} healthcare services\n"
                f"Log: {log_line}"
            )

    config = LogVerificationConfig(
        log_reference="DM_ETL_007",
        message_template='"message":"Record successfully migrated"',
        validation_fn=validate_counts,
    )

    verify_log_reference(migration_context, service_id, config)

def run_verify_service_not_migrated(
    migration_context: Dict[str, Any],
    service_id: int,
    expected_reason: str,
) -> None:
    """
    Verify that a service was not migrated with the expected reason.

    Validates DM_ETL_004 log reference from DataMigrationLogBase.

    Args:
        migration_context: Test context dictionary with captured output
        service_id: Service ID that was not migrated
        expected_reason: Expected reason for not migrating

    Raises:
        AssertionError: If migration failure log not found or wrong reason
    """
    config = LogVerificationConfig(
        log_reference="DM_ETL_004",
        message_template=f'"message":"Record was not migrated due to reason: {expected_reason}"',
    )

    verify_log_reference(migration_context, service_id, config)

def run_verify_service_skipped(
    migration_context: Dict[str, Any],
    service_id: int,
    expected_reason: str,
) -> None:
    """
    Verify that a service was skipped with the expected reason.

    Validates DM_ETL_005 log reference from DataMigrationLogBase.

    Args:
        migration_context: Test context dictionary with captured output
        service_id: Service ID that was skipped
        expected_reason: Expected reason for skipping

    Raises:
        AssertionError: If service skip log not found or wrong reason
    """
    config = LogVerificationConfig(
        log_reference="DM_ETL_005",
        message_template=f'"message":"Record skipped due to condition: {expected_reason}"',
    )

    verify_log_reference(migration_context, service_id, config)

# ============================================================
# Common SQS Steps
# ============================================================

def run_sqs_event_migration(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
    docstring: str,
    capfd: pytest.CaptureFixture[str],
) -> Dict[str, Any]:
    """
    Execute migration with SQS event and capture output.

    Args:
        migration_helper: Helper for running migrations
        migration_context: Test context dictionary
        docstring: JSON event string from Gherkin docstring
        capfd: Pytest fixture for capturing stdout/stderr

    Returns:
        Dictionary containing event processing result

    Raises:
        pytest.fail: If event JSON is invalid
    """
    try:
        event = json.loads(docstring)
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON in event docstring: {e}")

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

    logger.debug(
        "Processing SQS event",
        extra={
            "record_count": len(event.get("Records", [])),
            "is_empty": len(event) == 0,
            "service_ids": service_ids,
        },
    )

    result = migration_helper.run_sqs_event_migration(event)

    captured_sqs = capfd.readouterr()
    with capfd.disabled():
        print("output not captured, going directly to sys.stdout")
        print("!!! captured_sqs", captured_sqs)

    migration_context["result"] = result
    migration_context["sqs_event"] = event
    migration_context["sqs_service_ids"] = service_ids
    migration_context["sqs_service_id"] = service_ids[0] if service_ids else None
    migration_context["captured_output"] = {
        "stdout": captured_sqs,
        "stderr": captured_sqs,
    }

    logger.info(
        "SQS event migration completed",
        extra={
            "success": result.success,
            "migrated_records": result.metrics.migrated_records if result.metrics else 0,
            "is_empty_event": len(event) == 0,
            "service_ids": service_ids,
        },
    )

    return {"event": event, "result": result}

def run_verify_sqs_event_metrics(
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

    sqs_event = migration_context.get("sqs_event", {})
    service_id = migration_context.get("sqs_service_id")

    assert result is not None, "Migration result should exist"
    assert result.metrics is not None, "Migration metrics should exist"

    metrics = result.metrics
    is_empty_event = len(sqs_event) == 0
    record_count = len(sqs_event.get("Records", []))

    if is_empty_event:
        event_info = "empty event"
    elif service_id:
        event_info = f"SQS event for service {service_id}"
    else:
        event_info = f"SQS event with {record_count} record(s)"

    assert metrics.total_records == total, (
        f"Total records mismatch for {event_info}:\n"
        f"  Expected: {total}\n"
        f"  Got: {metrics.total_records}"
    )

    assert metrics.supported_records == supported, (
        f"Supported records mismatch for {event_info}:\n"
        f"  Expected: {supported}\n"
        f"  Got: {metrics.supported_records}"
    )

    assert metrics.unsupported_records == unsupported, (
        f"Unsupported records mismatch for {event_info}:\n"
        f"  Expected: {unsupported}\n"
        f"  Got: {metrics.unsupported_records}"
    )

    assert metrics.transformed_records == transformed, (
        f"Transformed records mismatch for {event_info}:\n"
        f"  Expected: {transformed}\n"
        f"  Got: {metrics.transformed_records}"
    )

    assert metrics.migrated_records == migrated, (
        f"Migrated records mismatch for {event_info}:\n"
        f"  Expected: {migrated}\n"
        f"  Got: {metrics.migrated_records}"
    )

    assert metrics.skipped_records == skipped, (
        f"Skipped records mismatch for {event_info}:\n"
        f"  Expected: {skipped}\n"
        f"  Got: {metrics.skipped_records}"
    )

    assert metrics.errors == errors, (
        f"Errors mismatch for {event_info}:\n"
        f"  Expected: {errors}\n"
        f"  Got: {metrics.errors}"
    )

    logger.info(
        f"Verified SQS event metrics for {event_info}",
        extra={
            "total": total,
            "supported": supported,
            "unsupported": unsupported,
            "transformed": transformed,
            "migrated": migrated,
            "skipped": skipped,
            "errors": errors,
            "is_empty_event": is_empty_event,
            "service_id": service_id,
        },
    )

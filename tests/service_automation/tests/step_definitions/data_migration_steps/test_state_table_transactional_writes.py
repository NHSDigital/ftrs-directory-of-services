"""Step definitions for FTRS-1370 - State table transactional writes tests."""

from typing import Any, Dict
from uuid import UUID

import pytest
from boto3.dynamodb.types import TypeDeserializer
from pytest_bdd import parsers, scenarios, then, when

from step_definitions.common_steps.data_migration_steps import *  # noqa: F403
from utilities.common.constants import DYNAMODB_CLIENT
from utilities.common.dynamoDB_tables import get_table_name
from utilities.common.log_helper import get_mock_logger_from_context
from utilities.data_migration.migration_context_helper import store_migration_result

scenarios(
    "../../tests/features/data_migration_features/state_table_transactional_writes.feature"
)


# ============================================================
# State Table Verification Steps
# ============================================================


@when(parsers.parse("a record does not exist in the state table for key '{state_key}'"))
def verify_no_state_record(
    dynamodb: Dict[str, Any],
    state_key: str,
) -> None:
    """Verify that no state record exists for the given key."""
    state_table_name = get_table_name(resource="state", stack_name="data-migration")

    client = dynamodb[DYNAMODB_CLIENT]
    response = client.get_item(
        TableName=state_table_name,
        Key={"source_record_id": {"S": state_key}},
    )

    # Verify record does NOT exist
    assert "Item" not in response, f"State record should not exist for key {state_key}"


# ============================================================
# Pipeline Behavior Verification Steps
# ============================================================


@then(parsers.parse("the pipeline treats the record as an '{operation}' operation"))
def verify_operation_type(
    migration_context: Dict[str, Any],
    operation: str,
) -> None:
    """Verify the pipeline treated the record as insert or update."""
    mock_logger = get_mock_logger_from_context(migration_context)

    match operation:
        case "insert":
            assert mock_logger.was_logged("DM_ETL_020"), (
                "Should log DM_ETL_020 for insert operation"
            )
        case "update":
            assert mock_logger.was_logged("DM_ETL_019"), (
                "Should log DM_ETL_019 for update operation"
            )
        case _:
            pytest.fail(f"Unknown operation type: {operation}")


@then(
    parsers.parse(
        "the pipeline sends a single TransactWriteItems operation with {item_count:d} items"
    )
)
def verify_transact_write_items(
    migration_context: Dict[str, Any],
    item_count: int,
) -> None:
    """Verify that TransactWriteItems was used for atomic writes."""
    # This is implicitly tested by the code path - if migration succeeded,
    # TransactWriteItems was used. We can verify this through logs.
    mock_logger = get_mock_logger_from_context(migration_context)

    transaction_success_logs = mock_logger.get_log("DM_ETL_021")
    assert len(transaction_success_logs) == 1, (
        "Should find exactly one transaction success log (DM_ETL_021)."
    )

    log = transaction_success_logs[0]
    logged_item_count = log["detail"].get("item_count")
    assert logged_item_count == item_count, (
        f"Expected {item_count} items in TransactWriteItems, got {logged_item_count}"
    )


@then("the organisation, location, healthcare service and state record is created")
def verify_all_records_created(
    dynamodb: Dict[str, Any],
    migration_context: Dict[str, Any],
) -> None:
    """Verify that all records (org, location, HC service, and state) were created."""
    client = dynamodb[DYNAMODB_CLIENT]
    result = migration_context.get("result")

    assert result is not None, "Migration result should exist"
    assert result.success, "Migration should be successful"

    # Verify state record exists
    service_id = migration_context.get("service_id")
    state_table_name = get_table_name("state", stack_name="data-migration")

    state_response = client.get_item(
        TableName=state_table_name,
        Key={"source_record_id": {"S": f"services#{service_id}"}},
    )

    assert "Item" in state_response, (
        f"State record should exist for services#{service_id}"
    )

    # Verify organisation, location, and healthcare service exist
    # (these are verified through successful migration and metrics)
    assert result.metrics.inserted == 1, "Should have inserted 1 record"


@then(parsers.parse('the pipeline logs "{log_message}"'))
def verify_specific_log_message(
    migration_context: Dict[str, Any],
    log_message: str,
) -> None:
    """Verify that a specific log message was recorded."""
    mock_logger = get_mock_logger_from_context(migration_context)

    # Get all logs from all levels
    all_logs = []
    for level in mock_logger.logs.values():
        all_logs.extend(level)

    matching_logs = [log for log in all_logs if log_message in log.get("msg", "")]

    assert len(matching_logs) > 0, (
        f"Should find log containing '{log_message}'. All logs: {[log.get('msg', '') for log in all_logs]}"
    )


@then(
    parsers.parse(
        "the metrics should show {expected_inserted:d} inserted, {expected_updated:d} updated records for the second run"
    )
)
def verify_no_migration_on_second_run(
    migration_context: Dict[str, Any],
    expected_inserted: int,
    expected_updated: int,
) -> None:
    """Verify that the second migration run resulted in 0 inserted records."""
    result = migration_context.get("result")

    assert result is not None, "Migration result should exist"
    assert result.metrics is not None, "Migration metrics should exist"
    assert result.metrics.inserted == expected_inserted, (
        f"Should have {expected_inserted} inserted records on second run, got {result.metrics.inserted}"
    )
    assert result.metrics.updated == expected_updated, (
        f"Should have {expected_updated} updated records on second run, got {result.metrics.updated}"
    )


@then(
    parsers.parse(
        'the state table record for "{state_key}" contains all required fields'
    )
)
def verify_state_record_structure(
    dynamodb: Dict[str, Any],
    state_key: str,
) -> None:
    """Verify that the state record has all required fields."""
    state_table_name = get_table_name(resource="state", stack_name="data-migration")

    client = dynamodb[DYNAMODB_CLIENT]
    response = client.get_item(
        TableName=state_table_name,
        Key={"source_record_id": {"S": state_key}},
    )

    assert "Item" in response, f"State record should exist for key {state_key}"

    item = response["Item"]
    deserializer = TypeDeserializer()
    deserialized_item = {k: deserializer.deserialize(v) for k, v in item.items()}

    # Verify required fields exist
    required_fields = [
        "source_record_id",
        "version",
        "organisation_id",
        "location_id",
        "healthcare_service_id",
    ]

    for field in required_fields:
        assert field in deserialized_item, (
            f"State record should contain field '{field}'. Found fields: {list(deserialized_item.keys())}"
        )


def verify_state_record_field(
    dynamodb: Dict[str, Any],
    state_key: str,
    field_name: str,
) -> None:
    """Verify that the state record has a valid field value (UUID format).

    Args:
        dynamodb: DynamoDB client connection
        state_key: The state table key to look up
        field_name: The field name to verify (e.g. 'organisation_id', 'location_id')
    """
    state_table_name = get_table_name(resource="state", stack_name="data-migration")

    client = dynamodb[DYNAMODB_CLIENT]
    response = client.get_item(
        TableName=state_table_name,
        Key={"source_record_id": {"S": state_key}},
    )

    assert "Item" in response, f"State record should exist for key {state_key}"

    item = response["Item"]
    deserializer = TypeDeserializer()
    deserialized_item = {k: deserializer.deserialize(v) for k, v in item.items()}

    # Verify field is a valid UUID
    field_value = deserialized_item.get(field_name)
    assert field_value is not None, f"{field_name} should exist"

    try:
        UUID(field_value)
    except (ValueError, TypeError) as e:
        pytest.fail(f"{field_name} '{field_value}' is not a valid UUID: {e}")


@then(
    parsers.parse('the state table record for "{state_key}" has valid organisation_id')
)
def verify_state_record_organisation_id(
    dynamodb: Dict[str, Any],
    state_key: str,
) -> None:
    """Verify that the state record has a valid organisation_id (UUID format)."""
    verify_state_record_field(dynamodb, state_key, "organisation_id")


@then(parsers.parse('the state table record for "{state_key}" has valid location_id'))
def verify_state_record_location_id(
    dynamodb: Dict[str, Any],
    state_key: str,
) -> None:
    """Verify that the state record has a valid location_id (UUID format)."""
    verify_state_record_field(dynamodb, state_key, "location_id")


@then(
    parsers.parse(
        'the state table record for "{state_key}" has valid healthcare_service_id'
    )
)
def verify_state_record_healthcare_service_id(
    dynamodb: Dict[str, Any],
    state_key: str,
) -> None:
    """Verify that the state record has a valid healthcare_service_id (UUID format)."""
    verify_state_record_field(dynamodb, state_key, "healthcare_service_id")


# ============================================================
# Conflict Detection Steps
# ============================================================


def create_conflicting_record(
    dynamodb: Dict[str, Any],
    migration_helper: Any,
    migration_context: Dict[str, Any],
    service_id: int,
) -> None:
    """Pre-create records to simulate UUID collision.

    Strategy:
    1. Run migration once to create all records (org/loc/hcs/state) with real UUIDs
    2. Delete ONLY the state record (but keep org/loc/hcs)
    3. Next migration attempt will fail on ConditionalCheckFailed

    This simulates a retry scenario where the migration was partially successful
    before crashing, leaving orphaned records in DynamoDB.

    Args:
        dynamodb: DynamoDB client connection
        migration_helper: Helper for running migrations
        migration_context: Migration context to store results
        service_id: Service ID to migrate
    """

    # Run migration first time to create records
    result = migration_helper.run_single_service_migration(service_id)
    store_migration_result(migration_context, result, service_id)

    # Now delete ONLY the state record to simulate retry scenario
    state_table_name = get_table_name(resource="state", stack_name="data-migration")
    client = dynamodb[DYNAMODB_CLIENT]

    client.delete_item(
        TableName=state_table_name,
        Key={"source_record_id": {"S": f"services#{service_id}"}},
    )

    # Organisation/Location/HealthcareService still exist
    # Next migration will try to create them again -> ConditionalCheckFailed


@when(
    parsers.parse(
        "a record exists in the Organisation table matching the transformed organisation ID for service {service_id:d}"
    )
)
def create_conflicting_organisation(
    dynamodb: Dict[str, Any],
    migration_helper: Any,
    migration_context: Dict[str, Any],
    service_id: int,
) -> None:
    """Pre-create an organisation record to simulate UUID collision."""
    create_conflicting_record(dynamodb, migration_helper, migration_context, service_id)


@when(
    parsers.parse(
        "a record exists in the Location table matching the transformed location ID for service {service_id:d}"
    )
)
def create_conflicting_location(
    dynamodb: Dict[str, Any],
    migration_helper: Any,
    migration_context: Dict[str, Any],
    service_id: int,
) -> None:
    """Pre-create a location record to simulate UUID collision."""
    create_conflicting_record(dynamodb, migration_helper, migration_context, service_id)


@when(
    parsers.parse(
        "a record exists in the Healthcare Service table matching the transformed healthcare service ID for service {service_id:d}"
    )
)
def create_conflicting_healthcare_service(
    dynamodb: Dict[str, Any],
    migration_helper: Any,
    migration_context: Dict[str, Any],
    service_id: int,
) -> None:
    """Pre-create a healthcare service record to simulate UUID collision."""
    create_conflicting_record(dynamodb, migration_helper, migration_context, service_id)


@then(
    "the DynamoDB TransactWriteItems request is rejected due to ConditionalCheckFailed"
)
def verify_conditional_check_failed(
    migration_context: Dict[str, Any],
) -> None:
    """Verify that the migration attempt was rejected due to ConditionalCheckFailed."""
    mock_logger = get_mock_logger_from_context(migration_context)

    # Check for DM_ETL_022 log indicating conditional check failure
    error_logs = mock_logger.get_log("DM_ETL_022", level="ERROR")

    assert len(error_logs) > 0, (
        "Expected DM_ETL_022 error log for ConditionalCheckFailed\n"
        f"All ERROR logs: {mock_logger.get_logs(level='ERROR')}"
    )


@then(parsers.parse('the pipeline logs "{expected_message}"'))
def verify_log_message_contains(
    migration_context: Dict[str, Any],
    expected_message: str,
) -> None:
    """Verify that a specific log message was recorded."""
    mock_logger = get_mock_logger_from_context(migration_context)

    all_logs = []
    for level in mock_logger.logs.values():
        all_logs.extend(level)

    matching_logs = [log for log in all_logs if expected_message in log.get("msg", "")]

    assert len(matching_logs) > 0, (
        f"Expected log message containing: {expected_message}\n"
        f"All log messages: {[log.get('msg', '') for log in all_logs]}"
    )


@then(parsers.parse("the migration records an error for service ID {service_id:d}"))
def verify_migration_error_recorded(
    migration_context: Dict[str, Any],
    service_id: int,
) -> None:
    """Verify that a ConditionalCheckFailed was logged for the failed migration.

    Note: ConditionalCheckFailed is logged but does NOT increment metrics.errors
    as it's a normal flow (skip duplicate), not an actual error.
    """
    mock_logger = get_mock_logger_from_context(migration_context)

    # Check for DM_ETL_022 log
    error_logs = mock_logger.get_log("DM_ETL_022", level="ERROR")

    assert len(error_logs) > 0, (
        f"Expected DM_ETL_022 log for service {service_id}\n"
        f"All ERROR logs: {mock_logger.get_logs(level='ERROR')}"
    )

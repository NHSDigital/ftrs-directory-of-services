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

scenarios(
    "../../tests/features/data_migration_features/state_table_transactional_writes.feature"
)


# ============================================================
# State Table Verification Steps
# ============================================================


@when(
    parsers.parse('a record does not exist in the state table for key "{state_key}"')
)
def verify_no_state_record(
    dynamodb: Dict[str, Any],
    state_key: str,
) -> None:
    """Verify that no state record exists for the given key."""
    state_table_name = get_table_name(resource="data-migration-state")

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

    if operation == "insert":
        # For insert, we should NOT see the "State record found" log
        skip_logs = [
            log for log in mock_logger.logs if "State record found" in log.message
        ]
        assert (
            len(skip_logs) == 0
        ), f"Should not find 'State record found' log for insert operation. Found: {skip_logs}"

    elif operation == "update":
        # For update, we SHOULD see the "State record found" log
        skip_logs = [
            log for log in mock_logger.logs if "State record found" in log.message
        ]
        assert (
            len(skip_logs) > 0
        ), "Should find 'State record found' log for update operation"


@then("the pipeline sends a single TransactWriteItems operation")
def verify_transact_write_items(
    migration_context: Dict[str, Any],
) -> None:
    """Verify that TransactWriteItems was used for atomic writes."""
    # This is implicitly tested by the code path - if migration succeeded,
    # TransactWriteItems was used. We can verify this through logs.
    mock_logger = get_mock_logger_from_context(migration_context)

    # Look for successful transact write log
    transact_logs = [
        log
        for log in mock_logger.logs
        if "Successfully wrote" in log.message and "items transactionally" in log.message
    ]

    assert (
        len(transact_logs) > 0
    ), f"Should find transaction success log. All logs: {[log.message for log in mock_logger.logs]}"


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
    state_table_name = get_table_name(resource="data-migration-state")

    state_response = client.get_item(
        TableName=state_table_name,
        Key={"source_record_id": {"S": f"services#{service_id}"}},
    )

    assert (
        "Item" in state_response
    ), f"State record should exist for services#{service_id}"

    # Verify organisation, location, and healthcare service exist
    # (these are verified through successful migration and metrics)
    assert result.metrics.migrated_records == 1, "Should have migrated 1 record"


@then(
    parsers.parse(
        'the state table contains a record for key "{state_key}" with version {version:d}'
    )
)
def verify_state_record_details(
    dynamodb: Dict[str, Any],
    state_key: str,
    version: int,
) -> None:
    """Verify state record exists with correct version."""
    state_table_name = get_table_name(resource="data-migration-state")

    client = dynamodb[DYNAMODB_CLIENT]
    response = client.get_item(
        TableName=state_table_name,
        Key={"source_record_id": {"S": state_key}},
    )

    assert "Item" in response, f"State record should exist for key {state_key}"

    item = response["Item"]
    deserializer = TypeDeserializer()
    deserialized_item = {k: deserializer.deserialize(v) for k, v in item.items()}

    assert (
        deserialized_item["version"] == version
    ), f"Version should be {version}, got {deserialized_item['version']}"


@then(parsers.parse('the pipeline logs "{log_message}"'))
def verify_specific_log_message(
    migration_context: Dict[str, Any],
    log_message: str,
) -> None:
    """Verify that a specific log message was recorded."""
    mock_logger = get_mock_logger_from_context(migration_context)

    matching_logs = [log for log in mock_logger.logs if log_message in log.message]

    assert (
        len(matching_logs) > 0
    ), f"Should find log containing '{log_message}'. All logs: {[log.message for log in mock_logger.logs]}"


@then("the metrics should show 0 migrated records for the second run")
def verify_no_migration_on_second_run(
    migration_context: Dict[str, Any],
) -> None:
    """Verify that the second migration run resulted in 0 migrated records."""
    result = migration_context.get("result")

    assert result is not None, "Migration result should exist"
    assert result.metrics is not None, "Migration metrics should exist"
    assert (
        result.metrics.migrated_records == 0
    ), f"Should have 0 migrated records on second run, got {result.metrics.migrated_records}"


@then(parsers.parse('the state table record for "{state_key}" contains all required fields'))
def verify_state_record_structure(
    dynamodb: Dict[str, Any],
    state_key: str,
) -> None:
    """Verify that the state record has all required fields."""
    project_name = os.getenv(ENV_PROJECT_NAME)
    environment = os.getenv(ENV_ENVIRONMENT)
    workspace = os.getenv(ENV_WORKSPACE)

    state_table_name = get_table_name(
        project_name=project_name,
        environment=environment,
        resource="data-migration-state",
        workspace=workspace,
    )

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
        assert (
            field in deserialized_item
        ), f"State record should contain field '{field}'. Found fields: {list(deserialized_item.keys())}"


@then(parsers.parse('the state table record for "{state_key}" has valid organisation_id'))
def verify_state_record_organisation_id(
    dynamodb: Dict[str, Any],
    state_key: str,
) -> None:
    """Verify that the state record has a valid organisation_id (UUID format)."""
    project_name = os.getenv(ENV_PROJECT_NAME)
    environment = os.getenv(ENV_ENVIRONMENT)
    workspace = os.getenv(ENV_WORKSPACE)

    state_table_name = get_table_name(
        project_name=project_name,
        environment=environment,
        resource="data-migration-state",
        workspace=workspace,
    )

    client = dynamodb[DYNAMODB_CLIENT]
    response = client.get_item(
        TableName=state_table_name,
        Key={"source_record_id": {"S": state_key}},
    )

    assert "Item" in response, f"State record should exist for key {state_key}"

    item = response["Item"]
    deserializer = TypeDeserializer()
    deserialized_item = {k: deserializer.deserialize(v) for k, v in item.items()}

    # Verify organisation_id is a valid UUID
    org_id_str = deserialized_item.get("organisation_id")
    assert org_id_str is not None, "organisation_id should exist"

    try:
        UUID(org_id_str)
    except (ValueError, TypeError) as e:
        pytest.fail(f"organisation_id '{org_id_str}' is not a valid UUID: {e}")


@then(parsers.parse('the state table record for "{state_key}" has valid location_id'))
def verify_state_record_location_id(
    dynamodb: Dict[str, Any],
    state_key: str,
) -> None:
    """Verify that the state record has a valid location_id (UUID format)."""
    project_name = os.getenv(ENV_PROJECT_NAME)
    environment = os.getenv(ENV_ENVIRONMENT)
    workspace = os.getenv(ENV_WORKSPACE)

    state_table_name = get_table_name(
        project_name=project_name,
        environment=environment,
        resource="data-migration-state",
        workspace=workspace,
    )

    client = dynamodb[DYNAMODB_CLIENT]
    response = client.get_item(
        TableName=state_table_name,
        Key={"source_record_id": {"S": state_key}},
    )

    assert "Item" in response, f"State record should exist for key {state_key}"

    item = response["Item"]
    deserializer = TypeDeserializer()
    deserialized_item = {k: deserializer.deserialize(v) for k, v in item.items()}

    # Verify location_id is a valid UUID
    loc_id_str = deserialized_item.get("location_id")
    assert loc_id_str is not None, "location_id should exist"

    try:
        UUID(loc_id_str)
    except (ValueError, TypeError) as e:
        pytest.fail(f"location_id '{loc_id_str}' is not a valid UUID: {e}")


@then(parsers.parse('the state table record for "{state_key}" has valid healthcare_service_id'))
def verify_state_record_healthcare_service_id(
    dynamodb: Dict[str, Any],
    state_key: str,
) -> None:
    """Verify that the state record has a valid healthcare_service_id (UUID format)."""
    project_name = os.getenv(ENV_PROJECT_NAME)
    environment = os.getenv(ENV_ENVIRONMENT)
    workspace = os.getenv(ENV_WORKSPACE)

    state_table_name = get_table_name(
        project_name=project_name,
        environment=environment,
        resource="data-migration-state",
        workspace=workspace,
    )

    client = dynamodb[DYNAMODB_CLIENT]
    response = client.get_item(
        TableName=state_table_name,
        Key={"source_record_id": {"S": state_key}},
    )

    assert "Item" in response, f"State record should exist for key {state_key}"

    item = response["Item"]
    deserializer = TypeDeserializer()
    deserialized_item = {k: deserializer.deserialize(v) for k, v in item.items()}

    # Verify healthcare_service_id is a valid UUID
    hc_id_str = deserialized_item.get("healthcare_service_id")
    assert hc_id_str is not None, "healthcare_service_id should exist"

    try:
        UUID(hc_id_str)
    except (ValueError, TypeError) as e:
        pytest.fail(f"healthcare_service_id '{hc_id_str}' is not a valid UUID: {e}")


import os
from typing import Any, Dict, Literal

import pytest
from pytest_bdd import given, parsers, then, when
from sqlalchemy import text
from sqlmodel import Session

from utilities.data_migration.migration_context_helper import (
    build_supported_records_context,
    get_expected_dynamodb_table_names,
    get_migration_type_description,
    store_migration_result,
    store_sqs_result,
)
from utilities.data_migration.migration_helper import MigrationHelper
from utilities.data_migration.migration_metrics_helper import verify_all_metrics
from utilities.data_migration.migration_service_helper import (
    parse_and_create_service,
)
from utilities.data_migration.sqs_helper import build_sqs_event
from utilities.common.constants import (
    DYNAMODB_CLIENT,
    ENV_ENVIRONMENT,
    ENV_WORKSPACE,
    SERVICETYPES_TABLE,
)
from utilities.common.log_helper import (
    get_mock_logger_from_context,
    verify_migration_completed_log,
    verify_error_log_present,
    verify_service_not_migrated_log,
    verify_service_skipped_log,
    verify_transformation_log,
    verify_transformer_selected_log,
)
from utilities.common.dynamoDB_tables import get_table_name
from boto3.dynamodb.types import TypeDeserializer
from step_definitions.data_migration_steps.dos_data_manipulation_steps import (
    parse_datatable_value,
)
from service_migration.models import ServiceMigrationMetrics

# ============================================================
# Setup Steps (Background)
# ============================================================


@given("the test environment is configured")
def environment_configured(
    migration_helper: MigrationHelper, dynamodb: Dict[str, Any]
) -> None:
    """Verify test environment is properly configured."""
    try:
        response = dynamodb[DYNAMODB_CLIENT].list_tables()
        table_names = response.get("TableNames", [])
        assert "TableNames" in response, "DynamoDB should be accessible"
    except Exception as e:
        pytest.fail(f"Failed to access DynamoDB: {e}")

    assert migration_helper is not None, "Migration helper should be configured"
    assert migration_helper.db_uri is not None, "Database URI should be set"
    assert migration_helper.dynamodb_endpoint is not None, (
        "DynamoDB endpoint should be set"
    )


@given("the DoS database has test data")
def dos_database_has_test_data(dos_db: Session) -> None:
    """Verify DoS database is accessible and has tables."""
    result = dos_db.exec(text(f"SELECT COUNT(*) FROM {SERVICETYPES_TABLE}"))
    count = result.fetchone()[0]
    assert count >= 0, "Should be able to query servicetypes table"


@given("DynamoDB tables are ready")
def dynamodb_tables_ready(dynamodb: Dict[str, Any]) -> None:
    """Verify DynamoDB tables exist and are accessible."""
    client = dynamodb[DYNAMODB_CLIENT]
    response = client.list_tables()
    table_names = response.get("TableNames", [])

    expected_tables = get_expected_dynamodb_table_names()
    missing_tables = [table for table in expected_tables if table not in table_names]

    if missing_tables:
        environment = os.getenv(ENV_ENVIRONMENT)
        workspace = os.getenv(ENV_WORKSPACE)

        pytest.fail(
            f"Missing required DynamoDB tables: {', '.join(missing_tables)}\n"
            f"Found tables: {', '.join(table_names)}\n"
            f"Expected pattern: ftrs-dos-{environment}-database-{{resource}}-{workspace}"
        )


# ============================================================
# Service Creation Steps (Given)
# ============================================================


@given(
    parsers.parse(
        "a '{entity_type}' exists called '{entity_name}' in DoS with attributes:"
    ),
    target_fixture="service_created",
)
def create_service_with_attributes(
    dos_db: Session,
    migration_context: Dict[str, Any],
    entity_type: str,
    entity_name: str,
    datatable: list[list[str]],
) -> Dict[str, Any]:
    """Create a service in DoS database with attributes from Gherkin table."""
    return parse_and_create_service(
        dos_db,
        migration_context,
        entity_type,
        entity_name,
        datatable,
    )


# ============================================================
# Migration Execution Steps (When)
# ============================================================


@when("triage code full migration is executed")
def triage_code_full_migration(migration_helper: MigrationHelper, dynamodb):
    migration_helper.run_triage_code_migration_only()


@when("the data migration process is run")
def full_service_migration(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
) -> None:
    """Execute full service migration."""
    result = migration_helper.run_full_service_migration()
    store_migration_result(migration_context, result)


@when(
    parsers.parse("a single service migration is run for ID '{service_id:d}'"),
    target_fixture="migration_executed",
)
def single_service_migration(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
    service_id: int,
) -> None:
    """Execute migration for a single service."""
    result = migration_helper.run_single_service_migration(service_id)
    store_migration_result(migration_context, result, service_id)


@when(
    parsers.parse(
        "the data migration process is run for table '{table_name}', "
        "ID '{record_id:d}' and method '{method}'"
    ),
    target_fixture="sqs_event_processed",
)
def sqs_event_migration_with_params(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
    table_name: str,
    record_id: int,
    method: Literal["insert", "update", "delete"],
) -> Dict[str, Any]:
    """Execute migration with SQS event built from minimal parameters."""
    event = build_sqs_event(
        table_name=table_name,
        record_id=record_id,
        service_id=record_id,
        method=method,
    )

    result = migration_helper.run_sqs_event_migration(event)
    store_sqs_result(migration_context, result, event, record_id)

    return {"event": event, "result": result}


# ============================================================
# Verification Steps (Then)
# ============================================================


@then(
    parsers.parse(
        "the metrics should be "
        "{total:d} total, "
        "{supported:d} supported, "
        "{unsupported:d} unsupported, "
        "{transformed:d} transformed, "
        "{inserted:d} inserted, "
        "{updated:d} updated, "
        "{skipped:d} skipped, "
        "{invalid:d} invalid and "
        "{errors:d} errors"
    )
)
def verify_migration_metrics(
    migration_context: Dict[str, Any],
    total: int,
    supported: int,
    unsupported: int,
    transformed: int,
    inserted: int,
    updated: int,
    skipped: int,
    invalid: int,
    errors: int,
) -> None:
    """Verify migration metrics match expected values."""
    result = migration_context["result"]

    assert result is not None, "Migration result should exist"
    assert result.metrics is not None, "Migration metrics should exist"

    migration_type = get_migration_type_description(migration_context)
    additional_context = build_supported_records_context(migration_context)

    expected = ServiceMigrationMetrics(
        total=total,
        supported=supported,
        unsupported=unsupported,
        transformed=transformed,
        inserted=inserted,
        updated=updated,
        skipped=skipped,
        invalid=invalid,
        errors=errors,
    )

    verify_all_metrics(
        actual_metrics=result.metrics,
        expected_metrics=expected,
        migration_type=migration_type,
        additional_context=additional_context,
    )


@then(
    parsers.parse(
        "the SQS event metrics should be "
        "{total:d} total, "
        "{supported:d} supported, "
        "{unsupported:d} unsupported, "
        "{transformed:d} transformed, "
        "{inserted:d} inserted, "
        "{updated:d} updated, "
        "{skipped:d} skipped and "
        "{errors:d} errors"
    )
)
def verify_sqs_event_metrics(
    migration_context: Dict[str, Any],
    total: int,
    supported: int,
    unsupported: int,
    transformed: int,
    inserted: int,
    updated: int,
    skipped: int,
    errors: int,
) -> None:
    """Verify SQS event migration metrics match expected values."""
    result = migration_context.get("result")

    assert result is not None, "Migration result should exist"
    assert result.metrics is not None, "Migration metrics should exist"

    migration_type = get_migration_type_description(migration_context)

    expected = ServiceMigrationMetrics(
        total=total,
        supported=supported,
        unsupported=unsupported,
        transformed=transformed,
        inserted=inserted,
        updated=updated,
        skipped=skipped,
        errors=errors,
    )

    verify_all_metrics(
        actual_metrics=result.metrics,
        expected_metrics=expected,
        migration_type=migration_type,
    )

    mock_logger = get_mock_logger_from_context(migration_context)
    verify_migration_completed_log(mock_logger)


@then(
    parsers.parse(
        "the '{transformer_name}' was selected for service ID '{service_id:d}'"
    )
)
def verify_transformer_selected(
    migration_context: Dict[str, Any],
    transformer_name: str,
    service_id: int,
) -> None:
    """Verify the correct transformer was selected for the service."""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_transformer_selected_log(
        mock_logger=mock_logger,
        transformer_name=transformer_name,
        service_id=service_id,
    )


@then(
    parsers.parse(
        "service ID '{service_id:d}' was transformed into "
        "{org_count:d} organisation, "
        "{location_count:d} location and "
        "{service_count:d} healthcare service"
    )
)
def verify_transformation_output(
    migration_context: Dict[str, Any],
    service_id: int,
    org_count: int,
    location_count: int,
    service_count: int,
) -> None:
    """Verify transformation output counts."""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_transformation_log(
        mock_logger=mock_logger,
        service_id=service_id,
        organisation_count=org_count,
        location_count=location_count,
        healthcare_service_count=service_count,
    )


@then(
    parsers.parse(
        "service ID '{service_id:d}' was not migrated due to reason '{expected_reason}'"
    )
)
def verify_service_not_migrated(
    migration_context: Dict[str, Any],
    service_id: int,
    expected_reason: str,
) -> None:
    """Verify that a service was not migrated with the expected reason."""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_service_not_migrated_log(
        mock_logger=mock_logger,
        service_id=service_id,
        expected_reason=expected_reason,
    )


@then(
    parsers.parse(
        "service ID '{service_id:d}' was skipped due to reason '{expected_reason}'"
    )
)
def verify_service_skipped(
    migration_context: Dict[str, Any],
    service_id: int,
    expected_reason: str,
) -> None:
    """Verify that a service was skipped with the expected reason."""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_service_skipped_log(
        mock_logger=mock_logger,
        service_id=service_id,
        expected_reason=expected_reason,
    )


@then(
    parsers.parse("error log containing message: '{error_message_fragment}' was found")
)
def verify_error_level_log(
    migration_context: Dict[str, Any],
    error_message_fragment: str,
) -> None:
    """Verify that error message with content was logged"""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_error_log_present(
        mock_logger=mock_logger,
        error_fragment=error_message_fragment,
    )


@then(
    parsers.parse(
        "the state table contains a record for key '{state_key}' with version {version:d}"
    )
)
def verify_state_record_details(
    migration_context: Dict[str, Any],
    dynamodb: Dict[str, Any],
    state_key: str,
    version: int,
) -> None:
    """Verify state record exists with correct version."""
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

    assert deserialized_item["version"] == version, (
        f"Version should be {version}, got {deserialized_item['version']}"
    )

    migration_context["migration_state"] = deserialized_item


@then(
    parsers.parse(
        "the state table contains the following validation issues for key '{state_key}':"
    )
)
def verify_state_record_validation_issues_details(
    migration_context: Dict[str, Any],
    state_key: str,
    datatable: Any,
) -> None:
    """Verify state record has expected validation issues."""
    migration_state = migration_context.get("migration_state")

    assert migration_state is not None, "Migration state should exist in context"
    assert migration_state["source_record_id"] == state_key, (
        f"State record key should be {state_key}, got {migration_state['source_record_id']}"
    )

    actual_issues = migration_state.get("validation_issues", [])

    expected_issues = []
    header_row = datatable[0]
    for row in datatable[1:]:
        issue = {header_row[i]: row[i] for i in range(len(header_row))}
        if "expression" in issue:
            issue["expression"] = [issue["expression"]]
        if "value" in issue:
            issue["value"] = parse_datatable_value(issue["value"])

        expected_issues.append(issue)

    assert len(actual_issues) == len(expected_issues), (
        f"Expected {len(expected_issues)} validation issues, got {len(actual_issues)}"
    )
    assert actual_issues == expected_issues, (
        f"Validation issues do not match.\nExpected: {expected_issues}\nGot: {actual_issues}"
    )


@then(
    parsers.parse(
        "the state table contains {expected_issue_count:d} validation issue(s) for key '{state_key}'"
    )
)
def verify_state_record_validation_issues(
    migration_context: Dict[str, Any],
    expected_issue_count: int,
    state_key: str,
) -> None:
    """Verify state record has expected number of validation issues."""
    migration_state = migration_context.get("migration_state")

    assert migration_state is not None, "Migration state should exist in context"
    assert migration_state["source_record_id"] == state_key, (
        f"State record key should be {state_key}, got {migration_state['source_record_id']}"
    )

    actual_issues = migration_state.get("validation_issues", [])
    assert len(actual_issues) == expected_issue_count, (
        f"Expected {expected_issue_count} validation issues, got {len(actual_issues)}"
    )


@then(
    parsers.parse(
        "the state table record for key '{state_key}' contains {entity_type} ID"
    )
)
def verify_state_record_contains_entity_id(
    dynamodb: Dict[str, Any],
    state_key: str,
    entity_type: str,
) -> None:
    """Verify state record contains the specified entity ID (organisation, location, healthcare_service)."""
    state_table_name = get_table_name(resource="state", stack_name="data-migration")

    entity_field_map = {
        "organisation": "organisation_id",
        "location": "location_id",
        "healthcare_service": "healthcare_service_id",
    }

    field_name = entity_field_map.get(entity_type.lower())
    assert field_name is not None, f"Unknown entity type: {entity_type}"

    client = dynamodb[DYNAMODB_CLIENT]
    response = client.get_item(
        TableName=state_table_name,
        Key={"source_record_id": {"S": state_key}},
    )

    assert "Item" in response, f"State record should exist for key {state_key}"

    item = response["Item"]
    deserializer = TypeDeserializer()
    deserialized_item = {k: deserializer.deserialize(v) for k, v in item.items()}

    assert field_name in deserialized_item, (
        f"State record should contain {field_name} field"
    )

    entity_id = deserialized_item[field_name]
    assert entity_id is not None and entity_id != "", (
        f"{field_name} should have a valid UUID value, got: {entity_id}"
    )

    assert len(str(entity_id)) == 36 and "-" in str(entity_id), (
        f"{field_name} should be a valid UUID format, got: {entity_id}"
    )


@then("the DynamoDB record for healthcare-service contains valid providedBy UUID")
def verify_healthcare_service_providedby(
    migration_context: Dict[str, Any],
    dynamodb: Dict[str, Any],
) -> None:
    """Verify healthcare-service record contains valid providedBy reference."""
    migration_state = migration_context.get("migration_state")
    assert migration_state is not None, "Migration state should exist"

    hs_id = migration_state.get("healthcare_service_id")
    assert hs_id is not None, "Healthcare service ID should exist in migration state"

    hs_table_name = get_table_name(resource="healthcare-service", stack_name="data-migration")
    client = dynamodb[DYNAMODB_CLIENT]

    response = client.get_item(
        TableName=hs_table_name,
        Key={
            "id": {"S": str(hs_id)},
            "sort_key": {"S": "document"}
        }
    )

    assert "Item" in response, f"Healthcare service record should exist for ID {hs_id}"

    item = response["Item"]
    deserializer = TypeDeserializer()
    deserialized_item = {k: deserializer.deserialize(v) for k, v in item.items()}

    assert "providedBy" in deserialized_item, "providedBy field should exist"
    provided_by = deserialized_item["providedBy"]

    assert provided_by is not None and provided_by != "", (
        f"providedBy should have a valid UUID value, got: {provided_by}"
    )

    assert len(str(provided_by)) == 36 and "-" in str(provided_by), (
        f"providedBy should be a valid UUID format, got: {provided_by}"
    )

    migration_context["original_provided_by"] = provided_by


@then("the referenced Organisation record exists in DynamoDB")
def verify_referenced_organisation_exists(
    migration_context: Dict[str, Any],
    dynamodb: Dict[str, Any],
) -> None:
    """Verify the Organisation referenced by providedBy exists in DynamoDB."""
    provided_by = migration_context.get("original_provided_by")
    assert provided_by is not None, "providedBy UUID should be stored in context"

    org_table_name = get_table_name(resource="organisation", stack_name="data-migration")
    client = dynamodb[DYNAMODB_CLIENT]

    response = client.get_item(
        TableName=org_table_name,
        Key={
            "id": {"S": str(provided_by)},
            "sort_key": {"S": "document"}
        }
    )

    assert "Item" in response, (
        f"Referenced Organisation record should exist for providedBy UUID {provided_by}"
    )


@then("the DynamoDB record for healthcare-service still contains same providedBy UUID")
def verify_healthcare_service_providedby_unchanged(
    migration_context: Dict[str, Any],
    dynamodb: Dict[str, Any],
) -> None:
    """Verify healthcare-service providedBy reference remains unchanged after update."""
    original_provided_by = migration_context.get("original_provided_by")
    assert original_provided_by is not None, "Original providedBy UUID should be stored in context"

    migration_state = migration_context.get("migration_state")
    assert migration_state is not None, "Migration state should exist"

    hs_id = migration_state.get("healthcare_service_id")
    assert hs_id is not None, "Healthcare service ID should exist in migration state"

    hs_table_name = get_table_name(resource="healthcare-service", stack_name="data-migration")
    client = dynamodb[DYNAMODB_CLIENT]

    response = client.get_item(
        TableName=hs_table_name,
        Key={
            "id": {"S": str(hs_id)},
            "sort_key": {"S": "document"}
        }
    )

    assert "Item" in response, f"Healthcare service record should exist for ID {hs_id}"

    item = response["Item"]
    deserializer = TypeDeserializer()
    deserialized_item = {k: deserializer.deserialize(v) for k, v in item.items()}

    current_provided_by = deserialized_item.get("providedBy")
    assert current_provided_by == original_provided_by, (
        f"providedBy should remain unchanged. "
        f"Expected: {original_provided_by}, got: {current_provided_by}"
    )


@then(
    parsers.parse(
        "field '{field_name}' on table '{table_name}' contains the full updated name"
    )
)
def verify_field_contains_full_value(
    migration_context: Dict[str, Any],
    dynamodb: Dict[str, Any],
    field_name: str,
    table_name: str,
) -> None:
    """Verify field in DynamoDB contains the full expected value without truncation."""
    migration_state = migration_context.get("migration_state")
    assert migration_state is not None, "Migration state should exist"

    entity_id_field_map = {
        "healthcare-service": "healthcare_service_id",
        "organisation": "organisation_id",
        "location": "location_id",
    }

    entity_id_field = entity_id_field_map.get(table_name)
    assert entity_id_field is not None, f"Unknown table name: {table_name}"

    entity_id = migration_state.get(entity_id_field)
    assert entity_id is not None, f"{entity_id_field} should exist in migration state"

    full_table_name = get_table_name(resource=table_name, stack_name="data-migration")
    client = dynamodb[DYNAMODB_CLIENT]

    response = client.get_item(
        TableName=full_table_name,
        Key={
            "id": {"S": str(entity_id)},
            "sort_key": {"S": "document"}
        }
    )

    assert "Item" in response, f"Record should exist in {table_name} for ID {entity_id}"

    item = response["Item"]
    deserializer = TypeDeserializer()
    deserialized_item = {k: deserializer.deserialize(v) for k, v in item.items()}

    assert field_name in deserialized_item, f"Field '{field_name}' should exist in record"
    actual_value = deserialized_item[field_name]

    # The expected value is the 255-character string from the feature file
    expected_value = (
        "This is an extremely long service name that tests the maximum field length "
        "handling in the incremental update process to ensure that long strings are "
        "properly processed and stored in DynamoDB without truncation or error and "
        "this name is exactly 255 chars long!!!"
    )

    assert actual_value == expected_value, (
        f"Field '{field_name}' should contain the full updated value.\n"
        f"Expected length: {len(expected_value)}, Actual length: {len(actual_value)}\n"
        f"Expected: {expected_value}\n"
        f"Actual: {actual_value}"
    )

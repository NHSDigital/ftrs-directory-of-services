"""BDD steps for verifying migration state in DynamoDB."""

import json
from typing import Any, Dict

import pytest
from boto3.dynamodb.types import TypeDeserializer
from deepdiff import DeepDiff
from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from pytest_bdd import parsers, then

from step_definitions.data_migration_steps.dos_data_manipulation_steps import (
    parse_datatable_value,
)
from step_definitions.data_migration_steps.dynamodb_utils import get_by_id_and_sort_key
from utilities.common.data_migration.migration_context_helper import (
    get_migration_type_description,
)
from utilities.common.dynamoDB_tables import get_table_name
from utilities.common.log_helper import get_mock_logger_from_context


def _get_migration_state(
    dynamodb: Dict[str, Any],
    service_id: str,
) -> Dict[str, Any] | None:
    """Retrieve migration state for a service from DynamoDB."""
    deserialiser = TypeDeserializer()

    table_name = get_table_name("state-table", stack_name="data-migration")
    result = dynamodb["client"].get_item(
        TableName=table_name,
        Key={"source_record_id": {"S": f"services#{service_id}"}},
    )

    if not result.get("Item"):
        return None

    deserialised_item = {
        k: deserialiser.deserialize(v) for k, v in result["Item"].items()
    }
    return deserialised_item


@then(
    parsers.parse(
        "the migration state of service ID '{service_id}' is version {version:d}"
    )
)
def verify_migration_state_version(
    migration_context: Dict[str, Any],
    dynamodb: Dict[str, Any],
    service_id: str,
    version: int,
) -> None:
    """Verify that the migration state version for a service matches expected."""
    if (
        not migration_context.get("state")
        or service_id not in migration_context["state"]["source_record_id"]
    ):
        migration_context["state"] = _get_migration_state(dynamodb, service_id)

    assert migration_context.get("state") is not None, (
        f"No migration state found for service ID '{service_id}'"
    )

    actual_version = migration_context["state"].get("version")
    assert actual_version == version, (
        f"Expected migration state version {version} for service ID '{service_id}', "
        f"but found {actual_version}"
    )


@then(
    parsers.parse(
        "the migration state of service ID '{service_id}' contains {issue_count:d} validation issues"
    )
)
def verify_migration_state_validation_issues(
    migration_context: Dict[str, Any],
    dynamodb: Dict[str, Any],
    service_id: str,
    issue_count: int,
) -> None:
    """Verify that the migration state validation issues count matches expected."""
    if (
        not migration_context.get("state")
        or service_id not in migration_context["state"]["source_record_id"]
    ):
        migration_context["state"] = _get_migration_state(dynamodb, service_id)

    assert migration_context.get("state") is not None, (
        f"No migration state found for service ID '{service_id}'"
    )

    validation_issues = migration_context["state"].get("validation_issues", [])
    actual_issue_count = len(validation_issues)
    assert actual_issue_count == issue_count, (
        f"Expected {issue_count} validation issues for service ID '{service_id}', "
        f"but found {actual_issue_count}\nValidation Issues: {json.dumps(validation_issues, indent=2)}"
    )


@then(
    parsers.parse(
        "the migration state of service ID '{service_id}' has the following validation issues:"
    )
)
def verify_migration_state_validation_issues_content(
    migration_context: Dict[str, Any],
    dynamodb: Dict[str, Any],
    service_id: str,
    datatable: list[list[str]],
) -> None:
    """Verify that the migration state validation issues match expected content."""
    if (
        not migration_context.get("state")
        or service_id not in migration_context["state"]["source_record_id"]
    ):
        migration_context["state"] = _get_migration_state(dynamodb, service_id)

    assert migration_context.get("state") is not None, (
        f"No migration state found for service ID '{service_id}'"
    )

    validation_issues = migration_context["state"].get("validation_issues", [])

    first_row = next(iter(datatable), None)
    if not first_row or set(first_row) != {
        "expression",
        "severity",
        "code",
        "diagnostics",
        "value",
    }:
        pytest.fail(
            "Validation issues table must have columns in order: "
            "'expression', 'severity', 'code', 'diagnostics', 'value'"
        )

    # Turn datatable into list of dicts
    expected_issues = []
    for row in datatable[1:]:
        expected_issues.append(
            {
                "expression": [row[0]],
                "severity": row[1],
                "code": row[2],
                "diagnostics": row[3],
                "value": parse_datatable_value(row[4]),
            }
        )

    diff = DeepDiff(
        expected_issues,
        validation_issues,
        ignore_order=True,
    )
    assert not diff, (
        f"Validation issues for service ID '{service_id}' do not match expected.\nDiff: {diff}"
    )


@then(
    parsers.parse(
        "the migration state of service ID '{service_id}' contains a '{entity_type}' with ID '{entity_id}'"
    )
)
def verify_migration_state_location_content(
    migration_context: Dict[str, Any],
    dynamodb: Dict[str, Any],
    service_id: str,
    entity_type: str,
    entity_id: str,
) -> None:
    """Verify that the migration state contains entity with expected ID."""
    if (
        not migration_context.get("state")
        or service_id not in migration_context["state"]["source_record_id"]
    ):
        migration_context["state"] = _get_migration_state(dynamodb, service_id)

    state = migration_context.get("state")

    assert state is not None, f"No migration state found for service ID '{service_id}'"

    entity = state.get(entity_type, None)
    assert entity is not None, (
        f"No {entity_type} found in migration state for service ID '{service_id}'"
    )

    actual_entity_id = entity.get("id", None)
    assert actual_entity_id == entity_id, (
        f"Expected {entity_type} ID '{entity_id}' in migration state for service ID '{service_id}', "
        f"but found '{actual_entity_id}'"
    )

    assert state.get(f"{entity_type}_id") == entity_id, (
        f"Expected {entity_type}_id '{entity_id}' in migration state for service ID '{service_id}', "
        f"but found '{state.get(f'{entity_type}_id')}'"
    )


@then(
    parsers.parse(
        "the migration state of service ID '{service_id}' matches the stored records"
    )
)
def verify_migration_state_matches_expected(
    migration_context: Dict[str, Any],
    dynamodb: Dict[str, Any],
    service_id: str,
) -> None:
    """Verify that the migration state matches the expected state."""
    if (
        not migration_context.get("state")
        or service_id not in migration_context["state"]["source_record_id"]
    ):
        migration_context["state"] = _get_migration_state(dynamodb, service_id)

    actual_state = migration_context.get("state")
    assert actual_state is not None, (
        f"No migration state found for service ID '{service_id}'"
    )

    if org := actual_state.get("organisation"):
        state_organisation = Organisation.model_validate(org)
        retrieved_item = Organisation.model_validate(
            get_by_id_and_sort_key(
                dynamodb,
                "organisation",
                str(state_organisation.id),
            ),
        )
        assert retrieved_item.model_dump() == state_organisation.model_dump(), (
            f"Organisation data does not match state for service ID '{service_id}'"
        )

    if loc := actual_state.get("location"):
        state_location = Location.model_validate(loc)
        retrieved_item = Location.model_validate(
            get_by_id_and_sort_key(
                dynamodb,
                "location",
                str(state_location.id),
            ),
        )
        assert retrieved_item.model_dump() == state_location.model_dump(), (
            f"Location data does not match state for service ID '{service_id}'"
        )

    if hs := actual_state.get("healthcare_service"):
        state_healthcare_service = HealthcareService.model_validate(hs)
        retrieved_item = HealthcareService.model_validate(
            get_by_id_and_sort_key(
                dynamodb,
                "healthcare-service",
                str(state_healthcare_service.id),
            ),
        )
        assert retrieved_item.model_dump() == state_healthcare_service.model_dump(), (
            f"HealthcareService data does not match state for service ID '{service_id}'"
        )


@then(
    parsers.parse(
        "the validated source record has the following changes before migration for service ID '{service_id}':"
    )
)
def verify_validated_source_record_changes(
    migration_context: Dict[str, Any],
    dynamodb: Dict[str, Any],
    service_id: str,
    datatable: list[list[str]],
) -> None:
    """Verify that the validated source record has expected changes."""
    mock_logger = get_mock_logger_from_context(migration_context)

    assert mock_logger.was_logged("SM_VAL_003"), (
        f"No validated source record changes found for service ID '{service_id}'"
    )

    expected_changes = [row[0] for row in datatable[1:]]  # Skip header row

    actual_change_logs = mock_logger.get_log("SM_VAL_003")
    assert len(actual_change_logs) == 1, (
        f"Expected one validated source record changes log for service ID '{service_id}', "
        f"but found {len(actual_change_logs)}"
    )

    actual_changes = actual_change_logs[0]["detail"].get("changes", [])
    diff = DeepDiff(
        expected_changes,
        actual_changes,
        ignore_order=True,
    )
    assert not diff, (
        f"Validated source record changes for service ID '{service_id}' do not match expected.\nDiff: {diff}"
    )

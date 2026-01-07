"""BDD steps for verifying entity (Organisation, Location, HealthcareService) operations."""

from typing import Any, Dict

from common.uuid_utils import generate_uuid
from deepdiff import DeepDiff
from pytest_bdd import parsers, then

from utilities.common.dynamoDB_tables import get_table_name
from utilities.common.log_helper import get_mock_logger_from_context


@then(parsers.parse("no organisation was created for service '{service_id:d}'"))
def verify_no_organisation_created(
    service_id: int,
    dynamodb: Dict[str, Any],
) -> None:
    """Verify that no organisation was created for the given service."""
    organisation_uuid = str(generate_uuid(service_id, "organisation"))

    dynamodb_resource = dynamodb["resource"]
    org_table = dynamodb_resource.Table(get_table_name("organisation"))

    response = org_table.get_item(Key={"id": organisation_uuid, "field": "document"})
    assert "Item" not in response, (
        f"Organisation with id {organisation_uuid} should not exist for service {service_id}"
    )


@then(parsers.parse("no location was created for service '{service_id:d}'"))
def verify_no_location_created(
    service_id: int,
    dynamodb: Dict[str, Any],
) -> None:
    """Verify that no location was created for the given service."""
    location_uuid = str(generate_uuid(service_id, "location"))

    dynamodb_resource = dynamodb["resource"]
    location_table = dynamodb_resource.Table(get_table_name("location"))

    response = location_table.get_item(Key={"id": location_uuid, "field": "document"})
    assert "Item" not in response, (
        f"Location with id {location_uuid} should not exist for service {service_id}"
    )


@then(parsers.parse("no healthcare service was created for service '{service_id:d}'"))
def verify_no_healthcare_service_created(
    service_id: int,
    dynamodb: Dict[str, Any],
) -> None:
    """Verify that no healthcare service was created for the given service."""
    healthcare_service_uuid = str(generate_uuid(service_id, "healthcare_service"))

    dynamodb_resource = dynamodb["resource"]
    service_table = dynamodb_resource.Table(get_table_name("healthcare-service"))

    response = service_table.get_item(
        Key={"id": healthcare_service_uuid, "field": "document"}
    )
    assert "Item" not in response, (
        f"Healthcare service with id {healthcare_service_uuid} should not exist for service {service_id}"
    )


@then("there is no Organisation update")
def verify_no_organisation_update(migration_context: Dict[str, Any]) -> None:
    """Verify that no organisation updates were made in the migration."""
    mock_logger = get_mock_logger_from_context(migration_context)

    assert mock_logger.was_logged("SM_PROC_017") is True, (
        "Expected organisation update log 'SM_PROC_017' not found"
    )

    assert mock_logger.was_logged("SM_PROC_018") is False, (
        "Unexpected organisation update log 'SM_PROC_018' found"
    )


@then("there is no Location update")
def verify_no_location_update(migration_context: Dict[str, Any]) -> None:
    """Verify that no location updates were made in the migration."""
    mock_logger = get_mock_logger_from_context(migration_context)

    assert mock_logger.was_logged("SM_PROC_019") is True, (
        "Expected location update log 'SM_PROC_019' not found"
    )

    assert mock_logger.was_logged("SM_PROC_020") is False, (
        "Unexpected location update log 'SM_PROC_020' found"
    )


@then("there is no Healthcare Service update")
def verify_no_healthcare_service_update(migration_context: Dict[str, Any]) -> None:
    """Verify that no healthcare service updates were made in the migration."""
    mock_logger = get_mock_logger_from_context(migration_context)

    assert mock_logger.was_logged("SM_PROC_021") is True, (
        "Expected healthcare service update log 'SM_PROC_021' not found"
    )

    assert mock_logger.was_logged("SM_PROC_022") is False, (
        "Unexpected healthcare service update log 'SM_PROC_022' found"
    )


@then("there is an Organisation update with changes:")
def verify_organisation_update_with_changes(
    migration_context: Dict[str, Any],
    datatable: list[list[str]],
) -> None:
    """Verify that organisation updates were made with expected changes."""
    mock_logger = get_mock_logger_from_context(migration_context)

    assert mock_logger.was_logged("SM_PROC_018") is True, (
        f"Expected organisation update log 'SM_PROC_018' not found\nLogs:\n{mock_logger.format_logs_for_print()}"
    )

    expected_changes = [row[0] for row in datatable[1:]]  # Skip header row

    actual_change_logs = mock_logger.get_log("SM_PROC_018")
    assert len(actual_change_logs) == 1, (
        f"Expected one organisation update log 'SM_PROC_018', "
        f"but found {len(actual_change_logs)}"
    )

    actual_changes = actual_change_logs[0]["detail"].get("changes", [])
    diff = DeepDiff(
        expected_changes,
        actual_changes,
        ignore_order=True,
    )
    assert not diff, f"Organisation update changes do not match expected.\nDiff: {diff}"


@then("there is a Location update with changes:")
def verify_location_update_with_changes(
    migration_context: Dict[str, Any],
    datatable: list[list[str]],
) -> None:
    """Verify that location updates were made with expected changes."""
    mock_logger = get_mock_logger_from_context(migration_context)

    assert mock_logger.was_logged("SM_PROC_020") is True, (
        "Expected location update log 'SM_PROC_020' not found"
    )

    expected_changes = [row[0] for row in datatable[1:]]  # Skip header row

    actual_change_logs = mock_logger.get_log("SM_PROC_020")
    assert len(actual_change_logs) == 1, (
        f"Expected one location update log 'SM_PROC_020', "
        f"but found {len(actual_change_logs)}"
    )

    actual_changes = actual_change_logs[0]["detail"].get("changes", [])
    diff = DeepDiff(
        expected_changes,
        actual_changes,
        ignore_order=True,
    )
    assert not diff, f"Location update changes do not match expected.\nDiff: {diff}"


@then("there is a Healthcare Service update with changes:")
def verify_healthcare_service_update_with_changes(
    migration_context: Dict[str, Any],
    datatable: list[list[str]],
) -> None:
    """Verify that healthcare service updates were made with expected changes."""
    mock_logger = get_mock_logger_from_context(migration_context)

    assert mock_logger.was_logged("SM_PROC_022") is True, (
        "Expected healthcare service update log 'SM_PROC_022' not found"
    )

    expected_changes = [row[0] for row in datatable[1:]]  # Skip header row

    actual_change_logs = mock_logger.get_log("SM_PROC_022")
    assert len(actual_change_logs) == 1, (
        f"Expected one healthcare service update log 'SM_PROC_022', "
        f"but found {len(actual_change_logs)}"
    )

    actual_changes = actual_change_logs[0]["detail"].get("changes", [])
    diff = DeepDiff(
        expected_changes,
        actual_changes,
        ignore_order=True,
    )
    assert not diff, (
        f"Healthcare service update changes do not match expected.\nDiff: {diff}"
    )


@then(parsers.parse("the organisation for service ID '{service_id}' has:"))
def verify_organisation_has_fields(
    service_id: str,
    datatable: list[list[str]],
    dynamodb: Dict[str, Any],
) -> None:
    """Verify that organisation for service has expected field values."""
    organisation_uuid = str(generate_uuid(service_id, "organisation"))

    dynamodb_resource = dynamodb["resource"]
    org_table = dynamodb_resource.Table(get_table_name("organisation"))

    response = org_table.get_item(Key={"id": organisation_uuid, "field": "document"})
    assert "Item" in response, (
        f"Organisation with id {organisation_uuid} not found for service {service_id}"
    )

    item = response["Item"]

    # Skip header row and verify each field
    for row in datatable[1:]:
        field_name = row[0]
        expected_value = row[1]

        assert field_name in item, (
            f"Field '{field_name}' not found in organisation for service {service_id}"
        )

        actual_value = item[field_name]

        # Handle boolean string comparisons
        if expected_value.lower() in ("true", "false"):
            expected_value = expected_value.lower() == "true"

        assert actual_value == expected_value, (
            f"Field '{field_name}' mismatch: expected '{expected_value}', got '{actual_value}'"
        )


@then(parsers.parse("the organisation for service ID '{service_id}' has telecom:"))
def verify_organisation_has_telecom(
    service_id: str,
    datatable: list[list[str]],
    dynamodb: Dict[str, Any],
) -> None:
    """Verify that organisation telecom has expected field values."""
    organisation_uuid = str(generate_uuid(service_id, "organisation"))

    dynamodb_resource = dynamodb["resource"]
    org_table = dynamodb_resource.Table(get_table_name("organisation"))

    response = org_table.get_item(Key={"id": organisation_uuid, "field": "document"})
    assert "Item" in response, (
        f"Organisation with id {organisation_uuid} not found for service {service_id}"
    )

    item = response["Item"]
    assert "telecom" in item, (
        f"Telecom not found in organisation for service {service_id}"
    )

    telecom = item["telecom"]

    # Skip header row and verify each telecom field
    for row in datatable[1:]:
        field_name = row[0]
        expected_value = row[1]

        assert field_name in telecom, (
            f"Telecom field '{field_name}' not found in organisation for service {service_id}"
        )

        actual_value = telecom[field_name]
        assert actual_value == expected_value, (
            f"Telecom field '{field_name}' mismatch: expected '{expected_value}', got '{actual_value}'"
        )


@then(
    parsers.parse(
        "the organisation for service ID '{service_id}' has {endpoint_count:d} endpoint with:"
    )
)
def verify_organisation_has_endpoints(
    service_id: str,
    endpoint_count: int,
    datatable: list[list[str]],
    dynamodb: Dict[str, Any],
) -> None:
    """Verify that organisation has expected number of endpoints with field values."""
    organisation_uuid = str(generate_uuid(service_id, "organisation"))

    dynamodb_resource = dynamodb["resource"]
    org_table = dynamodb_resource.Table(get_table_name("organisation"))

    response = org_table.get_item(Key={"id": organisation_uuid, "field": "document"})
    assert "Item" in response, (
        f"Organisation with id {organisation_uuid} not found for service {service_id}"
    )

    item = response["Item"]
    assert "endpoints" in item, (
        f"Endpoints not found in organisation for service {service_id}"
    )

    endpoints = item["endpoints"]
    assert len(endpoints) == endpoint_count, (
        f"Expected {endpoint_count} endpoints, found {len(endpoints)}"
    )

    # Verify the first endpoint fields (skip header row)
    if endpoint_count > 0:
        endpoint = endpoints[0]
        for row in datatable[1:]:
            field_name = row[0]
            expected_value = row[1]

            assert field_name in endpoint, (
                f"Endpoint field '{field_name}' not found for service {service_id}"
            )

            actual_value = endpoint[field_name]

            # Handle integer conversions
            if field_name == "order":
                expected_value = int(expected_value)

            assert actual_value == expected_value, (
                f"Endpoint field '{field_name}' mismatch: expected '{expected_value}', got '{actual_value}'"
            )


@then(
    parsers.parse(
        "the '{table_name}' for service ID '{service_id}' contains age eligibility criteria:"
    )
)
def verify_age_eligibility_criteria(
    table_name: str,
    service_id: str,
    datatable: list[list[str]],
    dynamodb: Dict[str, Any],
) -> None:
    """Verify that healthcare service contains expected age eligibility criteria."""
    namespace = table_name.replace("-", "_")
    service_uuid = str(generate_uuid(service_id, namespace))

    dynamodb_resource = dynamodb["resource"]
    service_table = dynamodb_resource.Table(get_table_name(table_name))

    response = service_table.get_item(Key={"id": service_uuid, "field": "document"})
    assert "Item" in response, (
        f"Healthcare service with id {service_uuid} not found for service {service_id}"
    )

    item = response["Item"]
    assert "ageEligibilityCriteria" in item, (
        f"Age eligibility criteria not found in healthcare service for service {service_id}"
    )

    age_criteria = item["ageEligibilityCriteria"]

    # Build expected criteria from datatable (skip header row)
    expected_criteria = []
    for row in datatable[1:]:
        expected_criteria.append(
            {
                "rangeFrom": row[0],
                "rangeTo": row[1],
                "type": row[2],
            }
        )

    assert len(age_criteria) == len(expected_criteria), (
        f"Expected {len(expected_criteria)} age eligibility criteria, found {len(age_criteria)}"
    )

    # Compare each criterion
    for expected, actual in zip(expected_criteria, age_criteria):
        diff = DeepDiff(expected, actual, ignore_order=True)
        assert not diff, (
            f"Age eligibility criteria mismatch.\nExpected: {expected}\nActual: {actual}\nDiff: {diff}"
        )

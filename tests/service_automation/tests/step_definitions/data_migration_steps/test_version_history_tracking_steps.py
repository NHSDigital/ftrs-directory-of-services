"""
Step definitions for version history tracking tests.

NOTE: Tests Lambda handler logic directly, NOT AWS Streams → Lambda integration.
"""

from datetime import datetime
from typing import Any, Dict

import boto3
import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps.data_migration_steps import *  # noqa: F403
from utilities.common.dynamodb_helper import (
    get_dynamodb_table,
    get_nested_value,
)
from utilities.common.dynamoDB_tables import get_table_name
from utilities.common.gherkin_helper import parse_gherkin_table, unescape_pipe_in_value
from utilities.data_migration.version_history import (
    verify_version_history_timestamp,
)
from utilities.data_migration.version_history_helper import VersionHistoryHelper

# Load all scenarios from the feature file
scenarios(
    "../../tests/features/data_migration_features/version_history_tracking.feature"
)


@given("the version history table exists")
def verify_version_history_table_exists(dynamodb: Dict[str, Any]) -> None:
    """Verify that the version history table exists."""
    # Check if table exists
    try:
        version_history_table = get_dynamodb_table(dynamodb, "version-history")
        version_history_table.load()
    except Exception as e:
        pytest.fail(f"Version history table does not exist: {e}")


@given("an Organisation document exists in DynamoDB with")
def create_organisation_document(
    dynamodb: Dict[str, Any],
    migration_context: Dict[str, Any],
    datatable,
) -> None:
    """Create an Organisation document in DynamoDB."""
    _create_entity_document(dynamodb, "organisation", datatable, migration_context)


@given("a Location document exists in DynamoDB with")
def create_location_document(
    dynamodb: Dict[str, Any],
    migration_context: Dict[str, Any],
    datatable,
) -> None:
    """Create a Location document in DynamoDB."""
    _create_entity_document(dynamodb, "location", datatable, migration_context)


@given("a HealthcareService document exists in DynamoDB with")
def create_healthcare_service_document(
    dynamodb: Dict[str, Any],
    migration_context: Dict[str, Any],
    datatable,
) -> None:
    """Create a HealthcareService document in DynamoDB."""
    _create_entity_document(
        dynamodb, "healthcare-service", datatable, migration_context
    )


def _create_entity_document(
    dynamodb: Dict[str, Any],
    entity_type: str,
    table_data: list,  # List of lists from pytest-bdd
    migration_context: Dict[str, Any],
) -> None:
    """Helper to create entity document from table data."""
    # Parse Gherkin table into dictionary using reusable utility
    data = parse_gherkin_table(table_data)

    # Extract id and create document with all other fields
    entity_id = data.pop("id", None)
    if not entity_id:
        raise ValueError("Entity id is required")

    # Store entity_id and document data in context
    migration_context["entity_id"] = entity_id
    migration_context["entity_type"] = entity_type
    migration_context["document_data"] = data.copy()

    # Create the document record in DynamoDB
    table = get_dynamodb_table(dynamodb, entity_type)

    item = {
        "id": entity_id,
        "field": "document",
        **data,
    }
    table.put_item(Item=item)


@when("the Organisation document is updated with changes")
def update_organisation_document(
    dynamodb: Dict[str, Any],
    migration_context: Dict[str, Any],
    datatable,
) -> None:
    """Update an Organisation document."""
    _update_entity_document_with_history(
        dynamodb, "organisation", datatable, migration_context
    )


@when("the Location document is updated with changes")
def update_location_document(
    dynamodb: Dict[str, Any],
    migration_context: Dict[str, Any],
    datatable,
) -> None:
    """Update a Location document."""
    _update_entity_document_with_history(
        dynamodb, "location", datatable, migration_context
    )


@when("the HealthcareService document is updated with changes")
def update_healthcare_service_document(
    dynamodb: Dict[str, Any],
    migration_context: Dict[str, Any],
    datatable,
) -> None:
    """Update a HealthcareService document."""
    _update_entity_document_with_history(
        dynamodb, "healthcare-service", datatable, migration_context
    )


def _update_entity_document_with_history(
    dynamodb: Dict[str, Any],
    entity_type: str,
    table_data: list,
    migration_context: Dict[str, Any],
) -> None:
    """Helper to update entity document and trigger version history processing."""
    entity_id = migration_context["entity_id"]
    old_document = migration_context.get("document_data", {}).copy()

    # Parse the changes from the table
    changes = parse_gherkin_table(table_data)

    # Apply changes to create new document
    new_document = old_document.copy()
    new_document.update(changes)

    # Update the record in DynamoDB
    table = get_dynamodb_table(dynamodb, entity_type)
    table.update_item(
        Key={"id": entity_id, "field": "document"},
        UpdateExpression="SET " + ", ".join([f"#{k} = :{k}" for k in changes.keys()]),
        ExpressionAttributeNames={f"#{k}": k for k in changes.keys()},
        ExpressionAttributeValues={f":{k}": v for k, v in changes.items()},
    )

    # Manually invoke handler (not testing Streams → Lambda integration)
    version_history_helper = VersionHistoryHelper(
        dynamodb_endpoint=dynamodb.get("endpoint_url")
    )

    table_name = get_table_name(entity_type)

    version_history_helper.process_document_update_as_stream_event(
        table_name=table_name,
        entity_id=entity_id,
        old_document=old_document,
        new_document=new_document,
        last_updated_by={
            "type": "app",
            "value": "INTERNAL001",
            "display": "Data Migration",
        },
    )

    # Update context with new document for subsequent updates
    migration_context["document_data"] = new_document


@then("a version history record should exist with")
def verify_version_history_record_exists(
    dynamodb: Dict[str, Any],
    migration_context: Dict[str, Any],
    datatable,
) -> None:
    """Verify that a version history record exists with expected attributes."""
    version_history_table = get_dynamodb_table(dynamodb, "version-history")

    # Parse Gherkin table into dictionary using reusable utility
    data = parse_gherkin_table(datatable)

    # Unescape pipe characters in entity_id
    entity_id = unescape_pipe_in_value(data.get("entity_id", ""))

    # Query for version history records
    response = version_history_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("entity_id").eq(entity_id),
        ScanIndexForward=False,  # Latest first
        Limit=1,
    )

    assert response["Items"], (
        f"No version history record found for entity_id: {entity_id}"
    )

    # Store for later assertions
    migration_context["version_record"] = response["Items"][0]

    # Verify change_type
    if "change_type" in data:
        assert response["Items"][0]["change_type"] == data["change_type"]


@then(parsers.parse('the version history "{path}" should be "{expected_value}"'))
def verify_version_history_field(
    migration_context: Dict[str, Any],
    path: str,
    expected_value: str,
) -> None:
    """Verify a specific field in the version history record."""
    version_record = migration_context.get("version_record")
    assert version_record, "No version history record in context"

    # Use shared helper to navigate nested path
    value = get_nested_value(version_record, path)

    # Convert to string for comparison
    assert str(value) == expected_value, (
        f"Expected {path} to be '{expected_value}', got '{value}'"
    )


@then(
    parsers.parse(
        'no version history record should be created for entity "{entity_id}"'
    )
)
def verify_no_version_history_record(
    dynamodb: Dict[str, Any],
    migration_context: Dict[str, Any],
    entity_id: str,
) -> None:
    """Verify that no new version history record was created."""
    version_history_table = get_dynamodb_table(dynamodb, "version-history")

    # Query for recent version history records
    response = version_history_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("entity_id").eq(entity_id),
        ScanIndexForward=False,  # Latest first
        Limit=1,
    )

    # If records exist, verify they're not recent (> 5 seconds old)
    if response["Items"]:
        latest_record = response["Items"][0]
        record_timestamp = datetime.fromisoformat(latest_record["timestamp"])
        now = datetime.now(record_timestamp.tzinfo)
        time_diff = (now - record_timestamp).total_seconds()

        assert time_diff > 5, (
            f"Recent version history record found (age: {time_diff}s), "
            f"expected no new records for identical values"
        )


@then("the version history record should have a valid timestamp")
def verify_version_history_timestamp_step(
    migration_context: Dict[str, Any],
) -> None:
    version_record = migration_context.get("version_record")
    assert version_record, "No version history record in context"

    verify_version_history_timestamp(version_record, max_age_seconds=10)

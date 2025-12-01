"""BDD steps for manipulating DoS source database data."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Type

import pytest
from pytest_bdd import given, when, then, parsers, scenarios
from sqlalchemy.orm import Session
from sqlmodel import select

from ftrs_data_layer.domain import legacy as legacy_model
from utilities.common.legacy_dos_rds_tables import TABLE_TO_ENTITY
from utilities.common.constants import STRING_FIELDS


def parse_datatable_value(value: str) -> Any:
    """
    Parse datatable values into appropriate Python types.

    Handles:
    - Boolean: "true", "false" (case-insensitive)
    - None: "null", "none", "" (case-insensitive or empty)
    - Datetime: ISO format strings with time
    - Strings: everything else (let Pydantic handle numeric conversion)

    Args:
        value: String value from datatable

    Returns:
        Parsed value in appropriate Python type
    """
    if not value or value.lower() in ("null", "none"):
        return None

    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    # Try to parse as datetime (for timestamp fields)
    if " " in value or "T" in value:
        try:
            return datetime.fromisoformat(value.replace(" ", "T"))
        except (ValueError, AttributeError):
            pass

    # Return as string and let Pydantic handle type conversion
    return value


def get_entity_class(entity_name: str) -> Type[legacy_model.LegacyDoSModel]:
    """
    Get and validate the legacy model class.

    Args:
        entity_name: Name of the legacy model class

    Returns:
        The legacy model class

    Raises:
        AssertionError: If entity class not found or invalid
    """
    entity_cls = getattr(legacy_model, entity_name, None)

    assert entity_cls is not None, f"Legacy data model not found: {entity_name}"
    assert issubclass(
        entity_cls, legacy_model.LegacyDoSModel
    ), f"{entity_name} does not inherit from LegacyDoSModel"

    return entity_cls


def normalize_value_for_comparison(
    actual_value: Any,
    expected_value: Any,
    field_name: str
) -> tuple[Any, Any]:
    """
    Normalize two values for comparison.

    Handles type conversions for:
    - Decimal to int (if whole number)
    - Datetime timezone normalization
    - Type coercion for non-string fields

    Args:
        actual_value: Value from database
        expected_value: Expected value from test
        field_name: Name of field being compared

    Returns:
        Tuple of (normalized_actual, normalized_expected)
    """
    # Convert Decimal to int if it's a whole number
    if isinstance(actual_value, Decimal) and actual_value == actual_value.to_integral_value():
        actual_value = int(actual_value)

    # Normalize datetime comparisons (remove timezone info)
    if isinstance(actual_value, datetime) and isinstance(expected_value, datetime):
        if actual_value.tzinfo is not None:
            actual_value = actual_value.replace(tzinfo=None)
        if expected_value.tzinfo is not None:
            expected_value = expected_value.replace(tzinfo=None)
        return actual_value, expected_value

    # Don't convert string fields
    if field_name in STRING_FIELDS:
        return actual_value, expected_value

    # Type coercion for other fields
    if isinstance(actual_value, int) and isinstance(expected_value, str):
        try:
            expected_value = int(expected_value)
        except ValueError:
            pass
    elif isinstance(actual_value, bool) and isinstance(expected_value, str):
        expected_value = expected_value.lower() == "true"
    elif isinstance(actual_value, datetime) and isinstance(expected_value, str):
        try:
            expected_value = datetime.fromisoformat(expected_value.replace(" ", "T"))
            if expected_value.tzinfo is not None:
                expected_value = expected_value.replace(tzinfo=None)
        except ValueError:
            pass

    return actual_value, expected_value


def validate_datatable(datatable: list[list[str]] | None, step_description: str) -> None:
    """
    Validate that datatable is present and has data.

    Args:
        datatable: pytest-bdd datatable
        step_description: Description of the step for error messages

    Raises:
        AssertionError: If datatable is invalid
    """
    assert datatable is not None, f"Datatable is required for {step_description}"
    assert len(datatable) > 1, f"Datatable must contain at least one row of data for {step_description}"


def create_model_data_from_datatable(
    entity_cls: Type[legacy_model.LegacyDoSModel],
    datatable: list[list[str]],
    entity_name: str
) -> dict[str, Any]:
    """
    Create model data dictionary from datatable.

    Args:
        entity_cls: The legacy model class
        datatable: pytest-bdd datatable with entity attributes
        entity_name: Name of the entity (for error messages)

    Returns:
        Dictionary with model data

    Raises:
        pytest.fail: If invalid attributes provided
    """
    # Initialize with all fields set to None
    model_data = {key: None for key in entity_cls.model_fields.keys()}

    # Override with values from datatable (skip header row)
    for row in datatable[1:]:
        key = row[0]
        value = parse_datatable_value(row[1])

        if key not in model_data:
            valid_fields = ", ".join(sorted(model_data.keys()))
            pytest.fail(
                f"Invalid attribute '{key}' for entity type '{entity_name}'.\n"
                f"Valid attributes: {valid_fields}"
            )

        model_data[key] = value

    return model_data


@given(
    parsers.parse('a "{entity_name}" exists in DoS with attributes'),
    target_fixture="dos_entity",
)
def dos_data_insert_step(
    migration_context: dict,
    dos_db_with_migration: Session,
    datatable,
    entity_name: str,
) -> legacy_model.LegacyDoSModel:
    """
    Insert data into the DoS source database.

    This step creates a record in the source PostgreSQL container based on
    the entity type and attributes provided in a datatable.

    Args:
        migration_context: Shared context for storing test data
        dos_db_with_migration: Database session fixture
        datatable: pytest-bdd datatable with entity attributes
        entity_name: Name of the legacy model class (e.g., 'Service', 'ServiceAgeRange')

    Returns:
        The created model instance

    Raises:
        AssertionError: If entity_name is invalid or datatable is missing
        pytest.fail: If model validation fails

    Example:
        Given a "Service" exists in DoS with attributes
        | key  | value        |
        | id   | 12345        |
        | name | Test Service |
    """
    validate_datatable(datatable, "data insertion")
    entity_cls = get_entity_class(entity_name)
    model_data = create_model_data_from_datatable(entity_cls, datatable, entity_name)

    # Validate and create model instance
    try:
        model_obj = entity_cls.model_validate(model_data)
    except Exception as e:
        pytest.fail(
            f"Failed to create {entity_name} with provided attributes.\n"
            f"Error: {str(e)}\n"
            f"Data: {model_data}"
        )

    # Insert into database
    dos_db_with_migration.add(model_obj)
    dos_db_with_migration.commit()
    dos_db_with_migration.refresh(model_obj)

    # Store in context for future reference
    if "created_entities" not in migration_context:
        migration_context["created_entities"] = []

    migration_context["created_entities"].append({
        "type": entity_name,
        "instance": model_obj
    })

    return model_obj


@given(
    parsers.parse('the "{entity_name}" with id "{entity_id}" is updated with attributes'),
    target_fixture="updated_dos_entity",
)
def dos_data_update_step(
    migration_context: dict,
    dos_db_with_migration: Session,
    datatable,
    entity_name: str,
    entity_id: str,
) -> legacy_model.LegacyDoSModel:
    """
    Update an existing record in the DoS source database.

    This step updates a record based on its ID and the attributes provided
    in a datatable.

    Args:
        migration_context: Shared context for storing test data
        dos_db_with_migration: Database session fixture
        datatable: pytest-bdd datatable with entity attributes to update
        entity_name: Name of the legacy model class
        entity_id: ID of the entity to update

    Returns:
        The updated model instance

    Raises:
        AssertionError: If entity not found or datatable invalid
        pytest.fail: If invalid attributes provided

    Example:
        Given the "Service" with id "12345" is updated with attributes
        | key  | value           |
        | name | Updated Service |
    """
    validate_datatable(datatable, "data update")
    entity_cls = get_entity_class(entity_name)

    # Parse entity_id and fetch existing entity
    parsed_id = parse_datatable_value(entity_id)
    model_obj = dos_db_with_migration.get(entity_cls, parsed_id)

    assert model_obj is not None, f"{entity_name} with id '{entity_id}' not found in database"

    # Update with values from datatable
    for row in datatable[1:]:
        key = row[0]
        value = parse_datatable_value(row[1])

        if not hasattr(model_obj, key):
            valid_attrs = ", ".join(entity_cls.model_fields.keys())
            pytest.fail(
                f"Invalid attribute '{key}' for entity type '{entity_name}'.\n"
                f"Valid attributes: {valid_attrs}"
            )

        setattr(model_obj, key, value)

    # Commit changes
    dos_db_with_migration.commit()
    dos_db_with_migration.refresh(model_obj)

    # Store in context
    if "updated_entities" not in migration_context:
        migration_context["updated_entities"] = []

    migration_context["updated_entities"].append({
        "type": entity_name,
        "id": entity_id,
        "instance": model_obj
    })

    return model_obj


@when(parsers.parse('I query the "{table_name}" table for "{field_name}" "{field_value}"'))
def query_table_by_field(
    migration_context: dict,
    dos_db_with_migration: Session,
    table_name: str,
    field_name: str,
    field_value: str,
) -> None:
    """
    Query a table by a specific field and value.

    Args:
        migration_context: Shared context for storing test data
        dos_db_with_migration: Database session fixture
        table_name: Name of the table to query (e.g., 'services')
        field_name: Name of the field to filter by (e.g., 'id')
        field_value: Value to search for

    Raises:
        AssertionError: If table name is unknown

    Example:
        When I query the "services" table for "id" "12345"
    """
    entity_name = TABLE_TO_ENTITY.get(table_name.lower())
    assert entity_name is not None, (
        f"Unknown table name: '{table_name}'. "
        f"Available tables: {', '.join(sorted(TABLE_TO_ENTITY.keys()))}"
    )

    entity_cls = get_entity_class(entity_name)
    parsed_value = parse_datatable_value(field_value)

    # Build and execute query
    statement = select(entity_cls).where(
        getattr(entity_cls, field_name) == parsed_value
    )
    result = dos_db_with_migration.exec(statement).first()

    # Store result in context
    migration_context.update({
        "queried_entity": result,
        "queried_table": table_name,
        "queried_field": field_name,
        "queried_value": parsed_value,
    })


@then("the record should exist in the database")
def verify_record_exists(migration_context: dict) -> None:
    """
    Verify that the queried record exists in the database.

    Args:
        migration_context: Shared context containing query results

    Raises:
        AssertionError: If the record was not found
    """
    queried_entity = migration_context.get("queried_entity")
    queried_table = migration_context.get("queried_table", "unknown")
    queried_field = migration_context.get("queried_field", "unknown")
    queried_value = migration_context.get("queried_value", "unknown")

    assert queried_entity is not None, (
        f"Record not found in '{queried_table}' table where "
        f"{queried_field} = '{queried_value}'"
    )


@then(parsers.parse('the "{field_name}" field should be "{expected_value}"'))
def verify_field_value(
    migration_context: dict,
    field_name: str,
    expected_value: str,
) -> None:
    """
    Verify that a specific field has the expected value.

    Args:
        migration_context: Shared context containing query results
        field_name: Name of the field to check
        expected_value: Expected value of the field

    Raises:
        AssertionError: If the field value doesn't match or no entity in context
    """
    queried_entity = migration_context.get("queried_entity")
    assert queried_entity is not None, "No entity found in context to verify"

    actual_value = getattr(queried_entity, field_name, None)
    parsed_expected = parse_datatable_value(expected_value)

    # Normalize both values for comparison
    actual_normalized, expected_normalized = normalize_value_for_comparison(
        actual_value, parsed_expected, field_name
    )

    assert actual_normalized == expected_normalized, (
        f"Field '{field_name}' mismatch:\n"
        f"  Actual:   '{actual_normalized}' (type: {type(actual_normalized).__name__})\n"
        f"  Expected: '{expected_normalized}' (type: {type(expected_normalized).__name__})"
    )

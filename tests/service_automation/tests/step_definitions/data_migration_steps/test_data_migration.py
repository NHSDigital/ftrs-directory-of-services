import json
import re
from datetime import datetime
from decimal import Decimal
from pprint import pprint

import pytest
from common.uuid_utils import generate_uuid
from deepdiff import DeepDiff
from pytest_bdd import parsers, scenarios, then
from step_definitions.common_steps.data_migration_steps import *  # noqa: F403
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.data_migration_steps.dos_data_manipulation_steps import *  # noqa: F403
from utilities.common.dynamoDB_tables import get_table_name  # noqa: F403


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)


META_TIME_FIELDS = ["createdDateTime", "modifiedDateTime"]

NESTED_PATHS_WITH_META_FIELDS = ["endpoints"]

IGNORED_PATHS = [
    "field",
    *META_TIME_FIELDS,
    *[
        re.compile(r"root\['{nested}']\[\d+]\['{field}']")
        for nested in NESTED_PATHS_WITH_META_FIELDS
        for field in META_TIME_FIELDS
    ],
]

scenarios(
    "../features/data_migration_features/gp_practice_migration_happy_path.feature",
    "../features/data_migration_features/gp_enhanced_access_happy_path.feature",
    "../features/data_migration_features/age_range_transformation.feature",
    "../features/data_migration_features/sgsd_transformation.feature",
    "../features/data_migration_features/position_gcs_transformation.feature",
    "../features/data_migration_features/triage_code_migration.feature",
    "../features/data_migration_features/endpoints_transformation.feature",
    "../features/data_migration_features/dispositions_transformation.feature",
    "../features/data_migration_features/opening_times_transformation.feature",
    "../features/data_migration_features/phone_transformation.feature",
    "../features/data_migration_features/email_transformation.feature",
    "../features/data_migration_features/service_migration_validation_failures.feature",
    # Incremental update tests
    "../features/data_migration_features/incremental_updates/update_organisation_fields.feature",
    "../features/data_migration_features/incremental_updates/update_healthcare_service_fields.feature",
    "../features/data_migration_features/incremental_updates/update_location_fields.feature",
    "../features/data_migration_features/incremental_updates/update_edge_cases.feature",
    "../features/data_migration_features/incremental_updates/update_multi_entity.feature",
    "../features/data_migration_features/incremental_updates/update_status.feature",
    "../features/data_migration_features/incremental_updates/update_endpoints.feature",
)


@then(
    parsers.parse(
        "there is {org_count_expected:d} organisation, {location_count_expected:d} location and {healthcare_service_count_expected:d} healthcare services created"
    )
)
def check_expected_table_counts(
    org_count_expected: int,
    location_count_expected: int,
    healthcare_service_count_expected: int,
    dynamodb,
):
    """
    Performs a complete table scan - consider a different option for large tables
    """
    dynamodb_resource = dynamodb["resource"]

    def check_table(table_name, count_expected):
        table = dynamodb_resource.Table(table_name)
        table_scan = table.scan()
        actual_count = len(table_scan["Items"])
        assert count_expected == actual_count, (
            f"Expected {table_name} count does not match actual"
        )

    check_table(get_table_name("organisation"), org_count_expected)
    check_table(get_table_name("location"), location_count_expected)
    check_table(get_table_name("healthcare-service"), healthcare_service_count_expected)


@then(parsers.parse("The '{table_name}' for service ID '{service_id}' has content:"))
def check_table_content_by_id(table_name, service_id, docstring, dynamodb):
    namespace = table_name.replace("-", "_")
    generated_uuid = str(generate_uuid(service_id, namespace))
    _check_by_id_and_sort_key(table_name, generated_uuid, docstring, dynamodb)


@then(
    parsers.re(
        r"field '(?P<field_name>[\w-]*)' on table '(?P<table_name>[\w-]*)' for id '(?P<primary_id>[\w-]+)' has content:"
    )
)
def check_field_on_a_table_by_id(
    field_name, table_name, primary_id, docstring, dynamodb
):
    _check_by_id_and_sort_key(
        table_name, primary_id, docstring, dynamodb, filtered_by_field=field_name
    )


@then(
    parsers.re(
        r"field '(?P<field_name>[\w-]*)' on table '(?P<table_name>[\w-]*)' for id '(?P<primary_id>[\w-]+)' and field sort key '(?P<field_sort_key>[\w-]+)' has content:"
    )
)
def check_field_on_a_table_by_id_and_sort_key(
    field_name, table_name, primary_id, docstring, dynamodb, field_sort_key
):
    _check_by_id_and_sort_key(
        table_name,
        primary_id,
        docstring,
        dynamodb,
        field_sort_key=field_sort_key,
        filtered_by_field=field_name,
    )


@then(
    parsers.re(
        r"the '(?P<table_name>[\w-]*)' for id '(?P<primary_id>[\w-]+)' has content:"
    )
)
def check_row_on_table_by_id(table_name, primary_id, docstring, dynamodb):
    _check_by_id_and_sort_key(table_name, primary_id, docstring, dynamodb)


@then(
    parsers.re(
        r"the '(?P<table_name>[\w-]*)' for id '(?P<primary_id>[\w-]+)' and field sort key '(?P<field_sort_key>[\w-]+)' has content:"
    )
)
def check_row_on_table_by_id_and_sort_key(
    table_name, primary_id, docstring, field_sort_key, dynamodb
):
    _check_by_id_and_sort_key(
        table_name, primary_id, docstring, dynamodb, field_sort_key
    )


def _check_by_id_and_sort_key(
    table_name,
    primary_id,
    docstring,
    dynamodb,
    field_sort_key="document",
    filtered_by_field=None,
):
    retrieved_item = json.loads(
        json.dumps(
            get_by_id_and_sort_key(
                dynamodb, table_name, primary_id, field_sort_key_value=field_sort_key
            ),
            cls=DecimalEncoder,
        )
    )
    expected = json.loads(docstring)
    actual = (
        {k: v for k, v in retrieved_item.items() if k == filtered_by_field}
        if filtered_by_field
        else retrieved_item
    )
    validate_diff(expected, actual)

    if not filtered_by_field:
        validate_dynamic_fields(actual)


def validate_diff(expected, retrieved_item):
    diff = DeepDiff(
        expected, retrieved_item, ignore_order=True, exclude_regex_paths=IGNORED_PATHS
    )

    assert diff == {}, f"Differences found: {pprint(diff, indent=2)}"


def validate_dynamic_fields(retrieved_item):
    def validate_metas(obj, root_path="$"):
        for field in META_TIME_FIELDS:
            assert field in obj, f"Expected field '{field}' not found in item"
            validate_timestamp_format(f"{root_path}.{field}", obj[field])

        relevant_fields = {
            k: v for k, v in obj.items() if k in NESTED_PATHS_WITH_META_FIELDS
        }
        for key, value in relevant_fields.items():
            if isinstance(value, dict):
                validate_metas(value, f"{root_path}.{key}")
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        validate_metas(item, f"{root_path}.{key}[{i}]")

    validate_metas(retrieved_item)


def validate_timestamp_format(path_to_field, date_text):
    try:
        datetime.fromisoformat(date_text)
    except ValueError:
        pytest.fail(
            f"Text under {path_to_field}: {date_text} not recognised as valid datetime"
        )


def get_by_id(dynamodb, table_name, service_id):
    dynamodb_resource = dynamodb["resource"]
    target_table = dynamodb_resource.Table(get_table_name(table_name))
    response = target_table.get_item(Key={"id": service_id, "field": "document"})

    assert "Item" in response, f"No item found under {service_id}"
    item = response["Item"]

    return item


def get_by_id_and_sort_key(
    dynamodb, table_name, id_value, field_sort_key_value="document"
):
    dynamodb_resource = dynamodb["resource"]
    target_table = dynamodb_resource.Table(get_table_name(table_name))
    response = target_table.get_item(
        Key={"id": id_value, "field": field_sort_key_value}
    )

    assert "Item" in response, (
        f"No item found under id: {id_value}, field sort key: {field_sort_key_value}"
    )
    item = response["Item"]

    return item


@then(parsers.parse("no organisation was created for service '{service_id:d}'"))
def verify_no_organisation_created(service_id: int, dynamodb):
    """Verify that no organisation was created for the given service."""
    organisation_uuid = str(generate_uuid(service_id, "organisation"))

    dynamodb_resource = dynamodb["resource"]
    org_table = dynamodb_resource.Table(get_table_name("organisation"))

    response = org_table.get_item(Key={"id": organisation_uuid, "field": "document"})
    assert "Item" not in response, (
        f"Organisation with id {organisation_uuid} should not exist for service {service_id}"
    )


@then(parsers.parse("no location was created for service '{service_id:d}'"))
def verify_no_location_created(service_id: int, dynamodb):
    """Verify that no location was created for the given service."""
    location_uuid = str(generate_uuid(service_id, "location"))

    dynamodb_resource = dynamodb["resource"]
    location_table = dynamodb_resource.Table(get_table_name("location"))

    response = location_table.get_item(Key={"id": location_uuid, "field": "document"})
    assert "Item" not in response, (
        f"Location with id {location_uuid} should not exist for service {service_id}"
    )


@then(parsers.parse("no healthcare service was created for service '{service_id:d}'"))
def verify_no_healthcare_service_created(service_id: int, dynamodb):
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

import datetime
import json
import re

from decimal import Decimal
from deepdiff import DeepDiff
from pprint import pprint
from pytest_bdd import scenarios, given, when, then, parsers, scenario
from step_definitions.data_migration_steps.dos_data_manipulation_steps import *  # noqa: F403
from step_definitions.common_steps.data_steps import *  # noqa: F403


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)


META_TIME_FIELDS = [
    'createdDateTime',
    'modifiedDateTime'
]

NESTED_PATHS = [
    "endpoints"
]

IGNORED_PATHS = [
    "field",
    *META_TIME_FIELDS,
    *[re.compile(r"root\['{nested}']\[\d+]\['{field}']") for nested in NESTED_PATHS for field in META_TIME_FIELDS],
]

scenarios("../features/data_migration_features/data_migration.feature")

@given("the data migration system is ready")
def data_migration_system_ready():
    pass


@given(parsers.parse("record for '{table_name}' from '{source_file_path}' is loaded"))
def sideload_data_to_dynamodb_table(
    table_name,
    source_file_path,
    request: pytest.FixtureRequest,
    model_repos_local,
):
    model_repo = model_repos_local[table_name]
    model = model_from_json_file(source_file_path, model_repo)
    if not check_record_in_repo(model_repo, model.id):
        model_repo.delete(model.id)
    model_repo.create(model)
    yield
    model_repo.delete(model.id)


@when("data migration is executed")
def data_migration_is_executed():
    pass


@then(
    parsers.parse(
        "there is {org_count_expected:d} organisation, {location_count_expected:d} location and {healthcare_service_count_expected:d} healthcare services created"
    )
)
def check_expected_table_counts(org_count_expected: int, location_count_expected: int, healthcare_service_count_expected: int, dynamodb):
    """
    Performs a complete table scan - consider a different option for large tables
    """
    dynamodb_resource = dynamodb["resource"]

    def check_table(table_name, count_expected):
        table = dynamodb_resource.Table(table_name)
        table_scan = table.scan()
        actual_count = len(table_scan["Items"])
        assert count_expected == actual_count, f"Expected {table_name} count does not match actual"

    check_table("organisation", org_count_expected)
    check_table("location", location_count_expected)
    check_table("healthcare-service", healthcare_service_count_expected)


@then(parsers.parse("The '{table_name}' for service ID '{service_id}' has content:"))
def check_table_content_by_id(table_name, service_id, docstring, dynamodb):
    retrieved_item = json.loads(
        json.dumps(
            get_by_id(dynamodb, table_name, service_id),
            cls=DecimalEncoder
        )
    )
    expected = json.loads(docstring)

    validated_diff(expected, retrieved_item)
    validate_dynamic_fields(retrieved_item)


def validated_diff(expected, retrieved_item):
    diff = DeepDiff(expected, retrieved_item, ignore_order=True, exclude_regex_paths=IGNORED_PATHS)

    assert diff == {}, f"Differences found: {pprint(diff, indent=2)}"


def validate_dynamic_fields(retrieved_item):
    def validate_metas(obj, root_path="$"):
        for field in META_TIME_FIELDS:
            assert field in obj, f"Expected field '{field}' not found in item"
            validate_timestamp_format(f"{root_path}.{field}", obj[field])

        for key, value in obj.items():
            if isinstance(value, dict):
                validate_metas(value, f"{root_path}.{key}")
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        validate_metas(item, f"{root_path}.{key}[{i}]")

    validate_metas(retrieved_item)


def validate_timestamp_format(path_to_field, date_text):
    try:
        datetime.datetime.fromisoformat(date_text)
    except ValueError:
        assert False, f"Text under {path_to_field}: {date_text} not recognised as valid datetime"


def get_by_id(dynamodb, table_name, service_id):
    dynamodb_resource = dynamodb["resource"]
    target_table = dynamodb_resource.Table(table_name)
    response = target_table.get_item(Key={ 'id': service_id, 'field': 'document'})

    assert 'Item' in response, f"No item found under {service_id}"
    item = response['Item']

    return item

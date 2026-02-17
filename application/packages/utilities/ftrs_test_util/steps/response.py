from http import HTTPStatus
import json
import chevron
from pytest_bdd import parsers, then
from ftrs_test_util.fixtures.context import TestContext
from ftrs_test_util.parsing import try_parse_json
import pytest
import deepdiff
import jmespath


# -----------------
# Header Assertions
# -----------------
@then(parsers.parse("the response status code should be {status_code:d}"))
def check_status_code(test_context: TestContext, status_code: int) -> None:
    assert test_context.last_response is not None, "No response received from the API"
    assert test_context.last_response.status_code == HTTPStatus(status_code), (
        f"Expected status code {status_code}, got {test_context.last_response.status_code}\nResponse body: {test_context.last_response.text}"
    )


@then(parsers.parse('the "{header_name}" header should be present in the response'))
def check_header_present(test_context: TestContext, header_name: str) -> None:
    assert test_context.last_response is not None, "No response received from the API"
    assert header_name in test_context.last_response.headers, (
        f"Expected header '{header_name}' to be present in the response"
    )


@then(
    parsers.parse(
        'the "{header_name}" response header should have value "{expected_value}"'
    )
)
def check_header_value(
    test_context: TestContext,
    header_name: str,
    expected_value: str,
) -> None:
    assert test_context.last_response is not None, "No response received from the API"
    assert header_name in test_context.last_response.headers, (
        f"Expected header '{header_name}' to be present in the response"
    )
    actual_value = test_context.last_response.headers.get(header_name)
    assert actual_value == expected_value, (
        f"Expected header '{header_name}' to have value '{expected_value}', but got '{actual_value}'"
    )


# -----------------
# Body Assertions
# -----------------
@then("the response body should match the following JSON:")
def check_response_body(test_context: TestContext, docstring: str) -> None:
    rendered_docstring = chevron.render(docstring, test_context.extracted_values)
    expected_body = try_parse_json(rendered_docstring)
    assert test_context.last_response is not None, "No response received from the API"

    actual_body = try_parse_json(test_context.last_response.text)

    diff = deepdiff.DeepDiff(expected_body, actual_body)
    if diff:
        pytest.fail(
            f"Response body does not match expected body. Differences:\n{diff.to_dict()}\n\nFull Body:\n{json.dumps(actual_body, indent=2)}"
        )


@then("the response body should match the following text:")
def check_response_body_text(test_context: TestContext, docstring: str) -> None:
    expected_body = chevron.render(docstring, test_context.extracted_values)
    assert test_context.last_response is not None, "No response received from the API"

    actual_body = test_context.last_response.text
    assert actual_body == expected_body, (
        f"Response body does not match expected body.\nExpected:\n{expected_body}\nActual:\n{actual_body}"
    )


@then(parsers.parse("the response body should contain the following JSON:"))
def check_response_body_contains(
    test_context: TestContext,
    docstring: str,
) -> None:
    rendered_docstring = chevron.render(docstring, test_context.extracted_values)
    expected_body = try_parse_json(rendered_docstring)
    assert test_context.last_response is not None, "No response received from the API"

    actual_body = try_parse_json(test_context.last_response.text)

    keys_to_check = expected_body.keys()
    for key in keys_to_check:
        assert key in actual_body, f"Expected key '{key}' not found in response body"
        assert actual_body[key] == expected_body[key], (
            f"Value for key '{key}' does not match expected value. "
            f"Expected: {expected_body[key]}, Actual: {actual_body[key]}"
        )


@then(
    parsers.parse(
        'the "{key_path}" field in the response body should be "{expected_value}"'
    )
)
def check_value_in_response_body(
    test_context: TestContext,
    key_path: str,
    expected_value: str,
) -> None:
    expected_value_rendered = chevron.render(
        expected_value, test_context.extracted_values
    )

    assert test_context.last_response is not None, "No response received from the API"

    actual_body = try_parse_json(test_context.last_response.text)

    actual_value = jmespath.search(key_path, actual_body)
    assert actual_value == expected_value_rendered, (
        f"Value for key path '{key_path}' does not match expected value. "
        f"Expected: {expected_value_rendered}, Actual: {actual_value}"
    )


@then("the response body should be empty")
def check_response_body_empty(test_context: TestContext) -> None:
    assert test_context.last_response is not None, "No response received from the API"
    assert test_context.last_response.text == "", "Expected response body to be empty"


# -----------------
# Header Extraction
# -----------------
@then(parsers.parse('the ID is extracted from the Location header as "{id_key}"'))
def extract_id_from_location_header(
    test_context: TestContext,
    id_key: str,
) -> None:
    assert test_context.last_response is not None, "No response received from the API"
    location_header = test_context.last_response.headers.get("Location")
    assert location_header is not None, "Location header is not present in the response"
    extracted_id = location_header.rsplit("/", 1)[-1]
    test_context.extracted_values[id_key] = extracted_id


# -----------------
# Body Extraction
# -----------------
@then(
    parsers.parse(
        'the "{key_path}" value is extracted from the response body as "{extracted_key}"'
    )
)
def extract_value_from_response_body(
    test_context: TestContext,
    key_path: str,
    extracted_key: str,
) -> None:
    assert test_context.last_response is not None, "No response received from the API"
    try:
        actual_body = test_context.last_response.json()
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse JSON from response body: {e}")

    extracted_value = jmespath.search(key_path, actual_body)
    assert extracted_value is not None, (
        f"Value for key path '{key_path}' not found in response body"
    )
    test_context.extracted_values[extracted_key] = extracted_value

import json
import re

from playwright.sync_api import APIResponse
from pytest_bdd import parsers, then


@then(parsers.parse('I receive a status code "{status_code:d}" in response'))
def status_code(fresponse: APIResponse, status_code: int) -> None:
    assert fresponse.status == status_code


@then(parsers.parse('the response body contains an "{resource_type}" resource'))
def api_check_resource_type(fresponse: APIResponse, resource_type: str) -> None:
    response = fresponse.json()
    assert response["resourceType"] == resource_type


@then(parsers.parse('I receive the error code "{error_code}"'))
def api_error_code(fresponse: APIResponse, error_code: str) -> None:
    response = fresponse.json()
    assert response["issue"][0]["details"]["coding"][0]["code"] == error_code


@then(parsers.parse('I receive the message "{error_message}"'))
def api_error_message(fresponse: APIResponse, error_message: str) -> None:
    response = fresponse.json()
    assert response["issue"][0]["details"]["text"] == (error_message)


@then(parsers.parse('I receive the diagnostics "{diagnostics}"'))
def api_diagnostics(fresponse: APIResponse, diagnostics: str) -> None:
    response = fresponse.json()
    assert (response["issue"][0]["diagnostics"]).startswith(diagnostics)


@then("the response body contains a bundle")
def api_check_bundle(fresponse: APIResponse) -> None:
    response = fresponse.json()
    assert response["resourceType"] == "Bundle"


@then(parsers.parse('the bundle contains "{number:d}" "{resource_type}" resources'))
def api_number_resources(
    fresponse: APIResponse, number: int, resource_type: str
) -> None:
    response = fresponse.json()
    assert count_resources(response, resource_type) == number


@then("the bundle contains a self link")
def api_check_bundle_self_link(fresponse: APIResponse) -> None:
    response = fresponse.json()
    assert any(link.get("relation") == "self" for link in response.get("link", []))


@then(parsers.parse('the bundle type is "{bundle_type}"'))
def api_check_bundle_type_searchset(fresponse: APIResponse, bundle_type: str) -> None:
    response = fresponse.json()
    assert response["type"] == (bundle_type)


@then(
    parsers.parse(
        'the response body contains JSON with a key "{key}" and value "{value}"'
    )
)
def api_json_key_value(fresponse: APIResponse, key: str, value: str) -> None:
    response = fresponse.json()
    assert response[key] == value


@then(parsers.parse('the resource has an id of "{resource_id}"'))
def api_check_resource_id(fresponse: APIResponse, resource_id: str) -> None:
    response = fresponse.json()
    assert response["id"] == resource_id


@then(parsers.parse('the OperationOutcome has issues all with {key} "{value}"'))
def api_check_operation_outcome_all_issue_by_key_value(
    fresponse: APIResponse, key: str, value: str
) -> None:
    response = fresponse.json()
    assert all(issue.get(key) == value for issue in response["issue"])


@then(parsers.parse('the OperationOutcome contains "{number:d}" issues'))
def api_check_operation_outcome_issue_count(
    fresponse: APIResponse, number: int
) -> None:
    response = fresponse.json()
    assert len(response["issue"]) == number


@then(parsers.parse('the OperationOutcome contains an issue with {key} "{value}"'))
def api_check_operation_outcome_any_issue_by_key_value(
    fresponse: APIResponse, key: str, value: str
) -> None:
    response = fresponse.json()
    assert any(issue.get(key) == value for issue in response["issue"])


@then(
    parsers.parse(
        'the response headers contain "{header_name}" with value "{header_value}"'
    )
)
def api_check_response_header(
    fresponse: APIResponse, header_name: str, header_value: str
) -> None:
    """Verify that a specific header is present in the response with the expected value."""
    response_headers = fresponse.headers
    # Check if header exists (case-insensitive)
    header_found = False
    actual_value = None
    for key, value in response_headers.items():
        if key == header_name:
            header_found = True
            actual_value = value
            break

    assert header_found, (
        f"Header '{header_name}' not found in response headers. Available headers: {list(response_headers.keys())}"
    )
    assert actual_value == header_value, (
        f"Header '{header_name}' has value '{actual_value}' but expected '{header_value}'"
    )


@then(
    parsers.parse(
        'the response headers contain the following headers and values "{headers_json}"'
    )
)
def api_check_multiple_response_headers(
    fresponse: APIResponse, headers_json: str
) -> None:
    expected_headers: dict = json.loads(headers_json)
    response_headers = fresponse.headers

    actual_headers = dict(response_headers.items())

    failures = []
    for expected_name, expected_value in expected_headers.items():
        match = actual_headers.get(expected_name)
        if match is None:
            failures.append(
                f"Header '{expected_name}' not found in response headers. "
                f"Available headers: {list(response_headers.keys())}"
            )
        elif match != expected_value:
            failures.append(
                f"Header '{expected_name}' has value '{match}' but expected '{expected_value}'"
            )

    assert not failures, "Response header assertion(s) failed:\n" + "\n".join(failures)


@then(
    parsers.parse(
        'the {resource} resource has "{field_name}" with value "{expected_value}"'
    )
)
def api_check_resource_field_value(
    fresponse: APIResponse, resource: str, field_name: str, expected_value: str
) -> None:
    """Verify resource field has expected value."""
    response = fresponse.json()
    resource_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == resource
    ]
    assert len(resource_entries) > 0, f"No {resource} resource found"
    res = resource_entries[0]["resource"]
    actual_value = res.get(field_name)
    assert actual_value == expected_value, (
        f"{resource}.{field_name} expected '{expected_value}' but got '{actual_value}'"
    )


@then(
    parsers.parse(
        'the {resource} resource has "{field_name}" with boolean {expected_value}'
    )
)
def api_check_resource_field_boolean(
    fresponse: APIResponse, resource: str, field_name: str, expected_value: str
) -> None:
    """Verify resource boolean field has expected value."""
    response = fresponse.json()
    resource_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == resource
    ]
    assert len(resource_entries) > 0, f"No {resource} resource found"
    res = resource_entries[0]["resource"]
    actual_value = res.get(field_name)
    expected_bool = expected_value.lower() == "true"
    assert actual_value == expected_bool, (
        f"Organization.{field_name} expected {expected_bool} but got {actual_value}"
    )


@then(
    parsers.parse(
        'the {resource} resource identifier has "{field_name}" with value "{expected_value}"'
    )
)
def api_check_resource_identifier_field(
    fresponse: APIResponse, resource: str, field_name: str, expected_value: str
) -> None:
    """Verify resource.identifier[0] field has expected value."""
    response = fresponse.json()
    resource_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == resource
    ]
    assert len(resource_entries) > 0, f"No {resource} resource found"
    res = resource_entries[0]["resource"]
    identifier = res.get("identifier", [{}])[0]
    actual_value = identifier.get(field_name)
    assert actual_value == expected_value, (
        f"{resource}.identifier[0].{field_name} expected '{expected_value}' but got '{actual_value}'"
    )


@then(parsers.parse("the {resource} resource has id matching UUID pattern"))
def api_check_resource_id_uuid_pattern(fresponse: APIResponse, resource: str) -> None:
    """Verify resource.id matches UUID pattern."""
    response = fresponse.json()
    resource_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == resource
    ]
    assert len(resource_entries) > 0, f"No {resource} resource found"
    res = resource_entries[0]["resource"]
    res_id = res.get("id")
    assert res_id is not None, f"{resource}.id is missing"
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    assert re.match(uuid_pattern, res_id, re.IGNORECASE), (
        f"{resource}.id '{res_id}' does not match UUID pattern"
    )


@then("the response includes security headers")
def verify_security_headers(fresponse: APIResponse) -> None:
    """Verify that the response includes all required security headers."""
    headers = fresponse.headers
    assert (
        headers.get("strict-transport-security")
        == "max-age=31536000; includeSubDomains"
    )
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert headers.get("cache-control") == "no-store"


def count_resources(lambda_response: dict, resource_type: str) -> int:
    return sum(
        entry.get("resource", {}).get("resourceType") == resource_type
        for entry in lambda_response.get("entry", [])
    )

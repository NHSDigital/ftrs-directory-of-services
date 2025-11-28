from pytest_bdd import parsers, then

@then(parsers.parse('I receive a status code "{status_code:d}" in response'))
def status_code(fresponse, status_code):
    assert fresponse.status == status_code

@then(parsers.parse('the response body contains an "{resource_type}" resource'))
def api_check_resource_type(fresponse, resource_type):
    response = fresponse.json()
    assert response["resourceType"] == resource_type

@then(parsers.parse('I receive the error code "{error_code}"'))
def api_error_code(fresponse, error_code):
    response = fresponse.json()
    assert response["issue"][0]["details"]["coding"][0]["code"] == error_code


@then(parsers.parse('I receive the message "{error_message}"'))
def api_error_message(fresponse, error_message):
    response = fresponse.json()
    assert response["issue"][0]["details"]["text"] == (error_message)


@then(parsers.parse('I receive the diagnostics "{diagnostics}"'))
def api_diagnostics(fresponse, diagnostics):
    response = fresponse.json()
    assert (response["issue"][0]["diagnostics"]).startswith(diagnostics)


@then('the response body contains a bundle')
def api_check_bundle(fresponse):
    response = fresponse.json()
    assert response["resourceType"] == "Bundle"


@then(parsers.parse('the bundle contains "{number:d}" "{resource_type}" resources'))
def api_number_resources(fresponse, number, resource_type):
    response = fresponse.json()
    assert count_resources(response, resource_type) == number


@then(parsers.parse('the response body contains JSON with a key "{key}" and value "{value}"'))
def api_json_key_value(fresponse, key, value):
    response = fresponse.json()
    assert response[key] == value

@then(parsers.parse('the resource has an id of "{resource_id}"'))
def api_check_resource_id(fresponse, resource_id):
    response = fresponse.json()
    assert response["id"] == resource_id


@then(parsers.parse('the OperationOutcome has issues all with {key} "{value}"'))
def api_check_operation_outcome_all_issue_diagnostics(fresponse, key, value):
    response = fresponse.json()
    assert all(issue.get(key) == value for issue in response["issue"])

@then(parsers.parse('the OperationOutcome contains "{number:d}" issues'))
def api_check_operation_outcome_issue_count(fresponse, number):
    response = fresponse.json()
    assert len(response["issue"]) == number

@then(parsers.parse('the OperationOutcome contains an issue with {key} "{value}"'))
def api_check_operation_outcome_any_issue_diagnostics(fresponse, key, value):
    response = fresponse.json()
    assert any(issue.get(key) == value for issue in response["issue"])


def count_resources(lambda_response, resource_type):
    return sum(
        entry.get("resource", {}).get("resourceType") == resource_type
        for entry in lambda_response.get("entry", [])
    )

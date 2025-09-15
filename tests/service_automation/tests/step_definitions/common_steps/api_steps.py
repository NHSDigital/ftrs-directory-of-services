from pytest_bdd import parsers, then

@then(parsers.parse('I receive a status code "{status_code:d}" in response'))
def status_code(fresponse, status_code):
    assert fresponse.status == status_code

@then(parsers.parse('the response body contains an "{resource_type}" resource'))
def api_check_resource_type(fresponse, resource_type):
    response = fresponse.json()
    assert response["resourceType"] == resource_type

@then(parsers.parse('the OperationOutcome contains "{number:d}" issues'))
def api_check_operation_outcome_issue_count(fresponse, number):
    response = fresponse.json()
    assert len(response["issue"]) == number

@then(parsers.parse('the OperationOutcome contains an issue with {key} "{value}"'))
def api_check_operation_outcome_any_issue_diagnostics(fresponse, key, value):
    response = fresponse.json()
    assert any(issue.get(key) == value for issue in response["issue"])

import pytest
import os
from loguru import logger
from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from step_definitions.common_steps.api_steps import *  # noqa: F403
from utilities.infra.api_util import get_r53, get_url
from utilities.infra.dns_util import wait_for_dns

INVALID_SEARCH_DATA_CODING = {
    "coding": [
        {
            "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-SpineErrorOrWarningCode",
            "version": "1.0.0",
            "code": "INVALID_SEARCH_DATA",
            "display": "Invalid search data",
        }
    ]
}

INVALID_AUTH_CODING = {
    "coding": [
        {
            "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
            "version": "1",
            "code": "UNAUTHORIZED",
            "display": "Unauthorized"
        }
    ]
}

# Load feature file
scenarios("./is_api_features/dos_search_backend.feature","./is_api_features/dos_search_apim.feature")

@pytest.fixture(scope="module")
def r53_name() -> str:
    r53_name = os.getenv("R53_NAME", "servicesearch")
    return r53_name

@given(parsers.re(r'the dns for "(?P<api_name>.*?)" is resolvable'))
def dns_resolvable(api_name, env, workspace):
    r53 = get_r53(workspace, api_name, env)
    assert wait_for_dns(r53)

@when(
    parsers.re(r'I request data from the "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)"'),
    target_fixture="fresponse",
)
def send_get_with_params(api_request_context_mtls, api_name, params, resource_name):
    url = get_url(api_name) + "/" + resource_name
    # Handle None or empty params
    if params is None or not params.strip():
        param_dict = {}
    else:
        # Parse the params string into a dictionary
        param_dict = dict(param.split('=', 1) for param in params.split('&') if '=' in param)

    response = api_request_context_mtls.get(
            url,  params=param_dict
        )
    return response

@when(
    parsers.re(r'I request data from the APIM "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)"'),
    target_fixture="fresponse",
)
def send_to_apim_get_with_params(new_apim_request_context, params, resource_name, nhsd_apim_proxy_url):
    url = nhsd_apim_proxy_url + "/" + resource_name
    logger.info(f"nhsd_apim_proxy_url : {nhsd_apim_proxy_url}")
    # Handle None or empty params
    if params is None or not params.strip():
        param_dict = {}
    else:
        # Parse the params string into a dictionary
        param_dict = dict(param.split('=', 1) for param in params.split('&') if '=' in param)
    response = new_apim_request_context.get(
            url,  params=param_dict
        )
    logger.info(f"response: {response.text}")
    return response

@when(
    parsers.re(r'I request data from the APIM "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)" and "(?P<token_type>.*?)" access token'),
    target_fixture="fresponse",
)
def send_to_apim_with_invalid_token(apim_request_context, params, resource_name, nhsd_apim_proxy_url, nhsd_apim_auth_headers, token_type):
    url = nhsd_apim_proxy_url + "/" + resource_name
    logger.info(f"token_type : {token_type}")
    # Handle None or empty params
    if params is None or not params.strip():
        param_dict = {}
    else:
        # Parse the params string into a dictionary
        param_dict = dict(param.split('=', 1) for param in params.split('&') if '=' in param)
    if token_type in ("missing", "no"):
        response = apim_request_context.get(
                url,  params=param_dict
            )
    elif token_type == "invalid":
        response = apim_request_context.get(
            url,  params=param_dict, headers={"Authorization": "Bearer invalid_token"}
        )
    else:
        raise ValueError(f"Unknown token_type: {token_type}")
    logger.info(f"response: {response.text}")
    return response


@then(parsers.parse('I receive a status code "{status_code:d}" in response'))
def status_code(fresponse, status_code):
    assert fresponse.status == status_code


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


@then(parsers.parse('the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding'))
def api_check_operation_outcome_any_issue_details_invalid_search_data(fresponse):
    api_check_operation_outcome_any_issue_diagnostics(
        fresponse,
        key="details",
        value=INVALID_SEARCH_DATA_CODING
    )

@then(parsers.parse('the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding'))
def api_check_operation_outcome_any_issue_details_invalid_auth_coding(fresponse):
    api_check_operation_outcome_any_issue_diagnostics(
        fresponse,
        key="details",
        value=INVALID_AUTH_CODING
    )


def count_resources(lambda_response, resource_type):
    return sum(
        entry.get("resource", {}).get("resourceType") == resource_type
        for entry in lambda_response.get("entry", [])
    )

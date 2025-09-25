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
    parsers.re(r'I request data from the APIM "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" with "(?P<param_type>.*?)" query params and "(?P<token_type>.*?)" access token'),
    target_fixture="fresponse",
)
def send_to_apim_with_invalid_token(new_apim_request_context, resource_name, param_type, nhsd_apim_proxy_url, token_type):
    if param_type == "valid":
        params = "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046"
    else:
        params = ""
    url = nhsd_apim_proxy_url + "/" + resource_name
    logger.info(f"token_type : {token_type}")
    # Handle None or empty params
    if params is None or not params.strip():
        param_dict = {}
    else:
        # Parse the params string into a dictionary
        param_dict = dict(param.split('=', 1) for param in params.split('&') if '=' in param)
    if token_type in ("missing", "no", "valid"):
        response = new_apim_request_context.get(
                url,  params=param_dict
            )
    elif token_type == "invalid":
        response = new_apim_request_context.get(
            url,  params=param_dict, headers={"Authorization": "Bearer invalid_token"}
        )
    else:
        raise ValueError(f"Unknown token_type: {token_type}")
    logger.info(f"response: {response.text}")
    return response

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


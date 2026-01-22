import os

import pytest
from loguru import logger
from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps import api_steps
from step_definitions.common_steps.api_steps import *  # noqa: F403
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from utilities.infra.api_util import get_r53, get_url
from utilities.infra.dns_util import wait_for_dns

CODING_MAP = {
    "INVALID_SEARCH_DATA": {
        "coding": [
            {
                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-SpineErrorOrWarningCode",
                "version": "1.0.0",
                "code": "INVALID_SEARCH_DATA",
                "display": "Invalid search data",
            }
        ]
    },
    "INVALID_AUTH_CODING": {
        "coding": [
            {
                "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                "version": "1",
                "code": "UNAUTHORIZED",
                "display": "Unauthorized",
            }
        ]
    },
    "UNSUPPORTED_SERVICE": {
        "coding": [
            {
                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-SpineErrorOrWarningCode",
                "version": "1.0.0",
                "code": "UNSUPPORTED_SERVICE",
                "display": "Unsupported service",
            }
        ]
    },
}

# Load feature file
scenarios(
    "./is_api_features/dos_search_backend.feature",
    "./is_api_features/dos_search_apim.feature",
    "./is_api_features/dos_search_apim_security.feature",
)


@pytest.fixture(scope="module")
def r53_name() -> str:
    r53_name = os.getenv("R53_NAME", "dos-search")
    return r53_name


@given(parsers.re(r'the dns for "(?P<api_name>.*?)" is resolvable'))
def dns_resolvable(api_name, env, workspace):
    r53 = get_r53(workspace, api_name, env)
    assert wait_for_dns(r53)


@when(
    parsers.re(
        r'I request data from the "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)"'
    ),
    target_fixture="fresponse",
)
def send_get_with_params(api_request_context_mtls, api_name, params, resource_name):
    url = get_url(api_name) + "/" + resource_name

    return _send_api_request(api_request_context_mtls, url, params)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)"'
    ),
    target_fixture="fresponse",
)
def send_to_apim_get_with_params(
    apim_request_context, nhsd_apim_proxy_url, params, resource_name
):
    url = nhsd_apim_proxy_url + "/" + resource_name

    return _send_api_request(apim_request_context, url, params)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)" without authentication'
    ),
    target_fixture="fresponse",
)
def send_to_apim_no_auth(
    api_request_context, nhsd_apim_proxy_url, params, resource_name
):
    url = nhsd_apim_proxy_url + "/" + resource_name
    return _send_api_request(api_request_context, url, params)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)" with invalid token'
    ),
    target_fixture="fresponse",
)
def send_to_apim_invalid_token(
    apim_request_context, nhsd_apim_proxy_url, params, resource_name
):
    url = nhsd_apim_proxy_url + "/" + resource_name
    headers = {"Authorization": "Bearer invalid_token"}
    return _send_api_request(apim_request_context, url, params, headers)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)" with status token'
    ),
    target_fixture="fresponse",
)
def send_to_apim_status_token(
    apim_request_context,
    status_endpoint_auth_headers,
    nhsd_apim_proxy_url,
    params,
    resource_name,
):
    url = nhsd_apim_proxy_url + "/" + resource_name
    return _send_api_request(
        apim_request_context, url, params, status_endpoint_auth_headers
    )


def _send_api_request(request_context, url, params: str = None, headers=None):
    param_dict = _convert_params_str_to_dict(params)

    response = request_context.get(
        url,
        params=param_dict,
        headers=headers,
    )

    logger.info(f"response: {response.text}")

    return response


def _convert_params_str_to_dict(params: str | None) -> dict[str, str]:
    if not params:
        return {}

    return dict(param.split("=", 1) for param in params.split("&") if "=" in param)


@then(
    parsers.re(
        r"the OperationOutcome contains an issue with details for (?P<coding_type>\w+) coding"
    )
)
def api_check_operation_outcome_any_issue_details_coding(fresponse, coding_type):
    api_steps.api_check_operation_outcome_any_issue_by_key_value(
        fresponse,
        key="details",
        value=CODING_MAP[coding_type],
    )

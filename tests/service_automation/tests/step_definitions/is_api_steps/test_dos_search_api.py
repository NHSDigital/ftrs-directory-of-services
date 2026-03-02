import json

from loguru import logger
from playwright._impl._errors import Error as PlaywrightError
from playwright.sync_api import APIRequestContext, APIResponse
from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps import api_steps
from step_definitions.common_steps.api_steps import *  # noqa: F403
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.schema_validation_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from step_definitions.is_api_steps.dos_search_response_steps import *  # noqa: F403
from utilities.infra.api_util import get_r53, get_url
from utilities.infra.dns_util import wait_for_dns

CODING_MAP = {
    "REC_BAD_REQUEST": {
        "coding": [
            {
                "system": "https://fhir.nhs.uk/CodeSystem/http-error-codes",
                "version": "1",
                "code": "REC_BAD_REQUEST",
                "display": "400: The Receiver was unable to process the request.",
            }
        ]
    },
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

# Single source of truth for mandatory headers to ensure consistency across tests and maintainability
MANDATORY_APIM_REQUEST_HEADERS: dict[str, str] = {
    # APIM headers send X-Request-Id as APIM maps this value to NHSD-Request-Id
    "X-Request-Id": "req_id",
    "version": "1",
}

MANDATORY_APIG_REQUEST_HEADERS: dict[str, str] = {
    # Direct requests to API Gateway directly send NHSD-Request-Id
    "NHSD-Request-Id": "req_id",
    "version": "1",
}

# Load feature file
scenarios(
    "./is_api_features/dos_search_backend.feature",
    "./is_api_features/dos_search_apim.feature",
    "./is_api_features/dos_search_apim_security.feature",
    "./is_api_features/dos_search_apim_headers.feature",
    "./is_api_features/dos_search_response_structure.feature",
    "./is_api_features/dos_search_smoke_tests.feature",
)


@given(parsers.re(r'the dns for "(?P<api_name>.*?)" is resolvable'))
def dns_resolvable(api_name: str, env: str, workspace: str) -> None:
    r53 = get_r53(workspace, api_name, env)
    assert wait_for_dns(r53)


@when(
    parsers.re(
        r'I request data from the "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" with valid query params and additional headers "(?P<headers>.*?)"'
    ),
    target_fixture="fresponse",
)
def send_get_with_params_with_headers(
    api_request_context_mtls: APIRequestContext,
    api_name: str,
    resource_name: str,
    headers: str,
) -> APIResponse:
    # headers can be manipulated in individual tests if needed
    params = "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046"
    headers = {**MANDATORY_APIG_REQUEST_HEADERS, **json.loads(headers)}
    url = get_url(api_name) + "/" + resource_name
    logger.info(
        f"Requesting URL: {url} HERE with params: {params} with headers: {headers}"
    )
    return _send_api_request(api_request_context_mtls, url, params, headers)


@when(
    parsers.re(
        r'I request data from the "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)"'
    ),
    target_fixture="fresponse",
)
def send_get_with_params(
    api_request_context_mtls: APIRequestContext,
    api_name: str,
    params: str,
    resource_name: str,
) -> APIResponse:
    # headers can be manipulated in individual tests if needed
    headers = {**MANDATORY_APIG_REQUEST_HEADERS}
    url = get_url(api_name) + "/" + resource_name
    logger.info(f"Requesting URL: {url} with params: {params} with headers: {headers}")
    return _send_api_request(api_request_context_mtls, url, params, headers)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)"'
    ),
    target_fixture="fresponse",
)
def send_to_apim_get_with_params(
    apim_request_context: APIRequestContext,
    nhsd_apim_proxy_url: str,
    params: str,
    resource_name: str,
) -> APIResponse:
    headers = {**MANDATORY_APIM_REQUEST_HEADERS}
    url = nhsd_apim_proxy_url + "/" + resource_name

    return _send_api_request(apim_request_context, url, params, headers)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)" with headers "(?P<headers>.*?)"'
    ),
    target_fixture="fresponse",
)
def send_to_apim_get_with_params_with_headers(
    apim_request_context: APIRequestContext,
    nhsd_apim_proxy_url: str,
    params: str,
    resource_name: str,
    headers: str,
) -> APIResponse:
    headers = {**json.loads(headers)}
    url = nhsd_apim_proxy_url + "/" + resource_name

    return _send_api_request(apim_request_context, url, params, headers)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)" without authentication'
    ),
    target_fixture="fresponse",
)
def send_to_apim_no_auth(
    api_request_context: APIRequestContext,
    nhsd_apim_proxy_url: str,
    params: str,
    resource_name: str,
) -> APIResponse:
    headers = {**MANDATORY_APIM_REQUEST_HEADERS}
    url = nhsd_apim_proxy_url + "/" + resource_name
    return _send_api_request(api_request_context, url, params, headers)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)" with invalid token'
    ),
    target_fixture="fresponse",
)
def send_to_apim_invalid_token(
    apim_request_context: APIRequestContext,
    nhsd_apim_proxy_url: str,
    params: str,
    resource_name: str,
) -> APIResponse:
    # Using mandatory headers as base and adding Authorization header with invalid token for this test case
    headers = {
        **MANDATORY_APIM_REQUEST_HEADERS,
        "Authorization": "Bearer invalid_token",
    }
    url = nhsd_apim_proxy_url + "/" + resource_name
    return _send_api_request(apim_request_context, url, params, headers)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)" with status token'
    ),
    target_fixture="fresponse",
)
def send_to_apim_status_token(
    apim_request_context: APIRequestContext,
    status_endpoint_auth_headers: dict[str, str],
    nhsd_apim_proxy_url: str,
    params: str,
    resource_name: str,
) -> APIResponse:
    url = nhsd_apim_proxy_url + "/" + resource_name
    return _send_api_request(
        apim_request_context, url, params, status_endpoint_auth_headers
    )


def _send_api_request(
    request_context: APIRequestContext,
    url: str,
    params: str | None = None,
    headers: dict[str, str] | None = None,
) -> APIResponse:
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
def api_check_operation_outcome_any_issue_details_coding(
    fresponse: APIResponse, coding_type: str
) -> None:
    api_steps.api_check_operation_outcome_any_issue_by_key_value(
        fresponse,
        key="details",
        value=CODING_MAP[coding_type],
    )


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with an odscode from dynamo organisation table but without authentication'
    ),
    target_fixture="fresponse",
)
def send_to_apim_no_auth_with_ods_code(
    api_request_context: APIRequestContext,
    dos_search_service_url: str,
    resource_name: str,
    ods_code: str,
) -> APIResponse:
    headers = {**MANDATORY_APIM_REQUEST_HEADERS}
    url = dos_search_service_url + "/" + resource_name
    params = f"_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|{ods_code}"
    return _send_api_request(api_request_context, url, params, headers)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with an odscode from dynamo organisation table but with invalid token'
    ),
    target_fixture="fresponse",
)
def send_to_apim_invalid_token_with_ods_code(
    api_request_context: APIRequestContext,
    dos_search_service_url: str,
    resource_name: str,
    ods_code: str,
) -> APIResponse:
    logger.info(
        f"Requesting APIM URL: {dos_search_service_url}/{resource_name} with ODS code: {ods_code}"
    )
    url = dos_search_service_url + "/" + resource_name
    headers = {
        **MANDATORY_APIM_REQUEST_HEADERS,
        "Authorization": "Bearer invalid_token",
    }
    params = f"_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|{ods_code}"
    # logger.info(f"Requesting URL: {url} with params: {params} with headers: {headers}")
    return _send_api_request(api_request_context, url, params, headers)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with an odscode from dynamo organisation table'
    ),
    target_fixture="fresponse",
)
def send_to_apim_get_with_ods_code_from_dynamo(
    api_request_context: APIRequestContext,
    dos_search_service_url: str,
    resource_name: str,
    ods_code: str,
    apim_token: str,
) -> APIResponse:
    logger.info(
        f"Requesting APIM URL: {dos_search_service_url}/{resource_name} with ODS code: {ods_code}"
    )
    url = dos_search_service_url + "/" + resource_name
    headers = {
        **MANDATORY_APIM_REQUEST_HEADERS,
        "Authorization": f"Bearer {apim_token}",
    }
    params = f"_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|{ods_code}"
    # logger.info(f"Requesting URL: {url} with params: {params} with headers: {headers}")
    return _send_api_request(api_request_context, url, params, headers)


@when(
    parsers.re(
        r'I attempt to request data from the "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" without authentication but with valid query params "(?P<params>.*?)"'
    ),
    target_fixture="connection_error",
)
def send_get_with_params_no_auth_expecting_error(
    api_request_context: APIRequestContext,
    api_name: str,
    params: str,
    resource_name: str,
) -> dict[str, str | None]:
    url = get_url(api_name) + "/" + resource_name
    error_details = {"error_type": None, "error_message": None}
    try:
        _send_api_request(api_request_context, url, params)
    except PlaywrightError as e:
        error_details["error_type"] = "PlaywrightError"
        error_details["error_message"] = str(e)
        logger.info(f"Caught expected connection error: {e}")
    return error_details


@when(
    parsers.re(
        r'I attempt to request data from the "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" with an odscode from dynamo organisation table but without authentication'
    ),
    target_fixture="connection_error",
)
def send_get_with_ods_code_no_auth_expecting_error(
    api_request_context: APIRequestContext,
    api_name: str,
    resource_name: str,
    ods_code: str,
) -> dict[str, str | None]:
    url = get_url(api_name) + "/" + resource_name
    params = f"_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|{ods_code}"
    error_details = {"error_type": None, "error_message": None}
    try:
        _send_api_request(api_request_context, url, params)
    except PlaywrightError as e:
        error_details["error_type"] = "PlaywrightError"
        error_details["error_message"] = str(e)
        logger.info(f"Caught expected connection error: {e}")
    return error_details


@then(parsers.re("I receive a connection reset error"))
def check_connection_reset_error(connection_error: dict[str, str | None]) -> None:
    assert connection_error["error_message"] is not None, (
        "Expected a connection error but none was raised"
    )
    assert "ECONNRESET" in connection_error["error_message"]


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>[^"]+)" with query params "(?P<params>[^"]+)" with malformed auth header'
    ),
    target_fixture="fresponse",
)
def send_to_apim_with_malformed_auth(
    apim_request_context: APIRequestContext,
    nhsd_apim_proxy_url: str,
    params: str,
    resource_name: str,
) -> APIResponse:
    """Send request to APIM with a malformed Authorization header."""
    url = nhsd_apim_proxy_url + "/" + resource_name
    headers = {**MANDATORY_APIM_REQUEST_HEADERS, "Authorization": "MalformedHeader"}
    logger.info(f"Requesting URL: {url} with params: {params} with headers: {headers}")
    return _send_api_request(apim_request_context, url, params, headers)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>[^"]+)" with query params "(?P<params>[^"]+)" with empty auth header'
    ),
    target_fixture="fresponse",
)
def send_to_apim_with_empty_auth(
    apim_request_context: APIRequestContext,
    nhsd_apim_proxy_url: str,
    params: str,
    resource_name: str,
) -> APIResponse:
    """Send request to APIM with an empty Authorization header."""
    url = nhsd_apim_proxy_url + "/" + resource_name
    headers = {**MANDATORY_APIM_REQUEST_HEADERS, "Authorization": ""}
    return _send_api_request(apim_request_context, url, params, headers)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>[^"]+)" with an odscode from dynamo organisation table but with malformed auth header'
    ),
    target_fixture="fresponse",
)
def send_to_apim_with_ods_code_malformed_auth(
    api_request_context: APIRequestContext,
    dos_search_service_url: str,
    resource_name: str,
    ods_code: str,
) -> APIResponse:
    """Send request to APIM with a malformed Authorization header."""
    url = dos_search_service_url + "/" + resource_name
    params = f"_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|{ods_code}"
    headers = {**MANDATORY_APIM_REQUEST_HEADERS, "Authorization": "MalformedHeader"}
    return _send_api_request(api_request_context, url, params, headers)


@when(
    parsers.re(
        r'I request data from the APIM endpoint "(?P<resource_name>[^"]+)" with an odscode from dynamo organisation table but with empty auth header'
    ),
    target_fixture="fresponse",
)
def send_to_apim_with_ods_code_empty_auth(
    api_request_context: APIRequestContext,
    dos_search_service_url: str,
    resource_name: str,
    ods_code: str,
) -> APIResponse:
    """Send request to APIM with an empty Authorization header."""
    url = dos_search_service_url + "/" + resource_name
    params = f"_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|{ods_code}"
    headers = {**MANDATORY_APIM_REQUEST_HEADERS, "Authorization": ""}
    return _send_api_request(api_request_context, url, params, headers)

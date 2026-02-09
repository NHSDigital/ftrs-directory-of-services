import os
from pathlib import Path

import pytest
from loguru import logger
from playwright._impl._errors import Error as PlaywrightError
from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps import api_steps
from step_definitions.common_steps.api_steps import *  # noqa: F403
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from utilities.infra.api_util import get_r53, get_url
from utilities.infra.dns_util import wait_for_dns
from utilities.infra.schema_validator import validate_api_response

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
}

# Load feature file
scenarios(
    "./is_api_features/dos_search_backend_headers.feature",
    "./is_api_features/dos_search_backend_parameters.feature",
    "./is_api_features/dos_search_backend_gateway_errors.feature",
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
        r'I request data from the "(?P<api_name>[^"]+)" endpoint "(?P<resource_name>[^"]+)" with header "(?P<header_params>[^"]+)" with query params "(?P<params>[^"]+)"'
    ),
    target_fixture="fresponse",
)
def send_get_with_headers_and_params(
    api_request_context_mtls,
    api_name: str,
    params: str,
    resource_name: str,
    header_params: str,
):
    """Send request to backend with headers and query params."""
    url = get_url(api_name) + "/" + resource_name

    # Parse headers - support both "Key: Value" and "Key=Value" formats
    headers = _convert_params_str_to_dict(header_params)
    logger.info(f"Requesting URL: {url} with params: {params} and headers: {headers}")

    return _send_api_request(api_request_context_mtls, url, params, headers)


@when(
    parsers.re(
        r'I request data from the "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)"'
    ),
    target_fixture="fresponse",
)
def send_get_with_params(api_request_context_mtls, api_name, params, resource_name):
    url = get_url(api_name) + "/" + resource_name
    logger.info(f"Requesting URL: {url} with params: {params}")
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
        r'I request data from the APIM endpoint "(?P<resource_name>.*?)" with header "(?P<header_params>.*?)" and query params "(?P<params>.*?)"'
    ),
    target_fixture="fresponse",
)
def send_to_apim_with_header(
    apim_request_context,
    nhsd_apim_auth_headers,
    nhsd_apim_proxy_url,
    params: str,
    resource_name: str,
    header_params: str,
):
    """Send request to APIM with specific header merged with auth headers."""
    url = nhsd_apim_proxy_url + "/" + resource_name

    # Start with auth headers and add header from key=value pairs
    headers = {**nhsd_apim_auth_headers}
    additional_headers = _convert_params_str_to_dict(header_params)
    headers.update(additional_headers)

    return _send_api_request(apim_request_context, url, params, headers)


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

    logger.info(f"response: {response.json()}")

    return response


def _convert_params_str_to_dict(params: str | None) -> dict[str, str]:
    if not params:
        return {}

    return dict(param.split("=", 1) for param in params.split("&") if "=" in param)


@when(
    parsers.re(
        r'I attempt to request data from the "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" without authentication but with valid query params "(?P<params>.*?)"'
    ),
    target_fixture="connection_error",
)
def send_get_with_params_no_auth_expecting_error(
    api_request_context, api_name, params, resource_name
):
    url = get_url(api_name) + "/" + resource_name
    error_details = {"error_type": None, "error_message": None}
    try:
        _send_api_request(api_request_context, url, params)
    except PlaywrightError as e:
        error_details["error_type"] = "PlaywrightError"
        error_details["error_message"] = str(e)
        logger.info(f"Caught expected connection error: {e}")
    return error_details


@then(parsers.parse("I receive a connection reset error"))
def check_connection_reset_error(connection_error):
    assert connection_error["error_type"] == "PlaywrightError"
    assert "ECONNRESET" in connection_error["error_message"]


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


@then(
    parsers.parse(
        'the response is valid against the dos-search schema for endpoint "{endpoint_path}"'
    )
)
def validate_response_against_dos_search_schema(fresponse, endpoint_path: str) -> None:
    """
    Validate the API response against the OpenAPI schema.

    Args:
        fresponse: The API response fixture
        endpoint_path: The API endpoint path (e.g., "/Organization")
    """
    # Path to the dos-search.yaml schema file - navigate from current file to repo root
    current_file = Path(__file__).resolve()
    repo_root = current_file.parents[
        5
    ]  # Go up: is_api_steps -> step_definitions -> tests -> service_automation -> tests -> repo_root
    schema_path = repo_root / "docs" / "specification" / "dos-search.yaml"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    # Get response data
    response_data = fresponse.json()
    status_code = str(fresponse.status)

    # Validate response
    is_valid, error_msg = validate_api_response(
        response_data=response_data,
        schema_path=str(schema_path),
        endpoint_path=endpoint_path,
        method="get",
        status_code=status_code,
    )

    assert is_valid, f"Response validation failed: {error_msg}"
    logger.info(f"Response successfully validated against schema for {endpoint_path}")


def _send_api_request(request_context, url, params: str = None, headers=None):
    param_dict = _convert_params_str_to_dict(params)

    response = request_context.get(
        url,
        params=param_dict,
        headers=headers,
    )
    return response


def _convert_params_str_to_dict(params: str | None) -> dict[str, str]:
    if not params:
        return {}

    return dict(param.split("=", 1) for param in params.split("&") if "=" in param)

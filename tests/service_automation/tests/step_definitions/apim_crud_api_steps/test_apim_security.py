from pytest_bdd import when, then, parsers, scenarios
from utilities.common.constants import ENDPOINTS
from utilities.common.json_helper import read_json_file
from step_definitions.common_steps.api_steps import *
from loguru import logger
from pathlib import Path
from typing import Optional

# Load feature file
scenarios("./apim_crud_api_features/apim_security.feature")

DEFAULT_PAYLOAD_PATH = (
    Path(__file__).resolve().parent
    / "../../json_files/Organisation/organisation-payload.json"
)


def _load_default_payload() -> dict:
    """Load the default organisation payload from JSON."""
    logger.info(f"Loading default payload from {DEFAULT_PAYLOAD_PATH}")
    return read_json_file(DEFAULT_PAYLOAD_PATH)


def build_endpoint(endpoint: str, org_id: Optional[str] = None) -> str:
    """Construct full endpoint URL including optional org_id."""
    logger.info(f"Building endpoint for: endpoint={endpoint}, org_id={org_id}")
    base_endpoint = ENDPOINTS.get(endpoint)
    if not base_endpoint:
        raise ValueError(f"Endpoint '{endpoint}' not found in ENDPOINTS")
    return f"{base_endpoint}/{org_id}" if org_id else base_endpoint


def send_api_request(
    request_context,
    method: str,
    endpoint: str,
    dos_ingestion_service_url: str,
    api_key: Optional[str] = None,
    payload: Optional[dict] = None,
    content_type: str = "application/fhir+json",
):
    """Generic function to send an API request with Playwright sync API."""
    url = f"{dos_ingestion_service_url.rstrip('/')}{endpoint}"
    headers = {"Content-Type": content_type}
    if api_key:
        headers["apikey"] = api_key

    data = payload if payload else None
    logger.info(f"Sending {method} request to {url}")
    logger.info(f"Headers: {headers}")
    if payload:
        logger.info(f"Payload: {payload}")

    if method.upper() == "GET":
        response = request_context.get(url, headers=headers)
    elif method.upper() == "PUT":
        response = request_context.put(url, headers=headers, data=payload)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    logger.info(f"Response received: Status Code = {response.status}")
    try:
        logger.info(f"Response Body: {response.json()}")
    except Exception:
        logger.info(f"Response Body (non-JSON): {response.text()}")
    return response


def _send_put_request(
    request_context,
    dos_ingestion_service_url: str,
    endpoint: str,
    api_key: Optional[str],
):
    """Helper to send a PUT request with optional API key."""
    payload = _load_default_payload()
    org_id = payload.get("id")
    full_endpoint = build_endpoint(endpoint, org_id)
    return send_api_request(
        request_context,
        "PUT",
        full_endpoint,
        dos_ingestion_service_url,
        api_key,
        payload,
    )


@when(
    parsers.parse('I send a GET request to the "{endpoint}" endpoint'),
    target_fixture="fresponse",
)
@when(
    parsers.cfparse(
        'I send a GET request to the "{endpoint}" endpoint without authentication'
    ),
    target_fixture="fresponse",
)
def step_get(api_request_context_mtls, dos_ingestion_service_url: str, endpoint: str):
    return send_api_request(
        api_request_context_mtls,
        "GET",
        ENDPOINTS.get(endpoint, endpoint),
        dos_ingestion_service_url,
    )


@when(
    parsers.cfparse(
        'I send a PUT request to the "{endpoint}" endpoint without authentication'
    ),
    target_fixture="fresponse",
)
def step_put_no_auth(
    api_request_context_mtls, dos_ingestion_service_url: str, endpoint: str
):
    return _send_put_request(
        api_request_context_mtls, dos_ingestion_service_url, endpoint, api_key=None
    )


@when(
    parsers.cfparse(
        'I send a PUT request to the "{endpoint}" endpoint with invalid API key "{api_key}"'
    ),
    target_fixture="fresponse",
)
def step_put_invalid_key(
    api_request_context_mtls,
    dos_ingestion_service_url: str,
    endpoint: str,
    api_key: str,
):
    return _send_put_request(
        api_request_context_mtls, dos_ingestion_service_url, endpoint, api_key
    )

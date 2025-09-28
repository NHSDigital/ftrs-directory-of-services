from pytest_bdd import when, then, parsers, scenarios
from utilities.common.constants import ENDPOINTS
from utilities.common.json_helper import read_json_file
from loguru import logger
import requests
import json
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
    method: str,
    endpoint: str,
    dos_ingestion_service_url: str,
    api_key: Optional[str] = None,
    payload: Optional[dict] = None,
    content_type: str = "application/fhir+json",
) -> requests.Response:
    """Generic function to send an API request with logging."""
    url = f"{dos_ingestion_service_url.rstrip('/')}{endpoint}"
    headers = {"Content-Type": content_type}
    if api_key:
        headers["apikey"] = api_key

    data = json.dumps(payload, indent=2) if payload else None
    logger.info(f"Sending {method} request to {url}")
    logger.info(f"Headers: {headers}")
    if payload:
        logger.info(f"Payload: {data}")

    response = requests.request(method, url, headers=headers, data=data)
    logger.info(f"Response received: Status Code = {response.status_code}")
    try:
        logger.info(f"Response Body: {response.json()}")
    except ValueError:
        logger.info(f"Response Body (non-JSON): {response.text}")
    return response


def _send_put_request(
    dos_ingestion_service_url: str, endpoint: str, api_key: Optional[str]
) -> requests.Response:
    """Helper to send a PUT request with optional API key."""
    payload = _load_default_payload()
    org_id = payload.get("id")
    full_endpoint = build_endpoint(endpoint, org_id)
    return send_api_request(
        "PUT", full_endpoint, dos_ingestion_service_url, api_key, payload
    )


@when(
    parsers.parse('I send a GET request to the "{endpoint}" endpoint'),
    target_fixture="response",
)
@when(
    parsers.cfparse(
        'I send a GET request to the "{endpoint}" endpoint without authentication'
    ),
    target_fixture="response",
)
def step_get(dos_ingestion_service_url: str, endpoint: str):
    return send_api_request(
        "GET", ENDPOINTS.get(endpoint, endpoint), dos_ingestion_service_url
    )


@when(
    parsers.cfparse(
        'I send a PUT request to the "{endpoint}" endpoint without authentication'
    ),
    target_fixture="response",
)
def step_put_no_auth(dos_ingestion_service_url: str, endpoint: str):
    return _send_put_request(dos_ingestion_service_url, endpoint, api_key=None)


@when(
    parsers.cfparse(
        'I send a PUT request to the "{endpoint}" endpoint with invalid API key "{api_key}"'
    ),
    target_fixture="response",
)
def step_put_invalid_key(dos_ingestion_service_url: str, endpoint: str, api_key: str):
    return _send_put_request(dos_ingestion_service_url, endpoint, api_key)


@then(parsers.parse('I receive a status code "{status_code:d}"'))
def step_validate_status(response: requests.Response, status_code: int):
    logger.info(
        f"Validating status code: expected={status_code}, actual={response.status_code}"
    )
    assert response.status_code == status_code, (
        f"Expected {status_code}, got {response.status_code}"
    )


@then(parsers.parse('the response should contain "{expected_message}"'))
def step_validate_message(response: requests.Response, expected_message: str):
    """Optional stronger assertion for body message validation."""
    body = response.text
    logger.info(
        f"Validating response body contains '{expected_message}'. Actual: {body}"
    )
    assert expected_message in body, f"Expected message '{expected_message}' not found."

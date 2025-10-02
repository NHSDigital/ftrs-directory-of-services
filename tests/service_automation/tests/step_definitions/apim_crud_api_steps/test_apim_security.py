from pytest_bdd import when, parsers, scenarios
from utilities.common.constants import ENDPOINTS
from utilities.common.json_helper import read_json_file
from step_definitions.common_steps.api_steps import *
from loguru import logger
from pathlib import Path
from typing import Optional
import json

# Load the feature file
scenarios("./apim_crud_api_features/apim_security.feature")

DEFAULT_PAYLOAD_PATH = (
    Path(__file__).resolve().parent
    / "../../json_files/Organisation/organisation-payload.json"
)


def load_payload() -> dict:
    """Load fresh organisation payload from JSON file."""
    payload = read_json_file(DEFAULT_PAYLOAD_PATH)
    logger.info(f"Loaded payload: {payload}")
    return payload


def send_request(
    playwright,
    method: str,
    base_url: str,
    endpoint: str,
    api_key: Optional[str] = None,
    payload: Optional[dict] = None,
    org_id: Optional[str] = None,
):
    """Send GET or PUT request, optionally with API key and payload."""
    if method.upper() == "PUT" and payload is None:
        payload = load_payload()
        if org_id is None:
            org_id = payload.get("id")

    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    if org_id:
        url = f"{url}/{org_id}"

    headers = {"Content-Type": "application/fhir+json"}
    if api_key:
        headers["apikey"] = api_key

    logger.info(f"➡️ {method.upper()} {url}")
    logger.info(f"Headers: {headers}")
    if payload:
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")

    context = playwright.request.new_context(ignore_https_errors=True)
    try:
        if method.upper() == "GET":
            response = context.get(url, headers=headers)
        elif method.upper() == "PUT":
            response = context.put(url, headers=headers, data=json.dumps(payload))
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        logger.info(f"⬅️ Response Status: {response.status}")
        try:
            logger.info(f"Response Body: {response.json()}")
        except Exception:
            logger.info(f"Response Body (non-JSON): {response.text()}")
        return response
    finally:
        context.dispose()


@when(
    parsers.parse('I send a GET request to the "{endpoint}" endpoint'),
    target_fixture="fresponse",
)
def step_get(playwright, dos_ingestion_service_url: str, endpoint: str, api_key: str):
    return send_request(
        playwright,
        "GET",
        dos_ingestion_service_url,
        ENDPOINTS.get(endpoint, endpoint),
        api_key=api_key,
    )


@when(
    parsers.cfparse(
        'I send a GET request to the "{endpoint}" endpoint without authentication'
    ),
    target_fixture="fresponse",
)
def step_get_no_auth(playwright, dos_ingestion_service_url: str, endpoint: str):
    return send_request(
        playwright, "GET", dos_ingestion_service_url, ENDPOINTS.get(endpoint, endpoint)
    )


@when(
    parsers.cfparse(
        'I send a PUT request to the "{endpoint}" endpoint without authentication'
    ),
    target_fixture="fresponse",
)
def step_put_no_auth(playwright, dos_ingestion_service_url: str, endpoint: str):
    payload = load_payload()
    org_id = payload.get("id")
    return send_request(
        playwright,
        "PUT",
        dos_ingestion_service_url,
        ENDPOINTS.get(endpoint, endpoint),
        payload=payload,
        org_id=org_id,
    )


@when(
    parsers.cfparse(
        'I send a PUT request to the "{endpoint}" endpoint with invalid API key "{api_key}"'
    ),
    target_fixture="fresponse",
)
def step_put_invalid_key(
    playwright, dos_ingestion_service_url: str, endpoint: str, api_key: str
):
    payload = load_payload()
    org_id = payload.get("id")
    return send_request(
        playwright,
        "PUT",
        dos_ingestion_service_url,
        ENDPOINTS.get(endpoint, endpoint),
        payload=payload,
        org_id=org_id,
        api_key=api_key,
    )

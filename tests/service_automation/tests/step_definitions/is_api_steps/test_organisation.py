from pytest_bdd import scenarios, when
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from step_definitions.common_steps.api_steps import *  # noqa: F403
from utilities.common.json_helper import read_json_file
import json
from loguru import logger


# Load feature file
scenarios("./is_api_features/organisation_api.feature")

def update_organisation(payload_path: str, api_request_context_api_key, service_url: str, api_key: str):
    """
    Function to update the organisation details using the provided payload.
    """
    payload = read_json_file(payload_path)
    org_id = payload.get("id")
    if not org_id:
        raise ValueError("Payload must include 'id'")

    url_path = f"Organization/{org_id}"
    full_url = f"{service_url.rstrip('/')}/{url_path}"

    logger.info(f"Full URL: {full_url}")
    logger.info(f"Request URL Path: {url_path}")
    logger.info(f"Using API key: {api_key[:4]}**** (hidden for safety)")
    logger.info(f"Request payload: {json.dumps(payload, indent=2)}")

    # Send PUT request to the API with the payload
    response = api_request_context_api_key.put(full_url, data=json.dumps(payload))
    try:
        response_body = response.json()
    except Exception:
        response_body = response.text

    logger.info(f"Response status: {response.status}")
    logger.info(f"Response body: {response_body}")

    return response

@when('I update the organisation details for ODS Code', target_fixture="fresponse")
@when('I update the organisation details using the same data for the ODS Code', target_fixture="fresponse")
def update_organisation_details(api_request_context_api_key, service_url, api_key):
    """
    Step to update the organisation details using the payload from a JSON file.
    """
    payload_path = "../../json_files/Organisation/organisation-payload.json"
    response = update_organisation(payload_path, api_request_context_api_key, service_url, api_key)
    return response

@when('I update the organisation details for ODS Code with mandatory fields only', target_fixture="fresponse")
def update_organisation_details_mandatoryfield(api_request_context_api_key, service_url, api_key):
    """
    Step to update the organisation details with mandatory fields only (removes optional fields like telecom).
    """
    payload_path = "../../json_files/Organisation/organisation-payload.json"
    payload = read_json_file(payload_path)
    payload.pop("telecom", None)  # Remove optional fields (telecom)
    logger.info(f"Payload with mandatory fields only: {payload}")
    return update_organisation(payload_path, api_request_context_api_key, service_url, api_key)

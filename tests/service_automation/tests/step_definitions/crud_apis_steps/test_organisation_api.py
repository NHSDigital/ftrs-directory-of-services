import json
from loguru import logger
from pytest_bdd import scenarios, when, then, parsers
from utilities.common.json_helper import read_json_file
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from step_definitions.common_steps.api_steps import *  # noqa: F403
from utilities.common.context import Context
from utilities.common.constants import ENDPOINTS
from utilities.infra.api_util import get_url

# Load feature file
scenarios("./apim_crud_apis_features/apim_organisation_api.feature")
scenarios("./crud_apis_features/organisation_api.feature")


def update_organisation_apim(
    payload: dict, api_request_context_api_key_factory, dos_ingestion_service_url: str
):
    """Send PUT request to update an organization."""
    org_id = payload.get("id")
    if not org_id:
        raise ValueError("Payload must include 'id'")
    full_url = (
        f"{dos_ingestion_service_url.rstrip('/')}{ENDPOINTS['organization']}/{org_id}"
    )
    logger.info(f"Full URL: {full_url}\nPayload: {json.dumps(payload, indent=2)}")
    response = api_request_context_api_key_factory("dos-ingestion").put(
        full_url, data=json.dumps(payload)
    )
    try:
        logger.info(f"Response body: {response.json()}")
    except Exception:
        logger.info(f"Response body: {response.text}")
    return response


def update_organisation(payload: dict, api_request_context_mtls_crud):
    """Send PUT request to update an organization."""
    org_id = payload.get("id")
    if not org_id:
        raise ValueError("Payload must include 'id'")
    full_url = f"{get_url('crud')}{ENDPOINTS['organization']}/{org_id}"
    logger.info(f"Full URL: {full_url}\nPayload: {json.dumps(payload, indent=2)}")
    response = api_request_context_mtls_crud.put(
        full_url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/fhir+json"},
    )
    try:
        logger.info(f"Response body: {response.json()}")
    except Exception:
        logger.info(f"Response body: {response.text}")
    return response


def get_db_item(model_repo, payload: dict):
    """Fetch item from DB by ODS code."""
    ods_code = payload["identifier"][0]["value"]
    item = get_from_repo(model_repo, ods_code)
    assert item, f"No data found in repository for ODS code {ods_code}"
    return item


def assert_item_matches_payload(item, payload, mandatory_only=False):
    """Assert DB item matches payload."""
    expected = {
        "identifier_ODS_ODSCode": payload["identifier"][0]["value"],
        "name": payload["name"],
        "type": payload["type"][0]["text"],
        "active": payload["active"],
        "modifiedBy": "ODS_ETL_PIPELINE",
    }
    if not mandatory_only:
        expected["telecom"] = payload.get("telecom", [{}])[0].get("value")

    for attr, exp in expected.items():
        actual = getattr(item, attr, None)
        logger.info(f"Validating {attr}: expected={exp}, actual={actual}")
        assert actual == exp, f"{attr} mismatch: {actual} != {exp}"


def update_payload_field(field: str, value: str):
    """Update a specific field in the payload."""
    payload = read_json_file("../../json_files/Organisation/organisation-payload.json")

    if field == "name":
        payload["name"] = value
    elif field == "type":
        if "type" not in payload or not payload["type"]:
            payload["type"] = [{"coding": [], "text": value}]
        else:
            payload["type"][0]["text"] = value
    elif field == "telecom":
        if "telecom" not in payload or not payload["telecom"]:
            payload["telecom"] = [{"system": "phone", "value": value}]
        else:
            payload["telecom"][0]["value"] = value
    else:
        raise ValueError(f"Unknown field: {field}")

    logger.info(
        f"Updated payload field '{field}' with value '{value}': {json.dumps(payload, indent=2)}"
    )
    return payload


@when(
    "I update the organisation details for ODS Code via APIM",
    target_fixture="fresponse",
)
def update_organisation_details_apim(
    api_request_context_api_key_factory, dos_ingestion_service_url, context: Context
):
    payload = read_json_file("../../json_files/Organisation/organisation-payload.json")
    context.other["current_payload"] = payload
    return update_organisation_apim(
        payload, api_request_context_api_key_factory, dos_ingestion_service_url
    )


@when("I update the organisation details for ODS Code", target_fixture="fresponse")
@when(
    "I update the organisation details using the same data for the ODS Code",
    target_fixture="fresponse",
)
def update_organisation_details(api_request_context_mtls_crud, context: Context):
    payload = read_json_file("../../json_files/Organisation/organisation-payload.json")
    context.other["current_payload"] = payload
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    "I update the organisation details for ODS Code with mandatory fields only",
    target_fixture="fresponse",
)
def update_organisation_details_mandatoryfield(
    api_request_context_mtls_crud, context: Context
):
    payload = read_json_file("../../json_files/Organisation/organisation-payload.json")
    payload.pop("telecom", None)
    logger.info(f"Payload with mandatory fields only: {json.dumps(payload, indent=2)}")
    context.other["current_payload"] = payload
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.cfparse('I set the "{field}" field to "{value}"'),
    target_fixture="fresponse",
)
def set_field_and_update(
    field: str, value: str, context: Context, api_request_context_mtls_crud
):
    payload = update_payload_field(field, value)
    context.other["current_payload"] = payload
    return update_organisation(payload, api_request_context_mtls_crud)


@then("the data in the database matches the inserted payload")
def assert_model_matches_repo(model_repo, context: Context):
    payload = context.other.get("current_payload")
    item = get_db_item(model_repo, payload)
    assert_item_matches_payload(item, payload)


@then("the data in the database matches the inserted payload with telecom null")
def assert_model_matches_repo_mandatory_only(model_repo, context: Context):
    payload = context.other.get("current_payload")
    item = get_db_item(model_repo, payload)
    assert_item_matches_payload(item, payload, mandatory_only=True)
    actual_telecom = getattr(item, "telecom", None)
    logger.info(f"Actual telecom in DB: {actual_telecom}")
    assert actual_telecom is None, (
        f"telecom is expected to be null, but got: {actual_telecom}"
    )


@then('I receive a status code "200" in response and save the modifiedBy timestamp')
def validate_status_and_save_modified(fresponse, context: Context, model_repo):
    assert fresponse.status == 200, f"Expected 200, got {fresponse.status}"
    payload = context.other.get("current_payload")
    item = get_db_item(model_repo, payload)
    context.other["modifiedBy_timestamp"] = getattr(item, "modifiedBy", None)
    context.other["modifiedDateTime"] = getattr(item, "modifiedDateTime", None)
    logger.info(
        f"Saved modifiedBy: {context.other['modifiedBy_timestamp']}, modifiedDateTime: {context.other['modifiedDateTime']}"
    )


@then("the database matches the inserted payload with the same modifiedBy timestamp")
def assert_database_modifiedBy_unchanged(context: Context, model_repo):
    payload = context.other.get("current_payload")
    item = get_db_item(model_repo, payload)
    assert_item_matches_payload(item, payload)
    saved_modifiedDateTime = context.other.get("modifiedDateTime")
    current_modifiedDateTime = getattr(item, "modifiedDateTime", None)
    assert current_modifiedDateTime == saved_modifiedDateTime, (
        f"modifiedDateTime changed! First: {saved_modifiedDateTime}, Now: {current_modifiedDateTime}"
    )
    logger.info(f"modifiedDateTime unchanged: {current_modifiedDateTime}")


@then(parsers.cfparse('the database reflects "{field}" with value "{value}"'))
def validate_db_field(field: str, value: str, context: Context, model_repo):
    if field == "active":
        logger.info("Skipping DB validation for 'active' field")
        return
    payload = context.other.get("current_payload")
    item = get_db_item(model_repo, payload)
    actual = (
        getattr(item, field, None)
        if field != "telecom"
        else getattr(item, "telecom", None)
    )
    expected = value
    logger.info(f"Validating DB field '{field}': expected={expected}, actual={actual}")
    assert actual == expected, f"{field} mismatch: expected {expected}, got {actual}"


@when(
    parsers.parse('I send a GET request to the "{endpoint}" endpoint'),
    target_fixture="fresponse",
)
def send_get_request(
    endpoint: str,
    api_request_context_api_key_factory,
    dos_ingestion_service_url: str,
    api_key: str,
):
    """Send a GET request to the specified endpoint."""
    url = f"{dos_ingestion_service_url.rstrip('/')}{ENDPOINTS.get(endpoint, endpoint)}"
    logger.info(f"Sending GET request to {url}")
    response = api_request_context_api_key_factory("dos-ingestion").get(url)
    try:
        logger.info(f"Response [{response.status}]: {response.json()}")
    except Exception:
        logger.info(f"Response [{response.status}]: {response.text}")
    return response

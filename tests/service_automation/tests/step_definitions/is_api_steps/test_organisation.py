import json
from loguru import logger
from pytest_bdd import scenarios, when, then
from utilities.common.json_helper import read_json_file
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from step_definitions.common_steps.api_steps import *  # noqa: F403


# Load feature file
scenarios("./is_api_features/organisation_api.feature")

def update_organisation(payload: dict, api_request_context_api_key, service_url: str, api_key: str):
    """Send PUT request to update an organisation."""
    org_id = payload.get("id")
    if not org_id:
        raise ValueError("Payload must include 'id'")
    full_url = f"{service_url.rstrip('/')}/Organization/{org_id}"
    logger.info(f"Full URL: {full_url}\nAPI key: {api_key[:4]}****\nPayload: {json.dumps(payload, indent=2)}")
    response = api_request_context_api_key.put(full_url, data=json.dumps(payload))
    try:
        logger.info(f"Response body: {response.json()}")
    except Exception:
        logger.info(f"Response body: {response.text}")
    return response


def assert_item_matches_payload(item, payload, mandatory_only=False):
    """Assert DB item matches the payload, optionally skipping optional fields."""
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

@when('I update the organisation details for ODS Code', target_fixture="fresponse")
@when('I update the organisation details using the same data for the ODS Code', target_fixture="fresponse")
def update_organisation_details(api_request_context_api_key, service_url, api_key):
    payload = read_json_file("../../json_files/Organisation/organisation-payload.json")
    return update_organisation(payload, api_request_context_api_key, service_url, api_key)


@when('I update the organisation details for ODS Code with mandatory fields only', target_fixture="fresponse")
def update_organisation_details_mandatoryfield(api_request_context_api_key, service_url, api_key):
    payload = read_json_file("../../json_files/Organisation/organisation-payload.json")
    payload.pop("telecom", None)
    logger.info(f"Payload with mandatory fields only: {json.dumps(payload, indent=2)}")
    return update_organisation(payload, api_request_context_api_key, service_url, api_key)


@then('the data in the database matches the inserted payload')
def assert_model_matches_repo(model_repo):
    payload = read_json_file("../../json_files/Organisation/organisation-payload.json")
    item = get_from_repo(model_repo, payload["identifier"][0]["value"])
    assert item, f"No data found in repository for ODS code {payload['identifier'][0]['value']}"
    assert_item_matches_payload(item, payload)

@then('I receive a status code "200" in response and save the modifiedBy timestamp')
def validate_status_and_save_modified(fresponse, context: Context, model_repo):
    """Validate status code 200 and save modifiedBy & modifiedDateTime in context."""
    assert fresponse.status == 200, f"Expected 200, got {fresponse.status}"
    payload = read_json_file("../../json_files/Organisation/organisation-payload.json")
    ods_code = payload["identifier"][0]["value"]
    item = get_from_repo(model_repo, ods_code)
    assert item, f"No data found in repository for ODS code {ods_code}"
    context.other["modifiedBy_timestamp"] = getattr(item, "modifiedBy", None)
    context.other["modifiedDateTime"] = getattr(item, "modifiedDateTime", None)
    logger.info(f"Saved modifiedBy: {context.other['modifiedBy_timestamp']}, modifiedDateTime: {context.other['modifiedDateTime']}")

@then('the database matches the inserted payload with the same modifiedBy timestamp')
def assert_database_modifiedBy_unchanged(context: Context, model_repo):
    """Validate DB matches payload and modifiedDateTime remains unchanged."""
    payload = read_json_file("../../json_files/Organisation/organisation-payload.json")
    ods_code = payload["identifier"][0]["value"]
    item = get_from_repo(model_repo, ods_code)
    assert item, f"No data found in repository for ODS code {ods_code}"
    # Validate payload fields
    assert_item_matches_payload(item, payload)
    # Validate modifiedDateTime
    saved_modifiedDateTime = context.other.get("modifiedDateTime")
    current_modifiedDateTime = getattr(item, "modifiedDateTime", None)
    assert current_modifiedDateTime == saved_modifiedDateTime, (
        f"modifiedDateTime changed! First: {saved_modifiedDateTime}, Now: {current_modifiedDateTime}"
    )
    logger.info(f"modifiedDateTime unchanged: {current_modifiedDateTime}")

@then('the data in the database matches the inserted payload with telecom null')
def assert_model_matches_repo_mandatory_only(model_repo):
    payload = read_json_file("../../json_files/Organisation/organisation-payload.json")
    item = get_from_repo(model_repo, payload["identifier"][0]["value"])
    assert item, f"No data found in repository for ODS code {payload['identifier'][0]['value']}"
    assert_item_matches_payload(item, payload, mandatory_only=True)
    actual_telecom = getattr(item, "telecom", None)
    logger.info(f"Actual telecom in DB: {actual_telecom}")
    assert actual_telecom is None, f"telecom is expected to be null, but got: {actual_telecom}"

def update_payload_field(field: str, value: str):
    """Read payload and update the specified field with the given value."""
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
    logger.info(f"Updated payload field '{field}' with value '{value}': {json.dumps(payload, indent=2)}")
    return payload

@when(parsers.cfparse('I set the "{field}" field to "{value}"'), target_fixture="fresponse")
def set_field_and_update(field: str, value: str, context: Context, api_request_context_api_key, service_url, api_key):
    # Prepare payload with field/value override
    payload = update_payload_field(field, value)
    context.other["current_payload"] = payload
    response = update_organisation(payload, api_request_context_api_key, service_url, api_key)
    return response

@then(parsers.cfparse('the database reflects "{field}" with value "{value}"'))
def validate_db_field(field: str, value: str, context: Context, model_repo):
    """Check that the database reflects the updated field value, except 'active' which is skipped."""
    if field == "active":
        logger.info("Skipping DB validation for 'active' field as per requirement")
        return
    payload = context.other.get("current_payload")
    assert payload, "No payload found in context — was the update step executed?"
    ods_code = payload["identifier"][0]["value"]
    item = get_from_repo(model_repo, ods_code)
    assert item, f"No data found in repository for ODS code {ods_code}"
    # For telecom or other fields
    actual = getattr(item, field, None)
    expected = value
    logger.info(f"Validating DB field '{field}': expected={expected}, actual={actual}")
    assert actual == expected, f"{field} mismatch: expected {expected}, got {actual}"








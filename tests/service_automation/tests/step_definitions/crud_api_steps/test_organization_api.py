from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from utilities.infra.api_util import get_r53, get_url
from utilities.infra.dns_util import wait_for_dns
from utilities.common.json_helper import read_json_file
from step_definitions.common_steps.api_steps import *  # noqa: F403
from utilities.common.constants import ENDPOINTS
from loguru import logger
from uuid import uuid4
import ast
import json


# Load feature file
scenarios(
    "./crud_api_features/organization_api.feature",
    "./apim_crud_api_features/apim_organization_api.feature",
)

DEFAULT_PAYLOAD_PATH = "../../json_files/Organisation/organisation-payload.json"


@when(
    parsers.re(
        r'I request data from the "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)"'
    ),
    target_fixture="fresponse",
)
def send_get(api_request_context_mtls_crud, api_name, resource_name):
    url = get_url(api_name) + "/" + resource_name
    # Handle None or empty params
    response = api_request_context_mtls_crud.get(url)
    return response


def _load_default_payload() -> dict:
    """Load the default organisation payload."""
    return read_json_file(DEFAULT_PAYLOAD_PATH)


def update_name(payload: dict, value: str):
    payload["name"] = value


def update_type(payload: dict, value: str):
    payload["type"][0]["text"] = value


def update_telecom(payload: dict, value: str):
    payload["telecom"][0]["value"] = value


FIELD_UPDATERS = {"name": update_name, "type": update_type, "telecom": update_telecom}


def update_payload_field(field: str, value: str) -> dict:
    """Update a single field in the default organisation payload."""
    payload = _load_default_payload()
    updater = FIELD_UPDATERS.get(field)
    if not updater:
        raise ValueError(f"Unknown field: {field}")
    updater(payload, value)
    logger.info(
        f"Updated field '{field}' with '{value}':\n{json.dumps(payload, indent=2)}"
    )
    return payload


def remove_field(payload: dict, field: str) -> dict:
    payload.pop(field, None)
    logger.info(f"Removed field '{field}':\n{json.dumps(payload, indent=2)}")
    return payload


def add_extra_field(payload: dict, field: str, value: str) -> dict:
    payload[field] = value
    logger.info(f"Added extra field '{field}':\n{json.dumps(payload, indent=2)}")
    return payload


def set_nonexistent_id(payload: dict) -> dict:
    payload["id"] = str(uuid4())
    logger.info(f"Set non-existent ID:\n{json.dumps(payload, indent=2)}")
    return payload


def update_organisation_generic(payload: dict, api_context, base_url: str):
    org_id = payload.get("id")
    if not org_id:
        raise ValueError("Payload must include 'id'")

    url = f"{base_url.rstrip('/')}{ENDPOINTS['organization']}/{org_id}"
    logger.info(
        f"Updating organisation at {url}\nPayload:\n{json.dumps(payload, indent=2)}"
    )

    response = api_context.put(url, data=json.dumps(payload))
    response.request_body = payload
    try:
        logger.info(f"Response [{response.status}]: {response.json()}")
    except (ValueError, AttributeError):
        logger.info(f"Response [{response.status}]: {response.text}")
    return response


def update_organisation_apim(
    payload: dict,
    new_apim_request_context,
    nhsd_apim_proxy_url: str,
):
    org_id = payload.get("id")
    url = f"{nhsd_apim_proxy_url}/{ENDPOINTS['organization']}/{org_id}"
    logger.info(f"PUT Request URL: {url}")
    logger.info(f"Request Payload:\n{json.dumps(payload, indent=2)}")
    headers = {"Content-Type": "application/fhir+json"}
    response = new_apim_request_context.put(
        url, data=json.dumps(payload), headers=headers
    )
    # Log response details
    logger.info(f"Response Status: {response.status}")
    response.request_body = payload
    try:
        logger.info(f"Response JSON:\n{json.dumps(response.json(), indent=2)}")
    except Exception:
        logger.info(f"Response Text:\n{response.text()}")
    return response


def update_organisation(payload: dict, api_request_context_mtls_crud):
    return update_organisation_generic(
        payload, api_request_context_mtls_crud, get_url("crud")
    )


def get_db_item(model_repo, payload: dict):
    ods_code = payload["identifier"][0]["value"]
    item = get_from_repo(model_repo, ods_code)
    assert item, f"No data found for ODS code {ods_code}"
    return item


def assert_item_matches_payload(item, payload: dict, mandatory_only: bool = False):
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


def get_diagnostics_list(fresponse):
    diagnostics_raw = fresponse.json()["issue"][0].get("diagnostics", "")
    if not diagnostics_raw:
        raise AssertionError("Diagnostics field is missing or empty.")
    try:
        diagnostics_list = ast.literal_eval(diagnostics_raw)
    except (ValueError, SyntaxError) as e:
        raise AssertionError(f"Failed to parse diagnostics: {e}")
    if not isinstance(diagnostics_list, list):
        raise AssertionError(
            f"Diagnostics should be a list, got {type(diagnostics_list).__name__}"
        )
    return diagnostics_list


def run_diagnostic_check(
    *,
    fresponse,
    mode,
    field=None,
    field_path=None,
    invalid_value=None,
    value=None,
):
    """
        mode:
    - "missing"
    - "invalid_chars"
    - "extra"
    """
    if mode == "missing":
        diagnostics_list = get_diagnostics_list(fresponse)
        assert len(diagnostics_list) == 1
        diagnostic = diagnostics_list[0]
        assert diagnostic["type"] == "missing"
        assert diagnostic["loc"] == ("body", field)
        assert diagnostic["msg"] == "Field required"
        assert isinstance(diagnostic["input"], dict)
        return

    if mode == "invalid_chars":
        issue = fresponse.json()["issue"][0]
        diagnostics = issue.get("diagnostics", "")
        assert field_path in diagnostics
        assert invalid_value in diagnostics
        assert "contains invalid characters" in diagnostics
        return

    if mode == "extra":
        diagnostic = get_diagnostics_list(fresponse)[0]
        assert diagnostic.get("type") == "extra_forbidden"
        loc = diagnostic.get("loc", [])
        assert field in loc or field == loc
        assert diagnostic.get("msg") == "Extra inputs are not permitted"
        assert diagnostic.get("input") == value
        return
    raise ValueError(f"Unknown diagnostic mode: {mode}")


@given(
    parsers.parse(
        'I have a valid organization payload with identifier "{identifier_data}"'
    ),
    target_fixture="payload",
)
def step_given_valid_payload_with_identifier(identifier_data):
    payload = _load_default_payload()
    try:
        identifier = json.loads(identifier_data)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse identifier data: {identifier_data}. Error: {e}"
        )
    payload["identifier"] = identifier
    logger.info(f"Prepared payload with identifier: {json.dumps(payload, indent=2)}")
    return payload


@when(
    "I update the organization details for ODS Code via APIM",
    target_fixture="fresponse",
)
def step_update_apim(new_apim_request_context, nhsd_apim_proxy_url):
    payload = _load_default_payload()
    return update_organisation_apim(
        payload, new_apim_request_context, nhsd_apim_proxy_url
    )


@when("I update the organization details for ODS Code", target_fixture="fresponse")
@when(
    "I update the organisation details using the same data for the ODS Code",
    target_fixture="fresponse",
)
def step_update_crud(api_request_context_mtls_crud):
    payload = _load_default_payload()
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    "I update the organization details for ODS Code with mandatory fields only",
    target_fixture="fresponse",
)
def step_update_mandatory(api_request_context_mtls_crud):
    payload = _load_default_payload()
    payload.pop("telecom", None)
    logger.info(f"Payload with mandatory fields only:\n{json.dumps(payload, indent=2)}")
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.cfparse('I set the "{field}" field to "{value}"'),
    target_fixture="fresponse",
)
def step_set_field(field: str, value: str, api_request_context_mtls_crud):
    payload = update_payload_field(field, value)
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.cfparse(
        'I remove the "{field}" field from the payload and update the organization'
    ),
    target_fixture="fresponse",
)
def step_remove_field(field: str, api_request_context_mtls_crud):
    payload = remove_field(_load_default_payload(), field)
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.cfparse(
        'I remove the "{field}" field from the payload and update the organization via APIM'
    ),
    target_fixture="fresponse",
)
def step_remove_field_apim(field: str, new_apim_request_context, nhsd_apim_proxy_url):
    payload = remove_field(_load_default_payload(), field)
    return update_organisation_apim(
        payload, new_apim_request_context, nhsd_apim_proxy_url
    )


@when("I update the organization with a non-existent ID", target_fixture="fresponse")
def step_nonexistent_id(api_request_context_mtls_crud):
    payload = set_nonexistent_id(_load_default_payload())
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.parse(
        'I add an extra field "{extra_field}" with value "{value}" to the payload and update the organization'
    ),
    target_fixture="fresponse",
)
def step_add_extra_field(extra_field: str, value: str, api_request_context_mtls_crud):
    payload = add_extra_field(_load_default_payload(), extra_field, value)
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.parse(
        "I send a PUT request with invalid Content-Type to the organization API"
    ),
    target_fixture="fresponse",
)
def step_send_invalid_content_type(api_request_context_mtls_crud):
    payload = _load_default_payload()
    org_id = payload.get("id")
    url = f"{get_url('crud').rstrip('/')}{ENDPOINTS['organization']}/{org_id}"
    headers = {"Content-Type": "application/json"}
    response = api_request_context_mtls_crud.put(
        url, data=json.dumps(payload), headers=headers
    )
    response.request_body = payload
    try:
        logger.info(f"Response [{response.status}]: {response.json()}")
    except Exception:
        logger.info(f"Response [{response.status}]: {response.text}")
    return response


@when(
    parsers.parse("I update the organization details with the identifier"),
    target_fixture="fresponse",
)
def step_update_with_identifier(payload, api_request_context_mtls_crud):
    logger.info(f"Payload to be sent to the API: {json.dumps(payload, indent=2)}")
    response = update_organisation(payload, api_request_context_mtls_crud)
    return response


@then(parsers.parse('the OperationOutcome contains an issue with code "{code}"'))
def step_check_operation_outcome_code(fresponse, code):
    body = fresponse.json()
    assert body.get("resourceType") == "OperationOutcome", (
        f"Unexpected response: {body}"
    )
    assert any(issue.get("code") == code for issue in body.get("issue", [])), (
        f"Expected code '{code}' not found"
    )


@then("the data in the database matches the inserted payload")
def step_validate_db(model_repo, fresponse):
    payload = fresponse.request_body
    item = get_db_item(model_repo, payload)
    assert_item_matches_payload(item, payload)


@then("the data in the database matches the inserted payload with telecom null")
def step_validate_db_mandatory(model_repo, fresponse):
    payload = fresponse.request_body
    item = get_db_item(model_repo, payload)
    assert_item_matches_payload(item, payload, mandatory_only=True)
    actual_telecom = getattr(item, "telecom", None)
    assert actual_telecom is None, f"telecom expected to be null, got: {actual_telecom}"


@then(
    'I receive a status code "200" in response and save the modifiedBy timestamp',
    target_fixture="saved_data",
)
def step_save_modified(fresponse, model_repo):
    assert fresponse.status == 200, f"Expected 200, got {fresponse.status}"
    payload = fresponse.request_body
    item = get_db_item(model_repo, payload)
    saved_data = {
        "modifiedBy": getattr(item, "modifiedBy", None),
        "modifiedDateTime": getattr(item, "modifiedDateTime", None),
        "payload": payload,
    }
    logger.info(f"Saved modifiedBy: {saved_data['modifiedBy']}")
    logger.info(f"Saved modifiedDateTime: {saved_data['modifiedDateTime']}")
    return saved_data


@then("the database matches the inserted payload with the same modifiedBy timestamp")
def step_validate_modified_unchanged(saved_data, model_repo):
    payload = saved_data["payload"]
    item = get_db_item(model_repo, payload)
    assert_item_matches_payload(item, payload)
    saved_dt = saved_data["modifiedDateTime"]
    current_dt = getattr(item, "modifiedDateTime")
    logger.info(f"Comparing modifiedDateTime: saved={saved_dt}, current={current_dt}")
    assert current_dt == saved_dt, (
        f"modifiedDateTime mismatch: expected {saved_dt}, got {current_dt}"
    )


@then(parsers.parse('the database reflects "{field}" with value "{value}"'))
def step_validate_db_field(field: str, value: str, model_repo, fresponse):
    payload = fresponse.request_body
    item = get_db_item(model_repo, payload)
    actual = (
        getattr(item, field, None)
        if field != "telecom"
        else getattr(item, "telecom", None)
    )
    assert actual == value, f"{field} mismatch: expected {value}, got {actual}"


@then(parsers.parse('the diagnostics message indicates "{field}" is missing'))
def step_diagnostics_missing(fresponse, field):
    run_diagnostic_check(
        fresponse=fresponse,
        mode="missing",
        field=field,
    )


@then(
    parsers.cfparse(
        'the diagnostics message indicates invalid characters in the "{field_path}" with value "{invalid_value}"'
    )
)
def step_diagnostics_invalid_chars(fresponse, field_path, invalid_value):
    run_diagnostic_check(
        fresponse=fresponse,
        mode="invalid_chars",
        field_path=field_path,
        invalid_value=invalid_value,
    )


@then(
    parsers.cfparse(
        'the diagnostics message indicates unexpected field "{field}" with value "{value}"'
    )
)
def step_diagnostics_extra_field(fresponse, field, value):
    run_diagnostic_check(
        fresponse=fresponse,
        mode="extra",
        field=field,
        value=value,
    )

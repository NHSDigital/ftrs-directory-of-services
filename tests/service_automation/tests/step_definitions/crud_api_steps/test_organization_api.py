import ast
import json
from uuid import uuid4

from _pytest.fixtures import FixtureLookupError
from loguru import logger
from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps.api_steps import *  # noqa: F403
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from utilities.common.constants import ENDPOINTS
from utilities.common.json_helper import read_json_file
from utilities.infra.api_util import get_url

# Load feature file
scenarios(
    "./crud_api_features/organization_api.feature",
    "./apim_crud_api_features/apim_organization_api.feature",
)

DEFAULT_PAYLOAD_PATH = "../../json_files/Organisation/organisation-payload.json"


def get_seeded_model_or_none(request):
    try:
        return request.getfixturevalue("seeded_model")
    except FixtureLookupError:
        return None


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


def build_payload(request) -> dict:
    payload = read_json_file(DEFAULT_PAYLOAD_PATH)
    seeded_model = get_seeded_model_or_none(request)
    if seeded_model:
        payload["id"] = str(seeded_model.id)
        payload["identifier"][0]["value"] = seeded_model.identifier_ODS_ODSCode
    return payload


def update_name(payload: dict, value: str):
    payload["name"] = value


def update_telecom(payload: dict, system: str, value: str):
    if "telecom" not in payload:
        payload["telecom"] = []
    existing_telecom = next(
        (item for item in payload["telecom"] if item["system"] == system), None
    )
    if existing_telecom:
        existing_telecom["value"] = value
    else:
        # Append a new telecom entry
        payload["telecom"].append(
            {
                "system": system,
                "value": value,
                "use": "work",
            }
        )


def update_identifier(payload: dict, value: str):
    payload["identifier"][0]["value"] = value


def update_active(payload: dict, value: str):
    payload["active"] = value


FIELD_UPDATERS = {
    "name": update_name,
    "telecom": update_telecom,
    "identifier": update_identifier,
    "active": update_active,
}


def update_payload_field(field: str, value: str, payload: dict) -> dict:
    """Update a single field in the default organisation payload."""
    if field in ["phone", "email", "url"]:
        system = field
        update_telecom(payload, system, value)
    else:
        updater = FIELD_UPDATERS.get(field)
        if updater is None:
            raise ValueError(f"Unknown field: {field}")
        updater(payload, value)
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


def modify_telecom_type(payload, actual_type, update_type):
    for entry in payload["telecom"]:
        if entry["system"] == actual_type:
            entry["system"] = update_type
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
    url = f"{nhsd_apim_proxy_url}{ENDPOINTS['organization']}/{org_id}"
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
    model_id = payload["id"]
    item = model_repo.get(model_id)
    logger.info(f"Retrieved DB item for model_id {model_id}: {item}")
    assert item, f"No data found for id {model_id}"
    return item


def assert_item_matches_payload(item, payload: dict, mandatory_only: bool = False):
    """
    Assert that the database item matches the payload.
    """
    fields = [
        ("identifier_ODS_ODSCode", payload["identifier"][0]["value"]),
        ("name", payload["name"].title()),
        ("active", payload["active"]),
    ]
    if not mandatory_only:
        fields.append(("telecom", payload.get("telecom", [{}])[0].get("value")))

    for attr, expected in fields:
        actual = getattr(item, attr, None)
        logger.info(f"Validating {attr}: expected={expected}, actual={actual}")
        assert actual == expected, f"{attr} mismatch: {actual} != {expected}"

    # Check legal dates from OrganisationRole extension
    legal_start, legal_end = extract_legal_dates_from_payload(payload)
    if legal_start or legal_end:
        # Check legal start date
        actual_start = (
            getattr(item.legalDates, "start", None) if item.legalDates else None
        )
        if actual_start and hasattr(actual_start, "isoformat"):
            actual_start = actual_start.isoformat()
        logger.info(
            f"Validating legal start: expected={legal_start}, actual={actual_start}"
        )
        assert actual_start == legal_start, (
            f"Legal start date mismatch: {actual_start} != {legal_start}"
        )

        # Check legal end date
        actual_end = getattr(item.legalDates, "end", None) if item.legalDates else None
        if actual_end and hasattr(actual_end, "isoformat"):
            actual_end = actual_end.isoformat()
        logger.info(f"Validating legal end: expected={legal_end}, actual={actual_end}")
        assert actual_end == legal_end, (
            f"Legal end date mismatch: {actual_end} != {legal_end}"
        )


def extract_legal_dates_from_payload(payload: dict) -> tuple[str | None, str | None]:
    """Extract legal start and end dates from OrganisationRole extension in payload."""
    extensions = payload.get("extension", [])

    for ext in extensions:
        if (
            ext.get("url")
            != "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
        ):
            continue

        role_extensions = ext.get("extension", [])
        typed_period = _find_typed_period_in_role(role_extensions)
        if typed_period:
            return _extract_legal_period_dates(typed_period)

    return None, None


def _find_typed_period_in_role(role_extensions: list) -> dict | None:
    """Find the Legal TypedPeriod extension in role extensions."""
    for role_ext in role_extensions:
        if (
            role_ext.get("url")
            == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
        ):
            if _is_legal_typed_period(role_ext):
                return role_ext
    return None


def _is_legal_typed_period(typed_period_ext: dict) -> bool:
    """Check if a TypedPeriod extension has dateType 'Legal'."""
    for tp_ext in typed_period_ext.get("extension", []):
        if tp_ext.get("url") == "dateType":
            coding = tp_ext.get("valueCoding", {})
            return coding.get("code") == "Legal"
    return False


def _extract_legal_period_dates(
    typed_period_ext: dict,
) -> tuple[str | None, str | None]:
    """Extract start and end dates from a Legal TypedPeriod extension."""
    for tp_ext in typed_period_ext.get("extension", []):
        if tp_ext.get("url") == "period":
            period = tp_ext.get("valuePeriod", {})
            return period.get("start"), period.get("end")
    return None, None


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
def step_given_valid_payload_with_identifier(identifier_data, request):
    payload = build_payload(request)
    try:
        identifier = json.loads(identifier_data)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse identifier data: {identifier_data}. Error: {e}"
        )
    payload["identifier"] = identifier
    logger.info(f"Prepared payload with identifier: {json.dumps(payload, indent=2)}")
    return payload


def build_typed_period_extension(
    start_date: str = None, end_date: str = None, date_type_code: str = "Legal"
) -> dict:
    period = {}
    if start_date:
        period["start"] = start_date
    if end_date:
        period["end"] = end_date

    return {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
        "extension": [
            {
                "url": "dateType",
                "valueCoding": {
                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                    "code": date_type_code,
                    "display": date_type_code,
                },
            },
            {"url": "period", "valuePeriod": period},
        ],
    }


def build_organisation_role_extension_with_typed_period(
    start_date: str = None, end_date: str = None, date_type_code: str = "Legal"
) -> dict:
    """Create an OrganisationRole extension containing a TypedPeriod extension."""
    typed_period = build_typed_period_extension(start_date, end_date, date_type_code)

    return {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
        "extension": [
            {"url": "instanceID", "valueInteger": 12345},
            {
                "url": "roleCode",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                            "code": "RO182",
                            "display": "Pharmacy",
                        }
                    ]
                },
            },
            typed_period,
            {"url": "active", "valueBoolean": True},
        ],
    }


def validate_db_entry_against_payload(item, payload):
    """
    Validates that the database entry matches the inserted payload.

    Args:
        item: The database item to compare against.
        payload: The payload that was inserted into the database.

    Raises:
        AssertionError: If any mismatch is found between the database item and the payload.
    """

    expected_fields = [
        ("identifier_ODS_ODSCode", payload["identifier"][0]["value"]),
        ("name", payload["name"].title()),
        ("active", payload["active"]),
    ]

    for attr, expected_value in expected_fields:
        actual_value = getattr(item, attr, None)
        logger.info(
            f"Validating {attr}: expected={expected_value}, actual={actual_value}"
        )
        assert actual_value == expected_value, (
            f"Field '{attr}' mismatch: expected={expected_value}, actual={actual_value}"
        )
    # Validate legal start and end dates
    validate_legal_dates(item, payload)

    # Validate telecom field if present in the payload
    validate_telecom_field(item, payload)


def validate_telecom_field(item, payload):
    """
    Validates the telecom field of the database entry against the payload.

    Args:
        item: The database item to compare against.
        payload: The payload containing the telecom details.

    Raises:
        AssertionError: If any mismatch is found in the telecom field.
    """
    payload_telecom = payload.get("telecom", [])
    db_telecom = getattr(item, "telecom", [])
    if payload_telecom == []:
        assert db_telecom == [], (
            f"Expected DB telecom to be empty, but found {len(db_telecom)} entries"
        )
        logger.info(
            f"Validating telecom entry: expected= {payload_telecom}, got= {db_telecom}"
        )
        return
    if payload_telecom:
        assert len(payload_telecom) == len(db_telecom), "Telecom entries count mismatch"
        for idx, payload_entry in enumerate(payload_telecom):
            db_entry = db_telecom[idx]
            logger.info(f"Validating telecom entry at index {idx}: {db_entry}")
            if payload_entry["system"] == "url":
                expected_system = "web"
                db_system = (
                    db_entry.type.value
                    if hasattr(db_entry.type, "value")
                    else db_entry.type
                )
                assert db_system == expected_system, (
                    f"Telecom system mismatch at index {idx}: expected='web' (for URL), got={db_system}"
                )
            else:
                assert payload_entry["system"].lower() == db_entry.type.value.lower(), (
                    f"Telecom system mismatch at index {idx}: expected={payload_entry['system']}, got={db_entry.type.value}"
                )
            assert payload_entry["value"] == db_entry.value, (
                f"Telecom value mismatch at index {idx}: expected={payload_entry['value']}, got={db_entry.value}"
            )
            # Validate that the isPublic field is set to True
            assert db_entry.isPublic is True, (
                f"Telecom isPublic mismatch at index {idx}: expected=True, got={db_entry.isPublic}"
            )
            logger.info(
                f"Telecom entry {idx}: system={payload_entry['system']} - value={payload_entry['value']} - isPublic={db_entry.isPublic}"
            )


def validate_legal_dates(item, payload):
    """
    Validates the legal start and end dates of the database entry against the payload.

    Args:
        item: The database item to compare against.
        payload: The payload containing the legal date information.

    Raises:
        AssertionError: If any mismatch is found between the database item and the payload.
    """

    # Extract legal start and end dates from the payload
    legal_start, legal_end = extract_legal_dates_from_payload(payload)

    if legal_start or legal_end:
        # Validate the legal start date
        actual_start = (
            getattr(item.legalDates, "start", None) if item.legalDates else None
        )
        if actual_start and hasattr(actual_start, "isoformat"):
            actual_start = actual_start.isoformat()
        logger.info(
            f"Validating legal start: expected={legal_start}, actual={actual_start}"
        )
        assert actual_start == legal_start, (
            f"Legal start date mismatch: {actual_start} != {legal_start}"
        )

        # Validate the legal end date
        actual_end = getattr(item.legalDates, "end", None) if item.legalDates else None
        if actual_end and hasattr(actual_end, "isoformat"):
            actual_end = actual_end.isoformat()
        logger.info(f"Validating legal end: expected={legal_end}, actual={actual_end}")
        assert actual_end == legal_end, (
            f"Legal end date mismatch: {actual_end} != {legal_end}"
        )


@when(
    "I update the organization details for ODS Code via APIM",
    target_fixture="fresponse",
)
def step_update_apim(new_apim_request_context, nhsd_apim_proxy_url, request):
    payload = build_payload(request)
    return update_organisation_apim(
        payload, new_apim_request_context, nhsd_apim_proxy_url
    )


@when("I update the organization details for ODS Code", target_fixture="fresponse")
@when(
    "I update the organisation details using the same data for the ODS Code",
    target_fixture="fresponse",
)
def step_update_crud(api_request_context_mtls_crud, request):
    payload = build_payload(request)
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.cfparse('I set the "{field}" field to "{value}"'),
    target_fixture="fresponse",
)
def step_set_field(field: str, value: str, api_request_context_mtls_crud, request):
    payload = build_payload(request)
    payload = update_payload_field(field, value, payload)
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.cfparse(
        'I remove the "{field}" field from the payload and update the organization'
    ),
    target_fixture="fresponse",
)
def step_remove_field(field: str, api_request_context_mtls_crud, request):
    payload = remove_field(build_payload(request), field)
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.cfparse(
        'I remove the "{field}" field from the payload and update the organization via APIM'
    ),
    target_fixture="fresponse",
)
def step_remove_field_apim(
    field: str, new_apim_request_context, nhsd_apim_proxy_url, seeded_model
):
    payload = remove_field(build_payload(seeded_model), field)
    return update_organisation_apim(
        payload, new_apim_request_context, nhsd_apim_proxy_url
    )


@when("I update the organization with a non-existent ID", target_fixture="fresponse")
def step_nonexistent_id(api_request_context_mtls_crud, request):
    payload = set_nonexistent_id(build_payload(request))
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.parse(
        'I add an extra field "{extra_field}" with value "{value}" to the payload and update the organization'
    ),
    target_fixture="fresponse",
)
def step_add_extra_field(
    extra_field: str, value: str, api_request_context_mtls_crud, request
):
    payload = add_extra_field(build_payload(request), extra_field, value)
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.parse(
        "I send a PUT request with invalid Content-Type to the organization API"
    ),
    target_fixture="fresponse",
)
def step_send_invalid_content_type(api_request_context_mtls_crud, request):
    payload = build_payload(request)
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
    parsers.parse(
        'I attempt to update the "{actual_type}" in telecom with "{update_type}"'
    ),
    target_fixture="fresponse",
)
def step_update_telecom_type(
    actual_type: str, update_type: str, api_request_context_mtls_crud, request
):
    payload = build_payload(request)
    org_id = payload.get("id")
    url = f"{get_url('crud').rstrip('/')}{ENDPOINTS['organization']}/{org_id}"
    modified_payload = modify_telecom_type(payload, actual_type, update_type)
    logger.info(
        f"Updating organisation at {url}\nPayload:\n{json.dumps(payload, indent=2)}"
    )
    response = api_request_context_mtls_crud.put(url, data=json.dumps(modified_payload))
    try:
        logger.info(f"Response [{response.status}]: {response.json()}")
    except (ValueError, AttributeError):
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


def _build_invalid_typed_period_extension(invalid_scenario: str) -> dict:
    """Build invalid TypedPeriod extensions for different test scenarios."""
    typed_period_url = (
        "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
    )

    if invalid_scenario == "missing dateType":
        return {
            "url": typed_period_url,
            "extension": [
                {
                    "url": "period",
                    "valuePeriod": {"start": "2020-01-15", "end": "2025-12-31"},
                }
            ],
        }
    elif invalid_scenario == "missing period":
        return {
            "url": typed_period_url,
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": "Legal",
                        "display": "Legal",
                    },
                }
            ],
        }
    elif invalid_scenario == "non-Legal dateType":
        return build_typed_period_extension("2020-01-15", "2025-12-31", "Operational")
    elif invalid_scenario == "invalid periodType extension url":
        return {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-InvalidTypedPeriod",
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": "Legal",
                        "display": "Legal",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {"start": "2020-01-15", "end": "2025-12-31"},
                },
            ],
        }
    elif invalid_scenario == "invalid periodType system":
        return {
            "url": typed_period_url,
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-InvalidPeriodType",
                        "code": "Legal",
                        "display": "Legal",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {"start": "2020-01-15", "end": "2025-12-31"},
                },
            ],
        }
    elif invalid_scenario == "missing start date with end":
        return {
            "url": typed_period_url,
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": "Legal",
                        "display": "Legal",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {"end": "2025-12-31"},  # Missing start date
                },
            ],
        }
    elif invalid_scenario == "missing both start and end":
        return {
            "url": typed_period_url,
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": "Legal",
                        "display": "Legal",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {},  # Missing both start and end dates
                },
            ],
        }
    elif invalid_scenario == "empty TypedPeriod extension url":
        return {
            "url": "",  # Empty string URL
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": "Legal",
                        "display": "Legal",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {"start": "2020-01-15", "end": "2025-12-31"},
                },
            ],
        }
    elif invalid_scenario == "missing TypedPeriod extension url":
        return {
            # "url" is missing here
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": "Legal",
                        "display": "Legal",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {"start": "2020-01-15", "end": "2025-12-31"},
                },
            ]
        }
    else:
        raise ValueError(f"Unknown TypedPeriod invalid_scenario: {invalid_scenario}")


def _build_invalid_role_extension(invalid_scenario: str) -> dict:
    """Build invalid OrganisationRole extensions for different test scenarios."""
    typed_period = build_typed_period_extension("2020-01-15", "2025-12-31", "Legal")

    if invalid_scenario == "invalid organisation role extension url":
        return {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole-INVALID",
            "extension": [
                {"url": "instanceID", "valueInteger": 12345},
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                "code": "RO76",
                                "display": "GP PRACTICE",
                            }
                        ]
                    },
                },
                typed_period,
            ],
        }
    elif invalid_scenario == "missing role organisation url":
        return {
            # "url" is missing here
            "extension": [{"url": "instanceID", "valueInteger": 12345}, typed_period]
        }
    elif invalid_scenario == "empty organisation role extension url":
        return {
            "url": "",  # Empty string URL
            "extension": [
                {"url": "instanceID", "valueInteger": 12345},
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                "code": "RO76",
                                "display": "GP PRACTICE",
                            }
                        ]
                    },
                },
                typed_period,
            ],
        }
    elif invalid_scenario == "missing roleCode extension":
        # OrganisationRole without any roleCode extension
        return {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [{"url": "instanceID", "valueInteger": 12345}, typed_period],
        }
    elif invalid_scenario == "roleCode missing valueCodeableConcept":
        # roleCode extension without valueCodeableConcept
        return {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {"url": "instanceID", "valueInteger": 12345},
                {
                    "url": "roleCode"
                    # No valueCodeableConcept
                },
                typed_period,
            ],
        }
    elif invalid_scenario == "roleCode missing coding array":
        # roleCode with valueCodeableConcept but no coding array
        return {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {"url": "instanceID", "valueInteger": 12345},
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        # No coding array
                    },
                },
                typed_period,
            ],
        }
    elif invalid_scenario == "roleCode empty code value":
        # roleCode with empty code value
        return {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {"url": "instanceID", "valueInteger": 12345},
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                "code": "",  # Empty code value
                                "display": "GP PRACTICE",
                            }
                        ]
                    },
                },
                typed_period,
            ],
        }
    elif invalid_scenario == "roleCode invalid enum value":
        # roleCode with invalid enum value
        return {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {"url": "instanceID", "valueInteger": 12345},
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                "code": "INVALID_CODE",  # Not a valid OrganisationTypeCode
                                "display": "Invalid Code",
                            }
                        ]
                    },
                },
                typed_period,
            ],
        }
    else:
        raise ValueError(f"Unknown role extension invalid_scenario: {invalid_scenario}")


def _build_role_extension_with_invalid_typed_period(invalid_typed_period: dict) -> dict:
    """Wrap an invalid TypedPeriod extension in a valid OrganisationRole extension."""
    return {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
        "extension": [
            {"url": "instanceID", "valueInteger": 12345},
            {
                "url": "roleCode",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                            "code": "RO76",
                            "display": "GP PRACTICE",
                        }
                    ]
                },
            },
            invalid_typed_period,
        ],
    }


@when(
    parsers.parse(
        'I update the organization with an invalid TypedPeriod extension "{invalid_scenario}"'
    ),
    target_fixture="fresponse",
)
def step_update_with_invalid_extension(
    invalid_scenario: str, api_request_context_mtls_crud, request
):
    """Update organization with various invalid extension scenarios."""
    payload = build_payload(request)

    # Handle role-level validation scenarios (URL and roleCode structure)
    role_level_scenarios = (
        "invalid organisation role extension url",
        "missing role organisation url",
        "empty organisation role extension url",
        "missing roleCode extension",
        "roleCode missing valueCodeableConcept",
        "roleCode missing coding array",
        "roleCode empty code value",
        "roleCode invalid enum value",
    )

    if invalid_scenario in role_level_scenarios:
        invalid_role_extension = _build_invalid_role_extension(invalid_scenario)
        payload["extension"] = [invalid_role_extension]
    else:
        # Handle TypedPeriod-level validation scenarios
        invalid_typed_period = _build_invalid_typed_period_extension(invalid_scenario)
        organisation_role_extension = _build_role_extension_with_invalid_typed_period(
            invalid_typed_period
        )
        payload["extension"] = [organisation_role_extension]

    logger.info(
        f"Payload with invalid extension ({invalid_scenario}):\n{json.dumps(payload, indent=2)}"
    )
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.parse(
        'I update the organization with legal dates start "{legal_start}" and end "{legal_end}"'
    ),
    target_fixture="fresponse",
)
def step_update_with_legal_dates(
    legal_start: str,
    legal_end: str,
    api_request_context_mtls_crud,
    request,
):
    """Update organization with legal start and end dates in YYYY-MM-DD format."""
    payload = build_payload(request)

    # Convert "null" string to None
    start = None if legal_start == "null" else legal_start
    end = None if legal_end == "null" else legal_end

    if start or end:
        payload["extension"] = [
            build_organisation_role_extension_with_typed_period(start, end)
        ]
    else:
        payload.pop("extension", None)

    logger.info(f"Payload with legal dates:\n{json.dumps(payload, indent=2)}")
    return update_organisation(payload, api_request_context_mtls_crud)


@when(
    parsers.parse(
        'I update the organization with invalid date format "{date_field}" value "{invalid_date}"'
    ),
    target_fixture="fresponse",
)
def step_update_with_invalid_date_format(
    date_field: str, invalid_date: str, api_request_context_mtls_crud, request
):
    """Update organization with invalid date format to test validation."""
    payload = build_payload(request)

    start = invalid_date if date_field == "start" else "2020-01-15"
    end = invalid_date if date_field == "end" else "2025-12-31"

    payload["extension"] = [
        build_organisation_role_extension_with_typed_period(start, end)
    ]

    logger.info(
        f"Payload with invalid {date_field} date '{invalid_date}':\n{json.dumps(payload, indent=2)}"
    )
    return update_organisation(payload, api_request_context_mtls_crud)


@then(parsers.parse('the OperationOutcome contains an issue with code "{code}"'))
def step_check_operation_outcome_code(fresponse, code):
    body = fresponse.json()
    assert body.get("resourceType") == "OperationOutcome", (
        f"Unexpected response: {body}"
    )
    assert any(issue.get("code") == code for issue in body.get("issue", [])), (
        f"Expected code '{code}' not found"
    )


@when(
    parsers.parse(
        'I update the organization with an invalid telecom field "{invalid_scenario}"'
    ),
    target_fixture="fresponse",
)
def step_update_invalid_telecom_field(
    invalid_scenario: str,
    api_request_context_mtls_crud,
    request,
):
    payload = build_payload(request)
    if invalid_scenario == "missing_type":
        payload["telecom"] = [{"value": "0300 311 22 34", "use": "work"}]
    elif invalid_scenario == "missing_value":
        payload["telecom"] = [{"system": "phone", "use": "work"}]
    elif invalid_scenario == "empty_type":
        payload["telecom"] = [{"system": "", "value": "0300 311 22 34", "use": "work"}]
    elif invalid_scenario == "empty_value":
        payload["telecom"] = [{"system": "phone", "value": "", "use": "work"}]
    elif invalid_scenario == "additional_field":
        payload["telecom"] = [
            {
                "system": "phone",
                "value": "0300 311 22 34",
                "use": "work",
                "extra_field": "unexpected",
            }
        ]
    elif invalid_scenario == "mixed_valid_invalid":
        payload["telecom"] = [
            {"system": "phone", "value": "0300 311 22 34", "use": "work"},
            {
                "system": "email",
                "value": "invalidemail",
                "use": "work",
            },
            {"system": "url", "value": "http://validurl.com", "use": "work"},
        ]
    elif invalid_scenario == "empty_telecom":
        payload["telecom"] = []
    elif invalid_scenario == "unsupported_system":
        payload["telecom"] = [
            {"system": "test", "value": "0300 311 22 34", "use": "work"}
        ]
    else:
        raise ValueError(f"Unknown invalid_scenario: {invalid_scenario}")
    logger.info(
        f"Payload with invalid telecom field for scenario {invalid_scenario}:\n{json.dumps(payload, indent=2)}"
    )
    return update_organisation(payload, api_request_context_mtls_crud)


@then("the data in the database matches the inserted payload")
def step_validate_db(model_repo, fresponse):
    payload = fresponse.request_body
    logger.info("Validating database entry against payload", payload)
    item = get_db_item(model_repo, payload)
    logger.info("Validating database entry from DB", item)
    validate_db_entry_against_payload(item, payload)


@then(
    'I receive a status code "200" in response and save the modifiedBy timestamp',
    target_fixture="saved_data",
)
def step_save_modified(fresponse, model_repo):
    assert fresponse.status == 200, f"Expected 200, got {fresponse.status}"
    payload = fresponse.request_body
    item = get_db_item(model_repo, payload)
    saved_data = {
        "lastUpdatedBy": getattr(item, "lastUpdatedBy", None),
        "lastUpdated": getattr(item, "lastUpdated", None),
        "payload": payload,
    }
    logger.info(f"Saved lastUpdatedBy: {saved_data['lastUpdatedBy']}")
    logger.info(f"Saved lastUpdated: {saved_data['lastUpdated']}")
    return saved_data


@then("the database matches the inserted payload with the same modifiedBy timestamp")
def step_validate_modified_unchanged(saved_data, model_repo):
    payload = saved_data["payload"]
    saved_dt = saved_data["lastUpdated"]
    item = get_db_item(model_repo, payload)
    validate_db_entry_against_payload(item, payload)
    # Compare the saved and current lastUpdated
    current_dt = getattr(item, "lastUpdated")
    logger.info(f"Comparing lastUpdated: saved={saved_dt}, current={current_dt}")
    assert current_dt == saved_dt, (
        f"lastUpdated mismatch: expected {saved_dt}, got {current_dt}"
    )


@then(parsers.parse('the database reflects "{field}" with value "{value}"'))
def step_validate_db_field(field: str, value: str, model_repo, fresponse):
    payload = fresponse.request_body
    item = get_db_item(model_repo, payload)
    actual = getattr(item, field, None)

    if field == "non_primary_role_codes":
        if value.strip() == "[]":
            expected = []
        else:
            # Remove brackets and split by comma, stripping whitespace from each code
            cleaned = value.strip().strip("[]")
            expected = [code.strip() for code in cleaned.split(",")] if cleaned else []

        # Convert actual values to strings for comparison if they are enums
        actual_codes = [
            str(code.value) if hasattr(code, "value") else str(code)
            for code in (actual or [])
        ]

        logger.info(f"Validating {field}: expected={expected}, actual={actual_codes}")
        assert actual_codes == expected, (
            f"{field} mismatch: expected {expected}, got {actual_codes}"
        )
        return

    # Convert string "None" to Python None for comparison
    expected = None if value == "None" else value
    # Handle legalDates structure - convert legalStartDate/legalEndDate to legalDates.start/end
    if field == "legalStartDate":
        actual = getattr(item.legalDates, "start", None) if item.legalDates else None
    elif field == "legalEndDate":
        actual = getattr(item.legalDates, "end", None) if item.legalDates else None
    else:
        actual = getattr(item, field, None)

    if field in ("legalStartDate", "legalEndDate") and actual is not None:
        if hasattr(actual, "isoformat"):
            actual = actual.isoformat()
    logger.info(f"Validating field '{field}': expected={expected}, actual={actual}")
    assert actual == expected, f"{field} mismatch: expected {expected}, got {actual}"


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


def set_field_to_null(payload: dict, field: str) -> dict:
    """Set a specific field to null in the payload."""
    payload[field] = None
    logger.info(f"Set field '{field}' to null:\n{json.dumps(payload, indent=2)}")
    return payload


@when(
    "I set the active field from the payload to null and update the organization",
    target_fixture="fresponse",
)
def step_set_active_null_crud(api_request_context_mtls_crud) -> object:
    """Set active field to null in the payload and update via CRUD API."""
    payload = set_field_to_null(build_payload(request), "active")
    return update_organisation(payload, api_request_context_mtls_crud)


@then(parsers.parse('the diagnostics message indicates the "{expected_message}"'))
def step_diagnostics_contains_message(fresponse, expected_message: str) -> None:
    """Verify that the diagnostics message contains the expected text."""
    body = fresponse.json()
    assert body.get("resourceType") == "OperationOutcome", (
        f"Unexpected response: {body}"
    )

    diagnostics = body["issue"][0].get("diagnostics", "")

    assert expected_message in diagnostics, (
        f"Expected diagnostics to contain '{expected_message}', got: {diagnostics}"
    )

    logger.info(f"Diagnostics correctly contains: {expected_message}")


@when(
    parsers.parse(
        'I set the role extensions to contain "{primary_role_code}" and "{non_primary_role_codes}"'
    ),
    target_fixture="fresponse",
)
def step_set_role_extensions(
    api_request_context_mtls_crud: object,
    primary_role_code: str,
    non_primary_role_codes: str,
    request,
) -> object:
    """Set role extensions with primary and non-primary role codes and update organization."""
    payload = build_payload(request)

    role_url = "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
    payload["extension"] = []

    # Handle None primary role code
    if primary_role_code.lower() == "none":
        primary_role_code = None

    # Build primary role extension if primary code exists
    if primary_role_code:
        primary_ext = {
            "url": role_url,
            "extension": [
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                "code": primary_role_code,
                            }
                        ]
                    },
                },
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                    "extension": [
                        {
                            "url": "dateType",
                            "valueCoding": {
                                "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                "code": "Legal",
                                "display": "Legal",
                            },
                        },
                        {
                            "url": "period",
                            "valuePeriod": {"start": "2020-01-15", "end": "2025-12-31"},
                        },
                    ],
                },
            ],
        }
        payload["extension"].append(primary_ext)

    role_codes_list = []
    if non_primary_role_codes and non_primary_role_codes.strip():
        cleaned = non_primary_role_codes.strip().strip("[]")
        if cleaned and cleaned.lower() != "none":
            role_codes_list = [code.strip() for code in cleaned.split(",")]

    # Build non-primary role extensions
    for code in role_codes_list:
        if code.lower() == "none":
            continue

        non_primary_ext = {
            "url": role_url,
            "extension": [
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                "code": code,
                            }
                        ]
                    },
                },
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                    "extension": [
                        {
                            "url": "dateType",
                            "valueCoding": {
                                "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                "code": "Legal",
                                "display": "Legal",
                            },
                        },
                        {
                            "url": "period",
                            "valuePeriod": {"start": "2020-01-15", "end": "2025-12-31"},
                        },
                    ],
                },
            ],
        }
        payload["extension"].append(non_primary_ext)

    logger.info(f"Extension count: {len(payload.get('extension', []))}")

    organisation_id = payload.get("id")
    url = get_url("crud") + f"/Organization/{organisation_id}"

    logger.info(f"Updating organization {organisation_id} with role extensions")
    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

    response = api_request_context_mtls_crud.put(
        url,
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json",
        },
    )

    response.request_body = payload

    logger.info(f"Response status: {response.status}")
    logger.debug(f"Response body: {response.text()}")

    return response

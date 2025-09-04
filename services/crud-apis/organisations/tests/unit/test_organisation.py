from http import HTTPStatus
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from ftrs_data_layer.domain import Organisation
from pytest_mock import MockerFixture
from starlette.responses import JSONResponse

from organisations.app.models.organisation import OrganizationQueryParams
from organisations.app.router.organisation import _get_organization_query_params, router

client = TestClient(router)

test_org_id = uuid4()


def get_organisation() -> dict:
    return {
        "id": str(test_org_id),
        "identifier_ODS_ODSCode": "ODS12345",
        "active": True,
        "name": "Test Organisation",
        "telecom": "123456789",
        "type": "GP Practice",
        "createdBy": "ROBOT",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "ROBOT",
        "modifiedDateTime": "2023-11-01T00:00:00Z",
        "endpoints": [
            {
                "id": "d5a852ef-12c7-4014-b398-661716a63027",
                "identifier_oldDoS_id": 67890,
                "status": "active",
                "connectionType": "itk",
                "description": "Primary",
                "payloadMimeType": "application/fhir",
                "isCompressionEnabled": True,
                "managedByOrganisation": "d5a852ef-12c7-4014-b398-661716a63027",
                "createdBy": "ROBOT",
                "createdDateTime": "2023-10-01T00:00:00Z",
                "modifiedBy": "ROBOT",
                "modifiedDateTime": "2023-11-01T00:00:00Z",
                "name": "Test Organisation Endpoint",
                "payloadType": "urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0",
                "service": None,
                "address": "https://example.com/endpoint",
                "order": 1,
            }
        ],
    }


@pytest.fixture(autouse=True)
def mock_repository(mocker: MockerFixture) -> MockerFixture:
    repository_mock = mocker.patch(
        "organisations.app.router.organisation.org_repository"
    )
    repository_mock.get.return_value = get_organisation()
    repository_mock.get_by_ods_code.return_value = [
        Organisation.model_construct(id="12345")
    ]
    repository_mock.iter_records.return_value = [get_organisation()]
    repository_mock.update.return_value = JSONResponse(
        {"message": "Data processed successfully"}, status_code=HTTPStatus.OK
    )
    repository_mock.delete.return_value = None
    repository_mock.create.return_value = None
    return repository_mock


@pytest.fixture(autouse=True)
def mock_organisation_service(mocker: MockerFixture) -> MockerFixture:
    service_mock = mocker.patch(
        "organisations.app.router.organisation.organisation_service"
    )
    service_mock.create_organisation.return_value = Organisation(**get_organisation())
    service_mock.process_organisation_update.return_value = True
    service_mock.get_by_ods_code.return_value = [Organisation(**get_organisation())]
    service_mock.get_all_organisations.return_value = [
        Organisation(**get_organisation())
    ]
    return service_mock


def test_get_organisation_by_id_success() -> None:
    response = client.get(f"/Organization/{test_org_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == str(get_organisation()["id"])


def test_get_organisation_by_id_returns_404_when_org_not_found(
    mock_repository: MockerFixture,
) -> None:
    mock_repository.get.return_value = None
    with pytest.raises(Exception) as exc_info:
        client.get(f"/Organization/{test_org_id}")
    assert "Organisation not found" in str(exc_info.value)


def test_get_organisation_by_id_returns_500_on_unexpected_error(
    mock_repository: MockerFixture,
) -> None:
    mock_repository.get.side_effect = Exception("Unexpected error")
    with pytest.raises(Exception) as exc_info:
        client.get(f"/Organization/{test_org_id}")
    assert "Unexpected error" in str(exc_info.value)


def test__get_organization_query_params_with_identifier() -> None:
    identifier = "odsOrganisationCode|ABC123"
    result = _get_organization_query_params(identifier)
    assert result is not None
    assert hasattr(result, "identifier")
    assert result.identifier == identifier


def test_get_handle_organisation_requests_all_success(mocker: MockerFixture) -> None:
    response = client.get("/Organization")
    assert response.status_code == HTTPStatus.OK
    bundle = response.json()
    assert bundle["resourceType"] == "Bundle"
    assert str(len(bundle["entry"])) == "1"
    assert bundle["entry"][0]["resource"]["id"] == str(get_organisation()["id"])


# Additional test to cover identifier with different valid ODS code (lines 79-85)
def test_get_handle_organisation_requests_by_identifier_success_with_different_code(
    mocker: MockerFixture,
) -> None:
    mock_org = Organisation(**get_organisation())
    mocker.patch(
        "organisations.app.router.organisation.org_repository.get_by_ods_code",
        return_value=mock_org,
    )
    response = client.get("/Organization?identifier=odsOrganisationCode|ODS54321")
    assert response.status_code == HTTPStatus.OK
    bundle = response.json()
    assert bundle["resourceType"] == "Bundle"
    assert len(bundle["entry"]) == 1
    assert bundle["entry"][0]["resource"]["id"] == str(test_org_id)
    # Also check the identifier is present in the response
    assert any(
        i["system"] == "https://fhir.nhs.uk/Id/ods-organization-code"
        for i in bundle["entry"][0]["resource"].get("identifier", [])
    )


def test_get_handle_organisation_requests_by_identifier_invalid_ods_code() -> None:
    with pytest.raises(Exception) as exc_info:
        client.get("/Organization?identifier=odsOrganisationCode|abc")
    outcome = exc_info.value.outcome
    assert outcome["issue"][0]["code"] == "invalid"
    assert (
        "Invalid identifier value: ODS code 'ABC' must follow format ^[A-Za-z0-9]{5,12}$"
        in outcome["issue"][0]["diagnostics"]
    )


def test_get_handle_organisation_requests_with_invalid_params(
    mocker: MockerFixture,
) -> None:
    # Mock check_organisation_params to raise an OperationOutcomeException
    mocker.patch(
        "organisations.app.router.organisation.organisation_service.check_organisation_params",
        side_effect=OperationOutcomeException(
            {
                "resourceType": "OperationOutcome",
                "issue": [
                    {
                        "severity": "error",
                        "code": "invalid",
                        "diagnostics": "Unexpected query parameter(s): abc. Only 'identifier' is allowed.",
                    }
                ],
            }
        ),
    )
    with pytest.raises(Exception) as exc_info:
        client.get("/Organization?identifier=odsOrganisationCode|ODS12345&abc=extra")
    outcome = exc_info.value.outcome
    assert outcome["resourceType"] == "OperationOutcome"
    assert outcome["issue"][0]["code"] == "invalid"
    assert (
        "Unexpected query parameter(s): abc. Only 'identifier' is allowed."
        in outcome["issue"][0]["diagnostics"]
    )


def test_get_handle_organisation_requests_by_identifier_not_found(
    mock_organisation_service: MockerFixture,
) -> None:
    mock_organisation_service.get_by_ods_code.side_effect = OperationOutcomeException(
        {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "not-found",
                    "diagnostics": "Organisation not found.",
                }
            ],
        }
    )
    with pytest.raises(OperationOutcomeException) as exc_info:
        client.get("/Organization?identifier=odsOrganisationCode|ODS12345")
    outcome = exc_info.value.outcome
    assert outcome["issue"][0]["code"] == "not-found"
    assert "not found" in outcome["issue"][0]["diagnostics"].lower()


def test_get_handle_organisation_requests_all_empty(
    mock_organisation_service: MockerFixture,
) -> None:
    mock_organisation_service.get_all_organisations.return_value = []
    response = client.get("/Organization")
    assert response.status_code == HTTPStatus.OK
    bundle = response.json()
    assert bundle["resourceType"] == "Bundle"
    assert bundle.get("entry", []) == []


def test_get_handle_organisation_requests_unhandled_exception(
    mock_organisation_service: MockerFixture,
) -> None:
    mock_organisation_service.get_all_organisations.side_effect = Exception("fail")
    with pytest.raises(Exception) as exc_info:
        client.get("/Organization")
    outcome = exc_info.value.outcome
    assert outcome["issue"][0]["code"] == "exception"
    assert "Unhandled exception occurred" in outcome["issue"][0]["diagnostics"]


def test_update_organisation_success() -> None:
    fhir_payload = {
        "resourceType": "Organization",
        "id": str(test_org_id),
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "12345"}
        ],
        "name": "Test Organisation",
        "active": False,
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Practice"}]}],
    }
    response = client.put(f"/Organization/{test_org_id}", json=fhir_payload)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["issue"][0]["code"] == "success"
    assert response.json()["issue"][0]["severity"] == "information"
    assert (
        response.json()["issue"][0]["diagnostics"]
        == "Organisation updated successfully"
    )


def test_update_organisation_no_updates(
    mock_organisation_service: MockerFixture,
) -> None:
    mock_organisation_service.process_organisation_update.return_value = False
    update_payload = {
        "resourceType": "Organization",
        "id": str(test_org_id),
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "12345"}
        ],
        "name": "Test Organisation",
        "active": False,
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Practice"}]}],
    }
    response = client.put(f"/Organization/{test_org_id}", json=update_payload)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["issue"][0]["code"] == "information"
    assert response.json()["issue"][0]["severity"] == "information"
    assert (
        response.json()["issue"][0]["diagnostics"]
        == "No changes made to the organisation"
    )


def test_update_organisation_operation_outcome(
    mock_organisation_service: MockerFixture,
) -> None:
    mock_organisation_service.process_organisation_update.side_effect = (
        OperationOutcomeException(
            {
                "resourceType": "OperationOutcome",
                "issue": [
                    {
                        "severity": "error",
                        "code": "not-found",
                        "diagnostics": "Organisation not found.",
                    }
                ],
            }
        )
    )
    update_payload = {
        "resourceType": "Organization",
        "id": str(test_org_id),
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "12345"}
        ],
        "name": "Test Organisation",
        "active": False,
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Practice"}]}],
    }
    with pytest.raises(OperationOutcomeException) as exc_info:
        client.put(f"/Organization/{test_org_id}", json=update_payload)
    assert exc_info.value.outcome["resourceType"] == "OperationOutcome"
    assert exc_info.value.outcome["issue"][0]["code"] == "not-found"
    assert exc_info.value.outcome["issue"][0]["severity"] == "error"


def test_update_organisation_missing_required_field() -> None:
    fhir_payload = {
        "resourceType": "Organization",
        "id": str(test_org_id),
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "12345"}
        ],
        "name": "ABC",
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Practice"}]}],
    }
    with pytest.raises(RequestValidationError) as exc_info:
        client.put(f"/Organization/{test_org_id}", json=fhir_payload)
    assert "'active'" in str(exc_info.value)
    assert "field required" in str(exc_info.value).lower()


def test_update_organisation_unexpected_exception(
    mock_organisation_service: MockerFixture,
) -> None:
    mock_organisation_service.process_organisation_update.side_effect = Exception(
        "Something went wrong"
    )
    update_payload = {
        "resourceType": "Organization",
        "id": str(test_org_id),
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "12345"}
        ],
        "name": "Test Organisation",
        "active": False,
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Practice"}]}],
    }
    with pytest.raises(OperationOutcomeException) as exc_info:
        client.put(f"/Organization/{test_org_id}", json=update_payload)
    assert exc_info.value.outcome["issue"][0]["code"] == "exception"
    assert exc_info.value.outcome["issue"][0]["severity"] == "error"
    assert "Something went wrong" in exc_info.value.outcome["issue"][0]["diagnostics"]


def test_create_organisation_success() -> None:
    organisation_data = get_organisation()
    response = client.post("/Organization", json=organisation_data)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "message": "Organisation created successfully",
        "organisation": organisation_data,
    }


def test_create_organisation_validation_error() -> None:
    organisation_data = get_organisation()
    organisation_data["identifier_ODS_ODSCode"] = None  # Missing ODS code
    with pytest.raises(RequestValidationError) as exc_info:
        client.post("/Organization", json=organisation_data)
    assert exc_info.type is RequestValidationError
    assert "Input should be a valid string" in str(exc_info.value)


def test_create_organisation_already_exists(
    mock_organisation_service: MockerFixture,
) -> None:
    organisation_data = get_organisation()
    mock_organisation_service.create_organisation.side_effect = HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="Organisation with this ODS code already exists",
    )
    with pytest.raises(HTTPException) as exc_info:
        client.post("/Organization", json=organisation_data)
    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc_info.value.detail == "Organisation with this ODS code already exists"


def test_delete_organisation_success(mock_repository: MockerFixture) -> None:
    mock_repository.get.return_value = get_organisation()
    response = client.delete(f"/Organization/{test_org_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_organisation_not_found(mock_repository: MockerFixture) -> None:
    mock_repository.get.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        client.delete(f"/Organization/{test_org_id}")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "Organisation not found"


def test_type_validator_invalid_coding_and_text_missing() -> None:
    update_payload = {
        "resourceType": "Organization",
        "id": str(test_org_id),
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "12345"}
        ],
        "name": "Test Org",
        "active": True,
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"coding": [{}]}],
    }
    with pytest.raises(RequestValidationError) as exc_info:
        client.put(f"/Organization/{test_org_id}", json=update_payload)
    assert exc_info.type is RequestValidationError
    assert "must have either 'coding' or 'text' populated" in str(exc_info.value)


def test_organization_query_params_success() -> None:
    query = OrganizationQueryParams(identifier="odsOrganisationCode|ABC123")
    assert query.identifier == "odsOrganisationCode|ABC123"
    assert query.ods_code == "ABC123"


def test_organization_query_params_invalid_system() -> None:
    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganizationQueryParams(identifier="wrongSystem|ABC123")
    outcome = exc_info.value.outcome
    assert outcome["issue"][0]["code"] == "invalid"
    assert "Invalid identifier system" in outcome["issue"][0]["diagnostics"]


def test_organization_query_params_invalid_ods_code() -> None:
    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganizationQueryParams(identifier="odsOrganisationCode|abc")
    outcome = exc_info.value.outcome
    assert outcome["issue"][0]["code"] == "invalid"
    assert (
        "Invalid identifier value: ODS code 'ABC' must follow format ^[A-Za-z0-9]{5,12}$"
        in outcome["issue"][0]["diagnostics"]
    )


def test_organization_query_params_missing_separator() -> None:
    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganizationQueryParams(identifier="odsOrganisationCodeABC123")
    outcome = exc_info.value.outcome
    assert outcome["issue"][0]["code"] == "invalid"
    assert (
        "Invalid identifier value: missing separator '|'. Must be in format 'odsOrganisationCode|<code>' and code must follow format ^[A-Za-z0-9]{5,12}$"
        in outcome["issue"][0]["diagnostics"]
    )


def test_organization_query_params_lowercase_ods_code() -> None:
    query = OrganizationQueryParams(identifier="odsOrganisationCode|abcde")
    assert query.ods_code == "ABCDE"

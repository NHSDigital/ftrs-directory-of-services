from http import HTTPStatus
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from ftrs_data_layer.models import Organisation
from pytest_mock import MockerFixture
from starlette.responses import JSONResponse

from organisations.app.router.organisation import router

client = TestClient(router)

test_org_id = uuid4()


def get_organisation() -> dict:
    return {
        "id": str(test_org_id),
        "identifier_ODS_ODSCode": "12345",
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
    repository_mock.get_by_ods_code.return_value = ["12345"]
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
    return service_mock


def test_get_organisation_by_id_success() -> None:
    response = client.get(f"/{test_org_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == str(get_organisation()["id"])


def test_get_organisation_by_id_returns_404_when_org_not_found(
    mock_repository: MockerFixture,
) -> None:
    mock_repository.get.return_value = None
    with pytest.raises(Exception) as exc_info:
        client.get(f"/{test_org_id}")
    assert "Organisation not found" in str(exc_info.value)


def test_get_organisation_by_id_returns_500_on_unexpected_error(
    mock_repository: MockerFixture,
) -> None:
    mock_repository.get.side_effect = Exception("Unexpected error")
    with pytest.raises(Exception) as exc_info:
        client.get(f"/{test_org_id}")
    assert "Unexpected error" in str(exc_info.value)


def test_get_organisation_by_id_returns_500_on_unexpected_error_in_get_all(
    mock_repository: MockerFixture,
) -> None:
    mock_repository.iter_records.side_effect = Exception("Unexpected error")
    with pytest.raises(Exception) as exc_info:
        client.get("/")
    assert "Unexpected error" in str(exc_info.value)


def test_get_all_organisations_success() -> None:
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == str(get_organisation()["id"])


def test_get_all_organisations_empty(
    mock_repository: MockerFixture,
) -> None:
    mock_repository.iter_records.return_value = []
    with pytest.raises(HTTPException) as exc_info:
        client.get("/")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "Unable to retrieve any organisations"


def test_update_organisation_success() -> None:
    fhir_payload = {
        "resourceType": "Organization",
        "id": str(test_org_id),
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "12345"}
        ],
        "active": False,
        "name": "Test Organisation",
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"text": "GP Practice"}],
    }
    response = client.put(f"/{test_org_id}", json=fhir_payload)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["success"] is True


def test_update_organisation_no_updates(
    mock_organisation_service: MockerFixture,
) -> None:
    mock_organisation_service.process_organisation_update.return_value = False
    update_payload = {
        "name": "Test Organisation",
        "active": False,
        "telecom": "0123456789",
        "type": "GP Practice",
        "modified_by": "ODS_ETL_PIPELINE",
    }
    response = client.put(f"/{test_org_id}", json=update_payload)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "message": "No changes made to the organisation",
    }


def test_update_organisation_operation_outcome(
    mock_organisation_service: MockerFixture,
) -> None:
    from ftrs_common.fhir.operation_outcome import OperationOutcomeException

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
        "name": "Test Organisation",
        "active": False,
        "telecom": "0123456789",
        "type": "GP Practice",
        "modified_by": "ODS_ETL_PIPELINE",
    }
    response = client.put(f"/{test_org_id}", json=update_payload)
    assert str(response.status_code) == "422"
    assert response.json()["resourceType"] == "OperationOutcome"
    assert response.json()["issue"][0]["code"] == "not-found"


def test_update_organisation_unexpected_exception(
    mock_organisation_service: MockerFixture,
) -> None:
    mock_organisation_service.process_organisation_update.side_effect = Exception(
        "Something went wrong"
    )
    update_payload = {
        "name": "Test Organisation",
        "active": False,
        "telecom": "0123456789",
        "type": "GP Practice",
        "modified_by": "ODS_ETL_PIPELINE",
    }
    response = client.put(f"/{test_org_id}", json=update_payload)
    assert str(response.status_code) == "500"
    assert response.json()["issue"][0]["code"] == "exception"
    assert "Something went wrong" in response.json()["issue"][0]["diagnostics"]


def test_get_organisation_by_ods_code_success() -> None:
    ods_code = "12345"
    response = client.get(f"/ods_code/{ods_code}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == "12345"


def test_get_organisation_by_ods_code_not_found(mock_repository: MockerFixture) -> None:
    mock_repository.get_by_ods_code.return_value = None
    ods_code = "12345"
    response = client.get(f"/ods_code/{ods_code}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["issue"] == [
        {
            "code": "not-found",
            "diagnostics": "Organisation not found",
            "severity": "error",
        }
    ]


def test_get_organisation_by_ods_code_unexpected_error(
    mock_repository: MockerFixture,
) -> None:
    mock_repository.get_by_ods_code.side_effect = Exception("Unexpected error")
    ods_code = "12345"
    response = client.get(f"/ods_code/{ods_code}")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json()["issue"] == [
        {
            "severity": "error",
            "code": "exception",
            "diagnostics": "Unexpected error: Unexpected error",
        }
    ]


def test_create_organisation_success() -> None:
    organisation_data = get_organisation()
    response = client.post("/", json=organisation_data)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "message": "Organisation created successfully",
        "organisation": organisation_data,
    }


def test_create_organisation_validation_error() -> None:
    organisation_data = get_organisation()
    organisation_data["identifier_ODS_ODSCode"] = None  # Missing ODS code
    with pytest.raises(RequestValidationError) as exc_info:
        client.post("/", json=organisation_data)
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
        client.post("/", json=organisation_data)
    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc_info.value.detail == "Organisation with this ODS code already exists"


def test_delete_organisation_success(mock_repository: MockerFixture) -> None:
    mock_repository.get.return_value = get_organisation()
    response = client.delete(f"/{test_org_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_organisation_not_found(mock_repository: MockerFixture) -> None:
    mock_repository.get.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        client.delete(f"/{test_org_id}")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "Organisation not found"

from http import HTTPStatus
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture, mocker
from starlette.responses import JSONResponse

from organisations.app.router.organisation import router

client = TestClient(router)


test_org_id = uuid4()


def get_organisation() -> dict:
    return {
        "id": test_org_id,
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
                "payloadMimeType": "xml",
                "isCompressionEnabled": True,
                "managedByOrganisation": "d5a852ef-12c7-4014-b398-661716a63027",
                "createdBy": "ROBOT",
                "createdDateTime": "2023-10-01T00:00:00Z",
                "modifiedBy": "ROBOT",
                "modifiedDateTime": "2023-11-01T00:00:00Z",
                "name": "Test Organisation Endpoint",
                "payloadType": "urn:nhs:example:interaction",
                "service": None,
                "address": "https://example.com/endpoint",
                "order": 1,
            }
        ],
    }


@pytest.fixture
def mock_repository(mocker: mocker) -> None:
    repository_mock = mocker.patch(
        "organisations.app.router.organisation.org_repository"
    )
    repository_mock.get.return_value = get_organisation()
    repository_mock.get_by_ods_code.return_value = [get_organisation()]
    repository_mock.iter_records.return_value = [get_organisation()]
    repository_mock.update.return_value = JSONResponse(
        {"message": "Data processed successfully"}, status_code=HTTPStatus.OK
    )
    return repository_mock


@pytest.fixture
def mock_apply_updates(mocker: mocker) -> None:
    apply_updates_mock = mocker.patch(
        "organisations.app.router.organisation.apply_updates"
    )
    apply_updates_mock.return_value = None
    return apply_updates_mock


def test_get_organisation_by_id_success(mock_repository: mocker) -> None:
    response = client.get(f"/{test_org_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == str(get_organisation()["id"])


def test_returns_404_when_org_not_found(mock_repository: mocker) -> None:
    mock_repository.get.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        client.get(f"/{test_org_id}")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "Organisation not found"


def test_returns_500_on_unexpected_error(mock_repository: mocker) -> None:
    mock_repository.get.side_effect = Exception("Unexpected error")
    with pytest.raises(Exception) as exc_info:
        client.get(f"/{test_org_id}")
    assert "Unexpected error" in str(exc_info.value)


def test_returns_500_on_unexpected_error_in_get_all(mock_repository: mocker) -> None:
    mock_repository.iter_records.side_effect = Exception("Unexpected error")
    with pytest.raises(Exception) as exc_info:
        client.get("/")
    assert "Unexpected error" in str(exc_info.value)


def test_get_all_organisations_success(mock_repository: mocker) -> None:
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == str(get_organisation()["id"])


def test_get_all_organisations_empty(mock_repository: mocker) -> None:
    mock_repository.iter_records.return_value = []
    with pytest.raises(HTTPException) as exc_info:
        client.get("/")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "Unable to retrieve any organisations"


def test_update_organisation_success(
    mock_repository: MockerFixture, mock_apply_updates: MockerFixture
) -> None:
    mock_repository.get.return_value = get_organisation()
    mock_apply_updates.return_value = None
    update_payload = {
        "name": "Test Organisation",
        "active": False,
        "telecom": "0123456789",
        "type": "GP Practice",
        "modified_by": "ODS_ETL_PIPELINE",
    }
    response = client.put(f"/{test_org_id}", json=update_payload)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Data processed successfully"}


def test_update_organisation_not_found(mock_repository: MockerFixture) -> None:
    mock_repository.get.return_value = None
    update_payload = {
        "name": "Test Organisation",
        "active": False,
        "telecom": "0123456789",
        "type": "GP Practice",
        "modified_by": "ODS_ETL_PIPELINE",
    }
    with pytest.raises(HTTPException) as exc_info:
        client.put(f"/{test_org_id}", json=update_payload)
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "Organisation not found"


def test_update_organisation_validation_error(mock_repository: MockerFixture) -> None:
    mock_repository.get.return_value = get_organisation()
    update_payload = {
        "name": "  ",  # Invalid name
        "active": False,
        "telecom": "0123456789",
        "type": "GP Practice",
        "modified_by": "ODS_ETL_PIPELINE",
    }
    with pytest.raises(RequestValidationError) as exc_info:
        client.put(f"/{test_org_id}", json=update_payload)
        assert exc_info.type == RequestValidationError
    assert "field required" in str(exc_info.value)


def test_get_organisation_by_ods_code_success(mock_repository: MockerFixture) -> None:
    mock_repository.get_by_ods_code.return_value = ["uuid"]
    ods_code = "12345"
    response = client.get(f"/ods_code/{ods_code}")
    assert response.status_code == HTTPStatus.OK
    assert response.json().get("id") == "uuid"


def test_get_organisation_by_ods_code_not_found(mock_repository: MockerFixture) -> None:
    ods_code = "12345"
    mock_repository.get_by_ods_code.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        client.get(f"/ods_code/{ods_code}")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "Organisation not found"


def test_get_organisation_by_ods_code_unexpected_error(
    mock_repository: MockerFixture,
) -> None:
    ods_code = "12345"
    mock_repository.get_by_ods_code.side_effect = Exception("Unexpected error")
    with pytest.raises(Exception) as exc_info:
        client.get(f"/ods_code/{ods_code}")
    assert "Unexpected error" in str(exc_info.value)

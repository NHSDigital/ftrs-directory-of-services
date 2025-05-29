from http import HTTPStatus
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pytest_mock import mocker


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
                "format": "xml",
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
        "healthcare_service.app.router.healthcare.repository"
    )
    repository_mock.get.return_value = get_organisation()
    repository_mock.iter_records.return_value = [get_organisation()]
    return repository_mock


def test_get_organisation_by_id_success(mock_repository: mocker) -> None:
    mock_repository.get.return_value = get_organisation()
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
    with pytest.raises(HTTPException) as exc_info:
        client.get(f"/{test_org_id}")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND

from http import HTTPStatus
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pytest_mock import mocker

from healthcare_service.app.router.healthcare import router

client = TestClient(router)

test_service_id = uuid4()


def get_mock_service() -> dict:
    return {
        "id": test_service_id,
        "createdBy": "test_user",
        "createdDateTime": "2025-05-27T12:50:55.481233Z",
        "modifiedBy": "test_user",
        "modifiedDateTime": "2025-05-27T12:50:55.481233Z",
        "identifier_oldDoS_uid": "161799",
        "active": True,
        "category": "GP Services",
        "providedBy": "96602abd-f265-4803-b4fb-413692279b5c",
        "location": "e13b21b1-8859-4364-9efb-951d43cc8264",
        "name": "test_service",
        "telecom": {
            "phone_private": "99999 000000",
            "web": "https://www.example.com/",
            "email": "example@nhs.gov.uk",
            "phone_public": "0208 883 5555",
        },
        "type": "Primary Care Network Enhanced Access Service",
        "openingTime": [
            {
                "allDay": False,
                "startTime": "08:00:00",
                "id": "d3d11647-87a5-43f3-a602-62585b852875",
                "dayOfWeek": "mon",
                "endTime": "18:30:00",
                "category": "availableTime",
            }
        ],
    }


@pytest.fixture
def mock_repository(mocker: mocker) -> None:
    repository_mock = mocker.patch(
        "healthcare_service.app.router.healthcare.repository"
    )
    repository_mock.get.return_value = get_mock_service()
    repository_mock.iter_records.return_value = [get_mock_service()]
    return repository_mock


def test_returns_healthcare_service_by_id(mock_repository: mocker) -> None:
    response = client.get(f"/{test_service_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == str(test_service_id)


def test_returns_404_when_service_not_found(mock_repository: mocker) -> None:
    mock_repository.get.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        client.get(f"/{test_service_id}")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "Healthcare Service not found"


def test_returns_all_healthcare_services(mock_repository: mocker) -> None:
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) > 0


def test_returns_404_when_no_services_found(mock_repository: mocker) -> None:
    mock_repository.iter_records.return_value = []
    with pytest.raises(HTTPException) as exc_info:
        client.get("/")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "No healthcare services found"


def test_returns_500_on_unexpected_error(mock_repository: mocker) -> None:
    mock_repository.get.side_effect = Exception("Unexpected error")
    with pytest.raises(HTTPException) as exc_info:
        client.get(f"/{test_service_id}")
    assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Failed to fetch healthcare services"


def test_returns_500_on_unexpected_error_in_get_all(
    mock_repository: mocker,
) -> None:
    mock_repository.iter_records.side_effect = Exception("Unexpected error")
    with pytest.raises(HTTPException) as exc_info:
        client.get("/")
    assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Failed to fetch healthcare services"


def test_delete_healthcare_service(mock_repository: mocker) -> None:
    mock_repository.get.return_value = get_mock_service()
    mock_repository.delete.return_value = None
    response = client.delete(f"/{test_service_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT
    mock_repository.delete.assert_called_once_with(test_service_id)


def test_delete_healthcare_service_not_found(mock_repository: mocker) -> None:
    mock_repository.get.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        client.delete(f"/{test_service_id}")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "No healthcare services found"


def test_create_healthcare_service(mock_repository: mocker) -> None:
    mock_repository.create.return_value = get_mock_service()
    response = client.post(
        "/",
        json={
            "name": "New Healthcare Service",
            "type": "GP Consultation Service",
            "category": "GP Services",
            "createdBy": "test_user",
            "active": True,
            "location": "e13b21b1-8859-4364-9efb-951d43cc8264",
            "providedBy": "96602abd-f265-4803-b4fb-413692279b5c",
            "telecom": {
                "phone_private": "99999 000000",
                "web": "https://www.example.com/",
                "email": "testmail@testmail.com",
            },
            "openingTime": [
                {
                    "allDay": False,
                    "startTime": "08:00:00",
                    "endTime": "18:30:00",
                    "dayOfWeek": "mon",
                    "category": "availableTime",
                }
            ],
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    mock_repository.create.assert_called_once()
    assert response.json()["message"] == "Healthcare Service created successfully"


def test_create_healthcare_service_invalid_data(mock_repository: mocker) -> None:
    with pytest.raises(RequestValidationError) as exc_info:
        client.post(
            "/",
            json={
                "name": "Invalid Healthcare Service",
                "type": "General Practice",
                # Missing the required field 'category'
            },
        )
    assert exc_info.type == RequestValidationError
    assert "Field required" in exc_info.value.errors()[0]["msg"]

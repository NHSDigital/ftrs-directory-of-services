from http import HTTPStatus
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pytest_mock import mocker

from location.app.router.location import router

client = TestClient(router)

test_location_id = uuid4()


def get_mock_location() -> dict:
    return {
        "id": test_location_id,
        "active": True,
        "managingOrganisation": "123e4567-e89b-12d3-a456-42661417400a",
        "name": None,
        "address": {
            "street": "10 made up road",
            "town": "thingyplace",
            "postcode": "TP00 9ZZ",
        },
        "positionGCS": {
            "latitude": "0.000003",
            "longitude": "-1.000005",
        },
        "positionReferenceNumber_UPRN": None,
        "positionReferenceNumber_UBRN": None,
        "partOf": None,
        "primaryAddress": True,
        "createdBy": "ROBOT",
        "createdDateTime": "2025-03-27T12:00:00Z",
        "modifiedBy": "ROBOT",
        "modifiedDateTime": "2025-03-27T12:00:00Z",
    }


@pytest.fixture
def mock_repository(mocker: mocker) -> None:
    repository_mock = mocker.patch("location.app.router.location.repository")
    repository_mock.get.return_value = get_mock_location()
    repository_mock.iter_records.return_value = [get_mock_location()]
    return repository_mock


def test_returns_location_by_id(mock_repository: mocker) -> None:
    response = client.get(f"/{test_location_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == str(test_location_id)


def test_returns_404_when_location_not_found(mock_repository: mocker) -> None:
    mock_repository.get.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        client.get(f"/{test_location_id}")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "Location not found"


def test_returns_all_locations(mock_repository: mocker) -> None:
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1


def test_returns_404_when_no_locations_found(mock_repository: mocker) -> None:
    mock_repository.iter_records.return_value = []
    with pytest.raises(HTTPException) as exc_info:
        client.get("/")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "No locations found"


def test_returns_500_on_unexpected_error(mock_repository: mocker) -> None:
    mock_repository.get.side_effect = Exception("Unexpected error")
    with pytest.raises(HTTPException) as exc_info:
        client.get(f"/{test_location_id}")
    assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Failed to fetch locations"


def test_returns_500_on_unexpected_error_in_get_all(
    mock_repository: mocker,
) -> None:
    mock_repository.iter_records.side_effect = Exception("Unexpected error")
    with pytest.raises(HTTPException) as exc_info:
        client.get("/")
    assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Failed to fetch locations"

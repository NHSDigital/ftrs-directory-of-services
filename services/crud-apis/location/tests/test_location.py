from http import HTTPStatus
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from ftrs_data_layer.models import Location
from pytest_mock import MockerFixture

from location.app.router.location import router

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


@pytest.fixture()
def mock_location_service(mocker: MockerFixture) -> MockerFixture:
    service_mock = mocker.patch("location.app.router.location.location_service")
    service_mock.get_location_by_id.return_value = Location(**get_mock_location())
    service_mock.get_locations.return_value = [Location(**get_mock_location())]
    service_mock.create_location.return_value = Location(**get_mock_location())
    return service_mock


client = TestClient(router)


def test_returns_location_by_id(mock_location_service: MockerFixture) -> None:
    response = client.get(f"/{test_location_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == str(test_location_id)


def test_returns_404_when_location_not_found(
    mock_location_service: MockerFixture,
) -> None:
    mock_location_service.get_location_by_id.side_effect = HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="Location not found"
    )
    with pytest.raises(HTTPException) as exc_info:
        client.get(f"/{test_location_id}")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND


def test_returns_404_when_no_locations_found(
    mock_location_service: MockerFixture,
) -> None:
    mock_location_service.get_locations.side_effect = HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="No locations found"
    )
    with pytest.raises(HTTPException) as exc_info:
        client.get("/")
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND


def test_returns_all_locations(mock_location_service: MockerFixture) -> None:
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1


def test_creates_new_location(mock_location_service: MockerFixture) -> None:
    new_location = Location(**get_mock_location())
    response = client.post("/", json=new_location.model_dump(mode="json"))
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["location"]["id"] == str(test_location_id)
    mock_location_service.create_location.assert_called_once_with(new_location)


def test_creates_new_location_with_uuid(mock_location_service: MockerFixture) -> None:
    new_location = Location(**get_mock_location())
    response = client.post("/", json=new_location.model_dump(mode="json"))
    assert response.status_code == HTTPStatus.CREATED
    assert "id" in response.json()["location"]
    mock_location_service.create_location.assert_called_once_with(new_location)


def test_creates_new_location_with_value_error(
    mock_location_service: MockerFixture,
) -> None:
    new_location = Location(**get_mock_location())
    new_location.id = "invalid-uuid"
    with pytest.raises(RequestValidationError) as exc_info:
        client.post("/", json=new_location.model_dump(mode="json"))
    assert exc_info.type == RequestValidationError
    mock_location_service.create_location.assert_not_called()  # Ensure no creation attempt was made


def test_creates_new_location_with_missing_fields(
    mock_location_service: MockerFixture,
) -> None:
    new_location = Location(**get_mock_location())
    new_location.name = None  # Simulate missing field
    response = client.post("/", json=new_location.model_dump(mode="json"))
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["location"]["name"] is None
    mock_location_service.create_location.assert_called_once_with(new_location)


def test_get_all_locations_500_error(mock_location_service: MockerFixture) -> None:
    mock_location_service.get_locations.side_effect = HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Internal Server Error"
    )
    with pytest.raises(HTTPException) as exc_info:
        client.get("/")
    assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Internal Server Error"


def test_get_location_by_id_500_error(mock_location_service: MockerFixture) -> None:
    mock_location_service.get_location_by_id.side_effect = HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Internal Server Error"
    )
    with pytest.raises(HTTPException) as exc_info:
        client.get(f"/{test_location_id}")
    assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Internal Server Error"

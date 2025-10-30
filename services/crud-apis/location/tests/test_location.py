from http import HTTPStatus
from uuid import uuid4

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from ftrs_data_layer.domain import Location
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
            "line1": "1 Test Street",
            "line2": None,
            "county": "Testshire",
            "town": "Testville",
            "postcode": "TE1 1ST",
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


@pytest.fixture()
def mock_repository(mocker: MockerFixture) -> MockerFixture:
    repository_mock = mocker.patch("location.app.router.location.location_repository")
    return repository_mock


test_app = FastAPI()
test_app.include_router(router)
client = TestClient(test_app)


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

    response = client.get(f"/{test_location_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_returns_404_when_no_locations_found(
    mock_location_service: MockerFixture,
) -> None:
    mock_location_service.get_locations.side_effect = HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="No locations found"
    )

    response = client.get("/")
    assert response.status_code == HTTPStatus.NOT_FOUND


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

    result = client.post("/", json=new_location.model_dump(mode="json"))
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert result.json() == {
        "detail": [
            {
                "ctx": {
                    "error": "invalid character: expected an optional prefix of `urn:uuid:` "
                    "followed by [0-9a-fA-F-], found `i` at 1",
                },
                "input": "invalid-uuid",
                "loc": [
                    "body",
                    "id",
                ],
                "msg": "Input should be a valid UUID, invalid character: expected an "
                "optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found "
                "`i` at 1",
                "type": "uuid_parsing",
            },
        ],
    }

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

    response = client.get("/")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Internal Server Error"


def test_get_location_by_id_500_error(mock_location_service: MockerFixture) -> None:
    mock_location_service.get_location_by_id.side_effect = HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Internal Server Error"
    )

    response = client.get(f"/{test_location_id}")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Internal Server Error"


def test_delete_location_success(mock_repository: MockerFixture) -> None:
    mock_repository.get.return_value = get_mock_location()
    mock_repository.delete.return_value = None
    response = client.delete(f"/{test_location_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT
    mock_repository.delete.assert_called_once_with(test_location_id)


def test_delete_location_not_found(mock_repository: MockerFixture) -> None:
    mock_repository.get.return_value = None

    response = client.delete(f"/{test_location_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Location not found"


def test_update_location_success(mock_repository: MockerFixture) -> None:
    mock_repository.update.return_value = None
    update_payload = {
        "id": str(test_location_id),
        "active": True,
        "address": {
            "line1": "123 Main St",
            "line2": None,
            "county": "Test County",
            "town": "Test Town",
            "postcode": "AB12 3CD",
        },
        "createdBy": "test_user",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "managingOrganisation": "96602abd-f265-4803-b4fb-413692279b5c",
        "modifiedBy": "test_user",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Location",
        "positionGCS": {"latitude": "51.5074", "longitude": "-0.1278"},
        "positionReferenceNumber_UPRN": 1234567890,
        "positionReferenceNumber_UBRN": 9876543210,
        "primaryAddress": True,
        "partOf": None,
    }

    response = client.put(f"/{test_location_id}", json=update_payload)
    assert response.status_code == HTTPStatus.OK

    assert response.json()["message"] == "Location updated successfully"
    assert response.json()["location"] == update_payload


def test_update_location_not_found(mock_repository: MockerFixture) -> None:
    mock_repository.update.side_effect = HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="Location not found"
    )

    update_payload = {
        "active": True,
        "address": {
            "line1": "123 Main St",
            "line2": None,
            "county": "Test County",
            "town": "Test Town",
            "postcode": "AB12 3CD",
        },
        "createdBy": "test_user",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "managingOrganisation": "96602abd-f265-4803-b4fb-413692279b5c",
        "modifiedBy": "test_user",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Location",
        "positionGCS": {"latitude": "51.5074", "longitude": "-0.1278"},
        "positionReferenceNumber_UPRN": 1234567890,
        "positionReferenceNumber_UBRN": 9876543210,
        "primaryAddress": True,
        "partOf": None,
    }

    response = client.put("/e13b21b1-8859-4364-9efb-951d43cc8264", json=update_payload)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Location not found"


def test_update_location_invalid_request_body() -> None:
    invalid_payload = {
        "name": "Test Update Location",
    }

    response = client.put(f"/{test_location_id}", json=invalid_payload)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        "detail": [
            {
                "input": {"name": "Test Update Location"},
                "loc": ["body", "active"],
                "msg": "Field required",
                "type": "missing",
            },
            {
                "input": {"name": "Test Update Location"},
                "loc": ["body", "address"],
                "msg": "Field required",
                "type": "missing",
            },
            {
                "input": {"name": "Test Update Location"},
                "loc": ["body", "managingOrganisation"],
                "msg": "Field required",
                "type": "missing",
            },
            {
                "input": {"name": "Test Update Location"},
                "loc": ["body", "primaryAddress"],
                "msg": "Field required",
                "type": "missing",
            },
        ]
    }

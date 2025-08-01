from http import HTTPStatus
from unittest.mock import MagicMock, Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from ftrs_data_layer.domain import Location
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from pytest_mock import MockerFixture

from location.app.service.location_service import LocationService

test_location_id = uuid4()


def get_mock_location() -> Location:
    return {
        "id": str(test_location_id),
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
        "modifiedDateTime": "2025-03-27T12:00:00",
    }


@pytest.fixture(autouse=True)
def mock_repository(mocker: MockerFixture) -> AttributeLevelRepository:
    mock_location_repository = MagicMock(spec=AttributeLevelRepository)
    mock_location_repository.get.return_value = Location(**get_mock_location())
    mock_location_repository.iter_records.return_value = iter(
        [Location(**get_mock_location())]
    )
    mock_location_repository.create = MagicMock()
    return mock_location_repository


@pytest.fixture(autouse=True)
def mock_logger(mocker: MockerFixture) -> Mock:
    mock_logger = Mock()
    return mock_logger


def test_get_location_by_id_returns_location(
    mock_repository: AttributeLevelRepository, mock_logger: Mock
) -> None:
    location_service = LocationService(
        location_repository=mock_repository, logger=mock_logger
    )
    result = location_service.get_location_by_id(location_id=test_location_id)
    assert isinstance(result, Location)
    assert result == Location(**get_mock_location())
    mock_repository.get.assert_called_once_with(test_location_id)


def test_get_location_by_id_raises_not_found(
    mock_repository: AttributeLevelRepository, mock_logger: Mock
) -> None:
    location_service = LocationService(
        location_repository=mock_repository, logger=mock_logger
    )
    test_location_id = str(uuid4())
    mock_repository.get.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        location_service.get_location_by_id(location_id=test_location_id)

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "Location not found"
    mock_repository.get.assert_called_once_with(test_location_id)


def test_get_locations_returns_list_of_locations(
    mock_repository: AttributeLevelRepository, mock_logger: Mock
) -> None:
    location_service = LocationService(
        location_repository=mock_repository, logger=mock_logger
    )
    result = location_service.get_locations()
    assert isinstance(result, list)
    assert result == [Location(**get_mock_location())]
    mock_repository.iter_records.assert_called_once()


def test_get_locations_raises_not_found(
    mock_repository: AttributeLevelRepository, mock_logger: Mock
) -> None:
    location_service = LocationService(
        location_repository=mock_repository, logger=mock_logger
    )
    mock_repository.iter_records.return_value = iter([])
    with pytest.raises(HTTPException) as exc_info:
        location_service.get_locations()
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "No locations found"
    mock_repository.iter_records.assert_called_once()


def test_create_location_creates_and_returns_location(
    mock_repository: AttributeLevelRepository, mock_logger: Mock
) -> None:
    location_service = LocationService(
        location_repository=mock_repository, logger=mock_logger
    )
    new_location = Location(**get_mock_location())
    new_location.id = str(uuid4())  # Ensure a new ID is generated
    mock_repository.create.return_value = new_location

    result = location_service.create_location(location=new_location)

    assert isinstance(result, Location)
    assert result == new_location
    mock_repository.create.assert_called_once_with(new_location)


def test_create_location_raises_error_on_invalid_data(
    mock_repository: AttributeLevelRepository, mock_logger: Mock
) -> None:
    location_service = LocationService(
        location_repository=mock_repository, logger=mock_logger
    )
    invalid_location = Location(**get_mock_location())
    invalid_location.id = None  # Simulate invalid data
    mock_repository.create = MagicMock(side_effect=ValueError("Invalid location data"))
    with pytest.raises(ValueError) as exc_info:
        location_service.create_location(location=invalid_location)
    assert exc_info.value.args[0] == "Invalid location data"

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from dos_ingest.service.location_service import LocationService
from fastapi import HTTPException
from ftrs_data_layer.domain import Location


@pytest.fixture
def location_service(
    location_repository_mock: MagicMock,
    logger_mock: MagicMock,
) -> LocationService:
    return LocationService(
        location_repository=location_repository_mock,
        logger=logger_mock,
    )


def test_get_location_by_id_returns_location(
    location_service: LocationService,
    location_repository_mock: MagicMock,
    sample_location: Location,
) -> None:
    location_repository_mock.get.return_value = sample_location

    result = location_service.get_location_by_id(location_id=str(sample_location.id))

    assert result == sample_location
    location_repository_mock.get.assert_called_once_with(str(sample_location.id))


def test_get_location_by_id_raises_not_found(
    location_service: LocationService,
    location_repository_mock: MagicMock,
) -> None:
    location_repository_mock.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        location_service.get_location_by_id(location_id="missing-id")

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "Location not found"


def test_get_locations_returns_items(
    location_service: LocationService,
    location_repository_mock: MagicMock,
    sample_location: Location,
) -> None:
    location_repository_mock.iter_records.return_value = [sample_location]

    result = location_service.get_locations()

    assert result == [sample_location]
    location_repository_mock.iter_records.assert_called_once()


def test_get_locations_raises_not_found_for_empty_result(
    location_service: LocationService,
    location_repository_mock: MagicMock,
) -> None:
    location_repository_mock.iter_records.return_value = []

    with pytest.raises(HTTPException) as exc_info:
        location_service.get_locations()

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == "No locations found"


def test_create_location_assigns_new_id_and_persists(
    location_service: LocationService,
    location_repository_mock: MagicMock,
    sample_location: Location,
) -> None:
    original_id = sample_location.id

    result = location_service.create_location(sample_location)

    assert result.id != original_id
    location_repository_mock.create.assert_called_once_with(sample_location)

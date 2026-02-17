from http import HTTPStatus
from typing import Iterator
from unittest.mock import MagicMock

import pytest
from dos_ingest import dependencies
from dos_ingest.router import location
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ftrs_data_layer.domain import Location


@pytest.fixture
def location_client(
    logger_mock: MagicMock,
    location_repository_mock: MagicMock,
    sample_location: Location,
) -> Iterator[tuple[TestClient, MagicMock, MagicMock]]:
    service_mock = MagicMock()
    service_mock.get_location_by_id.return_value = sample_location
    service_mock.get_locations.return_value = [sample_location]

    app = FastAPI()
    app.include_router(location.router, prefix="/Location")
    app.dependency_overrides[dependencies.logger_dependency] = lambda: logger_mock
    app.dependency_overrides[dependencies.loc_service_dependency] = lambda: service_mock
    app.dependency_overrides[dependencies.loc_repo_dependency] = lambda: location_repository_mock

    with TestClient(app) as client:
        yield client, service_mock, location_repository_mock

    app.dependency_overrides.clear()


def test_get_location_by_id_returns_location(
    location_client: tuple[TestClient, MagicMock, MagicMock],
    sample_location: Location,
) -> None:
    client, _, _ = location_client

    response = client.get(f"/Location/{sample_location.id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == str(sample_location.id)


def test_get_all_locations_returns_locations(
    location_client: tuple[TestClient, MagicMock, MagicMock],
) -> None:
    client, _, _ = location_client

    response = client.get("/Location/")

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), list)


def test_post_location_creates_record(
    location_client: tuple[TestClient, MagicMock, MagicMock],
    sample_location: Location,
) -> None:
    client, service_mock, _ = location_client

    response = client.post("/Location/", json=sample_location.model_dump(mode="json"))

    assert response.status_code == HTTPStatus.CREATED
    assert response.headers["location"].startswith("/Location/")
    service_mock.create_location.assert_called_once()


def test_delete_location_deletes_when_found(
    location_client: tuple[TestClient, MagicMock, MagicMock],
    sample_location: Location,
) -> None:
    client, _, location_repository_mock = location_client
    location_repository_mock.get.return_value = sample_location

    response = client.delete(f"/Location/{sample_location.id}")

    assert response.status_code == HTTPStatus.NO_CONTENT
    location_repository_mock.delete.assert_called_once_with(sample_location.id)


def test_delete_location_returns_404_when_missing(
    location_client: tuple[TestClient, MagicMock, MagicMock],
    sample_location: Location,
) -> None:
    client, _, location_repository_mock = location_client
    location_repository_mock.get.return_value = None

    response = client.delete(f"/Location/{sample_location.id}")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Location not found"


def test_put_location_updates_record(
    location_client: tuple[TestClient, MagicMock, MagicMock],
    sample_location: Location,
) -> None:
    client, _, location_repository_mock = location_client

    payload = sample_location.model_copy(update={"name": "Updated Site"})

    response = client.put(
        f"/Location/{sample_location.id}",
        json=payload.model_dump(mode="json"),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["name"] == "Updated Site"
    location_repository_mock.update.assert_called_once()

from http import HTTPStatus
from typing import Iterator
from unittest.mock import MagicMock

import pytest
from dos_ingest import dependencies
from dos_ingest.router import healthcare
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ftrs_data_layer.domain import HealthcareService


@pytest.fixture
def healthcare_client(
    logger_mock: MagicMock,
    healthcare_repository_mock: MagicMock,
    sample_healthcare_service: HealthcareService,
) -> Iterator[tuple[TestClient, MagicMock]]:
    healthcare_repository_mock.get.return_value = sample_healthcare_service
    healthcare_repository_mock.iter_records.return_value = [sample_healthcare_service]

    app = FastAPI()
    app.include_router(healthcare.router, prefix="/HealthcareService")
    app.dependency_overrides[dependencies.logger_dependency] = lambda: logger_mock
    app.dependency_overrides[dependencies.hs_repo_dependency] = (
        lambda: healthcare_repository_mock
    )

    with TestClient(app) as client:
        yield client, healthcare_repository_mock

    app.dependency_overrides.clear()


def test_get_healthcare_service_by_id_returns_record(
    healthcare_client: tuple[TestClient, MagicMock],
    sample_healthcare_service: HealthcareService,
) -> None:
    client, _ = healthcare_client

    response = client.get(f"/HealthcareService/{sample_healthcare_service.id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == str(sample_healthcare_service.id)


def test_get_healthcare_service_by_id_returns_404_when_missing(
    healthcare_client: tuple[TestClient, MagicMock],
    sample_healthcare_service: HealthcareService,
) -> None:
    client, healthcare_repository_mock = healthcare_client
    healthcare_repository_mock.get.return_value = None

    response = client.get(f"/HealthcareService/{sample_healthcare_service.id}")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Healthcare Service not found"


def test_get_all_healthcare_services_returns_list(
    healthcare_client: tuple[TestClient, MagicMock],
) -> None:
    client, healthcare_repository_mock = healthcare_client

    response = client.get("/HealthcareService/")

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), list)
    healthcare_repository_mock.iter_records.assert_called_once_with(10)


def test_put_healthcare_service_updates_existing_record(
    healthcare_client: tuple[TestClient, MagicMock],
    sample_healthcare_service: HealthcareService,
) -> None:
    client, healthcare_repository_mock = healthcare_client

    payload = sample_healthcare_service.model_copy(update={"name": "Updated Service"})

    response = client.put(
        f"/HealthcareService/{sample_healthcare_service.id}",
        json=payload.model_dump(mode="json"),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["name"] == "Updated Service"
    healthcare_repository_mock.update.assert_called_once()


def test_post_healthcare_service_creates_record(
    healthcare_client: tuple[TestClient, MagicMock],
) -> None:
    client, healthcare_repository_mock = healthcare_client

    response = client.post(
        "/HealthcareService/",
        json={
            "name": "Urgent GP Service",
            "active": True,
            "category": "GP Services",
            "type": "GP Consultation Service",
            "providedBy": "00000000-0000-0000-0000-00000000000a",
            "location": "10000000-0000-0000-0000-00000000000a",
            "telecom": {"phone_public": "0208 883 5555", "email": "example@nhs.net"},
            "openingTime": [],
            "symptomGroupSymptomDiscriminators": [],
            "dispositions": [],
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.headers["location"].startswith("/HealthcareService/")
    healthcare_repository_mock.create.assert_called_once()


def test_delete_healthcare_service_deletes_existing_record(
    healthcare_client: tuple[TestClient, MagicMock],
    sample_healthcare_service: HealthcareService,
) -> None:
    client, healthcare_repository_mock = healthcare_client

    response = client.delete(f"/HealthcareService/{sample_healthcare_service.id}")

    assert response.status_code == HTTPStatus.NO_CONTENT
    healthcare_repository_mock.delete.assert_called_once_with(sample_healthcare_service.id)

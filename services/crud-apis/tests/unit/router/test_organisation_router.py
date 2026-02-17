from http import HTTPStatus
from typing import Iterator
from unittest.mock import MagicMock

import pytest
from dos_ingest import dependencies
from dos_ingest.app import operation_outcome_exception_handler
from dos_ingest.router import organisation
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from ftrs_data_layer.domain import Organisation


@pytest.fixture
def organisation_client(
    logger_mock: MagicMock,
    org_repository_mock: MagicMock,
    sample_organisation: Organisation,
) -> Iterator[tuple[TestClient, MagicMock, MagicMock]]:
    service_mock = MagicMock()
    service_mock.get_all_organisations.return_value = [sample_organisation]
    service_mock.get_by_ods_code.return_value = [sample_organisation]

    app = FastAPI()
    app.include_router(organisation.router, prefix="/Organization")
    app.add_exception_handler(
        OperationOutcomeException, operation_outcome_exception_handler
    )
    app.dependency_overrides[dependencies.logger_dependency] = lambda: logger_mock
    app.dependency_overrides[dependencies.org_service_dependency] = lambda: service_mock
    app.dependency_overrides[dependencies.org_repo_dependency] = lambda: (
        org_repository_mock
    )

    with TestClient(app) as client:
        yield client, service_mock, org_repository_mock

    app.dependency_overrides.clear()


def _valid_update_payload(organisation_id: str) -> dict:
    return {
        "resourceType": "Organization",
        "id": organisation_id,
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ODS1",
            }
        ],
        "name": "Test Org",
        "active": True,
        "telecom": [{"system": "phone", "value": "0300 311 22 33", "use": "work"}],
    }


def test_get_organisations_returns_fhir_bundle(
    organisation_client: tuple[TestClient, MagicMock, MagicMock],
) -> None:
    client, _, _ = organisation_client

    response = client.get("/Organization/")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["resourceType"] == "Bundle"
    assert response.headers["content-type"].startswith("application/fhir+json")


def test_get_organisations_by_identifier_uses_ods_code(
    organisation_client: tuple[TestClient, MagicMock, MagicMock],
) -> None:
    client, service_mock, _ = organisation_client

    response = client.get("/Organization/?identifier=odsOrganisationCode|ODS1")

    assert response.status_code == HTTPStatus.OK
    service_mock.get_by_ods_code.assert_called_once_with("ODS1")


def test_get_organisation_by_id_returns_domain_record(
    organisation_client: tuple[TestClient, MagicMock, MagicMock],
    sample_organisation: Organisation,
) -> None:
    client, _, org_repository_mock = organisation_client
    org_repository_mock.get.return_value = sample_organisation

    response = client.get(f"/Organization/{sample_organisation.id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == str(sample_organisation.id)


def test_get_organisation_by_id_returns_404_when_missing(
    organisation_client: tuple[TestClient, MagicMock, MagicMock],
    sample_organisation: Organisation,
) -> None:
    client, _, org_repository_mock = organisation_client
    org_repository_mock.get.return_value = None

    response = client.get(f"/Organization/{sample_organisation.id}")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Organisation not found"


def test_update_organisation_returns_success_outcome(
    organisation_client: tuple[TestClient, MagicMock, MagicMock],
    sample_organisation: Organisation,
) -> None:
    client, service_mock, _ = organisation_client
    service_mock.process_organisation_update.return_value = True

    response = client.put(
        f"/Organization/{sample_organisation.id}",
        json=_valid_update_payload(str(sample_organisation.id)),
        headers={
            "nhse-product-id": "test-product-id",
            "content-type": "application/fhir+json",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["issue"][0]["code"] == "success"


def test_update_organisation_returns_information_when_no_change(
    organisation_client: tuple[TestClient, MagicMock, MagicMock],
    sample_organisation: Organisation,
) -> None:
    client, service_mock, _ = organisation_client
    service_mock.process_organisation_update.return_value = False

    response = client.put(
        f"/Organization/{sample_organisation.id}",
        json=_valid_update_payload(str(sample_organisation.id)),
        headers={
            "nhse-product-id": "test-product-id",
            "content-type": "application/fhir+json",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["issue"][0]["code"] == "information"


def test_update_organisation_bubbles_operation_outcome(
    organisation_client: tuple[TestClient, MagicMock, MagicMock],
    sample_organisation: Organisation,
) -> None:
    client, service_mock, _ = organisation_client
    service_mock.process_organisation_update.side_effect = OperationOutcomeException(
        {
            "resourceType": "OperationOutcome",
            "issue": [
                {"severity": "error", "code": "invalid", "diagnostics": "bad input"}
            ],
        }
    )

    response = client.put(
        f"/Organization/{sample_organisation.id}",
        json=_valid_update_payload(str(sample_organisation.id)),
        headers={
            "nhse-product-id": "test-product-id",
            "content-type": "application/fhir+json",
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json()["issue"][0]["code"] == "invalid"


def test_post_organisation_creates_record(
    organisation_client: tuple[TestClient, MagicMock, MagicMock],
    sample_organisation: Organisation,
) -> None:
    client, service_mock, _ = organisation_client
    service_mock.create_organisation.return_value = sample_organisation

    response = client.post(
        "/Organization/",
        json={
            "identifier_ODS_ODSCode": "ODS1",
            "active": True,
            "name": "Test Org",
            "telecom": [{"type": "phone", "value": "0300 311 22 33", "isPublic": True}],
            "endpoints": [],
        },
        headers={"nhse-product-id": "test-product-id"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.headers["location"].startswith("/Organization/")


def test_delete_organisation_removes_existing_record(
    organisation_client: tuple[TestClient, MagicMock, MagicMock],
    sample_organisation: Organisation,
) -> None:
    client, _, org_repository_mock = organisation_client
    org_repository_mock.get.return_value = sample_organisation

    response = client.delete(f"/Organization/{sample_organisation.id}")

    assert response.status_code == HTTPStatus.NO_CONTENT
    org_repository_mock.delete.assert_called_once_with(sample_organisation.id)

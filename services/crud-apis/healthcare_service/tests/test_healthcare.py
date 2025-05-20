
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from healthcare_service.app.router.healthcare import router

client = TestClient(router)

@patch("healthcare_service.app.router.healthcare.get_healthcare_service_by_id")
def test_get_healthcare_service_id_returns_service_if_exists(mock_get_service):
    mock_get_service.return_value = {"id": "00000000-0000-0000-0000-11111111111", "name": "Test Service"}
    response = client.get("/healthcareservice/00000000-0000-0000-0000-11111111111")
    assert response.status_code == 200
    assert response.json() == {"id": "00000000-0000-0000-0000-11111111111", "name": "Test Service"}

@patch("healthcare_service.app.router.healthcare.get_healthcare_service_by_id")
def test_get_healthcare_service_id_returns_404_if_not_found(mock_get_service):
    mock_get_service.return_value = JSONResponse(
        status_code=404, content={"message": "Healthcare Service not found"}
    )
    response = client.get("/healthcareservice/00000000-0000-0000-0000-11111111111")
    assert response.status_code == 404
    assert response.json() == {"message": "Healthcare Service not found"}


@patch("healthcare_service.app.router.healthcare.get_healthcare_service_repository")
def test_get_all_healthcare_services_returns_all_services(mock_repository):
    mock_repository.return_value.find_all.return_value = [
        {"id": "00000000-0000-0000-0000-11111111111", "name": "Service 1"},
        {"id": "00000000-0000-0000-0000-22222222222", "name": "Service 2"},
    ]
    response = client.get("/healthcareservice/")
    assert response.status_code == 200
    assert response.json() == [
        {"id": "00000000-0000-0000-0000-11111111111", "name": "Service 1"},
        {"id": "00000000-0000-0000-0000-22222222222", "name": "Service 2"},
    ]


@patch("healthcare_service.app.router.healthcare.get_healthcare_service_repository")
def test_get_all_healthcare_services_returns_empty_list_if_no_services(mock_repository):
    mock_repository.return_value.find_all.return_value = []
    response = client.get("/healthcareservice/")
    assert response.status_code == 200
    assert response.json() == []

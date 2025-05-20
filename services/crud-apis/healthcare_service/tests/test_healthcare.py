from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from healthcare_service.app.router.healthcare import (
    get_healthcare_service_by_id,
    router,
)

client = TestClient(router)


@patch("healthcare_service.app.router.healthcare.get_healthcare_service_by_id")
def test_get_healthcare_service_id_returns_service_if_exists(mock_get_service:MagicMock)-> None:
    mock_get_service.return_value = {
        "id": "00000000-0000-0000-0000-11111111111",
        "name": "Test Service",
    }
    response = client.get("/healthcareservice/00000000-0000-0000-0000-11111111111")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": "00000000-0000-0000-0000-11111111111",
        "name": "Test Service",
    }


@patch("healthcare_service.app.router.healthcare.get_healthcare_service_by_id")
def test_get_healthcare_service_id_returns_404_if_not_found(mock_get_service:MagicMock)-> None:
    mock_get_service.return_value = JSONResponse(
            status_code=HTTPStatus.NOT_FOUND, content={"message": "Healthcare Service not found"}
    )
    response = client.get("/healthcareservice/00000000-0000-0000-0000-11111111111")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"message": "Healthcare Service not found"}


def test_get_healthcare_service_id_raises_http_exception_for_invalid_id()-> None:
    with patch(
        "healthcare_service.app.router.healthcare.get_healthcare_service_by_id"
    ) as mock_get_service:
        mock_get_service.side_effect = HTTPException(
            status_code=404, detail="Healthcare Service not found"
        )
        with pytest.raises(HTTPException) as exc_info:
            get_healthcare_service_by_id("invalid-id")
        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert (
            exc_info.value.detail == "Invalid service_id format. Must be a valid UUID"
        )


@patch("healthcare_service.app.router.healthcare.get_healthcare_service_repository")
def test_get_all_healthcare_services_returns_all_services(mock_repository:MagicMock)-> None:
    mock_repository.return_value.find_all.return_value = [
        {"id": "00000000-0000-0000-0000-11111111111", "name": "Service 1"},
        {"id": "00000000-0000-0000-0000-22222222222", "name": "Service 2"},
    ]
    response = client.get("/healthcareservice/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {"id": "00000000-0000-0000-0000-11111111111", "name": "Service 1"},
        {"id": "00000000-0000-0000-0000-22222222222", "name": "Service 2"},
    ]


@patch("healthcare_service.app.router.healthcare.get_healthcare_service_repository")
def test_get_all_healthcare_services_returns_empty_list_if_no_services(mock_repository:MagicMock)-> None:
    mock_repository.return_value.find_all.return_value = []
    response = client.get("/healthcareservice/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []

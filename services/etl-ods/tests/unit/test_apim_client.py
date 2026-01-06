import os
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from pytest_mock import MockerFixture
from requests_mock import Mocker as RequestsMock

from common.apim_client import get_base_apim_api_url, make_apim_request


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "dev",
        "APIM_URL": "https://apim.nhs.uk/api",
    },
)
def test_get_base_apim_api_url_non_local() -> None:
    """Test get_base_apim_api_url returns APIM_URL for non-local environment."""
    get_base_apim_api_url.cache_clear()
    result = get_base_apim_api_url()
    assert result == "https://apim.nhs.uk/api"


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "local",
        "LOCAL_APIM_API_URL": "http://test-apim-api",
    },
)
def test_get_base_apim_api_url_local() -> None:
    """Test get_base_apim_api_url returns LOCAL_APIM_API_URL for local environment."""
    get_base_apim_api_url.cache_clear()
    result = get_base_apim_api_url()
    assert result == "http://test-apim-api"


def test_make_apim_request_success_with_jwt(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """Test make_apim_request for a successful request with JWT authentication."""
    mock_jwt_auth = MagicMock()
    mock_jwt_auth.get_auth_headers.return_value = {
        "Authorization": "Bearer test-jwt-token"
    }
    mocker.patch("common.apim_client.get_jwt_authenticator", return_value=mock_jwt_auth)

    mock_call = requests_mock.get(
        "https://apim.example.com/Organization",
        json={"resourceType": "Bundle", "total": 1},
        status_code=HTTPStatus.OK,
    )

    result = make_apim_request(
        "https://apim.example.com/Organization", jwt_required=True
    )

    assert result == {
        "resourceType": "Bundle",
        "total": 1,
        "status_code": HTTPStatus.OK,
    }
    assert mock_call.last_request.headers["Authorization"] == "Bearer test-jwt-token"
    assert mock_call.last_request.headers["Accept"] == "application/fhir+json"


def test_make_apim_request_without_jwt(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """Test make_apim_request without JWT authentication."""
    mock_call = requests_mock.get(
        "https://apim.example.com/Organization",
        json={"resourceType": "Bundle", "total": 0},
        status_code=HTTPStatus.OK,
    )

    result = make_apim_request(
        "https://apim.example.com/Organization", jwt_required=False
    )

    assert result == {
        "resourceType": "Bundle",
        "total": 0,
        "status_code": HTTPStatus.OK,
    }
    assert "Authorization" not in mock_call.last_request.headers


def test_make_apim_request_with_json_data(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """Test make_apim_request with JSON body and JWT."""
    mock_jwt_auth = MagicMock()
    mock_jwt_auth.get_auth_headers.return_value = {
        "Authorization": "Bearer test-jwt-token"
    }
    mocker.patch("common.apim_client.get_jwt_authenticator", return_value=mock_jwt_auth)

    expected_response = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "information"}],
    }
    mock_call = requests_mock.put(
        "https://apim.example.com/Organization/123",
        json={
            "resourceType": "OperationOutcome",
            "issue": [{"severity": "information"}],
        },
        status_code=HTTPStatus.OK,
    )

    result = make_apim_request(
        "https://apim.example.com/Organization/123",
        method="PUT",
        json={"name": "Updated Org"},
        jwt_required=True,
    )

    assert result == {**expected_response, "status_code": HTTPStatus.OK}
    assert mock_call.last_request.headers["Content-Type"] == "application/fhir+json"
    assert mock_call.last_request.headers["Authorization"] == "Bearer test-jwt-token"
    assert mock_call.last_request.json() == {"name": "Updated Org"}

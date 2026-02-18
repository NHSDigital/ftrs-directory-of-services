import json
from typing import Any
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from common.apim_client import make_apim_request


@pytest.fixture
def mock_jwt_auth() -> Mock:
    """Fixture providing a mock JWT authenticator."""
    mock_auth = Mock()
    mock_auth.get_auth_headers.return_value = {"Authorization": "Bearer test-token"}
    return mock_auth


@pytest.fixture
def mock_dependencies(mocker: MockerFixture, mock_jwt_auth: Mock) -> dict[str, Any]:
    """Fixture providing mocked dependencies for APIM requests."""
    mocks = {
        "get_jwt_authenticator": mocker.patch(
            "common.apim_client.get_jwt_authenticator", return_value=mock_jwt_auth
        ),
        "build_headers": mocker.patch(
            "common.apim_client.build_headers",
            return_value={"Content-Type": "application/json"},
        ),
        "make_request": mocker.patch(
            "common.apim_client.make_request", return_value={"success": True}
        ),
    }
    return mocks


class TestMakeApimRequest:
    """Test suite for make_apim_request function."""

    def test_make_apim_request_with_json_data(
        self, mock_dependencies: dict[str, Any], mock_jwt_auth: Mock
    ) -> None:
        """Test make_apim_request with JSON data payload."""
        mock_get_jwt_authenticator = mock_dependencies["get_jwt_authenticator"]
        mock_build_headers = mock_dependencies["build_headers"]
        mock_make_request = mock_dependencies["make_request"]

        test_url = "https://api.example.com/test"
        test_json_data = {"key": "value", "number": 123}

        result = make_apim_request(url=test_url, method="POST", json=test_json_data)

        expected_json_string = json.dumps(test_json_data)

        mock_get_jwt_authenticator.assert_called_once()
        mock_jwt_auth.get_auth_headers.assert_called_once()

        mock_build_headers.assert_called_once_with(
            json_data=test_json_data,
            json_string=expected_json_string,
            auth_headers={"Authorization": "Bearer test-token"},
        )

        mock_make_request.assert_called_once_with(
            url=test_url,
            method="POST",
            params=None,
            headers={"Content-Type": "application/json"},
            json=test_json_data,
        )

        assert result == {"success": True}

    def test_make_apim_request_without_json_data(
        self, mock_dependencies: dict[str, Any]
    ) -> None:
        """Test make_apim_request without JSON data."""
        mock_dependencies["make_request"].return_value = {"data": "response"}

        test_url = "https://api.example.com/get"

        result = make_apim_request(url=test_url)

        mock_dependencies["build_headers"].assert_called_once_with(
            json_data=None,
            json_string=None,
            auth_headers={"Authorization": "Bearer test-token"},
        )

        assert result == {"data": "response"}

    def test_make_apim_request_jwt_not_required(
        self, mock_dependencies: dict[str, Any]
    ) -> None:
        """Test make_apim_request when JWT authentication is not required."""
        mock_get_jwt_authenticator = mock_dependencies["get_jwt_authenticator"]
        mock_build_headers = mock_dependencies["build_headers"]
        mock_make_request = mock_dependencies["make_request"]
        mock_make_request.return_value = {"public": True}

        test_url = "https://api.example.com/public"

        result = make_apim_request(url=test_url, jwt_required=False)

        mock_get_jwt_authenticator.assert_not_called()

        mock_build_headers.assert_called_once_with(
            json_data=None,
            json_string=None,
            auth_headers=None,
        )

        assert result == {"public": True}

    def test_make_apim_request_with_params_and_kwargs(
        self, mock_dependencies: dict[str, Any], mock_jwt_auth: Mock
    ) -> None:
        """Test make_apim_request with additional params and kwargs."""
        mock_build_headers = mock_dependencies["build_headers"]
        mock_make_request = mock_dependencies["make_request"]
        mock_make_request.return_value = {"result": "success"}

        test_url = "https://api.example.com/complex"
        test_params = {"filter": "active", "limit": 10}
        test_json_data = {"update": "data"}

        result = make_apim_request(
            url=test_url,
            method="PUT",
            params=test_params,
            json=test_json_data,
            timeout=30,
            verify=True,
        )

        expected_json_string = json.dumps(test_json_data)

        mock_build_headers.assert_called_once_with(
            json_data=test_json_data,
            json_string=expected_json_string,
            auth_headers={"Authorization": "Bearer test-token"},
        )

        mock_make_request.assert_called_once_with(
            url=test_url,
            method="PUT",
            params=test_params,
            headers={"Content-Type": "application/json"},
            json=test_json_data,
            timeout=30,
            verify=True,
        )

        assert result == {"result": "success"}

    def test_make_apim_request_default_method_get(
        self, mock_dependencies: dict[str, Any]
    ) -> None:
        """Test make_apim_request uses default GET method."""
        mock_dependencies["build_headers"].return_value = {}
        mock_dependencies["make_request"].return_value = {"method": "GET"}

        test_url = "https://api.example.com/default"

        result = make_apim_request(url=test_url)

        mock_dependencies["make_request"].assert_called_once_with(
            url=test_url,
            method="GET",
            params=None,
            headers={},
        )

        assert result == {"method": "GET"}

    def test_make_apim_request_json_serialization_complex_data(
        self, mock_dependencies: dict[str, Any], mock_jwt_auth: Mock
    ) -> None:
        """Test json_string creation with complex data structures."""
        mock_dependencies["build_headers"].return_value = {}
        mock_dependencies["make_request"].return_value = {}

        complex_json_data = {
            "nested": {
                "list": [1, 2, {"inner": "value"}],
                "boolean": True,
                "null": None,
            }
        }

        make_apim_request(url="https://api.example.com/complex", json=complex_json_data)

        expected_json_string = json.dumps(complex_json_data)
        mock_dependencies["build_headers"].assert_called_once_with(
            json_data=complex_json_data,
            json_string=expected_json_string,
            auth_headers={"Authorization": "Bearer test-token"},
        )

    def test_make_apim_request_auth_headers_flow(
        self, mock_dependencies: dict[str, Any], mock_jwt_auth: Mock
    ) -> None:
        """Test the complete auth headers flow."""
        test_auth_headers = {
            "Authorization": "Bearer jwt-token-123",
            "X-API-Key": "api-key-456",
        }
        mock_jwt_auth.get_auth_headers.return_value = test_auth_headers

        mock_get_jwt_authenticator = mock_dependencies["get_jwt_authenticator"]

        mock_dependencies["build_headers"].return_value = {}
        mock_dependencies["make_request"].return_value = {}

        make_apim_request(url="https://api.example.com/auth")

        mock_get_jwt_authenticator.assert_called_once()
        mock_jwt_auth.get_auth_headers.assert_called_once()

        mock_dependencies["build_headers"].assert_called_once_with(
            json_data=None,
            json_string=None,
            auth_headers=test_auth_headers,
        )

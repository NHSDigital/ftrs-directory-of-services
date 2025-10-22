import os
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from pytest_mock import MockerFixture
from requests_mock import Mocker as RequestsMock

from pipeline.utilities import (
    build_headers,
    get_jwt_authenticator,
    handle_fhir_response,
    make_request,
)


def test_make_request_success(requests_mock: RequestsMock) -> None:
    """
    Test the make_request function for a successful request.
    """
    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    url = "https://api.example.com/resource"
    result = make_request(url)

    assert result.json() == {"key": "value"}

    assert mock_call.last_request.url == url
    assert mock_call.last_request.method == "GET"
    headers = mock_call.last_request.headers
    assert headers["Accept"] == "*/*"
    assert headers["Accept-Encoding"] == "gzip, deflate"
    assert headers["Connection"] == "keep-alive"
    assert "User-Agent" in headers


def test_make_request_with_params(
    requests_mock: RequestsMock,
) -> None:
    """
    Test the make_request function with parameters.
    """
    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    url = "https://api.example.com/resource"
    params = {"param1": "value1", "param2": "value2"}
    result = make_request(url, params=params)

    assert result.status_code == HTTPStatus.OK
    assert result.json() == {"key": "value"}

    assert (
        mock_call.last_request.url
        == "https://api.example.com/resource?param1=value1&param2=value2"
    )
    assert mock_call.last_request.method == "GET"
    headers = mock_call.last_request.headers
    assert headers["Accept"] == "*/*"
    assert headers["Accept-Encoding"] == "gzip, deflate"
    assert headers["Connection"] == "keep-alive"
    assert "User-Agent" in headers
    assert mock_call.last_request.qs == {"param1": ["value1"], "param2": ["value2"]}


def test_make_request_with_json_data(
    requests_mock: RequestsMock,
) -> None:
    """
    Test the make_request function with parameters.
    """
    mock_call = requests_mock.put(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    url = "https://api.example.com/resource"
    json = {"json": "value"}
    result = make_request(url, method="PUT", json=json)

    assert result.status_code == HTTPStatus.OK
    assert result.json() == {"key": "value"}

    assert mock_call.last_request.url == "https://api.example.com/resource"
    assert mock_call.last_request.method == "PUT"
    headers = mock_call.last_request.headers
    assert headers["Content-Type"] == "application/json"
    assert headers["Content-Length"] == "17"
    assert headers["Accept"] == "*/*"
    assert headers["Accept-Encoding"] == "gzip, deflate"
    assert headers["Connection"] == "keep-alive"
    assert "User-Agent" in headers
    assert mock_call.last_request.body.decode() == '{"json": "value"}'


def test_make_request_http_error(requests_mock: RequestsMock) -> None:
    """
    Test the make_request function for an HTTP error.
    """
    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        status_code=HTTPStatus.NOT_FOUND,
        json={"error": "Resource not found"},
    )

    url = "https://api.example.com/resource"

    with pytest.raises(
        requests.exceptions.HTTPError,
        match="404 Client Error: None for url: https://api.example.com/resource",
    ):
        make_request(url)

    assert mock_call.last_request.url == url
    assert mock_call.last_request.method == "GET"


def test_make_request_request_exception(requests_mock: RequestsMock) -> None:
    """
    Test the make_request function for a request exception.
    """
    mock_get = requests_mock.get(
        "https://api.example.com/resource",
        exc=requests.exceptions.RequestException("Connection error"),
    )

    url = "https://api.example.com/resource"

    with pytest.raises(requests.exceptions.RequestException, match="Connection error"):
        make_request(url)

    assert mock_get.last_request.url == url
    assert mock_get.last_request.method == "GET"


def test_make_request_fhir_operation_outcome(
    requests_mock: RequestsMock, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test make_request raises Exception on FHIR OperationOutcome and logs error.
    """
    fhir_response = {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "processing",
                "diagnostics": "FHIR error details",
            }
        ],
    }
    requests_mock.get(
        "https://api.example.com/fhir",
        json=fhir_response,
        status_code=200,
    )
    url = "https://api.example.com/fhir"
    with caplog.at_level("INFO"):
        with pytest.raises(OperationOutcomeException) as exc_info:
            make_request(url, fhir=True)
        assert str(exc_info.value) == "FHIR error details"
        assert "failed" not in caplog.text


def test_handle_fhir_response_no_operation_outcome(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test handle_fhir_response returns None if not OperationOutcome.
    """
    data = {"resourceType": "Patient", "id": "123"}
    with caplog.at_level("INFO"):
        result = handle_fhir_response(data, "GET")
    assert result is None


def test_handle_fhir_response_operation_outcome_error() -> None:
    """
    Test handle_fhir_response raises for OperationOutcome with error severity.
    """
    data = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "error", "code": "processing", "diagnostics": "fail"}],
    }
    with pytest.raises(OperationOutcomeException):
        handle_fhir_response(data, "GET")


def test_handle_fhir_response_operation_outcome_information_put() -> None:
    data = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "information", "code": "success", "diagnostics": "ok"}],
    }
    assert handle_fhir_response(data, "PUT") is None


def test_handle_fhir_response_operation_outcome_put_raises() -> None:
    data = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "error", "code": "success", "diagnostics": "ok"}],
    }
    with pytest.raises(OperationOutcomeException):
        handle_fhir_response(data, "PUT")


def test_handle_fhir_response_operation_outcome_non_put_raises() -> None:
    data = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "information", "code": "success", "diagnostics": "ok"}],
    }
    with pytest.raises(OperationOutcomeException):
        handle_fhir_response(data, "GET")


def test_build_headers_fhir_and_json() -> None:
    options = {
        "json_data": {"foo": "bar"},
        "json_string": '{"foo": "bar"}',
        "fhir": True,
        "url": "https://example.com",
        "method": "POST",
    }
    headers = build_headers(options)
    assert headers["Content-Type"] == "application/fhir+json"
    assert headers["Accept"] == "application/fhir+json"


def test_make_request_logs_http_error(
    requests_mock: RequestsMock, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test make_request logs HTTPError.
    """
    requests_mock.get(
        "https://api.example.com/resource",
        status_code=404,
        json={"error": "not found"},
    )
    url = "https://api.example.com/resource"
    with caplog.at_level("INFO"):
        with pytest.raises(requests.exceptions.HTTPError):
            make_request(url)
        assert (
            "HTTP error occurred: 404 Client Error: None for url: https://api.example.com/resource - Status Code: 404"
            in caplog.text
        )


def test_make_request_logs_request_exception(
    requests_mock: RequestsMock, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test make_request logs RequestException.
    """
    requests_mock.get(
        "https://api.example.com/resource",
        exc=requests.exceptions.RequestException("fail"),
    )
    url = "https://api.example.com/resource"
    with caplog.at_level("INFO"):
        with pytest.raises(requests.exceptions.RequestException):
            make_request(url)
        assert (
            "Request to GET https://api.example.com/resource failed: fail."
            in caplog.text
        )


def test_make_request_with_jwt_auth(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """
    Test the make_request function with JWT authentication.
    """
    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    # Mock the JWT authenticator
    mock_jwt_auth = MagicMock()
    mock_jwt_auth.get_auth_headers.return_value = {
        "Authorization": "Bearer test-jwt-token"
    }
    mocker.patch("pipeline.utilities.get_jwt_authenticator", return_value=mock_jwt_auth)

    url = "https://api.example.com/resource"
    result = make_request(url, jwt_required=True)

    assert result.status_code == HTTPStatus.OK
    assert result.json() == {"key": "value"}
    assert mock_call.last_request.headers["Authorization"] == "Bearer test-jwt-token"


def test_make_request_without_jwt_auth(requests_mock: RequestsMock) -> None:
    """
    Test the make_request function without JWT authentication.
    """
    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    url = "https://api.example.com/resource"
    result = make_request(url, jwt_required=False)

    assert result.status_code == HTTPStatus.OK
    assert result.json() == {"key": "value"}
    assert "Authorization" not in mock_call.last_request.headers


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
def test_get_jwt_authenticator_returns_configured_instance(
    mocker: MockerFixture,
) -> None:
    """
    Test that get_jwt_authenticator returns a properly configured JWTAuthenticator instance.
    """
    # Stop the global mock and create a new one for this test
    mocker.stopall()

    mock_jwt_authenticator_class = mocker.patch("pipeline.utilities.JWTAuthenticator")
    mock_instance = mocker.MagicMock()
    mock_jwt_authenticator_class.return_value = mock_instance

    # Call the function under test
    result = get_jwt_authenticator()

    # Verify the constructor was called with correct parameters
    mock_jwt_authenticator_class.assert_called_once_with(
        environment="dev",
        region="eu-west-2",
        secret_name="/ftrs-dos/dev/apim-jwt-credentials",
    )

    # Verify the instance is returned
    assert result == mock_instance


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "local",
        "AWS_REGION": "eu-west-2",
        "PROJECT_NAME": "ftrs",  # Add this if needed
    },
)
def test_get_jwt_authenticator_local_environment(mocker: MockerFixture) -> None:
    """
    Test that get_jwt_authenticator works with local environment.
    """
    mocker.stopall()

    mock_jwt_authenticator_class = mocker.patch("pipeline.utilities.JWTAuthenticator")
    mock_instance = mocker.MagicMock()
    mock_jwt_authenticator_class.return_value = mock_instance

    result = get_jwt_authenticator()

    # Check the actual call - it might be using a constructed secret path even for local
    mock_jwt_authenticator_class.assert_called_once_with(
        environment="local",
        region="eu-west-2",
        secret_name="/ftrs/local/apim-jwt-credentials",  # Adjust based on actual implementation
    )

    assert result == mock_instance


def test_build_headers_with_jwt_required(mocker: MockerFixture) -> None:
    """
    Test build_headers function includes JWT authentication headers when required.
    """
    mock_jwt_auth = MagicMock()
    mock_jwt_auth.get_auth_headers.return_value = {"Authorization": "Bearer test-token"}
    mocker.patch("pipeline.utilities.get_jwt_authenticator", return_value=mock_jwt_auth)

    options = {
        "json_data": {"foo": "bar"},
        "jwt_required": True,
        "fhir": False,
    }

    headers = build_headers(options)

    assert headers["Authorization"] == "Bearer test-token"
    assert headers["Content-Type"] == "application/json"


def test_build_headers_without_jwt_required() -> None:
    """
    Test build_headers function does not include JWT headers when not required.
    """
    options = {
        "json_data": {"foo": "bar"},
        "jwt_required": False,
        "fhir": False,
    }

    headers = build_headers(options)

    assert "Authorization" not in headers
    assert headers["Content-Type"] == "application/json"


def test_build_headers_fhir_with_jwt(mocker: MockerFixture) -> None:
    """
    Test build_headers function with both FHIR and JWT requirements.
    """
    mock_jwt_auth = MagicMock()
    mock_jwt_auth.get_auth_headers.return_value = {"Authorization": "Bearer fhir-token"}
    mocker.patch("pipeline.utilities.get_jwt_authenticator", return_value=mock_jwt_auth)

    options = {
        "json_data": {"resourceType": "Patient"},
        "json_string": '{"resourceType": "Patient"}',
        "fhir": True,
        "jwt_required": True,
    }

    headers = build_headers(options)

    assert headers["Authorization"] == "Bearer fhir-token"
    assert headers["Content-Type"] == "application/fhir+json"
    assert headers["Accept"] == "application/fhir+json"

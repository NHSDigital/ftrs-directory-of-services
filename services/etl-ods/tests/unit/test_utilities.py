import json
import os
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests
from botocore.exceptions import ClientError
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from pytest_mock import MockerFixture
from requests_mock import Mocker as RequestsMock

from pipeline.utilities import (
    _get_api_key,
    build_headers,
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
    Test handle_fhir_response returns data if not OperationOutcome.
    """
    data = {"resourceType": "Patient", "id": "123"}
    with caplog.at_level("INFO"):
        result = handle_fhir_response(data)
    assert result == data


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


def test_make_request_with_api_key(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """
    Test the make_request function with api_key header.
    """
    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )
    # Patch _get_api_key to return a known value
    mocker.patch("pipeline.utilities._get_api_key", return_value="test-api-key")
    url = "https://api.example.com/resource"
    result = make_request(url, api_key_required=True)
    assert result.status_code == HTTPStatus.OK
    assert result.json() == {"key": "value"}
    assert mock_call.last_request.headers["apikey"] == "test-api-key"


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "WORKSPACE": "test-workspace",
    },
)
@patch("pipeline.utilities.boto3.client")
def test__get_api_key_returns_value_from_json_secret(
    mock_boto_client: MagicMock,
) -> None:
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": '{"api_key": "super-secret-key"}'
    }

    api_key = _get_api_key()
    expected_secret_name = "/ftrs-dos/dev/apim-api-key"
    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId=expected_secret_name
    )
    assert api_key == "super-secret-key"


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "WORKSPACE": "test-workspace",
    },
)
@patch("pipeline.utilities.boto3.client")
def test__get_api_key_client_error_logs(
    mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    error_response = {"Error": {"Code": "ResourceNotFoundException"}}
    mock_secretsmanager.get_secret_value.side_effect = ClientError(
        error_response, "GetSecretValue"
    )
    with caplog.at_level("WARNING"):
        with pytest.raises(ClientError):
            _get_api_key()
        assert (
            "Error with secret: /ftrs-dos/dev/apim-api-key with message An error occurred (ResourceNotFoundException) when calling the GetSecretValue operation"
            in caplog.text
        )


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "WORKSPACE": "test-workspace",
    },
)
@patch("pipeline.utilities.boto3.client")
def test__get_api_key_json_decode_error_logs(
    mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test _get_api_key logs ETL_UTILS_007 when JSONDecodeError is thrown.
    """
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": "not-a-json-string"
    }
    with caplog.at_level("WARNING"):
        with pytest.raises(json.JSONDecodeError):
            _get_api_key()
        assert "Error secret is not in json format" in caplog.text

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
    _get_api_key_for_url,
    build_headers,
    get_base_apim_api_url,
    get_base_ods_terminology_api_url,
    handle_operation_outcomes,
    make_request,
)


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "dev",
        "APIM_URL": "non-local-api-url",
    },
)
def test_get_base_apim_api_url_non_local() -> None:
    """Test get_base_apim_api_url returns APIM_URL for non-local environment."""
    # Clear the cache to ensure the patched environment variables are used
    get_base_apim_api_url.cache_clear()
    result = get_base_apim_api_url()
    assert result == "non-local-api-url"


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "local",
        "LOCAL_APIM_API_URL": "http://test-apim-api",
    },
)
def test_get_base_apim_api_url_local() -> None:
    """Test get_base_apim_api_url returns LOCAL_APIM_API_URL for local environment."""
    # Clear the cache to ensure the patched environment variables are used
    get_base_apim_api_url.cache_clear()
    result = get_base_apim_api_url()
    assert result == "http://test-apim-api"


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "dev",
        "ODS_URL": "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
    },
)
def test_get_base_ods_terminology_api_url() -> None:
    """Test get_base_ods_terminology_api_url returns ODS_URL from environment."""
    # Clear the cache to ensure the patched environment variables are used
    get_base_ods_terminology_api_url.cache_clear()
    result = get_base_ods_terminology_api_url()
    assert (
        result
        == "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "local",
        "LOCAL_ODS_URL": "http://localhost:8080/ods-api",
    },
)
def test_get_base_ods_terminology_api_url_local() -> None:
    """Test get_base_ods_terminology_api_url returns LOCAL_ODS_URL for local environment."""
    # Clear the cache to ensure the patched environment variables are used
    get_base_ods_terminology_api_url.cache_clear()
    result = get_base_ods_terminology_api_url()
    assert result == "http://localhost:8080/ods-api"


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "local",
    },
    clear=True,
)
def test_get_base_ods_terminology_api_url_local_fallback() -> None:
    """Test get_base_ods_terminology_api_url falls back to int URL when LOCAL_ODS_URL is not set."""
    # Clear the cache to ensure the patched environment variables are used
    get_base_ods_terminology_api_url.cache_clear()
    result = get_base_ods_terminology_api_url()
    assert (
        result
        == "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )


def test_make_request_success(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """
    Test the make_request function for a successful request.
    """
    mocker.patch("pipeline.utilities._get_api_key_for_url", return_value="test-api-key")

    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    url = "https://api.example.com/resource"
    result = make_request(url)

    assert isinstance(result, dict)
    assert result == {"key": "value", "status_code": HTTPStatus.OK}

    assert mock_call.last_request.url == url
    assert mock_call.last_request.method == "GET"
    headers = mock_call.last_request.headers
    assert headers["Accept"] == "application/fhir+json"
    assert headers["apikey"] == "test-api-key"
    assert "X-Correlation-ID" in headers


def test_make_request_with_params(
    requests_mock: RequestsMock,
    mocker: MockerFixture,
) -> None:
    """
    Test the make_request function with parameters.
    """
    mocker.patch("pipeline.utilities._get_api_key_for_url", return_value="test-api-key")

    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    url = "https://api.example.com/resource"
    params = {"param1": "value1", "param2": "value2"}
    result = make_request(url, params=params)

    assert isinstance(result, dict)
    assert result == {"key": "value", "status_code": HTTPStatus.OK}

    assert (
        mock_call.last_request.url
        == "https://api.example.com/resource?param1=value1&param2=value2"
    )
    assert mock_call.last_request.method == "GET"
    headers = mock_call.last_request.headers
    assert headers["Accept"] == "application/fhir+json"
    assert headers["apikey"] == "test-api-key"
    assert "X-Correlation-ID" in headers
    assert mock_call.last_request.qs == {"param1": ["value1"], "param2": ["value2"]}


def test_make_request_with_json_data(
    requests_mock: RequestsMock,
    mocker: MockerFixture,
) -> None:
    """
    Test the make_request function with JSON data.
    """
    mocker.patch("pipeline.utilities._get_api_key_for_url", return_value="test-api-key")

    mock_call = requests_mock.put(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    url = "https://api.example.com/resource"
    json = {"json": "value"}
    result = make_request(url, method="PUT", json=json)

    assert result == {"key": "value", "status_code": HTTPStatus.OK}

    assert mock_call.last_request.url == "https://api.example.com/resource"
    assert mock_call.last_request.method == "PUT"
    headers = mock_call.last_request.headers
    assert headers["Content-Type"] == "application/fhir+json"
    assert headers["Accept"] == "application/fhir+json"
    assert headers["apikey"] == "test-api-key"
    assert "X-Correlation-ID" in headers
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
    requests_mock: RequestsMock, caplog: pytest.LogCaptureFixture, mocker: MockerFixture
) -> None:
    """
    Test make_request raises OperationOutcomeException on FHIR OperationOutcome with error severity.
    """
    mocker.patch("pipeline.utilities._get_api_key_for_url", return_value="test-api-key")

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
        with pytest.raises(OperationOutcomeException):
            make_request(url)


def test_handle_operation_outcomes_no_operation_outcome(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test handle_operation_outcomes returns data if not OperationOutcome.
    """
    data = {"resourceType": "Patient", "id": "123"}
    with caplog.at_level("INFO"):
        result = handle_operation_outcomes(data, "GET")
    assert result == {"resourceType": "Patient", "id": "123"}


def test_handle_operation_outcomes_error() -> None:
    """
    Test handle_operation_outcomes raises for OperationOutcome with error severity.
    """
    data = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "error", "code": "processing", "diagnostics": "fail"}],
    }
    with pytest.raises(OperationOutcomeException):
        handle_operation_outcomes(data, "GET")


def test_handle_operation_outcomes_information_put() -> None:
    """
    Test handle_operation_outcomes returns data for PUT with informational OperationOutcome.
    """
    data = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "information", "code": "success", "diagnostics": "ok"}],
    }
    result = handle_operation_outcomes(data, "PUT")
    assert result == data


def test_handle_operation_outcomes_put_raises() -> None:
    """
    Test handle_operation_outcomes raises for PUT with error OperationOutcome.
    """
    data = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "error", "code": "success", "diagnostics": "ok"}],
    }
    with pytest.raises(OperationOutcomeException):
        handle_operation_outcomes(data, "PUT")


def test_handle_operation_outcomes_non_put_raises() -> None:
    """
    Test handle_operation_outcomes raises for non-PUT with informational OperationOutcome.
    """
    data = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "information", "code": "success", "diagnostics": "ok"}],
    }
    with pytest.raises(OperationOutcomeException):
        handle_operation_outcomes(data, "GET")


def test_build_headers_fhir_and_json(mocker: MockerFixture) -> None:
    """
    Test build_headers creates proper FHIR headers with API key.
    """
    mocker.patch("pipeline.utilities._get_api_key_for_url", return_value="test-api-key")

    options = {
        "json_data": {"foo": "bar"},
        "json_string": '{"foo": "bar"}',
        "url": "https://example.com",
        "method": "POST",
    }
    headers = build_headers(options)
    assert headers["Content-Type"] == "application/fhir+json"
    assert headers["Accept"] == "application/fhir+json"
    assert headers["apikey"] == "test-api-key"
    assert "X-Correlation-ID" in headers


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


def test_make_request_json_decode_error(
    requests_mock: RequestsMock, caplog: pytest.LogCaptureFixture, mocker: MockerFixture
) -> None:
    """
    Test make_request logs and raises JSONDecodeError when response is not valid JSON.
    """
    mocker.patch("pipeline.utilities._get_api_key_for_url", return_value="test-api-key")

    requests_mock.get(
        "https://api.example.com/resource",
        text="This is not JSON",
        status_code=HTTPStatus.OK,
    )

    url = "https://api.example.com/resource"
    with caplog.at_level("INFO"):
        with pytest.raises(json.JSONDecodeError):
            make_request(url)
        assert "Error decoding json with issue:" in caplog.text


def test_make_request_with_ods_terminology_api_key(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """
    Test make_request uses ODS Terminology API key for api.service.nhs.uk URLs.
    """
    mocker.patch("pipeline.utilities._get_api_key_for_url", return_value="ods-api-key")

    mock_call = requests_mock.get(
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
        json={"resourceType": "Bundle", "total": 0},
        status_code=HTTPStatus.OK,
    )

    url = (
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )
    result = make_request(url)

    assert result == {
        "resourceType": "Bundle",
        "total": 0,
        "status_code": HTTPStatus.OK,
    }
    assert mock_call.last_request.headers["apikey"] == "ods-api-key"


def test_make_request_without_response_correlation_id(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """
    Test make_request handles response without X-Correlation-ID header.
    """
    mocker.patch("pipeline.utilities._get_api_key_for_url", return_value="test-api-key")

    # Mock response without X-Correlation-ID header
    requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
        headers={},  # No X-Correlation-ID in response
    )

    url = "https://api.example.com/resource"
    result = make_request(url)

    assert result == {"key": "value", "status_code": HTTPStatus.OK}


def test_make_request_with_response_correlation_id(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """
    Test make_request handles response with X-Correlation-ID header.
    """
    mocker.patch("pipeline.utilities._get_api_key_for_url", return_value="test-api-key")
    mock_logger = mocker.patch("pipeline.utilities.ods_utils_logger")

    # Mock response with X-Correlation-ID header
    requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
        headers={"X-Correlation-ID": "response-correlation-123"},
    )

    url = "https://api.example.com/resource"
    result = make_request(url)

    assert result == {"key": "value", "status_code": HTTPStatus.OK}
    # Verify logger was called with response correlation ID
    mock_logger.append_keys.assert_any_call(
        response_correlation_id="response-correlation-123"
    )


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("pipeline.utilities.boto3.client")
def test__get_api_key_for_url_returns_apim_key(
    mock_boto_client: MagicMock,
) -> None:
    """
    Test _get_api_key_for_url returns APIM API key for non-ODS Terminology URLs.
    """
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": '{"api_key": "apim-secret-key"}'
    }

    api_key = _get_api_key_for_url("https://test-apim-api.example.com/Organization")
    expected_secret_name = "/ftrs-dos/dev/apim-api-key"
    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId=expected_secret_name
    )
    assert api_key == "apim-secret-key"


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("pipeline.utilities.boto3.client")
def test__get_api_key_for_url_ods_terminology_key(
    mock_boto_client: MagicMock,
) -> None:
    """
    Test _get_api_key_for_url returns ODS Terminology API key for api.service.nhs.uk URLs.
    """
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": '{"api_key": "ods-terminology-key"}'
    }

    api_key = _get_api_key_for_url(
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )
    expected_secret_name = "/ftrs-dos/dev/ods-terminology-api-key"
    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId=expected_secret_name
    )
    assert api_key == "ods-terminology-key"


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("pipeline.utilities.boto3.client")
def test__get_api_key_for_url_client_error_logs(
    mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test _get_api_key_for_url logs and raises ClientError when secret not found.
    """
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    error_response = {"Error": {"Code": "ResourceNotFoundException"}}
    mock_secretsmanager.get_secret_value.side_effect = ClientError(
        error_response, "GetSecretValue"
    )
    with caplog.at_level("WARNING"):
        with pytest.raises(ClientError):
            _get_api_key_for_url("https://test-apim-api.example.com/Organization")
        assert "Error with secret: /ftrs-dos/dev/apim-api-key" in caplog.text


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("pipeline.utilities.boto3.client")
def test__get_api_key_for_url_client_error_non_resource_not_found(
    mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test _get_api_key_for_url raises ClientError for non-ResourceNotFoundException errors without logging.
    """
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    error_response = {"Error": {"Code": "AccessDeniedException"}}
    mock_secretsmanager.get_secret_value.side_effect = ClientError(
        error_response, "GetSecretValue"
    )
    with caplog.at_level("WARNING"):
        with pytest.raises(ClientError):
            _get_api_key_for_url("https://test-apim-api.example.com/Organization")
        assert "Error with secret:" not in caplog.text


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("pipeline.utilities.boto3.client")
def test__get_api_key_for_url_json_decode_error_logs(
    mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": "not-a-json-string"
    }
    with caplog.at_level("WARNING"):
        with pytest.raises(json.JSONDecodeError):
            _get_api_key_for_url("https://test-apim-api.example.com/Organization")
        assert "Error decoding json with issue:" in caplog.text


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "local",
        "LOCAL_API_KEY": "local-apim-key",
        "LOCAL_ODS_TERMINOLOGY_API_KEY": "local-ods-key",
    },
)
def test__get_api_key_for_url_local_environment(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test _get_api_key_for_url uses local environment variables in local environment.
    """
    with caplog.at_level("INFO"):
        apim_key = _get_api_key_for_url(
            "https://test-apim-api.example.com/Organization"
        )
        assert apim_key == "local-apim-key"
        assert (
            "Running in local environment, using LOCAL api key environment variable."
            in caplog.text
        )

        ods_key = _get_api_key_for_url(
            "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
        )
        assert ods_key == "local-ods-key"

        assert (
            "Running in local environment, using LOCAL api key environment variable."
            in caplog.text
        )


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "local",
        "LOCAL_API_KEY": "fallback-key",
    },
)
def test__get_api_key_for_url_local_ods_fallback_to_local_api_key(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test _get_api_key_for_url falls back to LOCAL_API_KEY when LOCAL_ODS_TERMINOLOGY_API_KEY is not set.
    """
    with caplog.at_level("INFO"):
        ods_key = _get_api_key_for_url(
            "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
        )
        assert ods_key == "fallback-key"
        assert (
            "Running in local environment, using LOCAL api key environment variable."
            in caplog.text
        )

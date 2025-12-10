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
    _add_api_key_to_headers,
    _get_api_key_for_url,
    _get_local_api_key,
    _get_production_api_key,
    _get_secret_from_aws,
    _is_mock_testing_mode,
    _is_ods_terminology_request,
    _update_logger_with_response_headers,
    build_headers,
    get_base_apim_api_url,
    get_base_ods_terminology_api_url,
    get_jwt_authenticator,
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
    """Test make_request logs HTTPError."""
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

    assert result == {"key": "value", "status_code": HTTPStatus.OK}
    assert mock_call.last_request.headers["Authorization"] == "Bearer test-jwt-token"


def test_make_request_without_jwt_auth(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """
    Test the make_request function without JWT authentication.
    """
    mocker.patch("pipeline.utilities._get_api_key_for_url", return_value="test-api-key")

    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    url = "https://api.example.com/resource"
    result = make_request(url, jwt_required=False)

    assert result == {"key": "value", "status_code": HTTPStatus.OK}
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
        secret_name="/ftrs-dos/dev/dos-ingest-jwt-credentials",
    )

    # Verify the instance is returned
    assert result == mock_instance


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
    Test _get_api_key_for_url returns ODS Terminology API key for terminology URLs.
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
@patch("pipeline.utilities._get_secret_from_aws")
def test__get_api_key_for_url_client_error_logs(
    mock_get_secret: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test _get_api_key_for_url logs and raises KeyError when secret not found.
    """
    mock_get_secret.side_effect = KeyError(
        "Secret not found: /ftrs-dos/dev/ods-terminology-api-key"
    )

    with caplog.at_level("WARNING"):
        with pytest.raises(KeyError):
            _get_api_key_for_url(
                "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
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
            _get_api_key_for_url(
                "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
            )
        assert "Error with secret:" not in caplog.text


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
        secret_name="/ftrs/local/dos-ingest-jwt-credentials",  # Adjust based on actual implementation
    )

    assert result == mock_instance


def test_build_headers_with_jwt_required(mocker: MockerFixture) -> None:
    """
    Test build_headers function includes JWT authentication headers when required.
    """
    mock_jwt_auth = MagicMock()
    mock_jwt_auth.get_auth_headers.return_value = {"Authorization": "Bearer test-token"}
    mocker.patch("pipeline.utilities.get_jwt_authenticator", return_value=mock_jwt_auth)
    mocker.patch("pipeline.utilities._get_api_key_for_url", return_value="test-api-key")

    options = {
        "json_data": {"foo": "bar"},
        "jwt_required": True,
        "url": "https://example.com",
    }

    headers = build_headers(options)

    assert headers["Authorization"] == "Bearer test-token"
    assert headers["Content-Type"] == "application/fhir+json"
    assert headers["Accept"] == "application/fhir+json"
    assert headers["apikey"] == "test-api-key"


def test_build_headers_without_jwt_required(mocker: MockerFixture) -> None:
    """
    Test build_headers function does not include JWT headers when not required.
    """
    mocker.patch("pipeline.utilities._get_api_key_for_url", return_value="test-api-key")
    options = {
        "json_data": {"foo": "bar"},
        "jwt_required": False,
        "url": "https://example.com",
    }

    headers = build_headers(options)

    assert "Authorization" not in headers
    assert headers["Content-Type"] == "application/fhir+json"
    assert headers["Accept"] == "application/fhir+json"
    assert headers["apikey"] == "test-api-key"


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


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("pipeline.utilities._get_secret_from_aws")
def test__get_api_key_for_url_json_decode_error_logs(
    mock_get_secret: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    mock_get_secret.return_value = "not-a-json-string"

    result = _get_api_key_for_url(
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )
    assert result == "not-a-json-string"


@patch.dict(
    os.environ,
    {"ENVIRONMENT": "local", "LOCAL_ODS_TERMINOLOGY_API_KEY": "local-ods-key"},
)
def test__get_api_key_for_url_local_environment() -> None:
    """
    Test _get_api_key_for_url returns local ODS Terminology API key in local environment.
    """
    api_key = _get_api_key_for_url(
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )
    assert api_key == "local-ods-key"


@patch.dict(
    os.environ,
    {"ENVIRONMENT": "local", "LOCAL_API_KEY": "fallback-key"},
)
def test__get_api_key_for_url_local_ods_fallback_to_local_api_key() -> None:
    """
    Test _get_api_key_for_url falls back to LOCAL_API_KEY when LOCAL_ODS_TERMINOLOGY_API_KEY is not set.
    """
    api_key = _get_api_key_for_url(
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )
    assert api_key == "fallback-key"


def test__get_api_key_for_url_non_ods_terminology_returns_empty() -> None:
    """
    Test _get_api_key_for_url returns empty string for non-ODS Terminology API URLs.
    """
    api_key = _get_api_key_for_url(
        "https://api.service.nhs.uk/dos-ingest/FHIR/R4/Organization"
    )
    assert api_key == ""

    api_key = _get_api_key_for_url("https://example.com/api")
    assert api_key == ""


@patch.dict(os.environ, {"ENVIRONMENT": "local", "LOCAL_API_KEY": "local-key"})
def test__get_api_key_for_url_non_ods_terminology_ignores_local_key() -> None:
    """
    Test _get_api_key_for_url ignores local API key for non-ODS Terminology URLs.
    """
    api_key = _get_api_key_for_url(
        "https://api.service.nhs.uk/dos-ingest/FHIR/R4/Organization"
    )
    assert api_key == ""


def test_get_api_key_returns_empty_in_mock_mode() -> None:
    """Test _get_api_key_for_url returns empty string when MOCK_TESTING_SCENARIOS is enabled (LocalStack has no auth)."""
    url = (
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )

    with patch.dict(
        "os.environ", {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "dev"}
    ):
        result = _get_api_key_for_url(url)

    assert result == ""


@patch("pipeline.utilities._get_secret_from_aws")
def test_get_api_key_uses_secrets_manager_when_no_test_mode(
    mock_get_secret: MagicMock,
) -> None:
    mock_get_secret.return_value = "real-secret-key"

    url = (
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )

    with patch.dict(
        "os.environ",
        {"ENVIRONMENT": "dev", "PROJECT_NAME": "ftrs", "AWS_REGION": "eu-west-2"},
        clear=True,
    ):
        result = _get_api_key_for_url(url)

    assert result == "real-secret-key"
    mock_get_secret.assert_called_once_with("/ftrs/dev/ods-terminology-api-key")


def test_get_api_key_returns_empty_for_non_ods_url() -> None:
    """Test _get_api_key_for_url returns empty string for non-ODS URLs."""
    url = "https://example.com/api/data"

    with patch.dict(
        "os.environ", {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "dev"}
    ):
        result = _get_api_key_for_url(url)

    assert result == ""


def test_mock_mode_returns_empty_and_takes_precedence_over_local_env() -> None:
    """Test MOCK_TESTING_SCENARIOS takes precedence over local environment and returns empty string."""
    url = (
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )
    local_key = "local-key"

    with patch.dict(
        "os.environ",
        {
            "ENVIRONMENT": "dev",
            "MOCK_TESTING_SCENARIOS": "true",
            "LOCAL_API_KEY": local_key,
        },
    ):
        result = _get_api_key_for_url(url)

    assert result == ""


def test_mock_mode_does_not_call_secrets_manager() -> None:
    """Test that MOCK_TESTING_SCENARIOS bypasses production Secrets Manager and returns empty string."""
    url = (
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )

    with patch("pipeline.utilities._get_secret_from_aws") as mock_get_secret:
        with patch.dict(
            "os.environ", {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "dev"}
        ):
            result = _get_api_key_for_url(url)

        mock_get_secret.assert_not_called()
        assert result == ""


def test_test_mode_key_only_from_environment() -> None:
    """Test mock testing only works when MOCK_TESTING_SCENARIOS is explicitly set."""
    url = (
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )

    # Without MOCK_TESTING_SCENARIOS env var, should not use mock mode
    with patch.dict(
        "os.environ", {"ENVIRONMENT": "local", "LOCAL_API_KEY": "local-key"}, clear=True
    ):
        result = _get_api_key_for_url(url)

    assert result == "local-key"


@patch("pipeline.utilities._get_secret_from_aws")
def test_normal_operation_without_test_mode(mock_get_secret: MagicMock) -> None:
    """Test normal Secrets Manager flow when MOCK_TESTING_SCENARIOS not set."""
    # Mock Secrets Manager
    mock_get_secret.return_value = "real-key"

    url = (
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )

    with patch.dict(
        "os.environ",
        {"ENVIRONMENT": "dev", "PROJECT_NAME": "ftrs", "AWS_REGION": "eu-west-2"},
        clear=True,
    ):
        result = _get_api_key_for_url(url)

    assert result == "real-key"
    mock_get_secret.assert_called_once_with("/ftrs/dev/ods-terminology-api-key")


def test_local_environment_without_test_mode() -> None:
    """Test local environment works when MOCK_TESTING_SCENARIOS not set."""
    url = (
        "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )

    with patch.dict(
        "os.environ",
        {"ENVIRONMENT": "local", "LOCAL_API_KEY": "my-local-key"},
        clear=True,
    ):
        result = _get_api_key_for_url(url)

    assert result == "my-local-key"


# Tests for refactored helper functions
class TestIsOdsTerminologyRequest:
    """Test cases for _is_ods_terminology_request function."""

    def test_ods_terminology_url_returns_true(self) -> None:
        """Test that ODS terminology URL returns True."""

        url = "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
        assert _is_ods_terminology_request(url) is True

    def test_non_ods_terminology_url_returns_false(self) -> None:
        """Test that non-ODS terminology URL returns False."""

        url = "https://api.example.com/other-api"
        assert _is_ods_terminology_request(url) is False

    def test_partial_match_returns_false(self) -> None:
        """Test that partial match returns False."""

        url = "https://api.service.nhs.uk/organisation-data"
        assert _is_ods_terminology_request(url) is False

    def test_empty_url_returns_false(self) -> None:
        """Test that empty URL returns False."""

        assert _is_ods_terminology_request("") is False


class TestIsMockTestingMode:
    """Test cases for _is_mock_testing_mode function."""

    def test_mock_testing_disabled_returns_false(self) -> None:
        """Test that when MOCK_TESTING_SCENARIOS is not set, returns False."""

        with patch.dict(os.environ, {}, clear=True):
            assert _is_mock_testing_mode() is False

    def test_mock_testing_false_returns_false(self) -> None:
        """Test that when MOCK_TESTING_SCENARIOS is false, returns False."""

        with patch.dict(os.environ, {"MOCK_TESTING_SCENARIOS": "false"}, clear=True):
            assert _is_mock_testing_mode() is False

    def test_mock_testing_dev_environment_returns_true(self) -> None:
        """Test that mock testing enabled in dev environment returns True."""

        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "dev"},
            clear=True,
        ):
            assert _is_mock_testing_mode() is True

    def test_mock_testing_test_environment_returns_true(self) -> None:
        """Test that mock testing enabled in test environment returns True."""

        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "test"},
            clear=True,
        ):
            assert _is_mock_testing_mode() is True

    def test_mock_testing_prod_environment_raises_error(self) -> None:
        """Test that mock testing in prod environment raises ValueError."""

        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "prod"},
            clear=True,
        ):
            with pytest.raises(
                ValueError,
                match="Mock testing scenarios cannot be enabled in environment 'prod'",
            ):
                _is_mock_testing_mode()

    def test_mock_testing_invalid_environment_raises_error(self) -> None:
        """Test that mock testing in invalid environment raises ValueError."""

        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "staging"},
            clear=True,
        ):
            with pytest.raises(
                ValueError,
                match="Mock testing scenarios cannot be enabled in environment 'staging'",
            ):
                _is_mock_testing_mode()

    def test_mock_testing_case_insensitive(self) -> None:
        """Test that environment checking is case insensitive."""

        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "TRUE", "ENVIRONMENT": "DEV"},
            clear=True,
        ):
            assert _is_mock_testing_mode() is True

    def test_mock_testing_empty_environment_raises_error(self) -> None:
        """Test that mock testing with empty environment raises ValueError."""

        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": ""},
            clear=True,
        ):
            with pytest.raises(
                ValueError,
                match="Mock testing scenarios cannot be enabled in environment ''",
            ):
                _is_mock_testing_mode()


class TestGetLocalApiKey:
    """Test cases for _get_local_api_key function."""

    def test_get_local_ods_api_key_priority(self) -> None:
        """Test that LOCAL_ODS_TERMINOLOGY_API_KEY has priority over LOCAL_API_KEY."""

        with patch.dict(
            os.environ,
            {
                "LOCAL_ODS_TERMINOLOGY_API_KEY": "ods-key",
                "LOCAL_API_KEY": "general-key",
            },
            clear=True,
        ):
            result = _get_local_api_key()
            assert result == "ods-key"

    def test_fallback_to_local_api_key(self) -> None:
        """Test fallback to LOCAL_API_KEY when LOCAL_ODS_TERMINOLOGY_API_KEY not set."""

        with patch.dict(os.environ, {"LOCAL_API_KEY": "general-key"}, clear=True):
            result = _get_local_api_key()
            assert result == "general-key"

    def test_both_keys_missing_returns_empty(self) -> None:
        """Test that when both keys are missing, returns empty string."""

        with patch.dict(os.environ, {}, clear=True):
            result = _get_local_api_key()
            assert result == ""


class TestGetSecretFromAws:
    """Test cases for _get_secret_from_aws function."""

    @patch("pipeline.utilities.boto3.client")
    def test_get_secret_json_format(self, mock_boto_client: MagicMock) -> None:
        """Test retrieving secret in JSON format."""

        mock_secretsmanager = MagicMock()
        mock_boto_client.return_value = mock_secretsmanager
        mock_secretsmanager.get_secret_value.return_value = {
            "SecretString": '{"api_key": "test-key-value"}'
        }

        result = _get_secret_from_aws("/test/secret")

        assert result == "test-key-value"
        mock_secretsmanager.get_secret_value.assert_called_once_with(
            SecretId="/test/secret"
        )

    @patch("pipeline.utilities.boto3.client")
    def test_get_secret_plain_text_format(self, mock_boto_client: MagicMock) -> None:
        """Test retrieving secret in plain text format."""

        mock_secretsmanager = MagicMock()
        mock_boto_client.return_value = mock_secretsmanager
        mock_secretsmanager.get_secret_value.return_value = {
            "SecretString": "plain-text-secret"
        }

        result = _get_secret_from_aws("/test/secret")

        assert result == "plain-text-secret"

    @patch("pipeline.utilities.boto3.client")
    def test_get_secret_json_without_api_key(self, mock_boto_client: MagicMock) -> None:
        """Test retrieving JSON secret without api_key field."""

        mock_secretsmanager = MagicMock()
        mock_boto_client.return_value = mock_secretsmanager
        mock_secretsmanager.get_secret_value.return_value = {
            "SecretString": '{"other_field": "value"}'
        }

        result = _get_secret_from_aws("/test/secret")

        assert result == '{"other_field": "value"}'

    @patch("pipeline.utilities.boto3.client")
    def test_get_secret_not_found_raises_key_error(
        self, mock_boto_client: MagicMock
    ) -> None:
        """Test that ResourceNotFoundException raises KeyError."""

        mock_secretsmanager = MagicMock()
        mock_boto_client.return_value = mock_secretsmanager
        error_response = {"Error": {"Code": "ResourceNotFoundException"}}
        mock_secretsmanager.get_secret_value.side_effect = ClientError(
            error_response, "GetSecretValue"
        )

        with pytest.raises(KeyError, match="Secret not found: /test/secret"):
            _get_secret_from_aws("/test/secret")

    @patch("pipeline.utilities.boto3.client")
    def test_get_secret_other_client_error_raises(
        self, mock_boto_client: MagicMock
    ) -> None:
        """Test that other ClientError types are re-raised."""

        mock_secretsmanager = MagicMock()
        mock_boto_client.return_value = mock_secretsmanager
        error_response = {"Error": {"Code": "AccessDeniedException"}}
        mock_secretsmanager.get_secret_value.side_effect = ClientError(
            error_response, "GetSecretValue"
        )

        with pytest.raises(ClientError):
            _get_secret_from_aws("/test/secret")


class TestGetProductionApiKey:
    """Test cases for _get_production_api_key function."""

    @patch("pipeline.utilities._get_secret_from_aws")
    @patch.dict(os.environ, {"PROJECT_NAME": "test-project", "ENVIRONMENT": "prod"})
    def test_get_production_api_key_success(self, mock_get_secret: MagicMock) -> None:
        """Test successful production API key retrieval."""

        mock_get_secret.return_value = "prod-api-key"

        result = _get_production_api_key()

        assert result == "prod-api-key"
        mock_get_secret.assert_called_once_with(
            "/test-project/prod/ods-terminology-api-key"
        )

    @patch("pipeline.utilities._get_secret_from_aws")
    @patch.dict(os.environ, {"PROJECT_NAME": "test-project", "ENVIRONMENT": "prod"})
    def test_get_production_api_key_key_error_reraises(
        self, mock_get_secret: MagicMock
    ) -> None:
        """Test that KeyError from _get_secret_from_aws is re-raised."""

        mock_get_secret.side_effect = KeyError("Secret not found")

        with pytest.raises(KeyError):
            _get_production_api_key()

    @patch("pipeline.utilities._get_secret_from_aws")
    @patch.dict(os.environ, {"PROJECT_NAME": "test-project", "ENVIRONMENT": "prod"})
    def test_get_production_api_key_other_exception_reraises(
        self, mock_get_secret: MagicMock
    ) -> None:
        """Test that other exceptions from _get_secret_from_aws are re-raised."""

        mock_get_secret.side_effect = Exception("Some other error")

        with pytest.raises(Exception):
            _get_production_api_key()


class TestAddApiKeyToHeaders:
    def test_add_api_key_no_key_does_nothing(self) -> None:
        headers = {"existing": "header"}
        _add_api_key_to_headers(headers, "")

        assert headers == {"existing": "header"}

    @patch("pipeline.utilities._is_mock_testing_mode")
    def test_add_api_key_production_mode(self, mock_is_mock_mode: MagicMock) -> None:
        mock_is_mock_mode.return_value = False
        headers = {}

        _add_api_key_to_headers(headers, "test-key")

        assert headers["apikey"] == "test-key"
        assert "x-api-key" not in headers


class TestGetBaseOdsTerminologyApiUrlMissingEnv:
    """Test cases for get_base_ods_terminology_api_url when ODS_URL is missing."""

    def test_get_base_ods_terminology_api_url_missing_env_raises_error(self) -> None:
        """Test that missing ODS_URL environment variable raises KeyError."""
        get_base_ods_terminology_api_url.cache_clear()

        with patch.dict(os.environ, {"ENVIRONMENT": "prod"}, clear=True):
            with pytest.raises(
                KeyError, match="ODS_URL environment variable is not set"
            ):
                get_base_ods_terminology_api_url()


class TestGetSecretFromAwsJsonError:
    """Test cases for JSON decode error handling in _get_secret_from_aws."""

    @patch("pipeline.utilities.json.loads")
    @patch("pipeline.utilities.boto3.client")
    @patch.dict(os.environ, {"AWS_REGION": "eu-west-2"})
    def test_get_secret_from_aws_json_decode_error_coverage(
        self, mock_boto_client: MagicMock, mock_json_loads: MagicMock
    ) -> None:
        """Test that JSONDecodeError is properly handled in _get_secret_from_aws."""
        mock_secretsmanager = MagicMock()
        mock_boto_client.return_value = mock_secretsmanager
        secret_string = "some-secret-value"
        mock_secretsmanager.get_secret_value.return_value = {
            "SecretString": secret_string
        }

        mock_json_loads.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)

        result = _get_secret_from_aws("/test/secret")

        assert result == secret_string
        mock_json_loads.assert_called_once_with(secret_string)


class TestUpdateLoggerWithResponseHeaders:
    """Test cases for _update_logger_with_response_headers function."""

    def test_update_logger_with_request_id_header(self) -> None:
        """Test that response request ID header is properly logged."""
        mock_response = MagicMock()
        mock_response.headers.get.side_effect = lambda header: {
            "X-Correlation-ID": None,
            "X-Request-ID": "test-request-id-123",
        }.get(header)

        with patch("pipeline.utilities.ods_utils_logger") as mock_logger:
            _update_logger_with_response_headers(mock_response)

            mock_logger.append_keys.assert_called_once_with(
                response_request_id="test-request-id-123"
            )

    def test_update_logger_with_both_headers(self) -> None:
        """Test that both correlation ID and request ID headers are properly logged."""
        mock_response = MagicMock()
        mock_response.headers.get.side_effect = lambda header: {
            "X-Correlation-ID": "test-correlation-id-456",
            "X-Request-ID": "test-request-id-123",
        }.get(header)

        with patch("pipeline.utilities.ods_utils_logger") as mock_logger:
            _update_logger_with_response_headers(mock_response)

            # Should be called twice - once for each header
            assert str(mock_logger.append_keys.call_count) == "2"
            mock_logger.append_keys.assert_any_call(
                response_correlation_id="test-correlation-id-456"
            )
            mock_logger.append_keys.assert_any_call(
                response_request_id="test-request-id-123"
            )

    def test_update_logger_with_no_headers(self) -> None:
        """Test that function handles missing headers gracefully."""
        mock_response = MagicMock()
        mock_response.headers.get.return_value = None

        with patch("pipeline.utilities.ods_utils_logger") as mock_logger:
            _update_logger_with_response_headers(mock_response)

            mock_logger.append_keys.assert_not_called()

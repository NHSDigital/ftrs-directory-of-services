import json
import os
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests
from botocore.exceptions import ClientError
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockerFixture
from requests_mock import Mocker as RequestsMock

from common.utils import (
    _get_api_key_for_url,
    build_headers,
    get_base_apim_api_url,
    get_base_ods_terminology_api_url,
    handle_operation_outcomes,
    is_mock_testing_mode,
    is_ods_terminology_request,
    make_request,
)


class TestUtils:
    """Test cases for utility functions in common.utils."""

    @patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "dev",
            "APIM_URL": "non-local-api-url",
        },
    )
    def test_get_base_apim_api_url_non_local(self) -> None:
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
    def test_get_base_apim_api_url_local(self) -> None:
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
    def test_get_base_ods_terminology_api_url(self) -> None:
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
    def test_get_base_ods_terminology_api_url_local(self) -> None:
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
    def test_get_base_ods_terminology_api_url_local_fallback(self) -> None:
        """Test get_base_ods_terminology_api_url falls back to int URL when LOCAL_ODS_URL is not set."""
        # Clear the cache to ensure the patched environment variables are used
        get_base_ods_terminology_api_url.cache_clear()
        result = get_base_ods_terminology_api_url()
        assert (
            result
            == "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
        )

    def test_make_request_success(
        self, requests_mock: RequestsMock, mocker: MockerFixture
    ) -> None:
        """
        Test the make_request function for a successful request.
        """
        mocker.patch("common.utils._get_api_key_for_url", return_value="test-api-key")

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
        self,
        requests_mock: RequestsMock,
        mocker: MockerFixture,
    ) -> None:
        """
        Test the make_request function with parameters.
        """
        mocker.patch("common.utils._get_api_key_for_url", return_value="test-api-key")

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
        self,
        requests_mock: RequestsMock,
        mocker: MockerFixture,
    ) -> None:
        """
        Test the make_request function with JSON data.
        """
        mocker.patch("common.utils._get_api_key_for_url", return_value="test-api-key")

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

    def test_make_request_http_error(self, requests_mock: RequestsMock) -> None:
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

    def test_make_request_request_exception(self, requests_mock: RequestsMock) -> None:
        """
        Test the make_request function for a request exception.
        """
        mock_get = requests_mock.get(
            "https://api.example.com/resource",
            exc=requests.exceptions.RequestException("Connection error"),
        )

        url = "https://api.example.com/resource"

        with pytest.raises(
            requests.exceptions.RequestException, match="Connection error"
        ):
            make_request(url)

        assert mock_get.last_request.url == url
        assert mock_get.last_request.method == "GET"

    def test_make_request_fhir_operation_outcome(
        self,
        requests_mock: RequestsMock,
        caplog: pytest.LogCaptureFixture,
        mocker: MockerFixture,
    ) -> None:
        """
        Test make_request raises OperationOutcomeException on FHIR OperationOutcome with error severity.
        """
        mocker.patch("common.utils._get_api_key_for_url", return_value="test-api-key")

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
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test handle_operation_outcomes returns data if not OperationOutcome.
        """
        data = {"resourceType": "Patient", "id": "123"}
        with caplog.at_level("INFO"):
            result = handle_operation_outcomes(data, "GET")
        assert result == {"resourceType": "Patient", "id": "123"}

    def test_handle_operation_outcomes_error(self) -> None:
        """
        Test handle_operation_outcomes raises for OperationOutcome with error severity.
        """
        data = {
            "resourceType": "OperationOutcome",
            "issue": [
                {"severity": "error", "code": "processing", "diagnostics": "fail"}
            ],
        }
        with pytest.raises(OperationOutcomeException):
            handle_operation_outcomes(data, "GET")

    def test_handle_operation_outcomes_information_put(self) -> None:
        """
        Test handle_operation_outcomes returns data for PUT with informational OperationOutcome.
        """
        data = {
            "resourceType": "OperationOutcome",
            "issue": [
                {"severity": "information", "code": "success", "diagnostics": "ok"}
            ],
        }
        result = handle_operation_outcomes(data, "PUT")
        assert result == data

    def test_handle_operation_outcomes_put_raises(self) -> None:
        """
        Test handle_operation_outcomes raises for PUT with error OperationOutcome.
        """
        data = {
            "resourceType": "OperationOutcome",
            "issue": [{"severity": "error", "code": "success", "diagnostics": "ok"}],
        }
        with pytest.raises(OperationOutcomeException):
            handle_operation_outcomes(data, "PUT")

    def test_handle_operation_outcomes_non_put_raises(self) -> None:
        """
        Test handle_operation_outcomes raises for non-PUT with informational OperationOutcome.
        """
        data = {
            "resourceType": "OperationOutcome",
            "issue": [
                {"severity": "information", "code": "success", "diagnostics": "ok"}
            ],
        }
        with pytest.raises(OperationOutcomeException):
            handle_operation_outcomes(data, "GET")

    def test_build_headers_fhir_and_json(self, mocker: MockerFixture) -> None:
        """
        Test build_headers creates proper FHIR headers with API key.
        """
        mocker.patch("common.utils._get_api_key_for_url", return_value="test-api-key")

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
        self, requests_mock: RequestsMock, caplog: pytest.LogCaptureFixture
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
        self, requests_mock: RequestsMock, caplog: pytest.LogCaptureFixture
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
        self,
        requests_mock: RequestsMock,
        caplog: pytest.LogCaptureFixture,
        mocker: MockerFixture,
    ) -> None:
        """
        Test make_request logs and raises JSONDecodeError when response is not valid JSON.
        """
        mocker.patch("common.utils._get_api_key_for_url", return_value="test-api-key")

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
        self, requests_mock: RequestsMock, mocker: MockerFixture
    ) -> None:
        """
        Test make_request uses ODS Terminology API key for api.service.nhs.uk URLs.
        """
        mocker.patch("common.utils._get_api_key_for_url", return_value="ods-api-key")

        mock_call = requests_mock.get(
            "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
            json={"resourceType": "Bundle", "total": 0},
            status_code=HTTPStatus.OK,
        )

        url = "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
        result = make_request(url)

        assert result == {
            "resourceType": "Bundle",
            "total": 0,
            "status_code": HTTPStatus.OK,
        }
        assert mock_call.last_request.headers["apikey"] == "ods-api-key"

    def test_make_request_without_response_correlation_id(
        self, requests_mock: RequestsMock, mocker: MockerFixture
    ) -> None:
        """
        Test make_request handles response without X-Correlation-ID header.
        """
        mocker.patch("common.utils._get_api_key_for_url", return_value="test-api-key")

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
        self, requests_mock: RequestsMock, mocker: MockerFixture
    ) -> None:
        """
        Test make_request handles response with X-Correlation-ID header.
        """
        mocker.patch("common.utils._get_api_key_for_url", return_value="test-api-key")
        mock_logger = mocker.patch("common.utils.utils_logger")

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
        self, requests_mock: RequestsMock, mocker: MockerFixture
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
        mocker.patch("common.utils.get_jwt_authenticator", return_value=mock_jwt_auth)

        url = "https://api.example.com/resource"
        result = make_request(url, jwt_required=True)

        assert result == {"key": "value", "status_code": HTTPStatus.OK}
        mock_jwt_auth.get_auth_headers.assert_called_once()
        print("Headers sent:", mock_call.last_request.headers)
        assert (
            mock_call.last_request.headers["Authorization"] == "Bearer test-jwt-token"
        )

    def test_make_request_without_jwt_auth(
        self, requests_mock: RequestsMock, mocker: MockerFixture
    ) -> None:
        """
        Test the make_request function without JWT authentication.
        """
        mocker.patch("common.utils._get_api_key_for_url", return_value="test-api-key")

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
    @patch("common.utils.boto3.client")
    def test_get_api_key_for_url_ods_terminology_key(
        self, mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
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
    @patch("common.utils.boto3.client")
    def test__get_api_key_for_url_client_error_logs(
        self, mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
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
                _get_api_key_for_url(
                    "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
                )
            assert (
                "Error with secret: /ftrs-dos/dev/ods-terminology-api-key"
                in caplog.text
            )

    @patch.dict(
        os.environ,
        {
            "PROJECT_NAME": "ftrs-dos",
            "ENVIRONMENT": "dev",
            "AWS_REGION": "eu-west-2",
        },
    )
    @patch("common.utils.boto3.client")
    def test__get_api_key_for_url_client_error_non_resource_not_found(
        self, mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
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

    def test_build_headers_with_jwt_required(self, mocker: MockerFixture) -> None:
        """
        Test build_headers function includes JWT authentication headers when required.
        """
        mock_jwt_auth = MagicMock()
        mock_jwt_auth.get_auth_headers.return_value = {
            "Authorization": "Bearer test-token"
        }
        mocker.patch("common.utils.get_jwt_authenticator", return_value=mock_jwt_auth)
        mocker.patch("common.utils._get_api_key_for_url", return_value="test-api-key")

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

    def test_build_headers_without_jwt_required(self, mocker: MockerFixture) -> None:
        """
        Test build_headers function does not include JWT headers when not required.
        """
        mocker.patch("common.utils._get_api_key_for_url", return_value="test-api-key")
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

    def test_build_headers_fhir_with_jwt(self, mocker: MockerFixture) -> None:
        """
        Test build_headers function with both FHIR and JWT requirements.
        """
        mock_jwt_auth = MagicMock()
        mock_jwt_auth.get_auth_headers.return_value = {
            "Authorization": "Bearer fhir-token"
        }
        mocker.patch("common.utils.get_jwt_authenticator", return_value=mock_jwt_auth)

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
    @patch("common.utils.boto3.client")
    def test__get_api_key_for_url_json_decode_error_logs(
        self, mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        mock_secretsmanager = MagicMock()
        mock_boto_client.return_value = mock_secretsmanager
        mock_secretsmanager.get_secret_value.return_value = {
            "SecretString": "not-a-json-string"
        }
        with caplog.at_level("WARNING"):
            with pytest.raises(json.JSONDecodeError):
                _get_api_key_for_url(
                    "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
                )
            assert "Error decoding json with issue:" in caplog.text

    @patch.dict(
        os.environ,
        {"ENVIRONMENT": "local", "LOCAL_ODS_TERMINOLOGY_API_KEY": "local-ods-key"},
    )
    def test__get_api_key_for_url_local_environment(self) -> None:
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
    def test__get_api_key_for_url_local_ods_fallback_to_local_api_key(self) -> None:
        """
        Test _get_api_key_for_url falls back to LOCAL_API_KEY when LOCAL_ODS_TERMINOLOGY_API_KEY is not set.
        """
        api_key = _get_api_key_for_url(
            "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
        )
        assert api_key == "fallback-key"

    def test__get_api_key_for_url_non_ods_terminology_returns_empty(self) -> None:
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
    def test__get_api_key_for_url_non_ods_terminology_ignores_local_key(self) -> None:
        """
        Test _get_api_key_for_url ignores local API key for non-ODS Terminology URLs.
        """
        api_key = _get_api_key_for_url(
            "https://api.service.nhs.uk/dos-ingest/FHIR/R4/Organization"
        )
        assert api_key == ""


class TestIsOdsTerminologyRequest:
    """Test cases for is_ods_terminology_request function."""

    def test_ods_terminology_url_returns_true(self) -> None:
        """Test that URLs containing 'organisation-data-terminology-api' return True."""
        url = "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
        assert is_ods_terminology_request(url) is True

    def test_non_ods_terminology_url_returns_false(self) -> None:
        """Test that URLs not containing 'organisation-data-terminology-api' return False."""
        url = "https://api.service.nhs.uk/some-other-api/fhir/Organization"
        assert is_ods_terminology_request(url) is False

    def test_partial_match_returns_false(self) -> None:
        """Test that partial matches don't incorrectly return True."""
        url = "https://api.service.nhs.uk/organisation-data-api/fhir/Organization"
        assert is_ods_terminology_request(url) is False

    def test_empty_url_returns_false(self) -> None:
        """Test that empty URL returns False."""
        assert is_ods_terminology_request("") is False

    def test_case_sensitive_check(self) -> None:
        """Test that the check is case sensitive."""
        url = "https://api.service.nhs.uk/ORGANISATION-DATA-TERMINOLOGY-API/fhir/Organization"
        assert is_ods_terminology_request(url) is False

    def test_url_with_additional_path_returns_true(self) -> None:
        """Test that URLs with additional path components still match."""
        url = "https://api.service.nhs.uk/organisation-data-terminology-api/v1/fhir/Organization/123"
        assert is_ods_terminology_request(url) is True


class TestIsMockTestingMode:
    """Test cases for is_mock_testing_mode function."""

    def test_mock_testing_disabled_returns_false(self) -> None:
        """Test that when MOCK_TESTING_SCENARIOS is not 'true', returns False."""
        with patch.dict(os.environ, {"MOCK_TESTING_SCENARIOS": "false"}, clear=False):
            assert is_mock_testing_mode() is False

    def test_mock_testing_not_set_returns_false(self) -> None:
        """Test that when MOCK_TESTING_SCENARIOS is not set, returns False."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_mock_testing_mode() is False

    def test_mock_testing_enabled_dev_environment_returns_true(self) -> None:
        """Test that mock testing enabled in dev environment returns True."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "dev"},
            clear=False,
        ):
            assert is_mock_testing_mode() is True

    def test_mock_testing_enabled_test_environment_returns_true(self) -> None:
        """Test that mock testing enabled in test environment returns True."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "test"},
            clear=False,
        ):
            assert is_mock_testing_mode() is True

    def test_mock_testing_enabled_production_environment_raises_error(self) -> None:
        """Test that mock testing in production environment raises ValueError."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "prod"},
            clear=False,
        ):
            with pytest.raises(ValueError) as exc_info:
                is_mock_testing_mode()

            assert (
                "Mock testing scenarios cannot be enabled in environment 'prod'"
                in str(exc_info.value)
            )
            assert "Only allowed in: dev, test" in str(exc_info.value)

    def test_mock_testing_enabled_invalid_environment_raises_error(self) -> None:
        """Test that mock testing in invalid environment raises ValueError."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "staging"},
            clear=False,
        ):
            with pytest.raises(ValueError) as exc_info:
                is_mock_testing_mode()

            assert (
                "Mock testing scenarios cannot be enabled in environment 'staging'"
                in str(exc_info.value)
            )

    def test_mock_testing_case_insensitive_environment(self) -> None:
        """Test that environment check is case insensitive."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "DEV"},
            clear=False,
        ):
            assert is_mock_testing_mode() is True

    def test_mock_testing_case_insensitive_scenarios_flag(self) -> None:
        """Test that MOCK_TESTING_SCENARIOS check is case insensitive."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "TRUE", "ENVIRONMENT": "dev"},
            clear=False,
        ):
            assert is_mock_testing_mode() is True

    def test_mock_testing_no_environment_set_raises_error(self) -> None:
        """Test that mock testing with no environment set raises ValueError."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true"},
            clear=True,
        ):
            with pytest.raises(ValueError) as exc_info:
                is_mock_testing_mode()

            assert "Mock testing scenarios cannot be enabled in environment ''" in str(
                exc_info.value
            )

    @patch("common.utils.utils_logger")
    def test_mock_testing_invalid_environment_logs_error(
        self, mock_logger: MagicMock
    ) -> None:
        """Test that invalid environment logs appropriate error."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "prod"},
            clear=False,
        ):
            with pytest.raises(ValueError):
                is_mock_testing_mode()

            mock_logger.log.assert_called_once_with(
                OdsETLPipelineLogBase.ETL_UTILS_011, env="prod"
            )

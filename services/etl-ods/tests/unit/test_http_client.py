import json
from http import HTTPStatus

import pytest
import requests
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from pytest_mock import MockerFixture
from requests_mock import Mocker as RequestsMock

from common.http_client import build_headers, handle_operation_outcomes, make_request


def test_make_request_success(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """Test the make_request function for a successful request."""
    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    headers = build_headers()
    result = make_request("https://api.example.com/resource", headers=headers)

    assert isinstance(result, dict)
    assert result == {"key": "value", "status_code": HTTPStatus.OK}
    assert mock_call.last_request.url == "https://api.example.com/resource"
    assert mock_call.last_request.method == "GET"


def test_make_request_with_params(requests_mock: RequestsMock) -> None:
    """Test the make_request function with parameters."""
    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    headers = build_headers()
    params = {"param1": "value1", "param2": "value2"}
    result = make_request(
        "https://api.example.com/resource", params=params, headers=headers
    )

    assert result == {"key": "value", "status_code": HTTPStatus.OK}
    assert mock_call.last_request.qs == {"param1": ["value1"], "param2": ["value2"]}


def test_make_request_with_json_data(requests_mock: RequestsMock) -> None:
    """Test the make_request function with JSON data."""
    mock_call = requests_mock.put(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    json_data = {"json": "value"}
    headers = build_headers(json_data=json_data)
    result = make_request(
        "https://api.example.com/resource",
        method="PUT",
        headers=headers,
        json=json_data,
    )

    assert result == {"key": "value", "status_code": HTTPStatus.OK}
    assert mock_call.last_request.headers["Content-Type"] == "application/fhir+json"
    assert mock_call.last_request.body.decode() == '{"json": "value"}'


def test_make_request_http_error(requests_mock: RequestsMock) -> None:
    """Test the make_request function for an HTTP error."""
    requests_mock.get(
        "https://api.example.com/resource",
        status_code=HTTPStatus.NOT_FOUND,
        json={"error": "Resource not found"},
    )

    headers = build_headers()
    with pytest.raises(
        requests.exceptions.HTTPError,
        match="404 Client Error: None for url: https://api.example.com/resource",
    ):
        make_request("https://api.example.com/resource", headers=headers)


def test_make_request_request_exception(requests_mock: RequestsMock) -> None:
    """Test the make_request function for a request exception."""
    requests_mock.get(
        "https://api.example.com/resource",
        exc=requests.exceptions.RequestException("Connection error"),
    )

    headers = build_headers()
    with pytest.raises(requests.exceptions.RequestException, match="Connection error"):
        make_request("https://api.example.com/resource", headers=headers)


def test_make_request_fhir_operation_outcome(requests_mock: RequestsMock) -> None:
    """Test make_request raises OperationOutcomeException on FHIR OperationOutcome with error severity."""
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

    headers = build_headers()
    with pytest.raises(OperationOutcomeException):
        make_request("https://api.example.com/fhir", headers=headers)


def test_make_request_json_decode_error(
    requests_mock: RequestsMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test make_request logs and raises JSONDecodeError when response is not valid JSON."""
    requests_mock.get(
        "https://api.example.com/resource",
        text="This is not JSON",
        status_code=HTTPStatus.OK,
    )

    headers = build_headers()
    with caplog.at_level("INFO"):
        with pytest.raises(json.JSONDecodeError):
            make_request("https://api.example.com/resource", headers=headers)
        assert "Error decoding json with issue:" in caplog.text


def test_make_request_logs_http_error(
    requests_mock: RequestsMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test make_request logs HTTPError."""
    requests_mock.get(
        "https://api.example.com/resource",
        status_code=404,
        json={"error": "not found"},
    )

    headers = build_headers()
    with caplog.at_level("INFO"):
        with pytest.raises(requests.exceptions.HTTPError):
            make_request("https://api.example.com/resource", headers=headers)
        assert "HTTP error occurred" in caplog.text


def test_make_request_logs_request_exception(
    requests_mock: RequestsMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test make_request logs RequestException."""
    requests_mock.get(
        "https://api.example.com/resource",
        exc=requests.exceptions.RequestException("fail"),
    )

    headers = build_headers()
    with caplog.at_level("INFO"):
        with pytest.raises(requests.exceptions.RequestException):
            make_request("https://api.example.com/resource", headers=headers)
        assert "failed: fail" in caplog.text


def test_make_request_with_response_correlation_id(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """Test make_request handles response with X-Correlation-ID header."""
    mock_logger = mocker.patch("common.http_client.http_client_logger")

    requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
        headers={"X-Correlation-ID": "response-correlation-123"},
    )

    headers = build_headers()
    result = make_request("https://api.example.com/resource", headers=headers)

    assert result == {"key": "value", "status_code": HTTPStatus.OK}
    mock_logger.append_keys.assert_any_call(
        response_correlation_id="response-correlation-123"
    )


def test_handle_operation_outcomes_no_operation_outcome() -> None:
    """Test handle_operation_outcomes returns data if not OperationOutcome."""
    data = {"resourceType": "Patient", "id": "123"}
    result = handle_operation_outcomes(data, "GET")
    assert result == {"resourceType": "Patient", "id": "123"}


def test_handle_operation_outcomes_error() -> None:
    """Test handle_operation_outcomes raises for OperationOutcome with error severity."""
    data = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "error", "code": "processing", "diagnostics": "fail"}],
    }
    with pytest.raises(OperationOutcomeException):
        handle_operation_outcomes(data, "GET")


def test_handle_operation_outcomes_information_put() -> None:
    """Test handle_operation_outcomes returns data for PUT with informational OperationOutcome."""
    data = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "information", "code": "success", "diagnostics": "ok"}],
    }
    result = handle_operation_outcomes(data, "PUT")
    assert result == data


def test_handle_operation_outcomes_put_with_error_raises() -> None:
    """Test handle_operation_outcomes raises for PUT with error OperationOutcome."""
    data = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "error", "code": "success", "diagnostics": "ok"}],
    }
    with pytest.raises(OperationOutcomeException):
        handle_operation_outcomes(data, "PUT")


def test_handle_operation_outcomes_non_put_with_information_raises() -> None:
    """Test handle_operation_outcomes raises for non-PUT with informational OperationOutcome."""
    data = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "information", "code": "success", "diagnostics": "ok"}],
    }
    with pytest.raises(OperationOutcomeException):
        handle_operation_outcomes(data, "GET")


def test_build_headers_basic() -> None:
    """Test build_headers creates basic FHIR headers."""
    headers = build_headers()
    assert headers["Accept"] == "application/fhir+json"
    assert "X-Correlation-ID" in headers
    assert "Content-Type" not in headers


def test_build_headers_with_json_data() -> None:
    """Test build_headers includes Content-Type for JSON data."""
    headers = build_headers(json_data={"foo": "bar"})
    assert headers["Content-Type"] == "application/fhir+json"
    assert headers["Accept"] == "application/fhir+json"


def test_build_headers_with_api_key() -> None:
    """Test build_headers includes API key when provided."""
    headers = build_headers(api_key="test-api-key")
    assert headers["apikey"] == "test-api-key"


def test_build_headers_with_auth_headers() -> None:
    """Test build_headers includes auth headers when provided."""
    auth_headers = {"Authorization": "Bearer test-token"}
    headers = build_headers(auth_headers=auth_headers)
    assert headers["Authorization"] == "Bearer test-token"


def test_build_headers_with_all_options() -> None:
    """Test build_headers with all options combined."""
    auth_headers = {"Authorization": "Bearer test-token"}
    headers = build_headers(
        json_data={"foo": "bar"},
        api_key="test-api-key",
        auth_headers=auth_headers,
    )
    assert headers["Content-Type"] == "application/fhir+json"
    assert headers["Accept"] == "application/fhir+json"
    assert headers["apikey"] == "test-api-key"
    assert headers["Authorization"] == "Bearer test-token"
    assert "X-Correlation-ID" in headers


def test_make_request_with_response_request_id_header(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
        headers={"X-Request-ID": "test-request-id-123"},
    )

    mock_logger_append_keys = mocker.patch(
        "common.http_client.http_client_logger.append_keys"
    )

    headers = build_headers()
    result = make_request("https://api.example.com/resource", headers=headers)

    assert result == {"key": "value", "status_code": HTTPStatus.OK}

    mock_logger_append_keys.assert_any_call(response_request_id="test-request-id-123")

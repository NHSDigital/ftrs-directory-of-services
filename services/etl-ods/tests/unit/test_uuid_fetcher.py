"""Tests for transformer UUID fetcher module."""

import pytest
from pytest_mock import MockerFixture
from requests import HTTPError

from common.exceptions import PermanentProcessingError
from transformer.uuid_fetcher import (
    fetch_organisation_uuid,
    validate_ods_code,
)


def test_fetch_organisation_uuid(mocker: MockerFixture) -> None:
    """Test fetching organisation UUID from APIM."""
    mocker.patch(
        "transformer.uuid_fetcher.get_base_apim_api_url",
        return_value="http://apim-proxy",
    )

    mock_response = {
        "resourceType": "Bundle",
        "type": "searchset",
        "status_code": 200,
        "entry": [
            {"resource": {"resourceType": "Organization", "id": "BUNDLE_ORG_ID"}}
        ],
    }
    make_request_mock = mocker.patch(
        "transformer.uuid_fetcher.make_apim_request", return_value=mock_response
    )

    result_bundle = fetch_organisation_uuid("XYZ999", "test-msg-123")

    assert result_bundle == "BUNDLE_ORG_ID"
    make_request_mock.assert_called_once_with(
        "http://apim-proxy/Organization?identifier=odsOrganisationCode|XYZ999",
        method="GET",
    )


def test_fetch_organisation_uuid_logs_and_raises_on_not_found(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test fetch_organisation_uuid handles 404 NOT_FOUND error."""
    mocker.patch(
        "transformer.uuid_fetcher.get_base_apim_api_url",
        return_value="http://apim-proxy",
    )

    # Create proper mock HTTP error with 404 response
    mock_response = mocker.MagicMock()
    mock_response.status_code = 404
    mock_response.headers = {"content-type": "application/fhir+json"}
    mock_response.json.return_value = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "error", "code": "not-found"}],
    }

    mock_http_error = HTTPError(response=mock_response)
    mock_http_error.response = mock_response

    mocker.patch(
        "transformer.uuid_fetcher.make_apim_request", side_effect=mock_http_error
    )

    with caplog.at_level("WARNING"):
        with pytest.raises(PermanentProcessingError) as excinfo:
            fetch_organisation_uuid("ABC123", "test-msg-123")
        assert str(excinfo.value.status_code) == "404"
        assert excinfo.value.message_id == "test-msg-123"
        assert (
            "HTTP 404 in ABC123: OperationOutcome: 1 issues"
            == excinfo.value.response_text
        )


def test_fetch_organisation_uuid_logs_and_raises_on_bad_request(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test fetch_organisation_uuid propagates non-404 HTTP errors."""
    mocker.patch(
        "transformer.uuid_fetcher.get_base_apim_api_url",
        return_value="http://apim-proxy",
    )

    # Create proper mock HTTP error with 422 response
    mock_response = mocker.MagicMock()
    mock_response.status_code = 422
    mock_response.headers = {"content-type": "application/fhir+json"}
    mock_response.json.return_value = {
        "resourceType": "OperationOutcome",
        "issue": [
            {"severity": "error", "code": "business-rule"},
            {"severity": "warning", "code": "invalid"},
        ],
    }

    mock_http_error = HTTPError(response=mock_response)
    mock_http_error.response = mock_response

    mocker.patch(
        "transformer.uuid_fetcher.make_apim_request", side_effect=mock_http_error
    )

    with caplog.at_level("ERROR"):
        with pytest.raises(PermanentProcessingError) as excinfo:
            fetch_organisation_uuid("ABC123", "test-msg-123")
        assert str(excinfo.value.status_code) == "422"
        assert excinfo.value.message_id == "test-msg-123"
        assert (
            "HTTP 422 in ABC123: OperationOutcome: 2 issues"
            == excinfo.value.response_text
        )


def test_fetch_organisation_uuid_invalid_resource_returned(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test fetch_organisation_uuid handles invalid resource type."""
    mocker.patch(
        "transformer.uuid_fetcher.get_base_apim_api_url",
        return_value="http://apim-proxy",
    )
    mocker.patch(
        "transformer.uuid_fetcher.make_apim_request",
        return_value={
            "resourceType": "OperationOutcome",
        },
    )

    with caplog.at_level("WARNING"):
        with pytest.raises(PermanentProcessingError) as excinfo:
            fetch_organisation_uuid("XYZ999", "test-msg-123")
        assert str(excinfo.value.status_code) == "400"
        assert (
            "Unexpected response type: OperationOutcome" == excinfo.value.response_text
        )


def test_fetch_organisation_uuid_no_organisation_returned(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test fetch_organisation_uuid raises error when no Organization found in Bundle."""
    mocker.patch(
        "transformer.uuid_fetcher.get_base_apim_api_url",
        return_value="http://apim-proxy",
    )
    mocker.patch(
        "transformer.uuid_fetcher.make_apim_request",
        return_value={
            "resourceType": "Bundle",
            "status_code": 200,
            "entry": [{"resource": {"resourceType": "ABC", "id": "BUNDLE_ORG_ID"}}],
        },
    )

    with caplog.at_level("INFO"):
        with pytest.raises(PermanentProcessingError) as excinfo:
            fetch_organisation_uuid("XYZ999", "test-msg-123")

        assert str(excinfo.value.status_code) == "400"
        assert excinfo.value.message_id == "test-msg-123"
        assert (
            "Organisation with ODS code XYZ999 not found in bundle response"
            == excinfo.value.response_text
        )


@pytest.mark.parametrize(
    "ods_code,should_pass",
    [
        ("ABC12", True),
        ("ABC123", True),
        ("ABC123456789", True),
        ("12345", True),
        ("", False),  # Empty string
        ("ABC1234567890", False),  # Too long
        ("AB-123", False),  # Invalid characters
        (123456, False),  # Not a string
    ],
)
def test_validate_ods_code(ods_code: str, should_pass: bool) -> None:
    """Test ODS code validation with various inputs."""
    if should_pass:
        validate_ods_code(ods_code, "test-msg-123")  # Should not raise
    else:
        with pytest.raises(PermanentProcessingError) as excinfo:
            validate_ods_code(ods_code, "test-msg-123")
        assert str(excinfo.value.status_code) == "400"
        assert "must match" in excinfo.value.response_text

"""Tests for transformer UUID fetcher module."""

from http import HTTPStatus

import pytest
from pytest_mock import MockerFixture
from requests import HTTPError

from common.exceptions import PermanentProcessingError, UnrecoverableError
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

    class MockResponse:
        status_code = HTTPStatus.NOT_FOUND

    def raise_http_error_not_found(*args: object, **kwargs: object) -> None:
        http_err = HTTPError()
        http_err.response = MockResponse()
        raise http_err

    mocker.patch(
        "transformer.uuid_fetcher.make_apim_request",
        side_effect=raise_http_error_not_found,
    )

    with caplog.at_level("WARNING"):
        with pytest.raises(PermanentProcessingError) as excinfo:
            fetch_organisation_uuid("ABC123", "test-msg-123")
        assert str(excinfo.value.status_code) == "404"
        assert excinfo.value.message_id == "test-msg-123"


def test_fetch_organisation_uuid_logs_and_raises_on_bad_request(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test fetch_organisation_uuid propagates non-404 HTTP errors."""
    mocker.patch(
        "transformer.uuid_fetcher.get_base_apim_api_url",
        return_value="http://apim-proxy",
    )

    class MockResponse:
        response = "Error"
        status_code = HTTPStatus.UNPROCESSABLE_ENTITY

    def raise_http_error_not_found(*args: object, **kwargs: object) -> Exception:
        http_err = HTTPError()
        http_err.response = MockResponse()
        raise http_err

    mocker.patch(
        "transformer.uuid_fetcher.make_apim_request",
        side_effect=raise_http_error_not_found,
    )
    with caplog.at_level("ERROR"):
        with pytest.raises(UnrecoverableError) as excinfo:
            fetch_organisation_uuid("ABC123", "test-msg-123")
        assert excinfo.value.error_type == "HTTP_422"
        assert excinfo.value.message_id == "test-msg-123"


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
            "resourceType": "Not Bundle",
            "status_code": 200,
        },
    )

    with caplog.at_level("WARNING"):
        with pytest.raises(UnrecoverableError) as excinfo:
            fetch_organisation_uuid("XYZ999", "test-msg-123")
        assert excinfo.value.error_type == "INVALID_RESPONSE_TYPE"
        assert "Unexpected response type" in excinfo.value.details


def test_fetch_organisation_uuid_no_organisation_returned(
    mocker: MockerFixture,
) -> None:
    """Test fetch_organisation_uuid returns None when no Organization found in Bundle."""
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

    result = fetch_organisation_uuid("XYZ999", "test-msg-123")
    assert result is None


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
        with pytest.raises(UnrecoverableError) as excinfo:
            validate_ods_code(ods_code, "test-msg-123")
        assert excinfo.value.error_type == "INVALID_ODS_CODE"
        assert "must match" in excinfo.value.details

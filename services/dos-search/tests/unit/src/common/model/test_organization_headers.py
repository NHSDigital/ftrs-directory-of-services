import pytest
from pydantic import ValidationError

from src.common.model.organization_headers import (
    VERSION_VALUE,
    InvalidVersionError,
    OrganizationHeaders,
)


class TestOrganizationHeaders:
    def test_valid_organization_headers(self):
        # Arrange
        headers = {
            "authorization": "Bearer token123",
            "version": VERSION_VALUE,
            "nhsd-request-id": "req-123",
        }

        # Act
        result = OrganizationHeaders(**headers)

        # Assert
        assert result.authorization == "Bearer token123"
        assert result.version == VERSION_VALUE
        assert result.nhsd_request_id == "req-123"

    def test_valid_organization_headers_with_optional_fields(self):
        # Arrange
        headers = {
            "authorization": "Bearer token123",
            "version": VERSION_VALUE,
            "nhsd-request-id": "req-123",
            "content-type": "application/json",
            "nhsd-correlation-id": "corr-123",
            "x-correlation-id": "x-corr-123",
            "x-request-id": "x-req-123",
            "end-user-role": "admin",
            "application-id": "app-123",
            "application-name": "test-app",
            "request-start-time": "2023-01-01T00:00:00Z",
            "accept": "application/json",
            "accept-encoding": "gzip",
            "accept-language": "en-US",
            "user-agent": "test-agent",
            "host": "example.com",
            "x-amzn-trace-id": "trace-123",
            "x-forwarded-for": "192.168.1.1",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
        }

        # Act
        result = OrganizationHeaders(**headers)

        # Assert
        assert result.authorization == "Bearer token123"
        assert result.version == VERSION_VALUE
        assert result.nhsd_request_id == "req-123"
        assert result.content_type == "application/json"
        assert result.nhsd_correlation_id == "corr-123"

    def test_case_insensitive_headers(self):
        # Arrange
        headers = {
            "AUTHORIZATION": "Bearer token123",
            "vErSiOn": VERSION_VALUE,
            "NHSD-Request-ID": "req-123",
        }

        # Act
        result = OrganizationHeaders(**headers)

        # Assert
        assert result.authorization == "Bearer token123"
        assert result.version == VERSION_VALUE
        assert result.nhsd_request_id == "req-123"

    @pytest.mark.parametrize(
        "missing_field",
        ["version", "nhsd-request-id"],
        ids=["missing version", "missing nhsd-request-id"],
    )
    def test_missing_required_fields(self, missing_field):
        # Arrange
        headers = {
            "authorization": "Bearer token123",
            "version": VERSION_VALUE,
            "nhsd-request-id": "req-123",
        }
        del headers[missing_field]

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            OrganizationHeaders(**headers)

        assert len(exc_info.value.errors()) == 1
        assert exc_info.value.errors()[0]["type"] == "missing"
        assert exc_info.value.errors()[0]["loc"] == (missing_field,)

    def test_invalid_version_validation(self):
        # Arrange
        headers = {
            "authorization": "Bearer token123",
            "version": "invalid",
            "nhsd-request-id": "req-123",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            OrganizationHeaders(**headers)

        assert len(exc_info.value.errors()) == 1
        assert (
            exc_info.value.errors()[0]["ctx"]["error"].__class__ == InvalidVersionError
        )

    def test_empty_nhsd_request_id_treated_as_missing(self):
        # Arrange
        headers = {
            "authorization": "Bearer token123",
            "version": "1",
            "NHSD-Request-ID": "",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            OrganizationHeaders(**headers)

        assert len(exc_info.value.errors()) == 1
        assert exc_info.value.errors()[0]["type"] == "missing"
        assert exc_info.value.errors()[0]["loc"] == ("nhsd-request-id",)

    def test_extra_fields_forbidden(self):
        # Arrange
        headers = {
            "authorization": "Bearer token123",
            "version": VERSION_VALUE,
            "nhsd-request-id": "req-123",
            "extra-field": "not-allowed",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            OrganizationHeaders(**headers)

        assert len(exc_info.value.errors()) == 1
        assert exc_info.value.errors()[0]["type"] == "extra_forbidden"

    def test_get_allowed_headers(self):
        # Act
        allowed_headers = OrganizationHeaders.get_allowed_headers()

        # Assert
        expected_headers = [
            "accept",
            "accept-encoding",
            "accept-language",
            "application-id",
            "application-name",
            "authorization",
            "content-type",
            "end-user-role",
            "host",
            "nhsd-correlation-id",
            "nhsd-request-id",
            "request-start-time",
            "user-agent",
            "version",
            "x-amzn-trace-id",
            "x-correlation-id",
            "x-forwarded-for",
            "x-forwarded-port",
            "x-forwarded-proto",
            "x-request-id",
        ]
        assert allowed_headers == expected_headers

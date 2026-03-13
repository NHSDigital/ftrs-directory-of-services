"""Tests for the canned responses module."""

from src.router.responses import (
    ERROR_INTERNAL_SERVER,
    ERROR_MISSING_IDENTIFIER,
    ERROR_MISSING_IDENTIFIER_SEPARATOR,
    PUT_NOT_FOUND_RESPONSE,
    PUT_SUCCESS_RESPONSE,
    PUT_VALIDATION_ERROR_RESPONSE,
    SUCCESS_BUNDLE_ABC123,
    build_invalid_identifier_system_error,
    build_invalid_identifier_value_error,
    build_not_found_error,
)


class TestSuccessBundle:
    """Tests for the SUCCESS_BUNDLE_ABC123 response."""

    def test_bundle_has_correct_resource_type(self) -> None:
        """Test that the bundle has correct resourceType."""
        assert SUCCESS_BUNDLE_ABC123["resourceType"] == "Bundle"

    def test_bundle_has_searchset_type(self) -> None:
        """Test that the bundle type is searchset."""
        assert SUCCESS_BUNDLE_ABC123["type"] == "searchset"

    def test_bundle_has_entry(self) -> None:
        """Test that the bundle has at least one entry."""
        assert len(SUCCESS_BUNDLE_ABC123["entry"]) == 1

    def test_entry_contains_organization(self) -> None:
        """Test that the entry contains an Organization resource."""
        entry = SUCCESS_BUNDLE_ABC123["entry"][0]
        assert entry["resource"]["resourceType"] == "Organization"

    def test_organization_has_ods_code(self) -> None:
        """Test that the Organization has the expected ODS code."""
        org = SUCCESS_BUNDLE_ABC123["entry"][0]["resource"]
        assert org["identifier"][0]["value"] == "ABC123"

    def test_organization_has_extension(self) -> None:
        """Test that the Organization has extensions."""
        org = SUCCESS_BUNDLE_ABC123["entry"][0]["resource"]
        assert "extension" in org
        assert len(org["extension"]) >= 1


class TestErrorResponses:
    """Tests for error response structures."""

    def test_not_found_has_correct_structure(self) -> None:
        """Test build_not_found_error has correct structure."""
        error = build_not_found_error("TEST123")
        assert error["resourceType"] == "OperationOutcome"
        assert error["issue"][0]["severity"] == "error"
        assert error["issue"][0]["code"] == "not-found"
        assert "TEST123" in error["issue"][0]["diagnostics"]

    def test_missing_identifier_has_correct_structure(self) -> None:
        """Test ERROR_MISSING_IDENTIFIER has correct structure."""
        assert ERROR_MISSING_IDENTIFIER["resourceType"] == "OperationOutcome"
        assert ERROR_MISSING_IDENTIFIER["issue"][0]["severity"] == "error"
        assert ERROR_MISSING_IDENTIFIER["issue"][0]["code"] == "invalid"
        assert "INVALID_SEARCH_DATA" in str(ERROR_MISSING_IDENTIFIER["issue"][0]["details"]["coding"])

    def test_missing_separator_has_correct_structure(self) -> None:
        """Test ERROR_MISSING_IDENTIFIER_SEPARATOR has correct structure."""
        assert ERROR_MISSING_IDENTIFIER_SEPARATOR["resourceType"] == "OperationOutcome"
        assert ERROR_MISSING_IDENTIFIER_SEPARATOR["issue"][0]["severity"] == "error"
        assert ERROR_MISSING_IDENTIFIER_SEPARATOR["issue"][0]["code"] == "structure"

    def test_invalid_system_has_correct_structure(self) -> None:
        """Test build_invalid_identifier_system_error has correct structure."""
        error = build_invalid_identifier_system_error("invalid-system")
        assert error["resourceType"] == "OperationOutcome"
        assert error["issue"][0]["severity"] == "error"
        assert error["issue"][0]["code"] == "structure"
        assert "invalid-system" in error["issue"][0]["diagnostics"]

    def test_invalid_value_has_correct_structure(self) -> None:
        """Test build_invalid_identifier_value_error has correct structure."""
        error = build_invalid_identifier_value_error("ABC!@")
        assert error["resourceType"] == "OperationOutcome"
        assert error["issue"][0]["severity"] == "error"
        assert error["issue"][0]["code"] == "structure"
        assert "ABC!@" in error["issue"][0]["diagnostics"]

    def test_internal_server_error_has_correct_structure(self) -> None:
        """Test ERROR_INTERNAL_SERVER has correct structure."""
        assert ERROR_INTERNAL_SERVER["resourceType"] == "OperationOutcome"
        assert ERROR_INTERNAL_SERVER["issue"][0]["severity"] == "fatal"
        assert ERROR_INTERNAL_SERVER["issue"][0]["code"] == "exception"


class TestPutResponses:
    """Tests for PUT response structures."""

    def test_put_success_has_correct_structure(self) -> None:
        """Test PUT_SUCCESS_RESPONSE has correct structure."""
        assert PUT_SUCCESS_RESPONSE["resourceType"] == "OperationOutcome"
        assert PUT_SUCCESS_RESPONSE["issue"][0]["severity"] == "information"

    def test_put_not_found_has_correct_structure(self) -> None:
        """Test PUT_NOT_FOUND_RESPONSE has correct structure."""
        assert PUT_NOT_FOUND_RESPONSE["resourceType"] == "OperationOutcome"
        assert PUT_NOT_FOUND_RESPONSE["issue"][0]["severity"] == "error"
        assert PUT_NOT_FOUND_RESPONSE["issue"][0]["code"] == "not-found"

    def test_put_validation_error_has_correct_structure(self) -> None:
        """Test PUT_VALIDATION_ERROR_RESPONSE has correct structure."""
        assert PUT_VALIDATION_ERROR_RESPONSE["resourceType"] == "OperationOutcome"
        assert PUT_VALIDATION_ERROR_RESPONSE["issue"][0]["severity"] == "error"
        assert PUT_VALIDATION_ERROR_RESPONSE["issue"][0]["code"] == "invalid"
        assert "UNPROCESSABLE_ENTITY" in str(PUT_VALIDATION_ERROR_RESPONSE["issue"][0]["details"]["coding"])

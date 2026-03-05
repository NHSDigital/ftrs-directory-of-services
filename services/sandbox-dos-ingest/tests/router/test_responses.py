"""Tests for the canned responses module."""

from src.router.responses import (
    ERROR_INTERNAL_SERVER,
    ERROR_INVALID_IDENTIFIER_SYSTEM,
    ERROR_INVALID_IDENTIFIER_VALUE,
    ERROR_MISSING_IDENTIFIER_SEPARATOR,
    ERROR_NOT_FOUND,
    PUT_NOT_FOUND_RESPONSE,
    PUT_SUCCESS_RESPONSE,
    SUCCESS_BUNDLE_ABC123,
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
        """Test ERROR_NOT_FOUND has correct structure."""
        assert ERROR_NOT_FOUND["resourceType"] == "OperationOutcome"
        assert ERROR_NOT_FOUND["issue"][0]["severity"] == "error"
        assert ERROR_NOT_FOUND["issue"][0]["code"] == "not-found"

    def test_missing_separator_has_correct_structure(self) -> None:
        """Test ERROR_MISSING_IDENTIFIER_SEPARATOR has correct structure."""
        assert ERROR_MISSING_IDENTIFIER_SEPARATOR["resourceType"] == "OperationOutcome"
        assert ERROR_MISSING_IDENTIFIER_SEPARATOR["issue"][0]["severity"] == "error"
        assert ERROR_MISSING_IDENTIFIER_SEPARATOR["issue"][0]["code"] == "structure"

    def test_invalid_system_has_correct_structure(self) -> None:
        """Test ERROR_INVALID_IDENTIFIER_SYSTEM has correct structure."""
        assert ERROR_INVALID_IDENTIFIER_SYSTEM["resourceType"] == "OperationOutcome"
        assert ERROR_INVALID_IDENTIFIER_SYSTEM["issue"][0]["severity"] == "error"
        assert ERROR_INVALID_IDENTIFIER_SYSTEM["issue"][0]["code"] == "structure"

    def test_invalid_value_has_correct_structure(self) -> None:
        """Test ERROR_INVALID_IDENTIFIER_VALUE has correct structure."""
        assert ERROR_INVALID_IDENTIFIER_VALUE["resourceType"] == "OperationOutcome"
        assert ERROR_INVALID_IDENTIFIER_VALUE["issue"][0]["severity"] == "error"
        assert ERROR_INVALID_IDENTIFIER_VALUE["issue"][0]["code"] == "invalid"

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

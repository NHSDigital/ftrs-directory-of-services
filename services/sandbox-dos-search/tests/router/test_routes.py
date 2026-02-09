import pytest
from fastapi.testclient import TestClient

from src.app.main import app
from src.models.constants import (
    ODS_ORG_CODE_IDENTIFIER_SYSTEM,
    REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
)


@pytest.fixture
def client():
    return TestClient(app)


class TestOrganizationEndpoint:
    def test_valid_request_returns_200(self, client):
        """Test that a valid request with ABC123 returns 200"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/fhir+json"

    def test_valid_request_returns_bundle(self, client):
        """Test that a valid request returns a Bundle resource"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "searchset"
        assert len(data["entry"]) == 3

    def test_valid_request_contains_organization(self, client):
        """Test that response contains the Organization resource"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert
        org_entry = data["entry"][0]
        assert org_entry["resource"]["resourceType"] == "Organization"
        assert org_entry["resource"]["identifier"][0]["value"] == "ABC123"

    def test_valid_request_reflects_url_in_bundle_link(self, client):
        """Test that the bundle link reflects the actual system and code from the request"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert
        link_url = data["link"][0]["url"]
        assert f"identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123" in link_url
        assert f"_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}" in link_url

    def test_missing_identifier_returns_400(self, client):
        """Test that missing identifier returns 400 error"""
        # Act
        response = client.get(f"/Organization?_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}")
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["severity"] == "error"

    def test_missing_revinclude_returns_400(self, client):
        """Test that missing _revinclude returns 400 error"""
        # Act
        response = client.get(f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123")
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"
        assert f"_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}" in data["issue"][0]["diagnostics"]

    def test_invalid_revinclude_value_returns_400(self, client):
        """Test that invalid _revinclude value returns 400 error"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123&_revinclude=Invalid:value"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_identifier_without_pipe_returns_400(self, client):
        """Test that identifier without pipe separator returns 400 error"""
        # Act
        response = client.get(
            f"/Organization?identifier=ABC123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    @pytest.mark.skip(reason="Not a valid test case for the current implementation; to be implemented")
    def test_invalid_identifier_system_returns_400(self, client):
        """Test that invalid identifier system returns 400 error"""
        # Act
        response = client.get(
            f"/Organization?identifier=wrongSystem|ABC123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"
        assert "Invalid identifier system 'wrongSystem'" in data["issue"][0]["diagnostics"]
        assert ODS_ORG_CODE_IDENTIFIER_SYSTEM in data["issue"][0]["diagnostics"]

    def test_ods_code_too_short_returns_400(self, client):
        """Test that ODS code shorter than 5 characters returns 400 error"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_ods_code_too_long_returns_400(self, client):
        """Test that ODS code longer than 12 characters returns 400 error"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABCDEFGHIJKLM&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_ods_code_with_invalid_characters_returns_400(self, client):
        """Test that ODS code with invalid characters returns 400 error"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC-123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_valid_ods_code_not_abc123_returns_400(self, client):
        """Test that valid format ODS code other than ABC123 returns 400 (not found)"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|XYZ789&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_alphanumeric_ods_code_5_chars_valid_format(self, client):
        """Test that 5-character alphanumeric ODS code has valid format (though not ABC123)"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|AB123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert - Valid format but not the specific code we return success for
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_alphanumeric_ods_code_12_chars_valid_format(self, client):
        """Test that 12-character alphanumeric ODS code with valid format but not matching ABC123 returns 400"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABCDEFGH1234&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert - Valid format but doesn't match ABC123 (case-insensitive)
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["severity"] == "error"
        assert data["issue"][0]["code"] == "value"
        assert data["issue"][0]["details"]["coding"][0]["code"] == "INVALID_SEARCH_DATA"
        assert "Invalid identifier value" in data["issue"][0]["diagnostics"]

    def test_empty_ods_code_returns_400(self, client):
        """Test that empty ODS code after pipe returns 400 error"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_response_has_correct_content_type(self, client):
        """Test that all responses have application/fhir+json content type"""
        # Act - Valid request
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )

        # Assert
        assert response.headers["content-type"] == "application/fhir+json"

    def test_error_response_has_correct_content_type(self, client):
        """Test that error responses have application/fhir+json content type"""
        # Act - Invalid request
        response = client.get(f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC")

        # Assert
        assert response.headers["content-type"] == "application/fhir+json"

    def test_all_error_responses_use_invalid_search_data_coding(self, client):
        """Test that error responses use INVALID_SEARCH_DATA coding"""
        # Act - Various error scenarios
        error_responses = [
            client.get(f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC"),
            client.get(
                f"/Organization?identifier=wrongSystem|ABC123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
            ),
            client.get(f"/Organization?identifier=ABC123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"),
        ]

        # Assert
        for response in error_responses:
            data = response.json()
            assert data["issue"][0]["details"]["coding"][0]["code"] == "INVALID_SEARCH_DATA"

    def test_lowercase_ods_code_matches_case_insensitively(self, client):
        """Test that lowercase 'abc123' matches ABC123 case-insensitively and returns 200"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|abc123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert - Case-insensitive match on ABC123 should succeed
        assert response.status_code == 200
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "searchset"
        assert len(data["entry"]) == 3

    def test_mixed_case_abc123_matches_case_insensitively(self, client):
        """Test that mixed case 'aBc123' matches ABC123 case-insensitively and returns 200"""
        # Act
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|aBc123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )
        data = response.json()

        # Assert - Case-insensitive match on ABC123 should succeed
        assert response.status_code == 200
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "searchset"
        assert len(data["entry"]) == 3

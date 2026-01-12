import pytest
from fastapi.testclient import TestClient

from src.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestOrganizationEndpoint:
    def test_valid_request_returns_200(self, client):
        """Test that a valid request with ABC123 returns 200"""
        # Act
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization"
        )

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/fhir+json"

    def test_valid_request_returns_bundle(self, client):
        """Test that a valid request returns a Bundle resource"""
        # Act
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization"
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
            "/Organization?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization"
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
            "/Organization?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization"
        )
        data = response.json()

        # Assert
        link_url = data["link"][0]["url"]
        assert "identifier=odsOrganisationCode|ABC123" in link_url
        assert "_revinclude=Endpoint:organization" in link_url

    def test_missing_identifier_returns_400(self, client):
        """Test that missing identifier returns 400 error"""
        # Act
        response = client.get("/Organization?_revinclude=Endpoint:organization")
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["severity"] == "error"

    def test_missing_revinclude_returns_400(self, client):
        """Test that missing _revinclude returns 400 error"""
        # Act
        response = client.get("/Organization?identifier=odsOrganisationCode|ABC123")
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"
        assert "_revinclude=Endpoint:organization" in data["issue"][0]["diagnostics"]

    def test_invalid_revinclude_value_returns_400(self, client):
        """Test that invalid _revinclude value returns 400 error"""
        # Act
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|ABC123&_revinclude=Invalid:value"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_identifier_without_pipe_returns_400(self, client):
        """Test that identifier without pipe separator returns 400 error"""
        # Act
        response = client.get(
            "/Organization?identifier=ABC123&_revinclude=Endpoint:organization"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_invalid_identifier_system_returns_400(self, client):
        """Test that invalid identifier system returns 400 error"""
        # Act
        response = client.get(
            "/Organization?identifier=wrongSystem|ABC123&_revinclude=Endpoint:organization"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"
        assert "Invalid identifier system 'wrongSystem'" in data["issue"][0]["diagnostics"]
        assert "odsOrganisationCode" in data["issue"][0]["diagnostics"]

    def test_ods_code_too_short_returns_400(self, client):
        """Test that ODS code shorter than 5 characters returns 400 error"""
        # Act
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|ABC&_revinclude=Endpoint:organization"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_ods_code_too_long_returns_400(self, client):
        """Test that ODS code longer than 12 characters returns 400 error"""
        # Act
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|ABCDEFGHIJKLM&_revinclude=Endpoint:organization"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_ods_code_with_invalid_characters_returns_400(self, client):
        """Test that ODS code with invalid characters returns 400 error"""
        # Act
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|ABC-123&_revinclude=Endpoint:organization"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_valid_ods_code_not_abc123_returns_400(self, client):
        """Test that valid format ODS code other than ABC123 returns 400 (not found)"""
        # Act
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|XYZ789&_revinclude=Endpoint:organization"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_alphanumeric_ods_code_5_chars_valid_format(self, client):
        """Test that 5-character alphanumeric ODS code has valid format (though not ABC123)"""
        # Act
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|AB123&_revinclude=Endpoint:organization"
        )
        data = response.json()

        # Assert - Valid format but not the specific code we return success for
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_alphanumeric_ods_code_12_chars_valid_format(self, client):
        """Test that 12-character alphanumeric ODS code has valid format (though not ABC123)"""
        # Act
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|ABCDEFGH1234&_revinclude=Endpoint:organization"
        )
        data = response.json()

        # Assert - Valid format but not the specific code we return success for
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_empty_ods_code_returns_400(self, client):
        """Test that empty ODS code after pipe returns 400 error"""
        # Act
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|&_revinclude=Endpoint:organization"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

    def test_response_has_correct_content_type(self, client):
        """Test that all responses have application/fhir+json content type"""
        # Act - Valid request
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization"
        )

        # Assert
        assert response.headers["content-type"] == "application/fhir+json"

    def test_error_response_has_correct_content_type(self, client):
        """Test that error responses have application/fhir+json content type"""
        # Act - Invalid request
        response = client.get("/Organization?identifier=odsOrganisationCode|ABC")

        # Assert
        assert response.headers["content-type"] == "application/fhir+json"

    def test_all_error_responses_use_invalid_search_data_coding(self, client):
        """Test that error responses use INVALID_SEARCH_DATA coding"""
        # Act - Various error scenarios
        error_responses = [
            client.get("/Organization?identifier=odsOrganisationCode|ABC"),
            client.get(
                "/Organization?identifier=wrongSystem|ABC123&_revinclude=Endpoint:organization"
            ),
            client.get("/Organization?identifier=ABC123&_revinclude=Endpoint:organization"),
        ]

        # Assert
        for response in error_responses:
            data = response.json()
            assert data["issue"][0]["details"]["coding"][0]["code"] == "INVALID_SEARCH_DATA"

    def test_lowercase_ods_code_valid_format(self, client):
        """Test that lowercase ODS code is accepted (regex allows [A-Za-z0-9])"""
        # Act
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|abc123&_revinclude=Endpoint:organization"
        )
        data = response.json()

        # Assert - Valid format (lowercase allowed) but not ABC123
        assert response.status_code == 400

    def test_mixed_case_abc123_not_matched(self, client):
        """Test that mixed case 'aBc123' is not matched (case sensitive comparison)"""
        # Act
        response = client.get(
            "/Organization?identifier=odsOrganisationCode|aBc123&_revinclude=Endpoint:organization"
        )
        data = response.json()

        # Assert - Valid format but doesn't match case-sensitive ABC123
        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"

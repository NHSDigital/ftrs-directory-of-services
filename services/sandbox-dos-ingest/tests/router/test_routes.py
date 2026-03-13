import pytest
from fastapi.testclient import TestClient

from src.app.main import app
from src.models.constants import ODS_ORG_CODE_IDENTIFIER_SYSTEM


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestOrganizationGetEndpoint:
    """Tests for GET /Organization endpoint."""

    def test_valid_request_returns_200(self, client: TestClient) -> None:
        """Test that a valid request with ABC123 returns 200."""

        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123"
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/fhir+json"

    def test_valid_request_returns_bundle(self, client: TestClient) -> None:
        """Test that a valid request returns a Bundle resource."""

        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123"
        )
        data = response.json()

        assert data["resourceType"] == "Bundle"
        assert data["type"] == "searchset"
        assert len(data["entry"]) == 1

    def test_valid_request_contains_organization(self, client: TestClient) -> None:
        """Test that response contains the Organization resource."""

        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123"
        )
        data = response.json()

        org_entry = data["entry"][0]
        assert org_entry["resource"]["resourceType"] == "Organization"
        assert org_entry["resource"]["identifier"][0]["value"] == "ABC123"

    def test_missing_identifier_returns_400(self, client: TestClient) -> None:
        """Test that missing identifier returns 400 with INVALID_SEARCH_DATA."""

        response = client.get("/Organization")
        data = response.json()

        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["code"] == "invalid"
        assert "INVALID_SEARCH_DATA" in str(data["issue"][0]["details"]["coding"])
        assert "identifier" in data["issue"][0]["diagnostics"]

    def test_missing_separator_returns_400(self, client: TestClient) -> None:
        """Test that missing separator in identifier returns 400 error."""

        response = client.get("/Organization?identifier=ABC123")
        data = response.json()

        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["code"] == "structure"
        assert "separator" in data["issue"][0]["diagnostics"].lower()

    def test_invalid_system_returns_400(self, client: TestClient) -> None:
        """Test that invalid identifier system returns 400 error with actual system value."""

        response = client.get("/Organization?identifier=invalid-system|ABC123")
        data = response.json()

        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["code"] == "structure"
        assert "invalid-system" in data["issue"][0]["diagnostics"]

    def test_invalid_ods_code_too_short_returns_400(self, client: TestClient) -> None:
        """Test that ODS code that's too short returns 400 error."""
        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|"
        )
        data = response.json()

        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["code"] == "structure"

    def test_invalid_ods_code_special_chars_returns_400(
        self, client: TestClient
    ) -> None:
        """Test that ODS code with special characters returns 400 error with actual code."""

        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC!!!"
        )
        data = response.json()

        assert response.status_code == 400
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["code"] == "structure"
        assert "ABC!!!" in data["issue"][0]["diagnostics"]

    def test_def456_returns_404_with_ods_code(self, client: TestClient) -> None:
        """Test that DEF456 returns 404 not found with ODS code in message."""

        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|DEF456"
        )
        data = response.json()

        assert response.status_code == 404
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["code"] == "not-found"
        assert "DEF456" in data["issue"][0]["diagnostics"]

    def test_ghi789_returns_500(self, client: TestClient) -> None:
        """Test that GHI789 returns 500 internal server error."""

        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|GHI789"
        )
        data = response.json()

        assert response.status_code == 500
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["code"] == "exception"

    def test_unknown_code_returns_404(self, client: TestClient) -> None:
        """Test that unknown ODS code returns 404 (matches CRUD API behavior)."""

        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|UNKNOWN123"
        )
        data = response.json()

        assert response.status_code == 404
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["code"] == "not-found"
        assert "UNKNOWN123" in data["issue"][0]["diagnostics"]

    def test_case_insensitive_ods_code(self, client: TestClient) -> None:
        """Test that ODS code matching is case-insensitive."""

        response = client.get(
            f"/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|abc123"
        )

        assert response.status_code == 200


class TestOrganizationPutEndpoint:
    """Tests for PUT /Organization/{id} endpoint."""

    def test_put_get_response_id_returns_200(self, client: TestClient) -> None:
        """Test that PUT to the GET response Organization ID returns 200."""

        response = client.put(
            "/Organization/04393ec4-198f-42dd-9507-f4fa5e9ebf96",
            json={
                "resourceType": "Organization",
                "id": "04393ec4-198f-42dd-9507-f4fa5e9ebf96",
                "active": True,
                "name": "Test Org",
            },
            headers={"Content-Type": "application/fhir+json"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["severity"] == "information"

    def test_put_unknown_id_returns_404(self, client: TestClient) -> None:
        """Test that PUT to any ID not matching GET response returns 404."""

        response = client.put(
            "/Organization/some-random-id",
            json={
                "resourceType": "Organization",
                "id": "some-random-id",
                "active": True,
                "name": "Test Org",
            },
            headers={"Content-Type": "application/fhir+json"},
        )
        data = response.json()

        assert response.status_code == 404
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["code"] == "not-found"

    def test_put_trigger_422_returns_validation_error(self, client: TestClient) -> None:
        """Test that PUT to trigger-422-validation-error returns 422."""

        response = client.put(
            "/Organization/trigger-422-validation-error",
            json={
                "resourceType": "Organization",
                "id": "trigger-422-validation-error",
                "active": True,
            },
            headers={"Content-Type": "application/fhir+json"},
        )
        data = response.json()

        assert response.status_code == 422
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["code"] == "invalid"

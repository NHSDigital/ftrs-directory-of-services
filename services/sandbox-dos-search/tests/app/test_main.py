import pytest
from fastapi.testclient import TestClient

from src.app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestMainApp:
    def test_status_endpoint_returns_200(self, client: TestClient) -> None:
        """Test that the /_status endpoint returns HTTP 200"""
        # Act
        response = client.get("/_status")

        # Assert
        assert response.status_code == 200

    def test_status_endpoint_returns_empty_body(self, client: TestClient) -> None:
        """Test that the /_status endpoint returns an empty response body"""
        # Act
        response = client.get("/_status")

        # Assert
        assert response.text == ""

    def test_ping_endpoint_returns_200(self, client: TestClient) -> None:
        """Test that the /_ping endpoint returns HTTP 200"""
        # Act
        response = client.get("/_ping")

        # Assert
        assert response.status_code == 200

    def test_ping_endpoint_returns_empty_body(self, client: TestClient) -> None:
        """Test that the /_ping endpoint returns an empty response body"""
        # Act
        response = client.get("/_ping")

        # Assert
        assert response.text == ""

    def test_app_includes_api_router(self, client: TestClient) -> None:
        """Test that the FastAPI app includes the API router"""
        # This test verifies the router is included by checking routes exist
        routes = [route.path for route in app.routes]

        # Assert
        assert "/Organization" in routes

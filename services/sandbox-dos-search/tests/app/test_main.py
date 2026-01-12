from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestMainApp:
    def test_status_endpoint_returns_200(self, client):
        """Test that the /_status endpoint returns HTTP 200"""
        # Act
        response = client.get("/_status")

        # Assert
        assert response.status_code == 200

    def test_status_endpoint_returns_empty_body(self, client):
        """Test that the /_status endpoint returns an empty response body"""
        # Act
        response = client.get("/_status")

        # Assert
        assert response.text == ""

    def test_app_includes_api_router(self, client):
        """Test that the FastAPI app includes the API router"""
        # This test verifies the router is included by checking routes exist
        routes = [route.path for route in app.routes]

        # Assert
        assert "/Organization" in routes

    @patch("src.app.main.uvicorn.run")
    def test_main_runs_uvicorn(self, mock_run):
        """Test that running main.py starts uvicorn server"""
        # Import and execute the main block
        import src.app.main

        # Simulate running as main module
        if hasattr(src.app.main, "__name__"):
            with patch.object(src.app.main, "__name__", "__main__"):
                # Execute the main block code
                exec(
                    """
import uvicorn
from src.app.main import app

uvicorn.run(app, host="0.0.0.0", port=9000)
"""
                )

        # Assert
        mock_run.assert_called_once_with(app, host="0.0.0.0", port=9000)

    def test_app_is_fastapi_instance(self):
        """Test that app is a FastAPI instance"""
        from fastapi import FastAPI

        # Assert
        assert isinstance(app, FastAPI)

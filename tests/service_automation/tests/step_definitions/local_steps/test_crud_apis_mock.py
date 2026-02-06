"""Local CRUD APIs tests using mock server.

These tests validate the CRUD APIs mock server for integration testing.
For full integration testing of the actual CRUD APIs service against
LocalStack, use the service's own test suite in services/crud-apis/tests/.

The mock server approach allows testing without the complexity of
starting the full FastAPI app with DynamoDB connections.
"""

import uuid
from typing import Generator

import pytest
import requests
from loguru import logger
from utilities.testcontainers.fixtures import is_local_test_mode

try:
    from utilities.local_servers.crud_api_mock_server import (
        run_crud_api_mock_server,
        stop_server,
    )
except ImportError:  # pragma: no cover
    run_crud_api_mock_server = None  # type: ignore[assignment]
    stop_server = None  # type: ignore[assignment]


def _skip_if_not_local() -> None:
    """Skip test if not in local test mode."""
    if not is_local_test_mode():
        pytest.skip("Local CRUD APIs tests require USE_LOCALSTACK=true")


# Mark tests for categorization
pytestmark = [pytest.mark.local]


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def crud_apis_mock_server() -> Generator[dict, None, None]:
    """Start the mock CRUD APIs server for testing.

    This uses the simplified mock server rather than the full
    CRUD APIs service, which has module-level DynamoDB initialization.
    """
    if not is_local_test_mode():
        yield {"mode": "aws", "base_url": None}
        return

    if run_crud_api_mock_server is None or stop_server is None:
        pytest.skip("crud_api_mock_server utilities are not available")

    port = 8005
    host = "127.0.0.1"

    try:
        process = run_crud_api_mock_server(port=port, host=host)
        base_url = f"http://{host}:{port}"
        logger.info(f"CRUD APIs mock server started at {base_url}")

        yield {
            "mode": "local",
            "base_url": base_url,
            "process": process,
        }
    except Exception as e:
        logger.error(f"Failed to start CRUD APIs mock server: {e}")
        yield {"mode": "error", "base_url": None, "error": str(e)}
        return
    finally:
        if "process" in locals() and process:
            stop_server(process)


# ============================================================================
# Tests
# ============================================================================


class TestCrudApisMockServer:
    """Tests for the CRUD APIs mock server."""

    def test_mock_server_starts(self, crud_apis_mock_server: dict) -> None:
        """Test that the mock server starts successfully."""
        _skip_if_not_local()

        if crud_apis_mock_server.get("mode") == "error":
            pytest.fail(f"Server failed: {crud_apis_mock_server.get('error')}")

        base_url = crud_apis_mock_server.get("base_url")
        assert base_url is not None, "Mock server base_url should not be None"

        # Verify server is responding
        response = requests.get(f"{base_url}/docs", timeout=5)
        assert response.status_code == 200

    def test_create_and_get_organization(self, crud_apis_mock_server: dict) -> None:
        """Test creating and then retrieving an organization."""
        _skip_if_not_local()

        base_url = crud_apis_mock_server.get("base_url")
        if not base_url:
            pytest.skip("Mock server not available")

        # Create an organization
        org_id = str(uuid.uuid4())
        org_payload = {
            "resourceType": "Organization",
            "id": org_id,
            "identifier_ODS_ODSCode": "TESTORG1",
            "name": "Test Organization for Mock",
            "active": True,
        }

        put_response = requests.put(
            f"{base_url}/Organization/{org_id}",
            json=org_payload,
            timeout=5,
        )
        assert put_response.status_code == 200

        # Now retrieve it
        get_response = requests.get(f"{base_url}/Organization/{org_id}", timeout=5)

        assert get_response.status_code == 200
        org = get_response.json()
        assert org["id"] == org_id
        assert org["resourceType"] == "Organization"

    def test_get_nonexistent_organization(self, crud_apis_mock_server: dict) -> None:
        """Test retrieving a non-existent organization returns 404."""
        _skip_if_not_local()

        base_url = crud_apis_mock_server.get("base_url")
        if not base_url:
            pytest.skip("Mock server not available")

        fake_id = str(uuid.uuid4())
        response = requests.get(f"{base_url}/Organization/{fake_id}", timeout=5)

        assert response.status_code == 404

    def test_oauth_token_endpoint(self, crud_apis_mock_server: dict) -> None:
        """Test the OAuth2 token endpoint returns a valid token."""
        _skip_if_not_local()

        base_url = crud_apis_mock_server.get("base_url")
        if not base_url:
            pytest.skip("Mock server not available")

        response = requests.post(
            f"{base_url}/oauth2/token",
            data={"grant_type": "client_credentials"},
            timeout=5,
        )

        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "Bearer"

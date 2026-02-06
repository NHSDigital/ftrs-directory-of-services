import os
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture


def _is_integration_test(request: pytest.FixtureRequest) -> bool:
    """Check if the current test is an integration test."""
    # Check if test is in the integration directory
    if hasattr(request, "fspath") and request.fspath:
        return "integration" in str(request.fspath)
    # Check for integration marker
    if hasattr(request, "node"):
        return request.node.get_closest_marker("integration") is not None
    return False


@pytest.fixture(autouse=True)
def set_environment_variables(request: pytest.FixtureRequest) -> Generator:
    """Set environment variables for local testing."""
    # Skip for integration tests - they manage their own environment
    if _is_integration_test(request):
        yield
        return

    # Clear any existing environment variables that might interfere
    with patch.dict(os.environ, clear=True):
        os.environ["AWS_REGION"] = "eu-west-2"
        os.environ["ENVIRONMENT"] = "local"
        os.environ["WORKSPACE"] = "test-workspace"
        os.environ["LOCAL_API_KEY"] = "test-api-key"
        os.environ["LOCAL_APIM_API_URL"] = "http://test-apim-api"
        os.environ["LOCAL_PRIVATE_KEY"] = "private-key"
        os.environ["LOCAL_KID"] = "test-kid"
        os.environ["LOCAL_TOKEN_URL"] = "http://test-token-url"
        yield


@pytest.fixture(autouse=True)
def mock_jwt_authenticator_global(
    request: pytest.FixtureRequest, mocker: MockerFixture
) -> MagicMock | None:
    """Automatically mock JWT authenticator for all tests."""
    # Skip for integration tests - they use real services
    if _is_integration_test(request):
        return None

    mock_auth = mocker.MagicMock()
    mock_auth.get_auth_headers.return_value = {"Authorization": "Bearer mock-jwt-token"}
    mock_auth.get_bearer_token.return_value = "mock-jwt-token"
    mocker.patch("common.auth.get_jwt_authenticator", return_value=mock_auth)
    mocker.patch("common.apim_client.get_jwt_authenticator", return_value=mock_auth)
    return mock_auth

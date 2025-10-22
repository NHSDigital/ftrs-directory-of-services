import os
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def set_environment_variables() -> Generator:
    """Set environment variables for local testing."""
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
def mock_jwt_authenticator_global(mocker: MockerFixture) -> MagicMock:
    """Automatically mock JWT authenticator for all tests."""
    mock_auth = mocker.MagicMock()
    mock_auth.get_auth_headers.return_value = {"Authorization": "Bearer mock-jwt-token"}
    mock_auth.get_bearer_token.return_value = "mock-jwt-token"
    mocker.patch("pipeline.utilities.get_jwt_authenticator", return_value=mock_auth)
    return mock_auth

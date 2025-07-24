import os
from typing import Generator
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def set_environment_variables() -> Generator:
    """Set environment variables for local testing."""
    # Clear any existing environment variables that might interfere
    with patch.dict(os.environ, clear=True):
        os.environ["AWS_REGION"] = "eu-west-2"
        os.environ["ENVIRONMENT"] = "local"
        os.environ["WORKSPACE"] = "test-workspace"
        os.environ["LOCAL_CRUD_API_URL"] = "http://test-crud-api"
        os.environ["LOCAL_API_KEY"] = "test-api-key"
        os.environ["LOCAL_FHIR_API_URL"] = "http://test-fhir-api"

        yield


@pytest.fixture(autouse=True)
def mock_signed_headers() -> Generator:
    """Mock signed headers for testing."""

    with patch(
        "pipeline.utilities.get_signed_request_headers"
    ) as mock_get_signed_headers:
        mock_get_signed_headers.return_value = {
            "Authorization": "MockedAuthorization",
            "X-Amz-Date": "MockedDate",
            "X-Amz-Security-Token": "MockedSecurityToken",
        }
        yield mock_get_signed_headers


@pytest.fixture(autouse=True)
def mock_get_parameter() -> Generator:
    """Mock the get_parameter function."""

    parameters = {
        "/ftrs-dos-dev-crud-apis-test-workspace/endpoint": "http://test-crud-api",
    }

    def _get_parameter(name: str) -> str:
        assert name in parameters, f"Parameter '{name}' not found in mock."
        return parameters[name]

    with patch("pipeline.utilities.get_parameter") as mock_get_param:
        mock_get_param.side_effect = _get_parameter
        yield mock_get_param

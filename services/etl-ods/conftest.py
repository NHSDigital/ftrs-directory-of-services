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
        os.environ["LOCAL_API_KEY"] = "test-api-key"
        os.environ["LOCAL_APIM_API_URL"] = "http://test-apim-api"

        yield

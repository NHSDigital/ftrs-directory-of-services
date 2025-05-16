import os
from unittest.mock import patch

import pytest

from functions.ftrs_service.config import (
    EnvironmentVariableNotFoundError,
    _get_env_var,
    get_config,
)


@pytest.fixture
def mock_environment():
    """Mock environment variables for testing."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DYNAMODB_TABLE_NAME", "test-table")
        mp.setenv("FHIR_BASE_URL", "https://test-fhir-url.org")
        mp.setenv("LOG_LEVEL", "DEBUG")
        yield mp


class TestConfig:
    def test_get_env_var_exists(self):
        # Arrange
        with patch.dict(os.environ, {"TEST_VAR": "test-value"}, clear=True):
            # Act
            result = _get_env_var("TEST_VAR")

            # Assert
            assert result == "test-value"

    def test_get_env_var_with_default(self):
        # Arrange
        with patch.dict(os.environ, {}, clear=True):
            # Act
            result = _get_env_var("TEST_VAR", "default-value")

            # Assert
            assert result == "default-value"

    def test_get_env_var_not_found(self):
        # Arrange
        with patch.dict(os.environ, {}, clear=True):
            # Act & Assert
            with pytest.raises(EnvironmentVariableNotFoundError) as excinfo:
                _get_env_var("TEST_VAR")

            assert "TEST_VAR" in str(excinfo.value)

    def test_get_config_all_vars_set(self, mock_environment):
        # Act
        config = get_config()

        # Assert
        assert config["DYNAMODB_TABLE_NAME"] == "test-table"
        assert config["FHIR_BASE_URL"] == "https://test-fhir-url.org"

    def test_get_config_missing_required(self):
        # Arrange
        with patch.dict(os.environ, {}, clear=True):
            # Act & Assert
            with pytest.raises(EnvironmentVariableNotFoundError) as excinfo:
                get_config()

            assert "DYNAMODB_TABLE_NAME" in str(excinfo.value)

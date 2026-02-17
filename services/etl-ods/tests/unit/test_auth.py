import os
from typing import Generator
from unittest.mock import patch

import pytest
from pytest_mock import MockerFixture

from common import auth


class TestGetJWTAuthenticator:
    @pytest.fixture(autouse=True)
    def setup_auth_test(self, mocker: MockerFixture) -> Generator[None, None, None]:
        """Reset auth cache before each test."""
        auth._jwt_authenticator = None
        yield
        auth._jwt_authenticator = None

    @patch.dict(
        os.environ,
        {
            "PROJECT_NAME": "ftrs-dos",
            "ENVIRONMENT": "dev",
            "AWS_REGION": "eu-west-2",
        },
    )
    def test_get_jwt_authenticator_returns_configured_instance(
        self,
        mocker: MockerFixture,
    ) -> None:
        """
        Test that get_jwt_authenticator returns a properly configured JWTAuthenticator instance.
        """
        mocker.stopall()  # Stop any existing mocks
        mock_jwt_authenticator_class = mocker.patch("common.auth.JWTAuthenticator")
        mock_instance = mocker.MagicMock()
        mock_jwt_authenticator_class.return_value = mock_instance

        # Call the function under test
        result = auth.get_jwt_authenticator()

        # Verify the constructor was called with correct parameters
        mock_jwt_authenticator_class.assert_called_once_with(
            environment="dev",
            region="eu-west-2",
            secret_name="/ftrs-dos/dev/dos-ingest-jwt-credentials",
        )

        # Verify the instance is returned
        assert result == mock_instance

    @patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "local",
            "AWS_REGION": "eu-west-2",
            "PROJECT_NAME": "ftrs-dos",
        },
    )
    def test_get_jwt_authenticator_local_environment(
        self, mocker: MockerFixture
    ) -> None:
        """
        Test that get_jwt_authenticator works with local environment.
        """
        mocker.stopall()  # Stop any existing mocks
        mock_jwt_authenticator_class = mocker.patch("common.auth.JWTAuthenticator")
        mock_instance = mocker.MagicMock()
        mock_jwt_authenticator_class.return_value = mock_instance

        result = auth.get_jwt_authenticator()

        mock_jwt_authenticator_class.assert_called_once_with(
            environment="local",
            region="eu-west-2",
            secret_name="/ftrs-dos/local/dos-ingest-jwt-credentials",
        )

        assert result == mock_instance

    @patch.dict(
        os.environ,
        {
            "PROJECT_NAME": "ftrs-dos",
            "ENVIRONMENT": "dev",
            "AWS_REGION": "eu-west-2",
        },
    )
    def test_get_jwt_authenticator_returns_cached_instance(
        self, mocker: MockerFixture
    ) -> None:
        """Test that get_jwt_authenticator returns cached instance on subsequent calls."""
        mocker.stopall()  # Stop any existing mocks
        mock_jwt_authenticator_class = mocker.patch("common.auth.JWTAuthenticator")
        mock_instance = mocker.MagicMock()
        mock_jwt_authenticator_class.return_value = mock_instance

        # First call should create new instance
        result1 = auth.get_jwt_authenticator()

        # Second call should return cached instance
        result2 = auth.get_jwt_authenticator()

        # Constructor should only be called once
        mock_jwt_authenticator_class.assert_called_once()
        assert result1 == result2 == mock_instance
        # Both calls should return same instance
        assert result1 == mock_instance
        assert result2 == mock_instance
        assert result1 is result2

    @patch.dict(
        os.environ,
        {
            "PROJECT_NAME": "ftrs-dos",
            "AWS_REGION": "eu-west-2",
        },
        clear=True,
    )
    def test_get_jwt_authenticator_default_environment(
        self, mocker: MockerFixture
    ) -> None:
        """Test that get_jwt_authenticator uses default environment when ENVIRONMENT is not set."""
        mocker.stopall()
        auth._jwt_authenticator = None

        # Mock SecretManager.get_resource_prefix to avoid environment variable dependencies
        mock_get_resource_prefix = mocker.patch(
            "common.auth.SecretManager.get_resource_prefix",
            return_value="ftrs-dos/local",
        )

        mock_jwt_authenticator_class = mocker.patch("common.auth.JWTAuthenticator")
        mock_instance = mocker.MagicMock()
        mock_jwt_authenticator_class.return_value = mock_instance

        result = auth.get_jwt_authenticator()

        # Verify SecretManager was called
        mock_get_resource_prefix.assert_called_once()

        mock_jwt_authenticator_class.assert_called_once_with(
            environment="local",  # Should default to "local"
            region="eu-west-2",
            secret_name="/ftrs-dos/local/dos-ingest-jwt-credentials",
        )
        assert result == mock_instance

    @patch.dict(
        os.environ,
        {
            "PROJECT_NAME": "ftrs-dos",
            "ENVIRONMENT": "dev",
        },
        clear=True,
    )
    @patch.dict(
        os.environ,
        {
            "PROJECT_NAME": "ftrs-dos",
            "ENVIRONMENT": "dev",
        },
        clear=True,
    )
    def test_get_jwt_authenticator_missing_aws_region(
        self, mocker: MockerFixture
    ) -> None:
        """Test that get_jwt_authenticator raises KeyError when AWS_REGION is missing."""
        mocker.stopall()  # Stop any existing mocks
        with pytest.raises(KeyError):
            auth.get_jwt_authenticator()
        """Test that get_jwt_authenticator raises KeyError when AWS_REGION is missing."""
        mocker.stopall()
        auth._jwt_authenticator = None

        mock_jwt_authenticator_class = mocker.patch("common.auth.JWTAuthenticator")
        mock_instance = mocker.MagicMock()
        mock_jwt_authenticator_class.return_value = mock_instance

        with pytest.raises(KeyError):
            auth.get_jwt_authenticator()

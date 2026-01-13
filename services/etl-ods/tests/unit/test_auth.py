import os
from unittest.mock import patch

from pytest_mock import MockerFixture

from common.auth import get_jwt_authenticator


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
def test_get_jwt_authenticator_returns_configured_instance(
    mocker: MockerFixture,
) -> None:
    """Test that get_jwt_authenticator returns a properly configured JWTAuthenticator instance."""
    mock_jwt_authenticator_class = mocker.patch("common.auth.JWTAuthenticator")
    mock_instance = mocker.MagicMock()
    mock_jwt_authenticator_class.return_value = mock_instance

    result = get_jwt_authenticator()

    mock_jwt_authenticator_class.assert_called_once_with(
        environment="dev",
        region="eu-west-2",
        secret_name="/ftrs-dos/dev/dos-ingest-jwt-credentials",
    )
    assert result == mock_instance


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs",
        "ENVIRONMENT": "local",
        "AWS_REGION": "eu-west-2",
    },
)
def test_get_jwt_authenticator_local_environment(mocker: MockerFixture) -> None:
    """Test that get_jwt_authenticator works with local environment."""
    mock_jwt_authenticator_class = mocker.patch("common.auth.JWTAuthenticator")
    mock_instance = mocker.MagicMock()
    mock_jwt_authenticator_class.return_value = mock_instance

    result = get_jwt_authenticator()

    mock_jwt_authenticator_class.assert_called_once_with(
        environment="local",
        region="eu-west-2",
        secret_name="/ftrs/local/dos-ingest-jwt-credentials",
    )
    assert result == mock_instance

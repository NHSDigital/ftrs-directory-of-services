from unittest.mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from common.secret_utils import get_secret

# TODO: Move these tests once dms_provisioner is implemented
from pipeline.utils.secret_utils import get_dms_workspaces


def test_get_secret_success(mocker: MockerFixture) -> None:
    """
    Test that secret retrieved when environment variables are set correctly.
    """
    mocker.patch(
        "os.getenv",
        side_effect=lambda key: {
            "ENVIRONMENT": "test_env",
            "PROJECT_NAME": "test_project",
        }.get(key),
    )
    mock_get_secret = mocker.patch(
        "aws_lambda_powertools.utilities.parameters.get_secret"
    )
    mock_get_secret.return_value = "mock_secret_value"

    secret = get_secret("my_secret")
    assert secret == "mock_secret_value"
    mock_get_secret.assert_called_once_with(
        name="/test_project/test_env/my_secret", transform=None
    )


@pytest.mark.parametrize(
    "env_vars",
    [
        {"ENVIRONMENT": None, "PROJECT_NAME": "test_project"},
        {"ENVIRONMENT": "test_env", "PROJECT_NAME": None},
    ],
)
def test_get_secret_missing_env_vars(mocker: MockerFixture, env_vars: dict) -> None:
    """
    Test that error is raised when the environment or project name is missing
    """
    mocker.patch(
        "os.getenv",
        side_effect=lambda key: env_vars.get(key),
    )

    with pytest.raises(ValueError):
        get_secret("my_secret")


@patch("pipeline.utils.secret_utils.os.environ.get")
@patch("pipeline.utils.secret_utils.get_parameters")
def test_returns_list_of_workspaces_when_ssm_path_exists(
    mock_get_multiple: MagicMock, mock_environ_get: MagicMock
) -> None:
    # Arrange
    mock_environ_get.return_value = "/path/to/ssm"
    mock_get_multiple.return_value = {"param1": "workspace1", "param2": "workspace2"}

    # Act
    result = get_dms_workspaces()

    # Assert
    assert result == ["workspace1", "workspace2"]
    mock_environ_get.assert_called_once_with("SQS_SSM_PATH")
    mock_get_multiple.assert_called_once_with(
        "/path/to/ssm", recursive=True, decrypt=True, max_age=300
    )


@patch("pipeline.utils.secret_utils.os.environ.get")
def test_raises_value_error_when_ssm_path_missing(mock_environ_get: MagicMock) -> None:
    # Arrange
    mock_environ_get.return_value = None

    # Act & Assert
    with pytest.raises(
        ValueError, match="Missing required environment variable: SQS_SSM_PATH"
    ):
        get_dms_workspaces()
    mock_environ_get.assert_called_once_with("SQS_SSM_PATH")


@patch("pipeline.utils.secret_utils.os.environ.get")
@patch("pipeline.utils.secret_utils.get_parameters")
def test_returns_empty_list_when_no_parameters_found(
    mock_get_multiple: MagicMock, mock_environ_get: MagicMock
) -> None:
    # Arrange
    mock_environ_get.return_value = "/path/to/ssm"
    mock_get_multiple.return_value = {}

    # Act
    result = get_dms_workspaces()

    # Assert
    assert result == []
    mock_get_multiple.assert_called_once()

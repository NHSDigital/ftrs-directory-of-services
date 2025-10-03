import os
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from pipeline.utils.secret_utils import get_dms_workspaces, get_secret


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
    Test that error is raised when environment or project name is missing
    """
    mocker.patch(
        "os.getenv",
        side_effect=lambda key: env_vars.get(key),
    )

    with pytest.raises(ValueError):
        get_secret("my_secret")


@pytest.fixture
def mock_ssm_client() -> MagicMock:
    with patch("pipeline.utils.secret_utils.SSM_CLIENT") as mock_client:
        mock_paginator = MagicMock()
        mock_client.get_paginator.return_value = mock_paginator
        yield mock_client, mock_paginator


def test_get_dms_workspaces_returns_list_of_workspace_values(
    mock_ssm_client: MagicMock,
) -> None:
    mock_client, mock_paginator = mock_ssm_client
    mock_paginator.paginate.return_value = [
        {"Parameters": [{"Value": "workspace-url-1"}, {"Value": "workspace-url-2"}]}
    ]

    with patch.dict(os.environ, {"SQS_SSM_PATH": "/test/path"}):
        result = get_dms_workspaces()

    assert result == ["workspace-url-1", "workspace-url-2"]
    mock_paginator.paginate.assert_called_once_with(
        Path="/test/path", Recursive=True, WithDecryption=True
    )


def test_get_dms_workspaces_returns_empty_list_when_no_parameters(
    mock_ssm_client: MagicMock,
) -> None:
    mock_client, mock_paginator = mock_ssm_client
    mock_paginator.paginate.return_value = [{"Parameters": []}]

    with patch.dict(os.environ, {"SQS_SSM_PATH": "/test/path"}):
        result = get_dms_workspaces()

    assert result == []


def test_get_dms_workspaces_handles_multiple_pages(mock_ssm_client: MagicMock) -> None:
    mock_client, mock_paginator = mock_ssm_client
    mock_paginator.paginate.return_value = [
        {"Parameters": [{"Value": "workspace-url-1"}, {"Value": "workspace-url-2"}]},
        {"Parameters": [{"Value": "workspace-url-3"}]},
    ]

    with patch.dict(os.environ, {"SQS_SSM_PATH": "/test/path"}):
        result = get_dms_workspaces()

    assert result == ["workspace-url-1", "workspace-url-2", "workspace-url-3"]


def test_get_dms_workspaces_handles_none_path_parameter(
    mock_ssm_client: MagicMock,
) -> None:
    mock_client, mock_paginator = mock_ssm_client
    mock_paginator.paginate.side_effect = Exception(
        "Invalid type for parameter Path, value: None, type: <class 'NoneType'>, valid types: <class 'str'>"
    )

    with patch.dict(os.environ, {}, clear=True):  # Ensure SQS_SSM_PATH is not set
        with pytest.raises(Exception) as excinfo:
            get_dms_workspaces()

    assert "Invalid type for parameter Path" in str(excinfo.value)


def test_get_dms_workspaces_handles_access_denied_error(
    mock_ssm_client: MagicMock,
) -> None:
    mock_client, mock_paginator = mock_ssm_client
    mock_paginator.paginate.side_effect = Exception("AccessDeniedException")

    with patch.dict(os.environ, {"SQS_SSM_PATH": "/test/path"}):
        with pytest.raises(Exception) as excinfo:
            get_dms_workspaces()

    assert "AccessDeniedException" in str(excinfo.value)


def test_get_dms_workspaces_handles_pagination_token(
    mock_ssm_client: MagicMock,
) -> None:
    mock_client, mock_paginator = mock_ssm_client

    # Create a more complex mock to test pagination behavior
    def paginate_side_effect(**kwargs: dict[str, object]) -> list[dict]:
        assert kwargs.get("Path") == "/test/path"
        assert kwargs.get("Recursive") is True
        assert kwargs.get("WithDecryption") is True
        return [
            {"Parameters": [{"Value": "workspace-url-1"}], "NextToken": "page2token"},
            {"Parameters": [{"Value": "workspace-url-2"}]},
        ]

    mock_paginator.paginate.side_effect = paginate_side_effect

    with patch.dict(os.environ, {"SQS_SSM_PATH": "/test/path"}):
        result = get_dms_workspaces()

    assert result == ["workspace-url-1", "workspace-url-2"]

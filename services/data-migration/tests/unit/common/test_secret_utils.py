import pytest
from pytest_mock import MockerFixture

from common.secret_utils import get_secret

# TODO: Move these tests once dms_provisioner is implemented


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

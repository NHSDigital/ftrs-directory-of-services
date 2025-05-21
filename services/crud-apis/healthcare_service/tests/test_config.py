from unittest.mock import MagicMock, patch

from healthcare_service.app.config import get_env_variables


@patch("os.getenv")
def test_env_variables_return_default_values_if_not_set(mock_getenv: MagicMock) -> None:
    mock_getenv.side_effect = lambda key, default=None: default
    env_vars = get_env_variables()
    assert env_vars == {
        "env": "local",
        "workspace": None,
        "endpoint_url": "http://localhost:8000",
        "entity_name": "healthcare-service",
    }


@patch("os.getenv")
def test_env_variables_return_correct_values_if_set(mock_getenv: MagicMock) -> None:
    mock_getenv.side_effect = lambda key, default=None: {
        "ENVIRONMENT": "production",
        "WORKSPACE": "team1",
        "ENDPOINT_URL": "https://api.example.com",
        "TABLENAME_HC": "custom-healthcare-service",
    }.get(key, default)
    env_vars = get_env_variables()
    assert env_vars == {
        "env": "production",
        "workspace": "team1",
        "endpoint_url": "https://api.example.com",
        "entity_name": "custom-healthcare-service",
    }

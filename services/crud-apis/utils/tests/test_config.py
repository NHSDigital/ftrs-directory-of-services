from unittest.mock import patch

from utils.config import Settings, get_env_variables


def test_get_env_variables_with_defaults() -> None:
    with patch("utils.config.os.getenv", side_effect=lambda key, default=None: default):
        settings = get_env_variables()
        assert isinstance(settings, Settings)
        assert settings.env == "local"
        assert settings.workspace is None
        assert settings.endpoint_url is None


def test_get_env_variables_with_custom_values() -> None:
    with patch("os.getenv") as mock_getenv:  # Note: patching os.getenv directly
        mock_getenv.side_effect = lambda key, default=None: {
            "ENVIRONMENT": "production",
            "WORKSPACE": "test_workspace",
            "ENDPOINT_URL": "http://custom-endpoint.com",
        }.get(key, default)

        settings = get_env_variables()
        assert isinstance(settings, Settings)
        assert settings.env == "production"
        assert settings.workspace == "test_workspace"
        assert settings.endpoint_url == "http://custom-endpoint.com"

import os
from unittest.mock import patch

from utils.config import Settings


def test_settings_default_values() -> None:
    settings = Settings()
    assert settings.env == "local"
    assert settings.workspace is None
    assert settings.endpoint_url is None


def test_settings_env_variable_override_environment() -> None:
    with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
        settings = Settings()
        assert settings.env == "production"


def test_settings_env_variable_override_workspace() -> None:
    with patch.dict(os.environ, {"WORKSPACE": "test_workspace"}):
        settings = Settings()
        assert settings.workspace == "test_workspace"


def test_settings_env_variable_override_endpoint_url() -> None:
    with patch.dict(os.environ, {"ENDPOINT_URL": "http://mock-endpoint-url.com"}):
        settings = Settings()
        assert settings.endpoint_url == "http://mock-endpoint-url.com"

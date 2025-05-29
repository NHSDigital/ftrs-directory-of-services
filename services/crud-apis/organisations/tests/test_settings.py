import os

import pytest
from pydantic import ValidationError

from organisations.settings import AppSettings


def test_get_app_settings_valid_direct_input() -> None:
    env_vars = {
        "ENVIRONMENT": "from_test",
        "WORKSPACE": "from_test_workspace",
        "ENDPOINT_URL": "from_test_endpoint_url",
    }

    settings = AppSettings(**env_vars)

    assert env_vars["ENVIRONMENT"] == settings.env
    assert env_vars["WORKSPACE"] == settings.workspace
    assert env_vars["ENDPOINT_URL"] == settings.endpoint_url


def test_get_app_settings_invalid_input() -> None:
    env_vars = {
        "ENV": "local",
        "WORKSPACE": "test_workspace",
        "ENDPOINT_URL": "http://localhost:8000",
    }

    with pytest.raises(ValidationError):
        AppSettings(**env_vars)


def test_get_app_settings_missing_input() -> None:
    os.environ.pop("ENVIRONMENT", None)
    env_vars = {
        "WORKSPACE": "test_workspace",
        "ENDPOINT_URL": "http://localhost:8000",
    }

    with pytest.raises(ValidationError):
        AppSettings(**env_vars)

from unittest.mock import patch

from organisations.dependencies import get_app_settings
from organisations.settings import AppSettings


def test_get_app_settings() -> None:
    with patch.dict("os.environ", {"ENVIRONMENT": "test"}):
        app_settings = get_app_settings()

    assert isinstance(app_settings, AppSettings)

import os
from unittest.mock import patch

import pytest
from ftrs_common.utils.splunk import get_splunk_index


@pytest.mark.parametrize(
    "environment, workspace, expected_index",
    [
        (None, None, "app_directoryofservices_dev"),
        ("", None, "app_directoryofservices_dev"),
        ("dev", None, "app_directoryofservices_dev"),
        ("test", None, "app_directoryofservices_dev"),
        ("prod", "my-workspace", "app_directoryofservices_dev"),
        ("int", "ws-123", "app_directoryofservices_dev"),
        (None, "any-workspace", "app_directoryofservices_dev"),
        ("local", None, "app_directoryofservices_local"),
        ("prod", None, "app_directoryofservices_prod"),
        ("ref", None, "app_directoryofservices_ref"),
    ],
)
def test_get_splunk_index(
    environment: str | None, workspace: str | None, expected_index: str
) -> None:
    env_overrides: dict[str, str] = {}
    keys_to_clear = ["ENVIRONMENT", "WORKSPACE"]

    if environment is not None:
        env_overrides["ENVIRONMENT"] = environment
    if workspace is not None:
        env_overrides["WORKSPACE"] = workspace

    with patch.dict(os.environ, env_overrides, clear=False):
        for key in keys_to_clear:
            if key not in env_overrides:
                os.environ.pop(key, None)
        assert get_splunk_index() == expected_index

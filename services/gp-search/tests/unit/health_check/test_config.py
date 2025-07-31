import os
from unittest.mock import patch

from health_check.config import GpHealthCheckSettings


def test_settings_env_variable_override_base_fhir_url() -> None:
    with patch.dict(os.environ, {"DYNAMODB_TABLE_NAME": "mock-dynamodb-table-name"}):
        settings = GpHealthCheckSettings()
        assert settings.dynamodb_table_name == "mock-dynamodb-table-name"

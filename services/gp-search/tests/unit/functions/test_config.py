import os
from unittest.mock import patch

from functions.config import GpSettings


def test_settings_env_variable_override_base_fhir_url() -> None:
    with patch.dict(os.environ, {"FHIR_BASE_URL": "http://mock-fhir-base-url.com"}):
        settings = GpSettings()
        assert settings.fhir_base_url == "http://mock-fhir-base-url.com"

from unittest.mock import patch

import pytest
from ftrs_data_layer.models import HealthcareService
from ftrs_data_layer.repository.dynamodb import DocumentLevelRepository

from utils.db_service import get_service_repository, get_table_name


def test_returns_correct_repository_for_healthcare_service() -> None:
    with patch("utils.db_service.get_env_variables") as mock_env_vars:
        mock_env_vars.return_value = {"endpoint_url": "http://localhost", "env": "dev"}
        repository = get_service_repository(HealthcareService, "healthcare-service")
        assert isinstance(repository, DocumentLevelRepository)
        assert repository.model_cls == HealthcareService


def test_returns_correct_table_name_with_workspace() -> None:
    with patch("utils.db_service.get_env_variables") as mock_env_vars:
        mock_env_vars.return_value = {"env": "dev", "workspace": "team1"}
        table_name = get_table_name("organisation")
        assert table_name == "ftrs-dos-dev-database-organisation-team1"


def test_raises_error_for_missing_env_variables() -> None:
    with patch("utils.db_service.get_env_variables") as mock_env_vars:
        mock_env_vars.side_effect = KeyError("Missing environment variable")
        with pytest.raises(KeyError):
            get_service_repository(HealthcareService, "healthcare-service")

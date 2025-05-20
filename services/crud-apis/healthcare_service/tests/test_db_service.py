import pytest
from unittest.mock import patch, MagicMock

from ftrs_data_layer.models import HealthcareService
from healthcare_service.app.services.db_service import get_healthcare_service_repository, get_table_name

@patch("healthcare_service.app.services.db_service.get_env_variables")
@patch("healthcare_service.app.services.db_service.DocumentLevelRepository")
def repository_returns_correct_instance(mock_repository, mock_get_env_variables):
    mock_get_env_variables.return_value = {
        "entity_name": "healthcare",
        "endpoint_url": "http://localhost:8000",
        "env": "dev",
        "workspace": None,
    }
    repo_instance = get_healthcare_service_repository()
    mock_repository.assert_called_once_with(
        table_name="ftrs-dos-dev-database-healthcare",
        model_cls=HealthcareService,
        endpoint_url="http://localhost:8000",
    )
    assert isinstance(repo_instance, MagicMock)

@patch("healthcare_service.app.services.db_service.get_env_variables")
def table_name_includes_workspace_if_present(mock_get_env_variables):
    mock_get_env_variables.return_value = {
        "entity_name": "healthcare",
        "env": "dev",
        "workspace": "team1",
    }
    table_name = get_table_name("healthcare")
    assert table_name == "ftrs-dos-dev-database-healthcare-team1"

@patch("healthcare_service.app.services.db_service.get_env_variables")
def table_name_excludes_workspace_if_absent(mock_get_env_variables):
    mock_get_env_variables.return_value = {
        "entity_name": "healthcare",
        "env": "dev",
        "workspace": None,
    }
    table_name = get_table_name("healthcare")
    assert table_name == "ftrs-dos-dev-database-healthcare"

@patch("healthcare_service.app.services.db_service.get_env_variables")
def table_name_handles_empty_entity_name(mock_get_env_variables):
    mock_get_env_variables.return_value = {
        "entity_name": "",
        "env": "dev",
        "workspace": None,
    }
    table_name = get_table_name("")
    assert table_name == "ftrs-dos-dev-database-"

@patch("healthcare_service.app.services.db_service.get_env_variables")
def table_name_handles_missing_env_variable(mock_get_env_variables):
    mock_get_env_variables.return_value = {}
    with pytest.raises(KeyError):
        get_table_name("healthcare")

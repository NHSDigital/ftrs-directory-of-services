from unittest.mock import patch

from ftrs_data_layer.models import HealthcareService
from healthcare_service.app.services.db_service import (
    get_healthcare_service_repository,
    get_table_name,
)


@patch("healthcare_service.app.services.db_service.get_env_variables")
@patch("healthcare_service.app.services.db_service.DocumentLevelRepository")
def repository_returns_correct_instance(mock_repository, mock_get_env_variables):
    mock_get_env_variables.return_value = {
        "env": "test",
        "workspace": "test_workspace",
        "endpoint_url": "http://localhost:8000",
    }
    repo_instance = get_healthcare_service_repository()
    mock_repository.assert_called_once_with(
        table_name="ftrs-dos-test-database-HealthcareService-test_workspace",
        model_cls=HealthcareService,
        endpoint_url="http://localhost:8000",
    )
    assert repo_instance == mock_repository.return_value


@patch("healthcare_service.app.services.db_service.get_env_variables")
def table_name_includes_workspace_if_present(mock_get_env_variables):
    mock_get_env_variables.return_value = {"env": "test", "workspace": "test_workspace"}
    table_name = get_table_name("HealthcareService")
    assert table_name == "ftrs-dos-test-database-HealthcareService-test_workspace"


@patch("healthcare_service.app.services.db_service.get_env_variables")
def table_name_excludes_workspace_if_not_present(mock_get_env_variables):
    mock_get_env_variables.return_value = {"env": "test"}
    table_name = get_table_name("HealthcareService")
    assert table_name == "ftrs-dos-test-database-HealthcareService"

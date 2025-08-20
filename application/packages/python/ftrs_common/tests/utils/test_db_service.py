from ftrs_common.utils.db_service import (
    env_variable_settings,
    get_service_repository,
    get_table_arn,
    get_table_name,
)
from ftrs_data_layer.domain import DBModel
from ftrs_data_layer.repository.dynamodb.attribute_level import AttributeLevelRepository
from pytest_mock import MockerFixture


class MockModel(DBModel):
    pass


def test_get_service_repository_returns_repository(mocker: MockerFixture) -> None:
    mocker.patch(
        "ftrs_common.utils.db_service.get_table_name",
        return_value="mock-table-name",
    )
    mocker.patch(
        "ftrs_common.utils.db_service.env_variable_settings.endpoint_url",
        "http://mock-endpoint.com",
    )

    repository = get_service_repository(MockModel, "entity-name")

    assert isinstance(repository, AttributeLevelRepository)
    assert repository.model_cls == MockModel


def test_get_service_repository_with_no_endpoint_url(mocker: MockerFixture) -> None:
    mocker.patch(
        "ftrs_common.utils.db_service.get_table_name",
        return_value="mock-table-name",
    )
    mocker.patch(
        "ftrs_common.utils.db_service.env_variable_settings.endpoint_url", None
    )

    repository = get_service_repository(MockModel, "entity-name")

    assert isinstance(repository, AttributeLevelRepository)
    assert repository.model_cls == MockModel


def test_returns_correct_table_name_for_given_entity() -> None:
    env_variable_settings.env = "dev"
    env_variable_settings.workspace = None
    entity_name = "healthcare"
    expected_table_name = "ftrs-dos-dev-database-healthcare"
    assert get_table_name(entity_name) == expected_table_name


def test_includes_workspace_in_table_name_if_present() -> None:
    env_variable_settings.env = "prod"
    env_variable_settings.workspace = "team1"
    entity_name = "organisation"
    expected_table_name = "ftrs-dos-prod-database-organisation-team1"
    assert get_table_name(entity_name) == expected_table_name


def test_handles_empty_entity_name_gracefully() -> None:
    env_variable_settings.env = "test"
    env_variable_settings.workspace = None
    entity_name = ""
    expected_table_name = "ftrs-dos-test-database-"
    assert get_table_name(entity_name) == expected_table_name


def test_handles_none_workspace_correctly() -> None:
    env_variable_settings.env = "staging"
    env_variable_settings.workspace = None
    entity_name = "service"
    expected_table_name = "ftrs-dos-staging-database-service"
    assert get_table_name(entity_name) == expected_table_name


def test_get_table_arn(mocker: MockerFixture) -> None:
    mock_ddb_client = mocker.MagicMock()
    mock_ddb_client.describe_table.return_value = {
        "Table": {"TableArn": "arn:aws:dynamodb:region:account-id:table/test_table"}
    }

    mocker.patch(
        "ftrs_common.utils.db_service.get_dynamodb_client",
        return_value=mock_ddb_client,
    )

    result = get_table_arn("test_table")

    assert result == "arn:aws:dynamodb:region:account-id:table/test_table"
    mock_ddb_client.describe_table.assert_called_once_with(TableName="test_table")

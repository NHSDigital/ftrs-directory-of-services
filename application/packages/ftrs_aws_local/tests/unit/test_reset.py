from unittest.mock import MagicMock

import boto3
import pytest
from ftrs_data_layer.models import HealthcareService, Location, Organisation
from pytest_mock import MockerFixture
from typer import Abort

from dynamodb.constants import TargetEnvironment
from dynamodb.reset import (
    DEFAULT_CLEARABLE_ENTITY_TYPES,
    ClearableEntityTypes,
    get_entity_cls,
    init_tables,
    reset,
)
from tests.utils.fixtures import mock_logging


def test_reset_invalid_environment() -> None:
    with pytest.raises(ValueError):
        reset(env="prod")


def test_reset_user_aborts(mocker: MockerFixture) -> None:
    mock_confirm = mocker.patch("dynamodb.reset.confirm", side_effect=Abort)

    with pytest.raises(Abort):
        reset(env=TargetEnvironment.dev, workspace="test-workspace")

    mock_confirm.assert_called_once_with(
        "Are you sure you want to reset the dev environment (workspace: test-workspace)? This action cannot be undone.",
        abort=True,
    )


def test_reset_user_aborts_with_exception(mocker: MockerFixture) -> None:
    mocker.patch("dynamodb.reset.confirm", side_effect=Abort())

    with pytest.raises(Abort):
        reset(env=TargetEnvironment.dev)


def test_reset_success(mocker: MockerFixture) -> None:
    mock_confirm = mocker.patch("dynamodb.reset.confirm", return_value=True)
    mocker.patch("dynamodb.reset.track", side_effect=lambda *args, **_: args[0])
    mock_repository = mocker.patch("dynamodb.reset.DocumentLevelRepository")

    mock_records: list[MagicMock] = [
        mocker.MagicMock(id="item1"),
        mocker.MagicMock(id="item2"),
    ]

    mock_repo_instance = mocker.MagicMock()
    mock_repo_instance.iter_records.return_value = mock_records
    mock_repository.return_value = mock_repo_instance

    reset(
        env=TargetEnvironment.dev,
        workspace="test-workspace",
        endpoint_url="http://localhost:8000",
        entity_type=[ClearableEntityTypes.organisation],
    )

    mock_confirm.assert_called_once()
    mock_repository.assert_called_once_with(
        table_name="ftrs-dos-dev-database-organisation-test-workspace",
        model_cls=Organisation,
        endpoint_url="http://localhost:8000",
    )
    mock_repo_instance.iter_records.assert_called_once_with(max_results=None)
    assert mock_repo_instance.delete.call_count == len(mock_records)
    mock_repo_instance.delete.assert_any_call("item1")
    mock_repo_instance.delete.assert_any_call("item2")


def test_reset_init_tables(mocker: MockerFixture) -> None:
    mock_init_tables = mocker.patch("dynamodb.reset.init_tables")
    mocker.patch("dynamodb.reset.confirm", return_value=True)
    mocker.patch("dynamodb.reset.track", return_value=[])
    reset(
        env=TargetEnvironment.dev,
        workspace="test-workspace",
        init=True,
    )

    mock_init_tables.assert_called_once_with(
        endpoint_url=None,
        env=TargetEnvironment.dev,
        workspace="test-workspace",
        entity_type=DEFAULT_CLEARABLE_ENTITY_TYPES,
    )


@pytest.mark.parametrize(
    "entity_type, expected_class",
    [
        (ClearableEntityTypes.organisation, Organisation),
        (ClearableEntityTypes.healthcare_service, HealthcareService),
        (ClearableEntityTypes.location, Location),
    ],
)
def test_get_entity_cls(
    entity_type: ClearableEntityTypes,
    expected_class: type,
) -> None:
    result = get_entity_cls(entity_type)
    assert result == expected_class


def test_get_entity_cls_invalid_type() -> None:
    with pytest.raises(ValueError, match="Unsupported entity type: invalid_type"):
        get_entity_cls("invalid_type")


def test_init_tables(mocker: MockerFixture) -> None:
    mock_client = MagicMock(create_table=MagicMock())
    mocker.patch("dynamodb.reset.get_dynamodb_client", return_value=mock_client)

    init_tables(
        endpoint_url="http://localhost:8000",
        env=TargetEnvironment.local,
        workspace="test-workspace",
        entity_type=[ClearableEntityTypes.organisation],
    )

    mock_client.create_table.assert_called_once_with(
        TableName="ftrs-dos-local-database-organisation-test-workspace",
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "field", "AttributeType": "S"},
            {"AttributeName": "identifier_ODS_ODSCode", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "field", "KeyType": "RANGE"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "OsdCodeValueIndex",
                "KeySchema": [
                    {
                        "AttributeName": "identifier_ODS_ODSCode",
                        "KeyType": "HASH",
                    },
                ],
                "Projection": {
                    "ProjectionType": "ALL",
                },
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )


def test_init_tables_invalid_env() -> None:
    with pytest.raises(
        ValueError, match="The init option is only supported for the local environment."
    ):
        init_tables(
            endpoint_url="http://localhost:8000",
            env=TargetEnvironment.dev,
            workspace="test-workspace",
            entity_type=[ClearableEntityTypes.organisation],
        )


def test_init_tables_existing_table(
    mocker: MockerFixture, mock_logging: MagicMock
) -> None:
    """
    Test that the init_tables function handles the case where the table already exists.
    """
    mock_client = boto3.client("dynamodb")
    mock_client.create_table = MagicMock(
        side_effect=mock_client.exceptions.ResourceInUseException(
            error_response={
                "Error": {
                    "Code": "ResourceInUseException",
                    "Message": "Table already exists",
                }
            },
            operation_name="CreateTable",
        )
    )
    mocker.patch("dynamodb.reset.get_dynamodb_client", return_value=mock_client)

    init_tables(
        endpoint_url="http://localhost:8000",
        env=TargetEnvironment.local,
        workspace="test-workspace",
        entity_type=[ClearableEntityTypes.organisation],
    )

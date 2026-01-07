import boto3
import pytest
from pytest_mock import MockerFixture

from dynamodb.constants import ClearableEntityType, TargetEnvironment
from dynamodb.init import get_entity_config, init_tables


def test_init_tables(mocker: MockerFixture) -> None:
    mock_client = mocker.MagicMock(create_table=mocker.MagicMock())
    mocker.patch("dynamodb.init.get_dynamodb_client", return_value=mock_client)

    init_tables(
        endpoint_url="http://localhost:8000",
        env=TargetEnvironment.local,
        workspace="test-workspace",
        entity_type=[ClearableEntityType.organisation],
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
                "IndexName": "OdsCodeValueIndex",
                "KeySchema": [
                    {"AttributeName": "identifier_ODS_ODSCode", "KeyType": "HASH"}
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
            entity_type=[ClearableEntityType.organisation],
        )


def test_init_tables_existing_table(
    mocker: MockerFixture,
) -> None:
    """
    Test that the init_tables function handles the case where the table already exists.
    """
    mock_client = boto3.client("dynamodb")
    mock_client.create_table = mocker.MagicMock(
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
    mocker.patch("dynamodb.init.get_dynamodb_client", return_value=mock_client)

    init_tables(
        endpoint_url="http://localhost:8000",
        env=TargetEnvironment.local,
        workspace="test-workspace",
        entity_type=[ClearableEntityType.organisation],
    )


def test_get_entity_config_includes_correct_indexes_for_healthcare_service() -> None:
    length = 2
    result = get_entity_config(ClearableEntityType.healthcare_service)
    assert len(result["global_secondary_indexes"]) == length
    assert result["global_secondary_indexes"][0]["IndexName"] == "ProvidedByValueIndex"
    assert result["global_secondary_indexes"][1]["IndexName"] == "LocationIndex"


def test_get_entity_config_includes_correct_indexes_for_location() -> None:
    result = get_entity_config(ClearableEntityType.location)
    assert len(result["global_secondary_indexes"]) == 1
    assert (
        result["global_secondary_indexes"][0]["IndexName"]
        == "ManagingOrganisationIndex"
    )


def test_get_entity_config_returns_same_key_schema_for_all_entities() -> None:
    base_schema = [
        {"AttributeName": "id", "KeyType": "HASH"},
        {"AttributeName": "field", "KeyType": "RANGE"},
    ]

    for entity_type in ClearableEntityType:
        result = get_entity_config(entity_type)

        if entity_type == ClearableEntityType.state:
            assert result["key_schema"] == [
                {"AttributeName": "source_record_id", "KeyType": "HASH"}
            ]
        else:
            assert result["key_schema"] == base_schema

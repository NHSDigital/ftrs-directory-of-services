import pytest
from pytest_mock import MockerFixture
from typer import Abort

from dynamodb.constants import ALL_ENTITY_TYPES, ClearableEntityType, TargetEnvironment
from dynamodb.reset import delete_all_table_items, iter_record_keys, reset


def test_reset_invalid_environment() -> None:
    with pytest.raises(ValueError):
        reset(env="prod")  # type: ignore


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
    mocker.patch("dynamodb.reset.confirm")
    mock_session_cls = mocker.patch("dynamodb.reset.Session")
    mock_session = mock_session_cls.return_value
    mock_delete = mocker.patch("dynamodb.reset.delete_all_table_items", return_value=10)
    mocker.patch(
        "dynamodb.reset.format_table_name",
        side_effect=lambda e, env, w: f"table-{e}-{env}-{w}",
    )
    mock_logger = mocker.patch("dynamodb.reset.LOGGER")

    reset(env=TargetEnvironment.dev, workspace="test-ws")

    assert mock_delete.call_count == len(ALL_ENTITY_TYPES)
    for entity in ALL_ENTITY_TYPES:
        expected_table = f"table-{entity}-dev-test-ws"
        mock_delete.assert_any_call(expected_table, mock_session, None)

    assert mock_logger.log.call_count == len(ALL_ENTITY_TYPES)


def test_reset_success_specific_entities(mocker: MockerFixture) -> None:
    mocker.patch("dynamodb.reset.confirm")
    mock_session = mocker.patch("dynamodb.reset.Session").return_value
    mock_delete = mocker.patch("dynamodb.reset.delete_all_table_items", return_value=5)
    mocker.patch("dynamodb.reset.format_table_name", return_value="some-table")

    env = TargetEnvironment.local
    entities = [ClearableEntityType.organisation, ClearableEntityType.location]

    reset(env=env, entity_type=entities)

    assert mock_delete.call_count == len(entities)
    mock_delete.assert_called_with("some-table", mock_session, None)


def test_delete_all_table_items(mocker: MockerFixture) -> None:
    mock_session = mocker.Mock()
    mock_resource = mock_session.resource.return_value
    mock_table = mock_resource.Table.return_value

    # keys generator
    keys = [{"pk": "1"}, {"pk": "2"}]
    mocker.patch("dynamodb.reset.iter_record_keys", return_value=iter(keys))

    # Mock track to just return the iterable
    mocker.patch("dynamodb.reset.track", side_effect=lambda x, description: x)

    count = delete_all_table_items(mock_session, "my-table", "http://localhost:8000")

    mock_session.resource.assert_called_with(
        "dynamodb", endpoint_url="http://localhost:8000"
    )
    mock_session.client.assert_called_with(
        "dynamodb", endpoint_url="http://localhost:8000"
    )
    mock_resource.Table.assert_called_with("my-table")

    expected_result_count = 2

    assert count == expected_result_count
    mock_table.delete_item.assert_has_calls(
        [mocker.call(Key={"pk": "1"}), mocker.call(Key={"pk": "2"})]
    )


def test_iter_record_keys(mocker: MockerFixture) -> None:
    mock_client = mocker.Mock()

    # describe_table
    mock_client.describe_table.return_value = {
        "Table": {
            "KeySchema": [
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ]
        }
    }

    # get_paginator
    mock_paginator = mock_client.get_paginator.return_value

    # Simulated items from DynamoDB (in Low-Level format as getting from scan)
    # The code uses TypeDeserializer on attributes.
    # scan returns items in DynamoDB JSON format: {"pk": {"S": "val"}}

    page1 = {
        "Items": [
            {"pk": {"S": "p1"}, "sk": {"S": "s1"}, "other": {"S": "o1"}},
            {"pk": {"S": "p2"}, "sk": {"S": "s2"}, "other": {"S": "o2"}},
        ]
    }

    mock_paginator.paginate.return_value = [page1]

    generator = iter_record_keys(mock_client, "my-table")
    results = list(generator)

    mock_client.get_paginator.assert_called_with("scan")
    mock_paginator.paginate.assert_called_with(
        TableName="my-table", ProjectionExpression="pk, sk"
    )

    expected_result_count = 2

    assert len(results) == expected_result_count
    assert results[0] == {"pk": "p1", "sk": "s1"}
    assert results[1] == {"pk": "p2", "sk": "s2"}

from unittest.mock import MagicMock

import pytest
from boto3 import Session
from boto3.dynamodb.types import TypeSerializer
from pytest_mock import MockerFixture
from typer import Abort

from dynamodb.constants import ALL_ENTITY_TYPES, ClearableEntityType, TargetEnvironment
from dynamodb.reset import delete_all_table_items, iter_record_keys, reset_command


def test_reset_invalid_environment() -> None:
    """Test that reset rejects production environment."""
    with pytest.raises(ValueError):
        reset_command(env="prod")  # type: ignore


def test_reset_user_aborts(mocker: MockerFixture) -> None:
    """Test that reset handles user aborting the confirmation prompt."""
    mock_confirm = mocker.patch("dynamodb.reset.confirm", side_effect=Abort)

    with pytest.raises(Abort):
        reset_command(env=TargetEnvironment.dev, workspace="test-workspace")

    mock_confirm.assert_called_once_with(
        "Are you sure you want to reset the dev environment (workspace: test-workspace)? This action cannot be undone.",
        abort=True,
    )


def test_reset_user_aborts_default_workspace(mocker: MockerFixture) -> None:
    """Test that reset shows 'default' when no workspace specified."""
    mock_confirm = mocker.patch("dynamodb.reset.confirm", side_effect=Abort())

    with pytest.raises(Abort):
        reset_command(env=TargetEnvironment.dev)

    # Verify the confirmation message includes 'default'
    args = mock_confirm.call_args[0][0]
    assert "default" in args


def test_reset_processes_all_entity_types(mocker: MockerFixture) -> None:
    """Test that reset processes all entity types by default."""
    mocker.patch("dynamodb.reset.confirm")
    mock_logger = mocker.patch("dynamodb.reset.LOGGER")

    # Track which tables were deleted
    deleted_tables = []

    def capture_table_name(
        session: Session, table_name: str, endpoint_url: str | None
    ) -> int:
        deleted_tables.append(table_name)
        return 5

    mocker.patch(
        "dynamodb.reset.delete_all_table_items", side_effect=capture_table_name
    )

    reset_command(env=TargetEnvironment.dev, workspace="test-ws")

    # Verify all entity types were processed
    assert len(deleted_tables) == len(ALL_ENTITY_TYPES)

    # Verify correct table names were generated for each entity
    for entity in ALL_ENTITY_TYPES:
        assert any(entity.value in table_name for table_name in deleted_tables)

    # Verify logging occurred for each table
    assert mock_logger.log.call_count == len(ALL_ENTITY_TYPES)


def test_reset_processes_specific_entity_types(mocker: MockerFixture) -> None:
    """Test that reset processes only specified entity types."""
    mocker.patch("dynamodb.reset.confirm")
    mocker.patch("dynamodb.reset.LOGGER")

    deleted_tables = []

    def capture_table_name(
        session: Session, table_name: str, endpoint_url: str | None
    ) -> int:
        deleted_tables.append(table_name)
        return 3

    mocker.patch(
        "dynamodb.reset.delete_all_table_items", side_effect=capture_table_name
    )

    entities = [ClearableEntityType.organisation, ClearableEntityType.location]
    reset_command(env=TargetEnvironment.local, entity_type=entities)

    # Should only process the two specified entities
    expected_entity_count = 2
    assert len(deleted_tables) == expected_entity_count
    assert any("organisation" in table for table in deleted_tables)
    assert any("location" in table for table in deleted_tables)


def test_delete_all_table_items(mocker: MockerFixture) -> None:
    """Test deleting items using actual iter_record_keys logic."""
    # Create a real session mock with proper structure
    mock_session = MagicMock()
    mock_resource = MagicMock()
    mock_client = MagicMock()
    mock_table = MagicMock()

    mock_session.resource.return_value = mock_resource
    mock_session.client.return_value = mock_client
    mock_resource.Table.return_value = mock_table

    # Setup the client responses for iter_record_keys
    serializer = TypeSerializer()
    mock_client.describe_table.return_value = {
        "Table": {
            "KeySchema": [
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ]
        }
    }

    # Create paginator with realistic DynamoDB response format
    mock_paginator = MagicMock()
    mock_client.get_paginator.return_value = mock_paginator

    mock_paginator.paginate.return_value = [
        {
            "Items": [
                {
                    "pk": serializer.serialize("org-1"),
                    "sk": serializer.serialize("metadata"),
                    "name": serializer.serialize("Organization 1"),
                },
                {
                    "pk": serializer.serialize("org-2"),
                    "sk": serializer.serialize("metadata"),
                    "name": serializer.serialize("Organization 2"),
                },
            ]
        }
    ]

    # Mock track to passthrough
    mocker.patch("dynamodb.reset.track", side_effect=lambda x, description: x)

    # Execute the function
    count = delete_all_table_items(mock_session, "test-table", "http://localhost:8000")

    # Verify correct AWS SDK calls
    mock_session.resource.assert_called_once_with(
        "dynamodb", endpoint_url="http://localhost:8000"
    )
    mock_session.client.assert_called_once_with(
        "dynamodb", endpoint_url="http://localhost:8000"
    )
    mock_resource.Table.assert_called_once_with("test-table")

    # Verify deletion count
    expected_item_count = 2
    assert count == expected_item_count

    # Verify delete_item was called for each item with only keys
    assert mock_table.delete_item.call_count == expected_item_count

    # Verify that only keys were passed (not the 'name' attribute)
    for call in mock_table.delete_item.call_args_list:
        keys = call.kwargs["Key"]
        assert set(keys.keys()) == {"pk", "sk"}
        assert "name" not in keys


def test_delete_all_table_items_empty_table(mocker: MockerFixture) -> None:
    """Test deleting from an empty table returns 0."""
    mock_session = MagicMock()
    mock_resource = MagicMock()
    mock_client = MagicMock()
    mock_table = MagicMock()

    mock_session.resource.return_value = mock_resource
    mock_session.client.return_value = mock_client
    mock_resource.Table.return_value = mock_table

    # Setup empty table response
    mock_client.describe_table.return_value = {
        "Table": {
            "KeySchema": [
                {"AttributeName": "pk", "KeyType": "HASH"},
            ]
        }
    }

    mock_paginator = MagicMock()
    mock_client.get_paginator.return_value = mock_paginator
    mock_paginator.paginate.return_value = [{"Items": []}]

    mocker.patch("dynamodb.reset.track", side_effect=lambda x, description: x)

    count = delete_all_table_items(mock_session, "empty-table")

    assert count == 0
    mock_table.delete_item.assert_not_called()


def test_iter_record_keys() -> None:
    """Test iterating record keys extracts only key attributes."""
    mock_client = MagicMock()

    # Setup table schema
    mock_client.describe_table.return_value = {
        "Table": {
            "KeySchema": [
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ]
        }
    }

    # Setup paginator with DynamoDB-formatted items
    mock_paginator = MagicMock()
    mock_client.get_paginator.return_value = mock_paginator

    serializer = TypeSerializer()
    mock_paginator.paginate.return_value = [
        {
            "Items": [
                {
                    "pk": serializer.serialize("item-1"),
                    "sk": serializer.serialize("sort-a"),
                    "data": serializer.serialize("some data"),
                    "count": serializer.serialize(42),
                },
                {
                    "pk": serializer.serialize("item-2"),
                    "sk": serializer.serialize("sort-b"),
                    "data": serializer.serialize("more data"),
                },
            ]
        }
    ]

    # Execute
    keys = list(iter_record_keys(mock_client, "test-table"))

    # Verify
    expected_key_count = 2
    assert len(keys) == expected_key_count

    # Each result should only have key attributes
    assert keys[0] == {"pk": "item-1", "sk": "sort-a"}
    assert keys[1] == {"pk": "item-2", "sk": "sort-b"}

    # Verify correct SDK calls
    mock_client.describe_table.assert_called_once_with(TableName="test-table")
    mock_client.get_paginator.assert_called_once_with("scan")
    mock_paginator.paginate.assert_called_once_with(
        TableName="test-table",
        ProjectionExpression="pk, sk",
    )


def test_iter_record_keys_single_key() -> None:
    """Test iterating record keys with single partition key."""
    mock_client = MagicMock()

    mock_client.describe_table.return_value = {
        "Table": {
            "KeySchema": [
                {"AttributeName": "id", "KeyType": "HASH"},
            ]
        }
    }

    mock_paginator = MagicMock()
    mock_client.get_paginator.return_value = mock_paginator

    serializer = TypeSerializer()
    mock_paginator.paginate.return_value = [
        {
            "Items": [
                {
                    "id": serializer.serialize("user-123"),
                    "name": serializer.serialize("John Doe"),
                },
            ]
        }
    ]

    keys = list(iter_record_keys(mock_client, "users-table"))

    assert len(keys) == 1
    assert keys[0] == {"id": "user-123"}

    # Verify projection expression only includes the key
    mock_paginator.paginate.assert_called_once_with(
        TableName="users-table",
        ProjectionExpression="id",
    )


def test_iter_record_keys_multiple_pages() -> None:
    """Test iterating record keys handles pagination correctly."""
    mock_client = MagicMock()

    mock_client.describe_table.return_value = {
        "Table": {
            "KeySchema": [
                {"AttributeName": "pk", "KeyType": "HASH"},
            ]
        }
    }

    mock_paginator = MagicMock()
    mock_client.get_paginator.return_value = mock_paginator

    serializer = TypeSerializer()
    # Simulate multiple pages
    mock_paginator.paginate.return_value = [
        {
            "Items": [
                {"pk": serializer.serialize("item-1")},
                {"pk": serializer.serialize("item-2")},
            ]
        },
        {
            "Items": [
                {"pk": serializer.serialize("item-3")},
                {"pk": serializer.serialize("item-4")},
            ]
        },
    ]

    keys = list(iter_record_keys(mock_client, "test-table"))

    expected_item_count = 4
    assert len(keys) == expected_item_count
    assert keys == [
        {"pk": "item-1"},
        {"pk": "item-2"},
        {"pk": "item-3"},
        {"pk": "item-4"},
    ]


def test_iter_record_keys_empty_table() -> None:
    """Test iterating keys from an empty table."""
    mock_client = MagicMock()

    mock_client.describe_table.return_value = {
        "Table": {
            "KeySchema": [
                {"AttributeName": "pk", "KeyType": "HASH"},
            ]
        }
    }

    mock_paginator = MagicMock()
    mock_client.get_paginator.return_value = mock_paginator
    mock_paginator.paginate.return_value = [{"Items": []}]

    keys = list(iter_record_keys(mock_client, "empty-table"))

    assert keys == []

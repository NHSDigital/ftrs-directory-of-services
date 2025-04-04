from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from ftrs_data_layer.repository.dynamodb import FieldLevelRepository


class MockModel(BaseModel):
    id: str
    name: str
    description: str


def test_field_create() -> None:
    """
    Test the create method of the FieldLevelRepository.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )
    obj = MockModel(id="1", name="Test", description="Test description")

    # Mock the batch_write_item method
    repo.resource.batch_write_item = MagicMock(
        return_value={
            "UnprocessedItems": {},
            "ConsumedCapacity": [
                {
                    "TableName": "test_table",
                    "CapacityUnits": 1,
                    "Table": {"CapacityUnits": 1},
                }
            ],
        }
    )

    # Call the create method
    repo.create(obj)

    repo.resource.batch_write_item.assert_called_once_with(
        RequestItems={
            "test_table": [
                {
                    "PutRequest": {
                        "Item": {
                            "id": "1",
                            "field": "name",
                            "value": "Test",
                        }
                    }
                },
                {
                    "PutRequest": {
                        "Item": {
                            "id": "1",
                            "field": "description",
                            "value": "Test description",
                        }
                    }
                },
            ]
        },
        ReturnConsumedCapacity="INDEXES",
    )


def test_field_get() -> None:
    """
    Test the get method of the FieldLevelRepository.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )
    obj = MockModel(id="1", name="Test", description="Test description")

    # Mock the query method
    repo.table.query = MagicMock(
        return_value={
            "Items": [
                {"id": "1", "field": "name", "value": "Test"},
                {"id": "1", "field": "description", "value": "Test description"},
            ]
        }
    )

    # Call the get method
    result = repo.get("1")
    assert result == obj

    repo.table.query.assert_called_once_with(
        KeyConditionExpression="id = :id",
        ExpressionAttributeValues={":id": "1"},
        ReturnConsumedCapacity="INDEXES",
        ProjectionExpression="id, field, value",
    )


def test_field_get_no_result() -> None:
    """
    Test the get method of the FieldLevelRepository when no item is found.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the query method
    repo.table.query = MagicMock(return_value={"Items": []})

    # Call the get method
    result = repo.get("1")
    assert result is None

    repo.table.query.assert_called_once_with(
        KeyConditionExpression="id = :id",
        ExpressionAttributeValues={":id": "1"},
        ReturnConsumedCapacity="INDEXES",
        ProjectionExpression="id, field, value",
    )


def test_field_update() -> None:
    """
    Test the update method of the FieldLevelRepository.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )
    obj = MockModel(id="1", name="Test", description="Test description")

    # Mock the batch_write_item method
    repo.resource.batch_write_item = MagicMock(
        return_value={
            "UnprocessedItems": {},
            "ConsumedCapacity": [
                {
                    "TableName": "test_table",
                    "CapacityUnits": 1,
                    "Table": {"CapacityUnits": 1},
                }
            ],
        }
    )

    # Call the update method
    repo.update("1", obj)

    repo.resource.batch_write_item.assert_called_once_with(
        RequestItems={
            "test_table": [
                {
                    "PutRequest": {
                        "Item": {
                            "id": "1",
                            "field": "name",
                            "value": "Test",
                        }
                    }
                },
                {
                    "PutRequest": {
                        "Item": {
                            "id": "1",
                            "field": "description",
                            "value": "Test description",
                        }
                    }
                },
            ]
        },
        ReturnConsumedCapacity="INDEXES",
    )


def test_field_delete() -> None:
    """
    Test the delete method of the FieldLevelRepository.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the batch_write_item method
    repo.table.query = MagicMock(
        return_value={
            "Items": [
                {"id": "1", "field": "name", "value": "Test"},
                {"id": "1", "field": "description", "value": "Test description"},
            ]
        }
    )
    repo.resource.batch_write_item = MagicMock(
        return_value={
            "UnprocessedItems": {},
            "ConsumedCapacity": [
                {
                    "TableName": "test_table",
                    "CapacityUnits": 1,
                    "Table": {"CapacityUnits": 1},
                }
            ],
        }
    )

    # Call the delete method
    repo.delete("1")

    repo.resource.batch_write_item.assert_called_once_with(
        RequestItems={
            "test_table": [
                {
                    "DeleteRequest": {
                        "Key": {
                            "id": "1",
                            "field": "name",
                        }
                    }
                },
                {
                    "DeleteRequest": {
                        "Key": {
                            "id": "1",
                            "field": "description",
                        }
                    }
                },
            ]
        },
        ReturnConsumedCapacity="INDEXES",
    )


def test_field_delete_not_found() -> None:
    """
    Test the delete method of the FieldLevelRepository when no item is found.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the query method to return an empty list
    repo.table.query = MagicMock(return_value={"Items": []})

    # Call the delete method
    with pytest.raises(ValueError) as excinfo:
        repo.delete("1")

    assert excinfo.exconly() == "ValueError: No items found to delete for id: 1"

    repo.table.query.assert_called_once_with(
        KeyConditionExpression="id = :id",
        ExpressionAttributeValues={":id": "1"},
        ReturnConsumedCapacity="INDEXES",
        ProjectionExpression="id, field, value",
    )


def test_field_serialise_item() -> None:
    """
    Test the _serialise_item method of the FieldLevelRepository.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )
    obj = MockModel(id="1", name="Test", description="Test description")

    # Call the _serialise_item method
    result = repo._serialise_item(obj)

    assert result == [
        {"id": "1", "field": "name", "value": "Test"},
        {"id": "1", "field": "description", "value": "Test description"},
    ]


def test_field_parse_item() -> None:
    """
    Test the _parse_item method of the FieldLevelRepository.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )
    item = [
        {"id": "1", "field": "name", "value": "Test"},
        {"id": "1", "field": "description", "value": "Test description"},
    ]

    # Call the _parse_item method
    result = repo._parse_item(item)
    assert result == MockModel(id="1", name="Test", description="Test description")

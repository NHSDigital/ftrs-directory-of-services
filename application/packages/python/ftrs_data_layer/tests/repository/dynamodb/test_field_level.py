from unittest.mock import MagicMock

import pytest
from boto3.dynamodb.conditions import Attr
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


def test_iter_record_ids_single_page() -> None:
    """
    Test the _iter_record_ids method when all records fit in a single page.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the _scan method
    repo._scan = MagicMock(
        return_value={
            "Items": [
                {"id": "1", "field": "createdDateTime"},
                {"id": "2", "field": "createdDateTime"},
            ]
        }
    )

    # Call the _iter_record_ids method
    result = list(repo._iter_record_ids(max_results=10))

    assert result == [("1", "createdDateTime"), ("2", "createdDateTime")]

    repo._scan.assert_called_once_with(
        ProjectionExpression="id, field",
        FilterExpression=Attr("field").eq("createdDateTime"),
        Limit=10,
    )


def test_iter_record_ids_multiple_pages() -> None:
    """
    Test the _iter_record_ids method when records span multiple pages.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the _scan method to simulate paginated results
    repo._scan = MagicMock(
        side_effect=[
            {
                "Items": [
                    {"id": "1", "field": "createdDateTime"},
                    {"id": "2", "field": "createdDateTime"},
                ],
                "LastEvaluatedKey": {"id": "2", "field": "createdDateTime"},
            },
            {
                "Items": [
                    {"id": "3", "field": "createdDateTime"},
                    {"id": "4", "field": "createdDateTime"},
                ]
            },
        ]
    )

    # Call the _iter_record_ids method
    result = list(repo._iter_record_ids(max_results=10))

    assert result == [
        ("1", "createdDateTime"),
        ("2", "createdDateTime"),
        ("3", "createdDateTime"),
        ("4", "createdDateTime"),
    ]

    expected_call_count = 2
    assert repo._scan.call_count == expected_call_count
    repo._scan.assert_any_call(
        ProjectionExpression="id, field",
        FilterExpression=Attr("field").eq("createdDateTime"),
        Limit=10,
    )
    repo._scan.assert_any_call(
        ExclusiveStartKey={"id": "2", "field": "createdDateTime"},
        ProjectionExpression="id, field",
        FilterExpression=Attr("field").eq("createdDateTime"),
        Limit=10,
    )


def test_iter_record_ids_max_results() -> None:
    """
    Test the _iter_record_ids method with a max_results limit.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the _scan method
    repo._scan = MagicMock(
        return_value={
            "Items": [
                {"id": "1", "field": "createdDateTime"},
                {"id": "2", "field": "createdDateTime"},
                {"id": "3", "field": "createdDateTime"},
            ]
        }
    )

    # Call the _iter_record_ids method with a max_results limit
    result = list(repo._iter_record_ids(max_results=2))

    assert result == [("1", "createdDateTime"), ("2", "createdDateTime")]

    repo._scan.assert_called_once_with(
        ProjectionExpression="id, field",
        FilterExpression=Attr("field").eq("createdDateTime"),
        Limit=2,
    )


def test_iter_record_ids_no_results() -> None:
    """
    Test the _iter_record_ids method when no records are found.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the _scan method to return no items
    repo._scan = MagicMock(return_value={"Items": []})

    # Call the _iter_record_ids method
    result = list(repo._iter_record_ids(max_results=10))

    assert result == []

    repo._scan.assert_called_once_with(
        ProjectionExpression="id, field",
        FilterExpression=Attr("field").eq("createdDateTime"),
        Limit=10,
    )


def test_iter_records() -> None:
    """
    Test the iter_records method.
    """
    repo = FieldLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the _iter_record_ids and get methods
    repo._iter_record_ids = MagicMock(
        return_value=[("1", "createdDateTime"), ("2", "createdDateTime")]
    )
    repo.get = MagicMock(
        side_effect=[
            MockModel(id="1", name="Test1", description="Description1"),
            MockModel(id="2", name="Test2", description="Description2"),
        ]
    )

    # Call the iter_records method
    result = list(repo.iter_records(max_results=10))

    assert result == [
        MockModel(id="1", name="Test1", description="Description1"),
        MockModel(id="2", name="Test2", description="Description2"),
    ]

    repo._iter_record_ids.assert_called_once_with(10)
    repo.get.assert_any_call("1")
    repo.get.assert_any_call("2")

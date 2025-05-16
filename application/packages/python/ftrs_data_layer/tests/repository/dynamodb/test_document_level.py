from unittest.mock import MagicMock

from pydantic import BaseModel

from ftrs_data_layer.repository.dynamodb import DocumentLevelRepository


class MockModel(BaseModel):
    id: str
    name: str

    @property
    def indexes(self) -> dict:
        return {
            "some": "index",
        }


def test_doc_create() -> None:
    """
    Test the create method of the DocumentLevelRepository.
    """
    repo = DocumentLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )
    obj = MockModel(id="1", name="Test")

    # Mock the put_item method
    repo.table.put_item = MagicMock(
        return_value={
            "ResponseMetadata": {
                "HTTPStatusCode": 200,
            },
            "ConsumedCapacity": {
                "TableName": "test_table",
                "CapacityUnits": 1,
            },
        }
    )

    # Call the create method
    repo.create(obj)
    repo.table.put_item.assert_called_once_with(
        Item={
            "id": "1",
            "field": "document",
            "value": {"id": "1", "name": "Test"},
            "some": "index",
        },
        ConditionExpression="attribute_not_exists(id)",
        ReturnConsumedCapacity="INDEXES",
    )


def test_doc_get() -> None:
    """
    Test the get method of the DocumentLevelRepository.
    """
    repo = DocumentLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )
    obj = MockModel(id="1", name="Test")

    # Mock the get_item method
    repo.table.get_item = MagicMock(
        return_value={"Item": {"id": "1", "value": {"id": "1", "name": "Test"}}}
    )

    # Call the get method
    result = repo.get("1")
    assert result == obj

    repo.table.get_item.assert_called_once_with(
        Key={"id": "1", "field": "document"},
        ProjectionExpression="id, #val",
        ExpressionAttributeNames={"#val": "value"},
        ReturnConsumedCapacity="INDEXES",
    )


def test_doc_get_no_result() -> None:
    """
    Test the get method of the DocumentLevelRepository when no item is found.
    """
    repo = DocumentLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the get_item method
    repo.table.get_item = MagicMock(return_value={})

    # Call the get method
    result = repo.get("1")
    assert result is None

    repo.table.get_item.assert_called_once_with(
        Key={"id": "1", "field": "document"},
        ProjectionExpression="id, #val",
        ExpressionAttributeNames={"#val": "value"},
        ReturnConsumedCapacity="INDEXES",
    )


def test_doc_update() -> None:
    """
    Test the update method of the DocumentLevelRepository.
    """
    repo = DocumentLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )
    obj = MockModel(id="1", name="Test", indexes={"some_index": "value"})

    # Mock the put_item method
    repo.table.put_item = MagicMock(
        return_value={
            "ResponseMetadata": {
                "HTTPStatusCode": 200,
            },
            "ConsumedCapacity": {
                "TableName": "test_table",
                "CapacityUnits": 1,
            },
        }
    )

    # Call the update method
    repo.update("1", obj)
    repo.table.put_item.assert_called_once_with(
        Item={
            "id": "1",
            "field": "document",
            "value": {"id": "1", "name": "Test"},
            "some": "index",
        },
        ConditionExpression="attribute_exists(id)",
        ReturnConsumedCapacity="INDEXES",
    )


def test_doc_delete() -> None:
    """
    Test the delete method of the DocumentLevelRepository.
    """
    repo = DocumentLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the delete_item method
    repo.table.delete_item = MagicMock(
        return_value={
            "ResponseMetadata": {
                "HTTPStatusCode": 200,
            },
            "ConsumedCapacity": {
                "TableName": "test_table",
                "CapacityUnits": 1,
            },
        }
    )

    # Call the delete method
    repo.delete("1")
    repo.table.delete_item.assert_called_once_with(
        Key={"id": "1", "field": "document"},
        ConditionExpression="attribute_exists(id)",
    )


def test_doc_serialise_item() -> None:
    """
    Test the _serialise_item method of the DocumentLevelRepository.
    """
    repo = DocumentLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )
    obj = MockModel(id="1", name="Test")

    # Call the _serialise_item method
    result = repo._serialise_item(obj)

    assert result == {
        "id": "1",
        "field": "document",
        "value": {"id": "1", "name": "Test"},
        "some": "index",
    }


def test_doc_parse_item() -> None:
    """
    Test the _parse_item method of the DocumentLevelRepository.
    """
    repo = DocumentLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )
    item = {"id": "1", "field": "document", "value": {"id": "1", "name": "Test"}}

    # Call the _parse_item method
    result = repo._parse_item(item)
    assert result == MockModel(id="1", name="Test")


def test_iter_records_single_page() -> None:
    """
    Test the iter_records method of the DocumentLevelRepository when all records fit in a single page.
    """
    repo = DocumentLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the _scan method
    repo.table.scan = MagicMock(
        return_value={
            "Items": [
                {"id": "1", "field": "document", "value": {"id": "1", "name": "Test1"}},
                {"id": "2", "field": "document", "value": {"id": "2", "name": "Test2"}},
            ]
        }
    )

    # Call the iter_records method
    results = list(repo.iter_records())

    assert results == [
        MockModel(id="1", name="Test1"),
        MockModel(id="2", name="Test2"),
    ]

    repo.table.scan.assert_called_once_with(Limit=100, ReturnConsumedCapacity="INDEXES")


def test_iter_records_multiple_pages() -> None:
    """
    Test the iter_records method of the DocumentLevelRepository when records span multiple pages.
    """
    repo = DocumentLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the _scan method for multiple pages
    repo.table.scan = MagicMock(
        side_effect=[
            {
                "Items": [
                    {
                        "id": "1",
                        "field": "document",
                        "value": {"id": "1", "name": "Test1"},
                    },
                ],
                "LastEvaluatedKey": {"id": "1", "field": "document"},
            },
            {
                "Items": [
                    {
                        "id": "2",
                        "field": "document",
                        "value": {"id": "2", "name": "Test2"},
                    },
                ]
            },
        ]
    )

    # Call the iter_records method
    results = list(repo.iter_records())

    assert results == [
        MockModel(id="1", name="Test1"),
        MockModel(id="2", name="Test2"),
    ]

    expected_call_count = 2
    assert repo.table.scan.call_count == expected_call_count
    repo.table.scan.assert_any_call(Limit=100, ReturnConsumedCapacity="INDEXES")
    repo.table.scan.assert_any_call(
        ExclusiveStartKey={"id": "1", "field": "document"},
        Limit=100,
        ReturnConsumedCapacity="INDEXES",
    )


def test_iter_records_with_max_results() -> None:
    """
    Test the iter_records method of the DocumentLevelRepository with a max_results limit.
    """
    repo = DocumentLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the _scan method
    repo.table.scan = MagicMock(
        return_value={
            "Items": [
                {"id": "1", "field": "document", "value": {"id": "1", "name": "Test1"}},
                {"id": "2", "field": "document", "value": {"id": "2", "name": "Test2"}},
            ]
        }
    )

    # Call the iter_records method with max_results=1
    results = list(repo.iter_records(max_results=1))

    assert results == [
        MockModel(id="1", name="Test1"),
    ]

    repo.table.scan.assert_called_once_with(Limit=1, ReturnConsumedCapacity="INDEXES")


def test_iter_records_no_results() -> None:
    """
    Test the iter_records method of the DocumentLevelRepository when no records are found.
    """
    repo = DocumentLevelRepository(
        table_name="test_table",
        model_cls=MockModel,
    )

    # Mock the _scan method
    repo.table.scan = MagicMock(return_value={"Items": []})

    # Call the iter_records method
    results = list(repo.iter_records())

    assert results == []

    repo.table.scan.assert_called_once_with(Limit=100, ReturnConsumedCapacity="INDEXES")

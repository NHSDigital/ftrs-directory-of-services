from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from ftrs_data_layer.repository.dynamodb import DynamoDBRepository


class ExampleDDBRepository(DynamoDBRepository):
    def create(self, obj: str) -> None:
        return super().create(obj)

    def get(self, obj_id: str) -> BaseModel | None:
        return super().get(obj_id)

    def update(self, obj_id: str, obj: BaseModel) -> None:
        return super().update(obj_id, obj)

    def delete(self, id: str) -> None:
        return super().delete(id)


def test_dynamodb_repository_not_init_by_default() -> None:
    """
    Test that the base DynamoDB repository cannot be initialised without
    defined CRUD methods
    """

    with pytest.raises(TypeError) as excinfo:
        DynamoDBRepository(
            table_name="test_table",
            model_cls=ExampleDDBRepository,
        )

    assert (
        str(excinfo.value)
        == "Can't instantiate abstract class DynamoDBRepository without an implementation for abstract methods 'create', 'delete', 'get', 'update'"
    )


def test_dynamodb_repository_init() -> None:
    """
    Test that the base DynamoDB repository can be initialised
    """

    ddb_repo = ExampleDDBRepository(
        table_name="test_table",
        model_cls=BaseModel,
    )

    assert ddb_repo.table.name == "test_table"
    assert ddb_repo.model_cls == BaseModel
    assert ddb_repo.resource is not None


def test_dynamodb_put_item() -> None:
    """
    Test that the _put_item method calls the DynamoDB resource
    with the correct parameters and logs details
    """

    class MockModel(BaseModel):
        id: str
        name: str

    ddb_repo = ExampleDDBRepository(table_name="test_table", model_cls=MockModel)

    # Mock the put_item method
    ddb_repo.table.put_item = Mock(return_value={"ConsumedCapacity": "1"})

    item = MockModel(id="123", name="test_item")

    result = ddb_repo._put_item(item)

    assert result == {"ConsumedCapacity": "1"}

    ddb_repo.table.put_item.assert_called_once_with(
        Item={"id": "123", "name": "test_item"}, ReturnConsumedCapacity="INDEXES"
    )


def test_dynamodb_get_item() -> None:
    """
    Test that the _get_item method calls the DynamoDB resource
    with the correct parameters and logs details
    """

    class MockModel(BaseModel):
        id: str
        name: str

    ddb_repo = ExampleDDBRepository(table_name="test_table", model_cls=MockModel)

    # Mock the get_item method
    ddb_repo.table.get_item = Mock(
        return_value={"Item": {"id": "123", "name": "test_item"}}
    )

    result = ddb_repo._get_item(Key={"id": "123"})

    assert result == MockModel(id="123", name="test_item")
    ddb_repo.table.get_item.assert_called_once_with(
        Key={"id": "123"}, ReturnConsumedCapacity="INDEXES"
    )


def test_dynamodb_get_item_no_result() -> None:
    """
    Test that the _get_item method returns None when no item is found
    """

    class MockModel(BaseModel):
        id: str
        name: str

    ddb_repo = ExampleDDBRepository(table_name="test_table", model_cls=MockModel)

    # Mock the get_item method to return no item
    ddb_repo.table.get_item = Mock(return_value={})

    result = ddb_repo._get_item(Key={"id": "123"})
    assert result is None


def test_dynamodb_query() -> None:
    """
    Test that the _query method calls the DynamoDB resource
    with the correct parameters and logs details
    """

    class MockModel(BaseModel):
        id: str
        name: str

    ddb_repo = ExampleDDBRepository(table_name="test_table", model_cls=MockModel)

    # Mock the query method
    ddb_repo.table.query = Mock(
        return_value={
            "Items": [
                {"id": "123", "name": "test_item"},
                {"id": "456", "name": "another_item"},
            ]
        }
    )

    expected_result_count = 2
    result = ddb_repo._query(key="id", value="123")

    assert len(result) == expected_result_count
    assert result[0] == MockModel(id="123", name="test_item")
    assert result[1] == MockModel(id="456", name="another_item")

    ddb_repo.table.query.assert_called_once_with(
        KeyConditionExpression="id = :id",
        ExpressionAttributeValues={":id": "123"},
        ReturnConsumedCapacity="INDEXES",
    )


def test_dynamodb_batch_write() -> None:
    """
    Test that the _batch_write method calls the DynamoDB resource
    with the correct parameters and logs details
    """

    class MockModel(BaseModel):
        id: str
        name: str

    ddb_repo = ExampleDDBRepository(table_name="test_table", model_cls=MockModel)

    # Mock the batch_write_item method
    ddb_repo.resource.batch_write_item = Mock(return_value={"UnprocessedItems": {}})

    put_items = [{"id": "123", "name": "test_item"}]
    delete_items = [{"id": "456"}]

    result = ddb_repo._batch_write(put_items=put_items, delete_items=delete_items)

    assert result == {"UnprocessedItems": {}}
    ddb_repo.resource.batch_write_item.assert_called_once_with(
        RequestItems={
            "test_table": [
                {"PutRequest": {"Item": {"id": "123", "name": "test_item"}}},
                {"DeleteRequest": {"Key": {"id": "456"}}},
            ]
        },
        ReturnConsumedCapacity="INDEXES",
    )

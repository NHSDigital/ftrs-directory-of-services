from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.repository.dynamodb import DynamoDBRepository
from pydantic import BaseModel


class ExampleDDBRepository(DynamoDBRepository):
    def create(self, obj: str) -> None:
        return super().create(obj)

    def get(self, obj_id: str) -> BaseModel | None:
        return super().get(obj_id)

    def update(self, obj_id: str, obj: BaseModel) -> None:
        return super().update(obj_id, obj)

    def delete(self, id: str) -> None:
        return super().delete(id)

    def iter_records(self, max_results: int | None = 100) -> list[BaseModel]:
        return super().iter_records(max_results)


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
        == "Can't instantiate abstract class DynamoDBRepository without an implementation for abstract methods 'create', 'delete', 'get', 'iter_records', 'update'"
    )


def test_dynamodb_repository_init(mock_logger: MockLogger) -> None:
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

    assert mock_logger.get_log_count() == 1
    assert mock_logger.get_log("DDB_CORE_001", "DEBUG") == [
        {
            "msg": "Initialised DynamoDB repository",
            "reference": "DDB_CORE_001",
            "detail": {
                "table_name": "test_table",
                "endpoint_url": None,
                "repository_cls": "ExampleDDBRepository",
                "model_cls": "pydantic.main:BaseModel",
            },
        }
    ]


def test_dynamodb_put_item(
    mock_logger: MockLogger,
) -> None:
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

    assert mock_logger.get_log("DDB_CORE_002", "DEBUG") == [
        {
            "reference": "DDB_CORE_002",
            "msg": "Putting item into DynamoDB table",
            "detail": {
                "request": {
                    "Item": {
                        "id": "123",
                        "name": "test_item",
                    },
                    "ReturnConsumedCapacity": "INDEXES",
                },
                "table": "test_table",
            },
        }
    ]

    ddb_repo.table.put_item.assert_called_once_with(
        Item={"id": "123", "name": "test_item"}, ReturnConsumedCapacity="INDEXES"
    )

    assert mock_logger.get_log("DDB_CORE_003", "INFO") == [
        {
            "reference": "DDB_CORE_003",
            "msg": "Item put into DynamoDB table",
            "detail": {
                "table": "test_table",
                "consumed_capacity": "1",
            },
        }
    ]


def test_dynamodb_put_item_error(
    mock_logger: MockLogger,
) -> None:
    """
    Test that the _put_item method raises an error and logs details
    """

    class MockModel(BaseModel):
        id: str
        name: str

    ddb_repo = ExampleDDBRepository(table_name="test_table", model_cls=MockModel)

    # Mock the put_item method to raise an error
    ddb_repo.table.put_item = Mock(
        side_effect=ClientError(
            {
                "Error": {
                    "Code": "TestException",
                    "Message": "Test exception",
                },
            },
            operation_name="PutItem",
        )
    )

    item = MockModel(id="123", name="test_item")

    with pytest.raises(ClientError):
        ddb_repo._put_item(item)

    assert mock_logger.was_logged("DDB_CORE_002", "DEBUG") is True
    assert mock_logger.was_logged("DDB_CORE_003", "INFO") is False
    assert mock_logger.get_log("DDB_CORE_004", "ERROR") == [
        {
            "reference": "DDB_CORE_004",
            "msg": "Error putting item into DynamoDB table",
            "detail": {
                "table": "test_table",
                "error": {
                    "Code": "TestException",
                    "Message": "Test exception",
                },
                "request": {
                    "Item": {
                        "id": "123",
                        "name": "test_item",
                    },
                    "ReturnConsumedCapacity": "INDEXES",
                },
            },
        }
    ]


def test_dynamodb_get_item(mock_logger: MockLogger) -> None:
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

    assert mock_logger.get_log("DDB_CORE_005", "DEBUG") == [
        {
            "reference": "DDB_CORE_005",
            "msg": "Getting item from DynamoDB table",
            "detail": {
                "request": {
                    "Key": {"id": "123"},
                    "ReturnConsumedCapacity": "INDEXES",
                },
                "table": "test_table",
            },
        }
    ]

    ddb_repo.table.get_item.assert_called_once_with(
        Key={"id": "123"}, ReturnConsumedCapacity="INDEXES"
    )

    assert mock_logger.get_log("DDB_CORE_006", "INFO") == [
        {
            "reference": "DDB_CORE_006",
            "msg": "Item retrieved from DynamoDB table",
            "detail": {
                "table": "test_table",
                "consumed_capacity": None,
            },
        }
    ]


def test_dynamodb_get_item_error(
    mock_logger: MockLogger,
) -> None:
    """
    Test that the _get_item method raises an error and logs details
    """

    class MockModel(BaseModel):
        id: str
        name: str

    ddb_repo = ExampleDDBRepository(table_name="test_table", model_cls=MockModel)

    # Mock the get_item method to raise an error
    ddb_repo.table.get_item = Mock(
        side_effect=ClientError(
            {
                "Error": {
                    "Code": "TestException",
                    "Message": "Test exception",
                },
            },
            operation_name="GetItem",
        )
    )

    with pytest.raises(ClientError):
        ddb_repo._get_item(Key={"id": "123"})

    assert mock_logger.was_logged("DDB_CORE_005", "DEBUG") is True
    assert mock_logger.was_logged("DDB_CORE_006", "INFO") is False
    assert mock_logger.get_log("DDB_CORE_007", "ERROR") == [
        {
            "reference": "DDB_CORE_007",
            "msg": "Error retrieving item from DynamoDB table",
            "detail": {
                "table": "test_table",
                "error": {
                    "Code": "TestException",
                    "Message": "Test exception",
                },
                "request": {
                    "Key": {"id": "123"},
                    "ReturnConsumedCapacity": "INDEXES",
                },
            },
        }
    ]


def test_dynamodb_get_item_no_result(
    mock_logger: MockLogger,
) -> None:
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

    assert mock_logger.was_logged("DDB_CORE_005", "DEBUG") is True
    assert mock_logger.was_logged("DDB_CORE_006", "INFO") is True
    assert mock_logger.was_logged("DDB_CORE_007", "ERROR") is False

    assert mock_logger.get_log("DDB_CORE_008", "WARNING") == [
        {
            "reference": "DDB_CORE_008",
            "msg": "Item not found in DynamoDB table",
            "detail": {
                "request": {
                    "Key": {"id": "123"},
                    "ReturnConsumedCapacity": "INDEXES",
                },
                "table": "test_table",
            },
        }
    ]


def test_dynamodb_query(
    mock_logger: MockLogger,
) -> None:
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

    assert mock_logger.get_log("DDB_CORE_009", "DEBUG") == [
        {
            "reference": "DDB_CORE_009",
            "msg": "Querying DynamoDB table",
            "detail": {
                "request": {
                    "KeyConditionExpression": "id = :id",
                    "ExpressionAttributeValues": {":id": "123"},
                    "ReturnConsumedCapacity": "INDEXES",
                },
                "table": "test_table",
            },
        }
    ]

    ddb_repo.table.query.assert_called_once_with(
        KeyConditionExpression="id = :id",
        ExpressionAttributeValues={":id": "123"},
        ReturnConsumedCapacity="INDEXES",
    )
    assert mock_logger.get_log("DDB_CORE_010", "INFO") == [
        {
            "reference": "DDB_CORE_010",
            "msg": "Completed query on DynamoDB table",
            "detail": {
                "table": "test_table",
                "item_count": expected_result_count,
                "consumed_capacity": None,
            },
        }
    ]


def test_dynamodb_query_error(
    mock_logger: MockLogger,
) -> None:
    """
    Test that the _query method raises an error and logs details
    """

    class MockModel(BaseModel):
        id: str
        name: str

    ddb_repo = ExampleDDBRepository(table_name="test_table", model_cls=MockModel)

    # Mock the query method to raise an error
    ddb_repo.table.query = Mock(
        side_effect=ClientError(
            {
                "Error": {
                    "Code": "TestException",
                    "Message": "Test exception",
                },
            },
            operation_name="Query",
        )
    )

    with pytest.raises(ClientError):
        ddb_repo._query(key="id", value="123")

    assert mock_logger.was_logged("DDB_CORE_009", "DEBUG") is True
    assert mock_logger.was_logged("DDB_CORE_010", "INFO") is False
    assert mock_logger.get_log("DDB_CORE_011", "ERROR") == [
        {
            "reference": "DDB_CORE_011",
            "msg": "Error querying DynamoDB table",
            "detail": {
                "table": "test_table",
                "error": {
                    "Code": "TestException",
                    "Message": "Test exception",
                },
                "request": {
                    "KeyConditionExpression": "id = :id",
                    "ExpressionAttributeValues": {":id": "123"},
                    "ReturnConsumedCapacity": "INDEXES",
                },
            },
        }
    ]


def test_dynamodb_batch_write(
    mock_logger: MockLogger,
) -> None:
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
    assert result is None

    ddb_repo.resource.batch_write_item.assert_called_once_with(
        RequestItems={
            "test_table": [
                {"PutRequest": {"Item": {"id": "123", "name": "test_item"}}},
                {"DeleteRequest": {"Key": {"id": "456"}}},
            ]
        },
        ReturnConsumedCapacity="INDEXES",
    )

    assert mock_logger.get_log("DDB_CORE_012", "DEBUG") == [
        {
            "reference": "DDB_CORE_012",
            "msg": "Perfoming batch write to DynamoDB",
            "detail": {
                "request": {
                    "RequestItems": {
                        "test_table": [
                            {
                                "PutRequest": {
                                    "Item": {"id": "123", "name": "test_item"}
                                }
                            },
                            {"DeleteRequest": {"Key": {"id": "456"}}},
                        ]
                    },
                    "ReturnConsumedCapacity": "INDEXES",
                },
                "table": "test_table",
            },
        }
    ]

    assert mock_logger.get_log("DDB_CORE_013", "INFO") == [
        {
            "reference": "DDB_CORE_013",
            "msg": "Completed batch write to DynamoDB",
            "detail": {
                "table": "test_table",
                "consumed_capacity": None,
            },
        }
    ]


def test_dynamodb_batch_write_error(
    mock_logger: MockLogger,
) -> None:
    """
    Test that the _batch_write method raises an error and logs details
    """

    class MockModel(BaseModel):
        id: str
        name: str

    ddb_repo = ExampleDDBRepository(table_name="test_table", model_cls=MockModel)

    # Mock the batch_write_item method to raise an error
    ddb_repo.resource.batch_write_item = Mock(
        side_effect=ClientError(
            {
                "Error": {
                    "Code": "TestException",
                    "Message": "Test exception",
                },
            },
            operation_name="BatchWriteItem",
        )
    )

    put_items = [{"id": "123", "name": "test_item"}]
    delete_items = [{"id": "456"}]

    with pytest.raises(ClientError):
        ddb_repo._batch_write(put_items=put_items, delete_items=delete_items)

    assert mock_logger.was_logged("DDB_CORE_012", "DEBUG") is True
    assert mock_logger.was_logged("DDB_CORE_013", "INFO") is False
    assert mock_logger.get_log("DDB_CORE_014", "ERROR") == [
        {
            "reference": "DDB_CORE_014",
            "msg": "Error performing batch write",
            "detail": {
                "table": "test_table",
                "error": {
                    "Code": "TestException",
                    "Message": "Test exception",
                },
                "request": {
                    "RequestItems": {
                        "test_table": [
                            {
                                "PutRequest": {
                                    "Item": {"id": "123", "name": "test_item"}
                                }
                            },
                            {"DeleteRequest": {"Key": {"id": "456"}}},
                        ]
                    },
                    "ReturnConsumedCapacity": "INDEXES",
                },
            },
        }
    ]


def test_dynamodb_batch_write_unprocessed_items(
    mock_logger: MockLogger,
) -> None:
    """
    Test that the _batch_write method handles unprocessed items correctly
    """

    class MockModel(BaseModel):
        id: str
        name: str

    ddb_repo = ExampleDDBRepository(table_name="test_table", model_cls=MockModel)

    # Mock the batch_write_item method to return unprocessed items
    ddb_repo.resource.batch_write_item = Mock(
        return_value={
            "UnprocessedItems": {
                "test_table": [
                    {"PutRequest": {"Item": {"id": "123", "name": "test_item"}}}
                ]
            }
        }
    )

    put_items = [{"id": "123", "name": "test_item"}]
    delete_items = [{"id": "456"}]

    with pytest.raises(RuntimeError):
        ddb_repo._batch_write(put_items=put_items, delete_items=delete_items)

    assert mock_logger.get_log("DDB_CORE_015", "ERROR") == [
        {
            "reference": "DDB_CORE_015",
            "msg": "Unprocessed items in batch write",
            "detail": {
                "table": "test_table",
                "request": {
                    "RequestItems": {
                        "test_table": [
                            {
                                "PutRequest": {
                                    "Item": {"id": "123", "name": "test_item"}
                                }
                            },
                            {"DeleteRequest": {"Key": {"id": "456"}}},
                        ]
                    },
                    "ReturnConsumedCapacity": "INDEXES",
                },
                "unprocessed_items": {
                    "test_table": [
                        {"PutRequest": {"Item": {"id": "123", "name": "test_item"}}}
                    ]
                },
            },
        }
    ]


def test_dynamodb_scan() -> None:
    """
    Test that the _scan method calls the DynamoDB resource
    with the correct parameters
    """

    class MockModel(BaseModel):
        id: str
        name: str

    ddb_repo = ExampleDDBRepository(table_name="test_table", model_cls=MockModel)

    # Mock the scan method
    ddb_repo.table.scan = Mock(
        return_value={
            "Items": [
                {"id": "123", "name": "test_item"},
                {"id": "456", "name": "another_item"},
            ]
        }
    )

    expected_result_count = 2
    result = list(ddb_repo._scan())

    assert len(result) == expected_result_count
    assert result[0] == {"id": "123", "name": "test_item"}
    assert result[1] == {"id": "456", "name": "another_item"}

    ddb_repo.table.scan.assert_called_once_with(
        Limit=1000, ReturnConsumedCapacity="INDEXES"
    )

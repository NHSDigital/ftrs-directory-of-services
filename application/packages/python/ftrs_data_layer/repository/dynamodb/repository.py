from typing import TYPE_CHECKING, Any
from uuid import UUID

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.type_defs import (
        PutItemInputTablePutItemTypeDef,
        ScanOutputTableTypeDef,
    )

from ftrs_data_layer.client import get_dynamodb_resource
from ftrs_data_layer.repository.base import BaseRepository, ModelType


class DynamoDBRepository(BaseRepository[ModelType]):
    """
    A class that represents a repository for DynamoDB.
    This class is agnostic of the methods of database storage.
    """

    def __init__(
        self,
        table_name: str,
        model_cls: ModelType = None,
        endpoint_url: str | None = None,
    ) -> None:
        super().__init__(model_cls)
        self.resource = get_dynamodb_resource(endpoint_url)
        self.table = self.resource.Table(table_name)

    def _serialise_item(self, item: ModelType) -> dict:
        """
        Prepare the item for DynamoDB.
        Can be extended to add custom index or serialisation logic by child classes.
        """
        return item.model_dump(mode="json")

    def _parse_item(self, item: dict) -> ModelType:
        """
        Prepare the item for DynamoDB.
        Can be extended to add custom index or serialisation logic by child classes.
        """
        return self.model_cls.model_validate(item)

    def _put_item(
        self, item: ModelType, **kwargs: dict
    ) -> PutItemInputTablePutItemTypeDef:
        """
        Puts an item into the DynamoDB table.
        """
        prepared_item = self._serialise_item(item)
        ddb_request = {
            "Item": prepared_item,
            "ReturnConsumedCapacity": "INDEXES",
            **kwargs,
        }

        return self.table.put_item(**ddb_request)

    def _get_item(self, **kwargs: dict) -> ModelType | None:
        """
        Gets an item from the DynamoDB table.
        """
        response = self.table.get_item(**kwargs, ReturnConsumedCapacity="INDEXES")
        item = response.get("Item")
        if item is None:
            return None

        return self._parse_item(item)

    def _query(self, key: str, value: str | UUID, **kwargs: dict) -> list[ModelType]:
        """
        Queries the DynamoDB table.
        """
        response = self.table.query(
            KeyConditionExpression=f"{key} = :{key}",
            ExpressionAttributeValues={f":{key}": str(value)},
            ReturnConsumedCapacity="INDEXES",
            **kwargs,
        )
        items = response.get("Items", [])
        return [self._parse_item(item) for item in items]

    def _batch_write(
        self,
        put_items: list[dict] | None = None,
        delete_items: list[dict] | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Performs a batch write operation on the DynamoDB table.
        """
        if not put_items:
            put_items = []

        if not delete_items:
            delete_items = []

        return self.resource.batch_write_item(
            RequestItems={
                self.table.name: [
                    *[{"PutRequest": {"Item": item}} for item in put_items],
                    *[{"DeleteRequest": {"Key": item}} for item in delete_items],
                ]
            },
            ReturnConsumedCapacity="INDEXES",
            **kwargs,
        )

    def _scan(self, **kwargs: dict) -> ScanOutputTableTypeDef:
        """
        Scans the DynamoDB table.
        """
        return self.table.scan(**kwargs, ReturnConsumedCapacity="INDEXES")

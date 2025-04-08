from typing import Any, Generator
from uuid import UUID

from botocore.exceptions import ClientError
from ftrs_common.logger import Logger
from ftrs_data_layer.client import get_dynamodb_resource
from ftrs_data_layer.logbase import DDBLogBase
from ftrs_data_layer.repository.base import BaseRepository, ModelType
from mypy_boto3_dynamodb.type_defs import PutItemInputTablePutItemTypeDef


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
        logger: Logger | None = None,
    ) -> None:
        super().__init__(model_cls, logger)
        self.resource = get_dynamodb_resource(endpoint_url)
        self.table = self.resource.Table(table_name)
        self.logger.log(
            DDBLogBase.DDB_CORE_001,
            table_name=table_name,
            endpoint_url=endpoint_url,
            repository_cls=self.__class__.__name__,
            model_cls=f"{model_cls.__module__}:{model_cls.__qualname__}",
        )

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
        self.logger.log(
            DDBLogBase.DDB_CORE_002, request=ddb_request, table=self.table.name
        )

        try:
            result = self.table.put_item(**ddb_request)
            self.logger.log(
                DDBLogBase.DDB_CORE_003,
                table=self.table.name,
                consumed_capacity=result.get("ConsumedCapacity"),
            )

        except ClientError as client_error:
            self.logger.log(
                DDBLogBase.DDB_CORE_004,
                table=self.table.name,
                error=client_error.response["Error"],
                request=ddb_request,
            )
            raise

        return result

    def _get_item(self, **kwargs: dict) -> ModelType | None:
        """
        Gets an item from the DynamoDB table.
        """
        ddb_request = {**kwargs, "ReturnConsumedCapacity": "INDEXES"}
        self.logger.log(
            DDBLogBase.DDB_CORE_005, request=ddb_request, table=self.table.name
        )

        try:
            response = self.table.get_item(**ddb_request)
            self.logger.log(
                DDBLogBase.DDB_CORE_006,
                table=self.table.name,
                consumed_capacity=response.get("ConsumedCapacity"),
            )

        except ClientError as client_error:
            self.logger.log(
                DDBLogBase.DDB_CORE_007,
                table=self.table.name,
                error=client_error.response["Error"],
                request=ddb_request,
            )
            raise

        item = response.get("Item")
        if item is None:
            self.logger.log(
                DDBLogBase.DDB_CORE_008,
                table=self.table.name,
                request=ddb_request,
            )
            return None

        return self._parse_item(item)

    def _query(self, key: str, value: str | UUID, **kwargs: dict) -> list[ModelType]:
        """
        Queries the DynamoDB table.
        """
        ddb_request = {
            "KeyConditionExpression": f"{key} = :{key}",
            "ExpressionAttributeValues": {f":{key}": str(value)},
            "ReturnConsumedCapacity": "INDEXES",
            **kwargs,
        }
        self.logger.log(
            DDBLogBase.DDB_CORE_009, request=ddb_request, table=self.table.name
        )
        try:
            response = self.table.query(**ddb_request)
            items = response.get("Items", [])

            self.logger.log(
                DDBLogBase.DDB_CORE_010,
                item_count=len(items),
                table=self.table.name,
                consumed_capacity=response.get("ConsumedCapacity"),
            )

        except ClientError as client_error:
            self.logger.log(
                DDBLogBase.DDB_CORE_011,
                table=self.table.name,
                error=client_error.response["Error"],
                request=ddb_request,
            )
            raise

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

        ddb_request = {
            "RequestItems": {
                self.table.name: [
                    *[{"PutRequest": {"Item": item}} for item in put_items],
                    *[{"DeleteRequest": {"Key": item}} for item in delete_items],
                ]
            },
            "ReturnConsumedCapacity": "INDEXES",
            **kwargs,
        }

        self.logger.log(
            DDBLogBase.DDB_CORE_012,
            request=ddb_request,
            table=self.table.name,
        )

        try:
            response = self.resource.batch_write_item(**ddb_request)
            self.logger.log(
                DDBLogBase.DDB_CORE_013,
                table=self.table.name,
                consumed_capacity=response.get("ConsumedCapacity"),
            )

        except ClientError as client_error:
            self.logger.log(
                DDBLogBase.DDB_CORE_014,
                table=self.table.name,
                error=client_error.response["Error"],
                request=ddb_request,
            )
            raise

        unprocessed_items = response.get("UnprocessedItems")
        if unprocessed_items:
            self.logger.log(
                DDBLogBase.DDB_CORE_015,
                table=self.table.name,
                request=ddb_request,
                unprocessed_items=unprocessed_items,
            )
            error_msg = f"Unprocessed items in batch write: {unprocessed_items}"
            raise RuntimeError(error_msg)

    def _scan(self, **kwargs: dict) -> Generator[dict, None, None]:
        """
        Scans the DynamoDB table.
        """
        limit = min(kwargs.pop("Limit", None) or 1000, 1000)
        response = self.table.scan(
            ReturnConsumedCapacity="INDEXES",
            Limit=limit,
            **kwargs,
        )

        while True:
            for record in response.get("Items", []):
                yield record

            if "LastEvaluatedKey" not in response:
                break

            response = self.table.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"],
                Limit=limit,
                ReturnConsumedCapacity="INDEXES",
                **kwargs,
            )

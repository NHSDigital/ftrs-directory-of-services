from typing import Generator
from uuid import UUID

from boto3.dynamodb.conditions import Attr

from ftrs_data_layer.repository.dynamodb.repository import (
    DynamoDBRepository,
    ModelType,
)


class FieldLevelRepository(DynamoDBRepository[ModelType]):
    def create(self, obj: ModelType) -> None:
        """
        Create a new document in DynamoDB.
        """
        self._batch_write(put_items=self._serialise_item(obj))

    def get(self, obj_id: str | UUID) -> ModelType | None:
        """
        Get a document from DynamoDB by ID.
        """
        response = self.table.query(
            KeyConditionExpression="id = :id",
            ExpressionAttributeValues={":id": str(obj_id)},
            ReturnConsumedCapacity="INDEXES",
        )
        items = response.get("Items")
        if not items:
            return None

        return self._parse_item(items)

    def update(self, obj_id: str | UUID, obj: ModelType) -> None:
        """
        Update an existing document in DynamoDB.
        """
        self._batch_write(put_items=self._serialise_item(obj))

    def delete(self, id: str | UUID) -> None:
        """
        Delete a document from DynamoDB by ID.
        """
        response = self.table.query(
            KeyConditionExpression="id = :id",
            ExpressionAttributeValues={":id": str(id)},
            ReturnConsumedCapacity="INDEXES",
        )
        items = response.get("Items")
        if not items:
            error_msg = f"No items found to delete for id: {id}"
            raise ValueError(error_msg)

        self._batch_write(
            delete_items=[{"id": item["id"], "field": item["field"]} for item in items]
        )

    def _serialise_item(self, item: ModelType) -> list[dict]:
        """
        Prepare the item for DynamoDB in a field-level format.
        """
        item_dict = item.model_dump(mode="json")
        item_id = item_dict.pop("id")

        return [
            {"id": str(item_id), "field": field, "value": value}
            for field, value in item_dict.items()
            if value is not None
        ]

    def _parse_item(self, item: list[dict]) -> ModelType:
        """
        Parse the field-level items from DynamoDB into the model format.
        """
        item_dict = {
            "id": item[0]["id"],
            **{item["field"]: item["value"] for item in item},
        }
        return self.model_cls.model_validate(item_dict)

    def _iter_record_ids(
        self, max_results: int | None = 100
    ) -> Generator[tuple[str, str], None, None]:
        """
        Iterate over the record IDs in the DynamoDB table.
        Generates tuples of (id, field).
        """
        count = 0
        response = self._scan(
            ProjectionExpression="id, field",
            FilterExpression=Attr("field").eq("createdDateTime"),
            Limit=max_results or 100,
        )

        for record in response.get("Items", []):
            yield record["id"], record["field"]
            count += 1

            if max_results is not None and count >= max_results:
                return

        while "LastEvaluatedKey" in response:
            response = self._scan(
                ExclusiveStartKey=response["LastEvaluatedKey"],
                ProjectionExpression="id, field",
                FilterExpression=Attr("field").eq("createdDateTime"),
                Limit=max_results or 100,
            )
            for record in response.get("Items", []):
                yield record["id"], record["field"]
                count += 1

                if max_results is not None and count >= max_results:
                    return

    def iter_records(
        self, max_results: int | None = 100
    ) -> Generator[ModelType, None, None]:
        """
        Iterate over the records in the DynamoDB table.
        """
        for record_id, _ in self._iter_record_ids(max_results):
            yield self.get(record_id)

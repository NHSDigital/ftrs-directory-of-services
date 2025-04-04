from uuid import UUID

from ftrs_data_layer.repository.dynamodb.repository import (
    DynamoDBRepository,
    ModelType,
)


class FieldLevelRepository(DynamoDBRepository[ModelType]):
    def create(self, obj: ModelType) -> None:
        self._batch_write(put_items=self._serialise_item(obj))

    def get(self, obj_id: str | UUID) -> ModelType | None:
        """
        Get a document from DynamoDB by ID.
        """
        response = self.table.query(
            KeyConditionExpression="id = :id",
            ExpressionAttributeValues={":id": str(obj_id)},
            ProjectionExpression="id, field, value",
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
            ProjectionExpression="id, field, value",
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
        Prepare the item for DynamoDB.
        Can be extended to add custom index or serialisation logic by child classes.
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
        Prepare the item for DynamoDB.
        Can be extended to add custom index or serialisation logic by child classes.
        """
        item_dict = {
            "id": item[0]["id"],
            **{item["field"]: item["value"] for item in item},
        }
        return self.model_cls.model_validate(item_dict)

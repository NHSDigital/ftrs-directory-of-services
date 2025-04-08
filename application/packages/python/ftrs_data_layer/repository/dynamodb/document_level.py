from ftrs_data_layer.repository.dynamodb.repository import (
    DynamoDBRepository,
    ModelType,
)


class DocumentLevelRepository(DynamoDBRepository[ModelType]):
    """
    DocumentLevelRepository is a class that provides methods for creating, reading,
    updating, and deleting documents in DynamoDB.
    """

    def create(self, obj: ModelType) -> None:
        """
        Create a new document in DynamoDB.
        """
        self._put_item(
            obj,
            ConditionExpression="attribute_not_exists(id)",
        )

    def get(self, id: str) -> ModelType | None:
        """
        Get a document from DynamoDB by ID.
        """
        response = self.table.get_item(
            Key={"id": id},
            ProjectionExpression="id, value",
            ReturnConsumedCapacity="INDEXES",
        )
        item = response.get("Item")
        if item is None:
            return None

        return self._parse_item(item)

    def update(self, id: str, obj: ModelType) -> None:
        """
        Update an existing document in DynamoDB.
        """
        self._put_item(
            obj,
            ConditionExpression="attribute_exists(id)",
        )

    def delete(self, id: str) -> None:
        """
        Delete a document from DynamoDB by ID.
        """
        self.table.delete_item(
            Key={"id": id},
            ConditionExpression="attribute_exists(id)",
        )

    def _serialise_item(self, item: ModelType) -> dict:
        """
        Prepare the item for DynamoDB in a document-level format.
        """
        return {
            "id": str(item.id),
            "value": item.model_dump(mode="json"),
        }

    def _parse_item(self, item: dict) -> ModelType:
        """
        Parse the item from DynamoDB into the model format.
        """
        return self.model_cls.model_validate(
            {
                "id": item["id"],
                **item["value"],
            }
        )

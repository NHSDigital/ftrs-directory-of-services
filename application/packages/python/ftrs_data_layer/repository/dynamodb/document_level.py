from itertools import islice
from typing import Generator
from uuid import UUID

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

    def get(self, id: str | UUID) -> ModelType | None:
        """
        Get a document from DynamoDB by ID.
        """
        response = self.table.get_item(Key={"id": str(id), "field": "document"})
        item = response.get("Item")
        if item is None:
            return None

        return self._parse_item(item)

    def update(self, id: str | UUID, obj: ModelType) -> None:
        """
        Update an existing document in DynamoDB.
        """
        self._put_item(
            obj,
            ConditionExpression="attribute_exists(id)",
        )

    def delete(self, id: str | UUID) -> None:
        """
        Delete a document from DynamoDB by ID.
        """
        self.table.delete_item(
            Key={"id": str(id), "field": "document"},
            ConditionExpression="attribute_exists(id)",
        )

    def _serialise_item(self, item: ModelType) -> dict:
        base_item = {
            "id": str(item.id),
            "field": "document",  # Required a sort key
        }
        # Add model attributes
        model_data = item.model_dump(mode="json")
        base_item.update(model_data)
        base_item.update(item.indexes)
        return base_item

    def _parse_item(self, item: dict) -> ModelType:
        """
        Parse the item from DynamoDB into the model format.
        """
        parsed_item = item.copy()
        return self.model_cls.model_construct(**parsed_item)

    def iter_records(
        self, max_results: int | None = 100
    ) -> Generator[ModelType, None, None]:
        """
        Iterate across all items in the table.
        """
        return islice(
            map(self._parse_item, self._scan(Limit=max_results)),
            max_results,
        )

    def get_by_ods_code(self, ods_code: str) -> list[str]:
        ods_code_field = "identifier_ODS_ODSCode"
        records = self._query(
            key=ods_code_field,
            value=ods_code,
            IndexName="OdsCodeValueIndex",
        )
        return [record.id for record in records]

from itertools import islice
from typing import Generator
from uuid import UUID

from ftrs_data_layer.repository.dynamodb.repository import (
    DynamoDBRepository,
    ModelType,
)


class AttributeLevelRepository(DynamoDBRepository[ModelType]):
    """
    AttributeLevelRepository is a class that provides methods for creating, reading,
    updating, and deleting documents in DynamoDB.
    """

    def create(self, obj: ModelType) -> None:
        """
        Create a new item in DynamoDB.
        """
        self._put_item(
            obj,
            ConditionExpression="attribute_not_exists(id)",
        )

    def get(self, id: str | UUID) -> ModelType | None:
        """
        Get an item from DynamoDB by ID.
        """
        response = self.table.get_item(
            Key={"id": str(id), "field": "document"}, ReturnConsumedCapacity="INDEXES"
        )
        item = response.get("Item")
        if item is None:
            return None

        return self._parse_item(item)

    def upsert(self, obj: ModelType) -> None:
        """
        Upsert an item in DynamoDB.
        If the item exists, it will be updated; if not, it will be created.
        """
        self._put_item(obj)

    def update(self, id: str | UUID, obj: ModelType) -> None:
        """
        Update an existing item in DynamoDB.
        """
        self._put_item(
            obj,
            ConditionExpression="attribute_exists(id)",
        )

    def delete(self, id: str | UUID) -> None:
        """
        Delete an item from DynamoDB by ID.
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
        return base_item

    def _parse_item(self, item: dict) -> ModelType:
        """
        Parse the item from DynamoDB into the model format.
        """
        parsed_item = item.copy()
        return self.model_cls.model_validate(parsed_item)

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
        return self._get_records_by_ods_code(ods_code)

    def get_first_record_by_ods_code(self, ods_code: str) -> ModelType | None:
        records = self._get_records_by_ods_code(ods_code)
        return records[0] if records else None

    def _get_records_by_ods_code(self, ods_code: str) -> list[ModelType]:
        ods_code_field = "identifier_ODS_ODSCode"
        records: list[ModelType] = self._query(
            key=ods_code_field,
            value=ods_code,
            IndexName="OdsCodeValueIndex",
        )

        return list(records)

"""DynamoDB implementation."""

import json
import logging
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)


class DynamoRepository:
    def __init__(self, table_name: str) -> None:
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def get_first_record_by_ods_code(self, ods_code: str) -> dict[str, Any] | None:
        """Retrieve an organization by its ODS code.

        Args:
            ods_code: The ODS code to look up

        Returns:
            The organization raw_data or None if not found

        """
        items = self.get_records_by_ods_code(ods_code)
        if items and len(items) > 0:
            item = items[0]

            logger.info(f"Retrieved record: {json.dumps(item, indent=2, default=str)}")

            return item
        return None

    def get_records_by_ods_code(self, ods_code: str) -> list[dict[str, Any]]:
        """Retrieve all organizations matching an ODS code.

        Args:
            ods_code: The ODS code to look up

        Returns:
            List of organization raw_data matching the ODS code

        """
        response = self.table.query(
            IndexName="ods-code-index",
            KeyConditionExpression=Key("ods-code").eq(ods_code),
        )
        return response.get("Items", [])

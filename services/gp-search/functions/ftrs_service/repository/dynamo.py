import json
from datetime import datetime
from typing import Any, Dict, Optional

import boto3
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticUseDefault

logger = Logger()


class DynamoModel(BaseModel):
    @field_validator("*", mode="before")
    def none_to_default(cls, v: object) -> object:
        """Converts None values (when Dynamo returns null values) to default values for Pydantic models."""
        if v is None:
            raise PydanticUseDefault()
        return v


class EndpointValue(DynamoModel):
    """Represents an endpoint associated with an organization."""

    id: str = Field()
    identifier_oldDoS_id: int = Field()
    address: str = Field()
    format: str = Field()
    description: str = Field()
    isCompressionEnabled: bool = Field()
    connectionType: str = Field()
    payloadType: str = Field()
    managedByOrganisation: str = Field()
    status: str = Field()
    order: int = Field()
    createdBy: str = Field()
    modifiedBy: str = Field()
    createdDateTime: datetime = Field()
    modifiedDateTime: datetime = Field()
    service: str = Field("dummy-service")
    name: str = Field("dummy-name")

    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
    )


class OrganizationValue(DynamoModel):
    """Represents the 'value' field of an organization record."""

    id: str = Field()
    name: str = Field()
    type: str = Field()
    active: bool = Field()
    endpoints: list[EndpointValue] = Field(default_factory=list)
    identifier_ODS_ODSCode: str = Field()
    createdBy: str = Field()
    modifiedBy: str = Field()
    createdDateTime: datetime = Field()
    modifiedDateTime: datetime = Field()
    telecom: str = Field("dummy-telecom")

    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
    )


class OrganizationRecord(DynamoModel):
    """Represents a complete organization record from DynamoDB."""

    id: str = Field()
    ods_code: str = Field(alias="ods-code")
    value: OrganizationValue = Field()
    field: str = Field()

    model_config = ConfigDict(
        populate_by_name=True,
        validate_by_name=True,
        frozen=True,
    )

    @classmethod
    def from_dynamo_item(cls, item: Dict[str, Any]) -> "OrganizationRecord":
        """Create an OrganizationRecord model from a DynamoDB item."""
        try:
            return cls.model_validate(item)
        except Exception:
            logger.exception(
                f"Error validating DynamoDB item. "
                f"Problem item: {json.dumps(item, indent=2, default=str)}"
            )
            raise


class DynamoRepository:
    def __init__(self, table_name: str) -> None:
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def get_first_record_by_ods_code(
        self, ods_code: str
    ) -> Optional[OrganizationRecord]:
        response = self.table.query(
            IndexName="ods-code-index",
            KeyConditionExpression=Key("ods-code").eq(ods_code),
        )

        items = response.get("Items", [])

        if items and len(items) > 0:
            if len(items) > 1:
                logger.warning(
                    f"Multiple records found for ODS code {ods_code}: {len(items)}."
                    f" Retrieving the first record."
                )

            item = items[0]
            logger.info(f"Retrieved record: {json.dumps(item, indent=2, default=str)}")
            return OrganizationRecord.from_dynamo_item(item)

        return None

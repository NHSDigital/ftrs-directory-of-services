from datetime import datetime, timezone
from typing import Self

from boto3.dynamodb.types import TypeSerializer
from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import get_table_name
from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from ftrs_data_layer.domain.auditevent import AuditEvent, AuditEventType
from ftrs_data_layer.logbase import DataMigrationLogBase
from pydantic import BaseModel

from common.diff_utils import (
    DynamoDBUpdateExpressions,
    deepdiff_to_dynamodb_expressions,
    get_healthcare_service_diff,
    get_location_diff,
    get_organisation_diff,
)
from service_migration.exceptions import ServiceMigrationException
from service_migration.models import ServiceMigrationState


class ServiceTransactionBuilder:
    """
    Build DynamoDB TransactWriteItems as required to insert/update/delete items in DynamoDB.

    This class constructs transactional write operations for migrating healthcare
    data (organisations, locations, and healthcare services) to DynamoDB tables.
    It tracks migration state to enable incremental updates and ensure data consistency.

    Attributes:
        migration_state: The current state of the migration for the given record.
        migration_state_table_name: The name of the DynamoDB table storing migration state.
        record_id: The source record identifier being migrated.
        serialiser: DynamoDB type serialiser for converting Python types.
        items: List of transaction items to be written.
    """

    def __init__(
        self,
        service_id: int,
        logger: Logger,
        migration_state: ServiceMigrationState | None = None,
        validation_issues: list = [],
    ) -> None:
        """
        Initialise the TransactionBuilder.

        Args:
            config: Configuration object containing environment and workspace settings.
            record_id: The source record identifier being migrated.
            migration_state: Optional existing migration state. If None, a new state
                is created for the given record_id.
        """
        self.migration_state = (
            migration_state.model_copy()
            if migration_state
            else ServiceMigrationState.init(
                service_id=service_id,
                validation_issues=validation_issues,
            )
        )
        self.logger = logger
        self.service_id = service_id
        self.serialiser = TypeSerializer()
        self.items = []
        self.current_time = datetime.now(timezone.utc)

    def add_organisation(self, organisation: Organisation | None) -> Self:
        """
        Add an organisation write to the transaction
        """
        if self.migration_state.organisation:
            return self._update_organisation(organisation)

        return self._insert_organisation(organisation)

    def add_location(self, location: Location | None) -> Self:
        """
        Add a location write to the transaction
        """
        if self.migration_state.location:
            return self._update_location(location)

        return self._insert_location(location)

    def add_healthcare_service(
        self,
        healthcare_service: HealthcareService | None,
    ) -> Self:
        """
        Add a healthcare service write to the transaction
        """
        if self.migration_state.healthcare_service and healthcare_service is None:
            raise ServiceMigrationException(
                "HealthcareService deletion not supported in data migration",
                requeue=False,
            )

        if healthcare_service is None:
            return self

        if not self.migration_state.healthcare_service:
            return self._insert_healthcare_service(healthcare_service)

        return self._update_healthcare_service(healthcare_service)

    def _insert_organisation(self, organisation: Organisation | None) -> Self:
        """Insert a new organisation into DynamoDB.

        Args:
            organisation: The organisation entity to insert.

        Returns:
            Self for method chaining.
        """
        if organisation is None:
            self.logger.log(DataMigrationLogBase.DM_ETL_023)
            return self

        self.items.append(
            {
                "Put": {
                    "TableName": get_table_name("organisation"),
                    "Item": self._serialise_item(organisation, field="document"),
                    "ConditionExpression": "attribute_not_exists(id) AND attribute_not_exists(#field)",
                    "ExpressionAttributeNames": {"#field": "field"},
                }
            }
        )
        self.migration_state.organisation_id = organisation.id
        self.migration_state.organisation = organisation

        self.logger.log(
            DataMigrationLogBase.DM_ETL_024,
            organisation_id=organisation.id,
        )
        return self

    def _update_organisation(self, organisation: Organisation | None) -> Self:
        """Update an existing organisation in DynamoDB.

        Compares the current organisation with the previous state and applies
        only the changed fields.

        Args:
            organisation: The updated organisation entity.

        Returns:
            Self for method chaining.
        """
        if organisation is None:
            raise ServiceMigrationException(
                "Organisation deletion not currently supported in service migration",
                requeue=False,
            )

        diff = get_organisation_diff(
            previous=self.migration_state.organisation,
            current=organisation,
        )
        if not diff:
            self.logger.log(DataMigrationLogBase.DM_ETL_029)
            return self

        self.logger.log(
            DataMigrationLogBase.DM_ETL_030,
            changes=diff.pretty().splitlines(),
            diff=diff.to_dict(view_override="text"),
        )

        expressions = deepdiff_to_dynamodb_expressions(diff)
        if expressions.is_empty():
            return self

        update_item = self._build_update_item(
            item_id=str(organisation.id),
            table_name="organisation",
            expressions=expressions,
        )

        self.items.append({"Update": update_item})
        self.migration_state.organisation = organisation

        return self

    def _insert_location(self, location: Location | None) -> Self:
        """Insert a new location into DynamoDB.

        Args:
            location: The location entity to insert.

        Returns:
            Self for method chaining.
        """
        if location is None:
            self.logger.log(DataMigrationLogBase.DM_ETL_025)
            return self

        self.items.append(
            {
                "Put": {
                    "TableName": get_table_name("location"),
                    "Item": self._serialise_item(location, field="document"),
                    "ConditionExpression": "attribute_not_exists(id) AND attribute_not_exists(#field)",
                    "ExpressionAttributeNames": {"#field": "field"},
                }
            }
        )
        self.migration_state.location_id = location.id
        self.migration_state.location = location

        self.logger.log(
            DataMigrationLogBase.DM_ETL_026,
            location_id=location.id,
        )
        return self

    def _update_location(self, location: Location | None) -> Self:
        """Update an existing location in DynamoDB.

        Compares the current location with the previous state and applies
        only the changed fields.

        Args:
            location: The updated location entity.

        Returns:
            Self for method chaining.
        """
        if location is None:
            raise ServiceMigrationException(
                "Location deletion not currently supported in service migration",
                requeue=False,
            )

        diff = get_location_diff(
            previous=self.migration_state.location,
            current=location,
        )
        if not diff:
            self.logger.log(DataMigrationLogBase.DM_ETL_031)
            return self

        self.logger.log(
            DataMigrationLogBase.DM_ETL_032,
            changes=diff.pretty().splitlines(),
            diff=diff.to_dict(view_override="text"),
        )

        expressions = deepdiff_to_dynamodb_expressions(diff)
        if expressions.is_empty():
            return self

        update_item = self._build_update_item(
            item_id=str(location.id),
            table_name="location",
            expressions=expressions,
        )
        self.items.append({"Update": update_item})
        self.migration_state.location = location

        return self

    def _insert_healthcare_service(
        self, healthcare_service: HealthcareService | None
    ) -> Self:
        """Insert a new healthcare service into DynamoDB.

        Args:
            healthcare_service: The healthcare service entity to insert.

        Returns:
            Self for method chaining.
        """
        if healthcare_service is None:
            self.logger.log(DataMigrationLogBase.DM_ETL_027)
            return self

        self.items.append(
            {
                "Put": {
                    "TableName": get_table_name("healthcare-service"),
                    "Item": self._serialise_item(healthcare_service, field="document"),
                    "ConditionExpression": "attribute_not_exists(id) AND attribute_not_exists(#field)",
                    "ExpressionAttributeNames": {"#field": "field"},
                }
            }
        )
        self.migration_state.healthcare_service_id = healthcare_service.id
        self.migration_state.healthcare_service = healthcare_service

        self.logger.log(
            DataMigrationLogBase.DM_ETL_028,
            healthcare_service_id=healthcare_service.id,
        )
        return self

    def _update_healthcare_service(
        self, healthcare_service: HealthcareService | None
    ) -> Self:
        """Update an existing healthcare service in DynamoDB.

        Compares the current healthcare service with the previous state and applies
        only the changed fields.

        Args:
            healthcare_service: The updated healthcare service entity.

        Returns:
            Self for method chaining.
        """
        if healthcare_service is None:
            raise ServiceMigrationException(
                "HealthcareService deletion not currently supported in service migration",
                requeue=False,
            )

        diff = get_healthcare_service_diff(
            previous=self.migration_state.healthcare_service,
            current=healthcare_service,
        )
        if not diff:
            self.logger.log(DataMigrationLogBase.DM_ETL_033)
            return self

        self.logger.log(
            DataMigrationLogBase.DM_ETL_034,
            changes=diff.pretty().splitlines(),
            diff=diff.to_dict(view_override="text"),
        )

        expressions = deepdiff_to_dynamodb_expressions(diff)
        if expressions.is_empty():
            return self

        update_item = self._build_update_item(
            item_id=str(healthcare_service.id),
            table_name="healthcare-service",
            expressions=expressions,
        )
        self.items.append({"Update": update_item})
        self.migration_state.healthcare_service = healthcare_service

        return self

    def _serialise_item(self, item: BaseModel, **additional_fields: dict) -> dict:
        """Serialise a Pydantic model to DynamoDB format.

        Args:
            item: The Pydantic model to serialise.
            **additional_fields: Extra fields to include in the serialised output.

        Returns:
            A dictionary in DynamoDB AttributeValue format.
        """
        item_dict = item.model_dump(mode="json")
        item_dict.update(additional_fields)
        return self.serialiser.serialize(item_dict)["M"]

    def build(self) -> list[dict]:
        """Build and return the complete list of transaction items.

        Finalises the transaction by adding the migration state record
        (insert or update) to track the migration progress.

        Returns:
            A list of DynamoDB TransactWriteItem dictionaries ready for
            submission to DynamoDB transact_write_items.
        """
        if not self.items:
            self.logger.log(DataMigrationLogBase.DM_ETL_037)
            return []

        if self.migration_state.version == 0:
            self._insert_state_record()
        else:
            self._update_state_record()

        return self.items

    def _insert_state_record(self) -> Self:
        """Insert a new migration state record into DynamoDB.

        Creates the initial state record with version 1 for tracking
        the migration progress of a source record.

        Returns:
            Self for method chaining.
        """
        self.migration_state.version = 1
        self.items.append(
            {
                "Put": {
                    "TableName": get_table_name("data-migration-state"),
                    "Item": self._serialise_item(self.migration_state),
                    "ConditionExpression": "attribute_not_exists(source_record_id)",
                }
            }
        )
        self.logger.log(
            DataMigrationLogBase.DM_ETL_035,
            source_record_id=self.migration_state.source_record_id,
            version=self.migration_state.version,
        )

        return self

    def _update_state_record(self) -> Self:
        """Update an existing migration state record in DynamoDB.

        Increments the version number and uses optimistic locking to ensure
        concurrent updates don't overwrite each other.

        Returns:
            Self for method chaining.
        """
        self.migration_state.version += 1
        self.items.append(
            {
                "Put": {
                    "TableName": get_table_name("data-migration-state"),
                    "Item": self._serialise_item(self.migration_state),
                    "ConditionExpression": "attribute_exists(source_record_id) AND version = :current_version",
                    "ExpressionAttributeValues": {
                        ":current_version": {"N": str(self.migration_state.version - 1)}
                    },
                }
            }
        )

        self.logger.log(
            DataMigrationLogBase.DM_ETL_036,
            source_record_id=self.migration_state.source_record_id,
            new_version=self.migration_state.version,
        )
        return self

    def _build_update_item(
        self,
        item_id: str,
        table_name: str,
        expressions: DynamoDBUpdateExpressions,
    ) -> dict:
        """Build a DynamoDB update item for a transaction.

        Args:
            item_id: The unique identifier of the item to update.
            table_name: The name of the DynamoDB table.
            expressions: The DynamoDB update expressions.
        """
        # Add audit timestamps to all UPDATE operations
        expressions.add_audit_timestamps(
            timestamp=self.current_time.isoformat(),
            updated_by=AuditEvent(
                type=AuditEventType.app, value="INTERNAL001", display="Data Migration"
            ),
            serializer=self.serialiser,
        )

        update_item: dict = {
            "TableName": get_table_name(table_name),
            "Key": {
                "id": {"S": item_id},
                "field": {"S": "document"},
            },
            "UpdateExpression": expressions.update_expression,
            "ExpressionAttributeNames": expressions.expression_attribute_names,
        }

        # Only include ExpressionAttributeValues if non-empty (REMOVE-only updates have no values)
        if expression_values := expressions.get_expression_attribute_values_or_none():
            update_item["ExpressionAttributeValues"] = expression_values

        return update_item

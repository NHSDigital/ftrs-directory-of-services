from time import perf_counter
from typing import Any, Iterable
from uuid import uuid4

from boto3.dynamodb.types import TypeSerializer
from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import format_table_name
from ftrs_data_layer.client import get_dynamodb_client
from ftrs_data_layer.domain import legacy
from ftrs_data_layer.domain.data_migration_state import DataMigrationState
from ftrs_data_layer.logbase import DataMigrationLogBase
from pydantic import BaseModel
from sqlalchemy import Engine
from sqlmodel import Session, create_engine, select

from common.cache import DoSMetadataCache
from service_migration.config import DataMigrationConfig
from service_migration.transformer import (
    SUPPORTED_TRANSFORMERS,
    ServiceTransformer,
    ServiceTransformOutput,
)
from service_migration.validation.types import ValidationIssue


class DataMigrationMetrics(BaseModel):
    total_records: int = 0
    supported_records: int = 0
    unsupported_records: int = 0
    transformed_records: int = 0
    migrated_records: int = 0
    skipped_records: int = 0
    invalid_records: int = 0
    errors: int = 0

    def reset(self) -> None:
        """
        Reset all metrics to zero.
        """
        self.total_records = 0
        self.supported_records = 0
        self.unsupported_records = 0
        self.transformed_records = 0
        self.migrated_records = 0
        self.skipped_records = 0
        self.invalid_records = 0
        self.errors = 0


class DataMigrationProcessor:
    """
    This class is responsible for managing the data migration process.
    It includes methods to transform legacy service data into the new format.
    """

    serializer: TypeSerializer = TypeSerializer()

    def __init__(
        self,
        config: DataMigrationConfig,
        logger: Logger,
    ) -> None:
        self.logger = logger
        self.config = config
        self.engine = self.create_db_engine()
        self.metrics = DataMigrationMetrics()
        self.metadata = DoSMetadataCache(self.engine)

    def sync_all_services(self) -> None:
        """
        Run the full sync process.
        """
        for record in self._iter_records():
            self._process_service(record)

    def sync_service(self, record_id: int, method: str) -> None:
        """
        Run the single record sync process.
        """
        with Session(self.engine) as session:
            record = session.get(legacy.Service, record_id)
            if not record:
                raise ValueError(f"Service with ID {record_id} not found")

            service = legacy.Service(
                **record.model_dump(mode="python", warnings=False),
                endpoints=list(record.endpoints),
                scheduled_opening_times=list(record.scheduled_opening_times),
                specified_opening_times=list(record.specified_opening_times),
                sgsds=list(record.sgsds),
                dispositions=list(record.dispositions),
                age_range=list(record.age_range),
            )
            self._process_service(service)

    def _process_service(self, service: legacy.Service) -> None:
        """
        Process a single record by transforming it using the appropriate transformer.

        TODO: FTRS-1595 Process a single service through the migration pipeline.

        TODO: FTRS-1595 Pipeline workflow steps
        1. Extract service from source database
        2. Validate the service can be migrated
        3. Transform to future data model
        4. Lookup existing state (step 5 - determines insert vs update)
        5. Compare and determine what needs updating (future implementation)
        6. Save to future system tables

        TODO: Current behavior per acceptance criteria
        - When state record NOT found (key "services#{service_id}" doesn't exist):
        * Treat as 'insert' operation
        * Save records directly to DynamoDB tables
        * No state record is created at this stage

        - When state record EXISTS (key "services#{service_id}" found):
        * Treat as 'update' operation
        * Exit early with log message
        * Update logic not yet implemented

        TODO: FTRS-1595 Future implementation for update operations
        - Compare transformed data with last known state from state table
        - Identify what has changed between current and previous migration
        - Perform targeted updates only on changed data
        - Use optimistic locking via version numbers to prevent conflicts
        - Handle concurrent updates by failing and requeuing subsequent updates
        """

        self.logger.append_keys(record_id=service.id)
        self.logger.log(
            DataMigrationLogBase.DM_ETL_001,
            record=service.model_dump(exclude_none=True, mode="json", warnings=False),
        )

        try:
            start_time = perf_counter()
            self.metrics.total_records += 1

            transformer = self.get_transformer(service)
            if not transformer:
                self.metrics.unsupported_records += 1
                self.logger.log(
                    DataMigrationLogBase.DM_ETL_004,
                    reason="No suitable transformer found",
                )
                return

            self.metrics.supported_records += 1
            should_include, reason = transformer.should_include_service(service)
            if not should_include:
                self.metrics.skipped_records += 1
                self.logger.log(DataMigrationLogBase.DM_ETL_005, reason=reason)
                return

            validation_result = transformer.validator.validate(service)
            if not validation_result.is_valid:
                issues = [
                    issue.model_dump(mode="json") for issue in validation_result.issues
                ]
                self.logger.log(
                    DataMigrationLogBase.DM_ETL_013,
                    record_id=service.id,
                    issue_count=len(issues),
                    issues=issues,
                )

            if not validation_result.should_continue:
                self.metrics.invalid_records += 1
                self.logger.log(
                    DataMigrationLogBase.DM_ETL_014,
                    record_id=service.id,
                )
                return

            issues = self._convert_validation_issues(validation_result.issues)
            result = transformer.transform(validation_result.sanitised, issues)
            self.metrics.transformed_records += 1

            self.logger.log(
                DataMigrationLogBase.DM_ETL_006,
                transformer_name=transformer.__class__.__name__,
                original_record=service.model_dump(
                    exclude_none=True, mode="json", warnings=False
                ),
                transformed_record=result.model_dump(
                    exclude_none=True, mode="json", warnings=False
                ),
            )

            # TODO: FTRS-1595 Step 5 - Check state table to determine insert vs update operation
            # Check if state record exists (Step 5)
            state = self.verify_state_record_exist(
                service.id
            )  # CHANGED: Now returns DataMigrationState | None

            if state is not None:  # CHANGED: Check if state object exists
                # TODO: FTRS-1595 Update scenario - state record exists
                # This service has been previously migrated
                # Currently: Log and exit early (update logic not implemented)
                # Future: Compare state, identify changes, perform targeted updates

                # Update scenario - exit early
                # self.logger.log(
                #     DataMigrationLogBase.DM_ETL_019,
                #     record_id=service.id,
                # )
                # Note: DM_ETL_019 is now logged inside verify_state_record_exist
                # # Exit early - no save operation occurs
                return

            # TODO: FTRS-1595 Insert scenario - no state record exists
            # This is a new service that hasn't been migrated before
            # Continue with migration to insert into future system tables
            # Note: Not creating state records at this stage per acceptance criteria

            # Insert scenario - continue with save
            self._save(result, service.id)
            self.metrics.migrated_records += 1

            elapsed_time = perf_counter() - start_time

            self.logger.log(
                DataMigrationLogBase.DM_ETL_007,
                elapsed_time=elapsed_time,
                transformer_name=transformer.__class__.__name__,
                healthcare_service_count=len(result.healthcare_service),
                location_count=len(result.location),
                organisation_count=len(result.organisation),
                healthcare_service_ids=[hs.id for hs in result.healthcare_service],
                location_ids=[loc.id for loc in result.location],
                organisation_ids=[org.id for org in result.organisation],
            )

        except Exception as e:
            self.metrics.errors += 1
            self.logger.exception(
                "Unexpected error encountered whilst processing service record"
            )
            self.logger.log(DataMigrationLogBase.DM_ETL_008, error=str(e))
            return

        finally:
            self.logger.remove_keys(["record_id"])

    def get_transformer(self, service: legacy.Service) -> ServiceTransformer | None:
        """
        Get the appropriate transformer for the service.
        """
        for TransformerClass in SUPPORTED_TRANSFORMERS:
            is_supported, reason = TransformerClass.is_service_supported(service)

            if not is_supported:
                self.logger.log(
                    DataMigrationLogBase.DM_ETL_002,
                    transformer_name=TransformerClass.__name__,
                    reason=reason,
                )
                continue

            self.logger.log(
                DataMigrationLogBase.DM_ETL_003,
                transformer_name=TransformerClass.__name__,
            )
            return TransformerClass(logger=self.logger, metadata=self.metadata)

    def _iter_records(self, batch_size: int = 1000) -> Iterable[legacy.Service]:
        """
        Iterate over records in the database.
        """
        stmt = select(legacy.Service).execution_options(yield_per=batch_size)
        with Session(self.engine) as session:
            yield from session.scalars(stmt)

    def _create_put_item(
        self, model: BaseModel, table_name: str, **kwargs: dict[str, Any]
    ) -> dict:
        """Helper method to create DynamoDB Put item with proper serialization."""
        data = model.model_dump(mode="json")
        data["id"] = str(model.id)
        data["field"] = "document"

        put_item = {
            "Put": {
                "TableName": table_name,
                "Item": {k: self.serializer.serialize(v) for k, v in data.items()},
                **kwargs,
            },
        }
        return put_item

    def _save(self, result: ServiceTransformOutput, service_id: int) -> None:
        """
        Save the transformed result to DynamoDB using transact_write_items for atomic writes.

        TODO: FTRS-1595 Save all transformed entities to the future system tables.

        TODO: FTRS-1595 Current save behavior
        - Saves all entities to their respective DynamoDB tables
        - Creates a state record (will be modified in future tickets)

        TODO: FTRS-1595 Future behavior changes
        - Only save when no state record exists (insert operation)
        - For update operations, perform targeted saves based on comparison
        - State record creation will be conditional based on operation type
        - Implement optimistic locking using version numbers
        """
        dynamodb_client = get_dynamodb_client(self.config.dynamodb_endpoint)

        # Cache table names
        env = self.config.env
        workspace = self.config.workspace
        tables = {
            "organisation": format_table_name("organisation", env, workspace),
            "location": format_table_name("location", env, workspace),
            "healthcare_service": format_table_name(
                "healthcare-service", env, workspace
            ),
            "state": format_table_name("data-migration-state", env, workspace),
        }

        # Build transaction items
        transact_items = []

        # Add all organisations
        transact_items.extend(
            self._create_put_item(
                org,
                tables["organisation"],
                ConditionExpression="attribute_not_exists(id) AND attribute_not_exists(#field)",
                ExpressionAttributeNames={"#field": "field"},
            )
            for org in result.organisation
        )

        # Add all locations
        transact_items.extend(
            self._create_put_item(
                loc,
                tables["location"],
                ConditionExpression="attribute_not_exists(id) AND attribute_not_exists(#field)",
                ExpressionAttributeNames={"#field": "field"},
            )
            for loc in result.location
        )

        # Add all healthcare services
        transact_items.extend(
            self._create_put_item(
                hc,
                tables["healthcare_service"],
                ConditionExpression="attribute_not_exists(id) AND attribute_not_exists(#field)",
                ExpressionAttributeNames={"#field": "field"},
            )
            for hc in result.healthcare_service
        )

        # Add DataMigrationState record
        state_data = DataMigrationState(
            id=uuid4(),
            source_record_id=f"services#{service_id}",
            version=1,
            organisation_id=result.organisation[0].id,
            organisation=result.organisation[0],
            location_id=result.location[0].id,
            location=result.location[0],
            healthcare_service_id=result.healthcare_service[0].id,
            healthcare_service=result.healthcare_service[0],
        )
        transact_items.append(
            self._create_put_item(
                state_data,
                tables["state"],
                ConditionExpression="attribute_not_exists(source_record_id)",
            )
        )

        # Execute atomic transaction
        try:
            dynamodb_client.transact_write_items(TransactItems=transact_items)
            self.logger.log(
                DataMigrationLogBase.DM_ETL_021,
                record_id=service_id,
                item_count=len(transact_items),
            )
        except Exception as e:
            # Check if it's a TransactionCanceledException with ConditionalCheckFailed
            error_code = None
            if hasattr(e, "response"):
                error_code = e.response.get("Error", {}).get("Code")

            if (
                e.__class__.__name__ == "TransactionCanceledException"
                or error_code == "TransactionCanceledException"
            ):
                # Check if the cancellation reason is ConditionalCheckFailed
                cancellation_reasons = []
                if hasattr(e, "response"):
                    cancellation_reasons = e.response.get("CancellationReasons", [])

                # If any item failed due to ConditionalCheckFailed, it means records already exist
                if any(
                    reason.get("Code") == "ConditionalCheckFailed"
                    for reason in cancellation_reasons
                ):
                    self.logger.log(
                        DataMigrationLogBase.DM_ETL_022,
                        record_id=service_id,
                    )
                    return

            # For all other exceptions, log and re-raise
            self.logger.exception(
                f"Failed to write items transactionally for service {service_id}"
            )
            raise

    def _convert_validation_issues(self, issues: list[ValidationIssue]) -> list[str]:
        """
        Convert validation issues to a list of strings.
        """
        return [
            f"field:{issue.expression} ,error: {issue.code},message:{issue.diagnostics},value:{issue.value}"
            for issue in issues
        ]

    def create_db_engine(self) -> Engine:
        # Validate the presence of a real connection string to avoid confusing errors when given mocks
        connection_string = getattr(
            getattr(self.config, "db_config", None), "connection_string", None
        )
        if not isinstance(connection_string, str) or not connection_string.strip():
            raise ValueError(
                "Invalid DataMigrationConfig: db_config.connection_string must be a non-empty string"
            )

        return create_engine(connection_string, echo=False).execution_options(
            postgresql_readonly=True
        )

    def verify_state_record_exist(self, record_id: int) -> DataMigrationState | None:
        """
        Check if a data migration state record exists for the given service ID.
        Returns True if the state record exists.
        Uses get_item with the source_record_id as the key.

        TODO: FTRS-1595 Step 5 of data migration workflow - State Table Lookup
        This method checks the DynamoDB state table to determine if a service has been
        previously migrated. The state table uses composite keys in format "services#{service_id}".

        TODO: FTRS-1595 Technical Implementation Detail - Direct DynamoDB Access
        Uses direct DynamoDB client instead of repositories because:
        1. State table uses different key structure (source_record_id) vs standard tables (id + field)
        2. Repositories are configured for standard table structure and cannot handle state table
        3. Future tickets will use TransactWriteItems for atomic updates across all tables
        4. No need to create separate data migration repository - direct client access is sufficient

        TODO: FTRS-1595 Purpose of separate state table
        1. Limiting data updates: Only compares against last DoS-migrated state, allowing
        future system to accept data from other sources (ODS, Ordinance Survey) without
        the migration pipeline overwriting those updates.
        2. Ensuring consistency: Provides optimistic locking mechanism via versioning to
        prevent concurrent updates from causing conflicts.

        TODO: FTRS-1595 Consistent Read requirement
        Uses ConsistentRead=True to ensure we get the latest committed state and prevent
        race conditions when multiple Lambda invocations process the same service concurrently.

        Args: service_id the DoS service ID to lookup

        Returns: DataMigrationState object if record exists (update operation), None otherwise (insert operation)
        """
        # 1. Get DynamoDB client - bypasses repositories due to different key structure
        dynamodb_client = get_dynamodb_client(self.config.dynamodb_endpoint)

        # 2. Format the state table name with environment and workspace
        state_table = format_table_name(
            "data-migration-state", self.config.env, self.config.workspace
        )

        # 3. Construct the composite key in format "services#{service_id}"
        # Note: State table uses "source_record_id" as primary key, not "id" + "field"
        source_record_id = "services#" + str(record_id)

        # 4. Perform GetItem operation to check if state record exists
        # FTRS-1595 Perform GetItem with ConsistentRead=True to ensure latest state
        response = dynamodb_client.get_item(
            TableName=state_table,
            Key={
                "source_record_id": {"S": source_record_id},
            },
            ConsistentRead=True,  # ADDED: Ensures we get latest committed state
        )

        # 5. Check if Item exists in response
        exists = "Item" in response

        # 6. Log the result
        # FTRS-1595 Check if the item exists in the response
        if exists:
            self.logger.debug(f"State record found for service ID: {record_id}")

            # State record exists - this service has been previously migrated
            # Parse the DynamoDB item into DataMigrationState object
            state = DataMigrationState.from_dynamodb_item(response["Item"])

            self.logger.log(
                DataMigrationLogBase.DM_ETL_019,
                record_id=record_id,
                version=state.version,
                message="State record found - treating as update operation",
            )
            return state
        else:
            self.logger.debug(f"No state record found for service ID: {record_id}")

            # No state record exists - this is a new service to the migration pipeline
            self.logger.debug(
                f"No state record found for service ID: {record_id} - treating as insert operation"
            )
            return None

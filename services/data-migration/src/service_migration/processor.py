from time import perf_counter
from typing import Any, Iterable
from uuid import UUID

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import get_table_name
from ftrs_data_layer.client import get_dynamodb_client
from ftrs_data_layer.domain import legacy
from ftrs_data_layer.logbase import DataMigrationLogBase
from sqlalchemy import Engine
from sqlmodel import Session, create_engine, select

from common.cache import DoSMetadataCache
from service_migration.config import DataMigrationConfig
from service_migration.ddb_transactions import ServiceTransactionBuilder
from service_migration.exceptions import ParentPharmacyNotFoundError
from service_migration.models import ServiceMigrationMetrics, ServiceMigrationState
from service_migration.transformer import (
    SUPPORTED_TRANSFORMERS,
    ServiceTransformer,
)
from service_migration.transformer.base import ServiceTransformOutput
from service_migration.transformer.base_pharmacy import (
    BasePharmacyTransformer,
    LinkedPharmacyTransformer,
)
from service_migration.validation.types import ValidationResult


class DataMigrationProcessor:
    """
    This class is responsible for managing the data migration process.
    It includes methods to transform legacy service data into the new format.
    """

    serializer: TypeSerializer = TypeSerializer()
    deserializer: TypeDeserializer = TypeDeserializer()

    def __init__(
        self,
        config: DataMigrationConfig,
        logger: Logger,
    ) -> None:
        self.logger = logger
        self.config = config
        self.engine = self._create_db_engine()
        self.metrics = ServiceMigrationMetrics()
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
            return TransformerClass(
                logger=self.logger,
                metadata=self.metadata,
            )

    def get_state_record(self, service_id: int) -> ServiceMigrationState | None:
        """
        Check if a data migration state record exists for the given service ID.
        Returns the state record if it exists, None otherwise.
        Uses get_item with the source_record_id as the key.
        """
        dynamodb_client = get_dynamodb_client(self.config.dynamodb_endpoint)
        state_table = get_table_name("data-migration-state")

        source_record_id = ServiceMigrationState.format_source_record_id(service_id)

        response = dynamodb_client.get_item(
            TableName=state_table,
            Key={"source_record_id": {"S": source_record_id}},
            ConsistentRead=True,
        )

        item = response.get("Item")
        if not item:
            self.logger.log(
                DataMigrationLogBase.DM_ETL_020,
                record_id=service_id,
            )
            return None

        # Deserialize the item back into a ServiceMigrationState
        deserialized_data = {
            k: self.deserializer.deserialize(v) for k, v in item.items()
        }

        self.logger.log(
            DataMigrationLogBase.DM_ETL_019,
            record_id=service_id,
        )
        return ServiceMigrationState.model_validate(deserialized_data)

    def _process_service(self, service: legacy.Service) -> None:
        """
        Process a single record by transforming it using the appropriate transformer.
        """
        self.logger.append_keys(record_id=service.id)
        self.logger.log(
            DataMigrationLogBase.DM_ETL_001,
            record=service.model_dump(exclude_none=True, mode="json", warnings=False),
        )

        try:
            start_time = perf_counter()
            self.metrics.total += 1

            transformer, state_record = self._get_ready_transformer(service)
            if transformer is None:
                return

            validation_result = self._validate_service(transformer, service)
            if validation_result is None:
                return

            result = self._transform_and_persist(
                service, transformer, validation_result, state_record
            )

            elapsed_time = perf_counter() - start_time
            self._log_migration_completion(transformer, result, elapsed_time)

        except Exception as e:
            self.metrics.errors += 1
            self.logger.exception(
                "Unexpected error encountered whilst processing service record"
            )
            self.logger.log(DataMigrationLogBase.DM_ETL_008, error=str(e))
            return

        finally:
            self.logger.remove_keys(["record_id"])

    # Core processing methods

    def _get_ready_transformer(
        self, service: legacy.Service
    ) -> tuple[ServiceTransformer | None, ServiceMigrationState | None]:
        """
        Get transformer and prepare it for use, including linked pharmacy setup
        and migration state resolution.
        """
        transformer = self.get_transformer(service)
        if not transformer:
            self.metrics.unsupported += 1
            self.logger.log(
                DataMigrationLogBase.DM_ETL_004,
                reason="No suitable transformer found",
            )
            return None, None

        self.metrics.supported += 1

        if isinstance(transformer, LinkedPharmacyTransformer):
            if not self._setup_linked_transformer(transformer, service):
                return None, None

        should_include, reason = transformer.should_include_service(service)
        should_continue, state_record = self._resolve_migration_state(
            service, should_include, reason
        )
        if not should_continue:
            return None, None

        return transformer, state_record

    def _resolve_migration_state(
        self, service: legacy.Service, should_include: bool, reason: str | None
    ) -> tuple[bool, ServiceMigrationState | None]:
        if should_include:
            return True, None

        if service.statusid != 1:
            state_record = self.get_state_record(service.id)
            if state_record is not None:
                return True, state_record

        self.metrics.skipped += 1
        self.logger.log(
            DataMigrationLogBase.DM_ETL_005,
            reason=reason or "No reason provided",
        )
        return False, None

    # Validation & transformation helpers

    def _validate_service(
        self, transformer: ServiceTransformer, service: legacy.Service
    ) -> ValidationResult[legacy.Service] | None:
        validation_result = transformer.validator.validate(
            service
        )  # note: some pre-transformation logic here

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
            self.metrics.invalid += 1
            self.logger.log(
                DataMigrationLogBase.DM_ETL_014,
                record_id=service.id,
            )
            return None

        return validation_result

    def _transform_and_persist(
        self,
        service: legacy.Service,
        transformer: ServiceTransformer,
        validation_result: ValidationResult[legacy.Service],
        state_record: ServiceMigrationState | None,
    ) -> ServiceTransformOutput:
        """
        Transform service data and persist to DynamoDB.
        """
        result = transformer.transform(validation_result.sanitised)
        self.metrics.transformed += 1

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

        current_state = state_record or self.get_state_record(service.id)
        transaction_items = self._build_transaction_items(
            service.id, current_state, validation_result.issues, result
        )
        self._execute_transaction_and_track(current_state, transaction_items)

        return result

    # Transaction & persistence helpers

    def _build_transaction_items(
        self,
        service_id: int,
        state_record: ServiceMigrationState | None,
        validation_issues: list[Any],
        result: ServiceTransformOutput,
    ) -> list[dict[str, Any]]:
        return (
            ServiceTransactionBuilder(
                service_id=service_id,
                logger=self.logger,
                migration_state=state_record,
                validation_issues=validation_issues,
            )
            .add_organisation(result.organisation[0] if result.organisation else None)
            .add_location(result.location[0] if result.location else None)
            .add_healthcare_service(
                result.healthcare_service[0] if result.healthcare_service else None
            )
            .build()
        )

    def _execute_transaction_and_track(
        self,
        state_record: ServiceMigrationState | None,
        transaction_items: list[dict[str, Any]],
    ) -> None:
        if not transaction_items:
            return

        self._execute_transaction(transaction_items)
        if state_record is None:
            self.metrics.inserted += 1
            return

        self.metrics.updated += 1

    def _log_migration_completion(
        self,
        transformer: ServiceTransformer,
        result: ServiceTransformOutput,
        elapsed_time: float,
    ) -> None:
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

    # State & database helpers

    def _iter_records(self, batch_size: int = 1000) -> Iterable[legacy.Service]:
        """
        Iterate over records in the database.
        """
        stmt = select(legacy.Service).execution_options(yield_per=batch_size)
        with Session(self.engine) as session:
            yield from session.scalars(stmt)

    def _execute_transaction(self, transact_items: list[dict[str, Any]]) -> None:
        """
        Save the transformed result to DynamoDB using transact_write_items for atomic writes.
        """
        dynamodb_client = get_dynamodb_client(self.config.dynamodb_endpoint)

        # Execute atomic transaction
        try:
            dynamodb_client.transact_write_items(TransactItems=transact_items)
            self.logger.log(
                DataMigrationLogBase.DM_ETL_021,
                item_count=len(transact_items),
            )
        except Exception as e:
            # Check if it's a TransactionCanceledException with ConditionalCheckFailed
            error_code = None
            if hasattr(e, "response"):
                error_code = e.response.get("Error", {}).get("Code")

            if error_code == "ValidationException":
                self.logger.log(
                    DataMigrationLogBase.DM_ETL_041,
                    transact_items=transact_items,
                    response=e.response if hasattr(e, "response") else None,
                )
                raise

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
                        DataMigrationLogBase.DM_ETL_022, response=e.response
                    )
                    return

            raise  # Reraise other exceptions

    def _create_db_engine(self) -> Engine:
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

    # Specialized helpers (pharmacy-related)

    def _setup_linked_transformer(
        self, transformer: LinkedPharmacyTransformer, service: legacy.Service
    ) -> bool:
        """
        Resolve the parent for a linked-pharmacy transformer, migrate it if needed,
        and set the org/location IDs on the transformer.
        Returns False if processing should stop (parent not found or parent migration failed).
        """
        try:
            parent_service, org_id, loc_id = transformer.resolve_parent(
                service, self.engine, self.get_state_record
            )
        except ParentPharmacyNotFoundError:
            self.metrics.errors += 1
            return False

        if parent_service is not None:
            try:
                org_id, loc_id = self._migrate_parent_pharmacy(parent_service)
            except Exception as e:
                self.metrics.errors += 1
                self.logger.exception("Parent pharmacy migration failed")
                self.logger.log(
                    DataMigrationLogBase.DM_ETL_039,
                    parent_record_id=parent_service.id,
                    record_id=service.id,
                    error=str(e),
                )
                return False

        if org_id is None or loc_id is None:
            self.metrics.errors += 1
            self.logger.log(
                DataMigrationLogBase.DM_ETL_040,
                record_id=service.id,
            )
            return False

        transformer.parent_organisation_id = org_id
        transformer.parent_location_id = loc_id
        return True

    def _migrate_parent_pharmacy(
        self, parent_service: legacy.Service
    ) -> tuple[UUID | None, UUID | None]:
        """
        Run the BasePharmacyTransformer on the parent pharmacy service and persist it
        as transaction 1 of a two-transaction linked-pharmacy migration.

        Returns the organisation_id and location_id from the newly written state record.
        """
        parent_transformer = BasePharmacyTransformer(
            logger=self.logger, metadata=self.metadata
        )

        validation_result = parent_transformer.validator.validate(parent_service)
        if not validation_result.should_continue:
            raise ValueError(
                f"Parent pharmacy service {parent_service.id} failed validation "
                "and cannot be migrated as part of linked pharmacy processing"
            )

        parent_result = parent_transformer.transform(validation_result.sanitised)

        parent_state = self.get_state_record(parent_service.id)

        parent_transaction_items = (
            ServiceTransactionBuilder(
                service_id=parent_service.id,
                logger=self.logger,
                migration_state=parent_state,
                validation_issues=validation_result.issues,
            )
            .add_organisation(
                parent_result.organisation[0] if parent_result.organisation else None
            )
            .add_location(parent_result.location[0] if parent_result.location else None)
            .add_healthcare_service(
                parent_result.healthcare_service[0]
                if parent_result.healthcare_service
                else None
            )
            .build()
        )

        if parent_transaction_items:
            self._execute_transaction(parent_transaction_items)

        parent_state_after = self.get_state_record(parent_service.id)
        if parent_state_after is None:
            raise ValueError(
                f"Parent pharmacy state record not found after migration "
                f"for service {parent_service.id}"
            )

        return parent_state_after.organisation_id, parent_state_after.location_id

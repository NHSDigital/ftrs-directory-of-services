from time import perf_counter
from typing import Any, Iterable

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import get_table_name
from ftrs_data_layer.client import get_dynamodb_client
from ftrs_data_layer.domain import legacy
from ftrs_data_layer.logbase import DataMigrationLogBase
from pydantic import BaseModel
from sqlalchemy import Engine
from sqlmodel import Session, create_engine, select

from common.cache import DoSMetadataCache
from service_migration.config import DataMigrationConfig
from service_migration.ddb_transactions import ServiceTransactionBuilder
from service_migration.models import ServiceMigrationState
from service_migration.transformer import (
    SUPPORTED_TRANSFORMERS,
    ServiceTransformer,
)


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
    deserializer: TypeDeserializer = TypeDeserializer()

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

            result = transformer.transform(validation_result.sanitised)
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

            state_record = self.get_state_record(service.id)

            transaction_items = (
                ServiceTransactionBuilder(
                    service_id=service.id,
                    logger=self.logger,
                    migration_state=state_record,
                    validation_issues=validation_result.issues,
                )
                .add_organisation(
                    result.organisation[0] if result.organisation else None
                )
                .add_location(result.location[0] if result.location else None)
                .add_healthcare_service(
                    result.healthcare_service[0] if result.healthcare_service else None
                )
                .build()
            )

            if transaction_items:
                self._execute_transaction(transaction_items)

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

    def get_state_record(self, service_id: int) -> ServiceMigrationState | None:
        """
        Check if a data migration state record exists for the given service ID.
        Returns True if the state record exists.
        Uses get_item with the source_record_id as the key.
        """
        dynamodb_client = get_dynamodb_client(self.config.dynamodb_endpoint)
        state_table = get_table_name("data-migration-state")

        source_record_id = ServiceMigrationState.format_source_record_id(service_id)

        response = dynamodb_client.get_item(
            TableName=state_table,
            Key={"source_record_id": {"S": source_record_id}},
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

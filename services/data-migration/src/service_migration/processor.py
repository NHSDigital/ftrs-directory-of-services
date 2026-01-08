from typing import Generator, Type

from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError
from ftrs_data_layer.domain.legacy.data_models import ServiceData
from ftrs_data_layer.domain.legacy.db_models import Service
from sqlalchemy import select
from sqlalchemy.orm import Session

from common.logbase import ServiceMigrationLogBase
from service_migration.dependencies import ServiceMigrationDependencies
from service_migration.dynamodb import ServiceTransactionBuilder
from service_migration.exceptions import (
    FatalValidationException,
    ServiceMigrationException,
    ServiceNotSupportedException,
    ServiceSkippedException,
)
from service_migration.models import (
    MigrationState,
    ServiceMigrationMetrics,
    TransformResult,
)
from service_migration.transformer import SUPPORTED_TRANSFORMERS, ServiceTransformer


class ServiceMigrationProcessor:
    """
    This class is responsible for managing the data migration process.
    It includes methods to transform legacy service data into the new format.
    """

    def __init__(self, deps: ServiceMigrationDependencies) -> None:
        self.deps = deps
        self.metrics = ServiceMigrationMetrics()

    def sync_service(self, service_id: int, method: str) -> None:
        """
        Run the single record sync process.
        """
        try:
            self.metrics.total += 1
            self.deps.logger.append_keys(service_id=service_id)

            existing_state = self.get_state_record(service_id)

            service = self.get_source_service(service_id)
            transformed_records = self.transform_service(service)

            transaction_items = (
                ServiceTransactionBuilder(
                    deps=self.deps,
                    service_id=service_id,
                    migration_state=existing_state,
                    validation_issues=transformed_records.validation_issues,
                )
                .add_organisation(transformed_records.organisation)
                .add_location(transformed_records.location)
                .add_healthcare_service(transformed_records.healthcare_service)
                .build()
            )

            self.execute_transaction(transaction_items)
            if not existing_state:
                self.metrics.inserted += 1
            else:
                self.metrics.updated += 1

        except FatalValidationException:
            self.metrics.invalid += 1
            raise

        except ServiceNotSupportedException:
            self.metrics.unsupported += 1
            raise

        except ServiceSkippedException:
            self.metrics.skipped += 1
            raise

        except Exception:
            self.metrics.errored += 1
            raise

        finally:
            self.deps.logger.remove_keys(["service_id"])

    def get_source_service(self, service_id: int) -> Generator[ServiceData, None, None]:
        """
        Retrieve a legacy service record by its ID.
        """
        with Session(self.deps.engine, autocommit=False) as session:
            stmt = select(Service).where(Service.id == service_id)

            self.deps.logger.log(
                ServiceMigrationLogBase.SM_PROC_001,
                statement=stmt.compile(self.deps.engine).string,
            )

            record = session.execute(stmt).scalars().unique().one_or_none()
            if not record:
                raise ServiceMigrationException(
                    f"Service record with ID {service_id} not found in source database",
                    should_requeue=False,
                )

            data = ServiceData.model_validate(record)
            self.deps.logger.log(
                ServiceMigrationLogBase.SM_PROC_002,
                service_uid=data.uid,
                service_name=data.name,
                last_updated=data.modifiedtime,
            )

            return data

    def transform_service(self, service: ServiceData) -> TransformResult:
        """
        Transform a legacy service record using the appropriate transformer.
        """
        transformer = self.get_transformer(service)
        self.metrics.supported += 1

        should_include, reason = transformer.should_include_service(service)
        if not should_include:
            self.deps.logger.log(ServiceMigrationLogBase.SM_PROC_006, reason=reason)
            raise ServiceSkippedException(reason)

        validation_result = transformer.validator.validate(service)
        if not validation_result.should_continue:
            raise FatalValidationException(
                service_id=service.id,
                issues=validation_result.issues,
            )

        transformer.validator.log_sanitisations(
            original=service,
            sanitised=validation_result.sanitised,
        )

        result = transformer.transform(validation_result.sanitised)
        result.validation_issues = validation_result.issues

        self.deps.logger.log(ServiceMigrationLogBase.SM_PROC_007)
        self.deps.logger.log(
            ServiceMigrationLogBase.SM_PROC_007a,
            transformed_record=result.model_dump(
                exclude_none=True, mode="json", warnings=False
            ),
            original_record=service.model_dump(
                exclude_none=True, mode="json", warnings=False
            ),
        )
        self.metrics.transformed += 1

        return result

    def get_transformer(self, service: ServiceData) -> ServiceTransformer:
        """
        Get the appropriate transformer for the service.
        """
        valid_transformers: list[Type[ServiceTransformer]] = []

        for TransformerClass in SUPPORTED_TRANSFORMERS:
            is_supported, reason = TransformerClass.is_service_supported(service)

            if not is_supported:
                self.deps.logger.log(
                    ServiceMigrationLogBase.SM_PROC_003,
                    transformer_name=TransformerClass.__name__,
                    reason=reason,
                )
                continue

            self.deps.logger.log(
                ServiceMigrationLogBase.SM_PROC_004,
                transformer_name=TransformerClass.__name__,
            )
            valid_transformers.append(TransformerClass)

        if not valid_transformers:
            raise ServiceNotSupportedException(
                f"No suitable transformer found for service ID {service.id}"
            )

        if len(valid_transformers) > 1:
            transformer_names = [cls.__name__ for cls in valid_transformers]
            raise ServiceMigrationException(
                f"Multiple suitable transformers found for service ID {service.id}: {transformer_names}",
                should_requeue=False,
            )

        transformer_cls = valid_transformers[0]
        self.deps.logger.log(
            ServiceMigrationLogBase.SM_PROC_005,
            transformer_name=transformer_cls.__name__,
        )

        return transformer_cls(deps=self.deps)

    def get_state_record(self, source_record_id: int) -> MigrationState | None:
        """
        Retrieve the migration state record for the given source record ID.
        """
        table_name = ServiceTransactionBuilder.format_migration_state_table_name(
            env=self.deps.config.env,
            workspace=self.deps.config.workspace,
        )
        source_record_key = {
            "source_record_id": {
                "S": MigrationState.format_source_record_id(source_record_id)
            },
        }

        self.deps.logger.log(
            ServiceMigrationLogBase.SM_PROC_008,
            table_name=table_name,
            key=source_record_key,
        )

        response = self.deps.ddb_client.get_item(
            TableName=table_name,
            Key=source_record_key,
        )

        if not (item := response.get("Item")):
            self.deps.logger.log(ServiceMigrationLogBase.SM_PROC_009)
            return None

        state = MigrationState.model_validate(
            TypeDeserializer().deserialize({"M": item})
        )
        self.deps.logger.log(
            ServiceMigrationLogBase.SM_PROC_010,
            state_version=state.version,
            organisation_id=state.organisation_id,
            location_id=state.location_id,
            healthcare_service_id=state.healthcare_service_id,
        )
        return state

    def execute_transaction(self, transaction_items: list[dict]) -> None:
        """
        Execute the DynamoDB transaction with the given items.
        """
        if not transaction_items:
            self.deps.logger.log(ServiceMigrationLogBase.SM_PROC_026)
            return

        self.deps.logger.log(
            ServiceMigrationLogBase.SM_PROC_027,
            item_count=len(transaction_items),
            items=transaction_items,
        )

        try:
            response = self.deps.ddb_client.transact_write_items(
                TransactItems=transaction_items, ReturnConsumedCapacity="INDEXES"
            )
            self.deps.logger.log(
                ServiceMigrationLogBase.SM_PROC_028,
                consumed_capacity=response.get("ConsumedCapacity"),
            )

        except ClientError as exc:
            error = exc.response.get("Error", {})

            if error.get("Code") == "TransactionCanceledException":
                if any(
                    reason.get("Code") == "ConditionalCheckFailed"
                    for reason in exc.response.get("CancellationReasons", [])
                ):
                    self.deps.logger.log(
                        ServiceMigrationLogBase.SM_PROC_029,
                        error=error.get("Message"),
                        items=transaction_items,
                        response=exc.response,
                    )
                    raise ServiceMigrationException(
                        "DynamoDB transaction cancelled: see logs for details",
                        should_requeue=True,
                    ) from exc

            self.deps.logger.log(
                ServiceMigrationLogBase.SM_PROC_030,
                error=error.get("Message"),
                items=transaction_items,
                response=exc.response,
            )
            raise ServiceMigrationException(
                f"DynamoDB transaction failed: {error.get('Message')}",
                should_requeue=True,
            )

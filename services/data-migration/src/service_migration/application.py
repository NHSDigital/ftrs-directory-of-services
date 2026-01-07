from time import perf_counter
from uuid import uuid4

import boto3
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    process_partial_response,
)
from aws_lambda_powertools.utilities.batch.exceptions import BatchProcessingError
from aws_lambda_powertools.utilities.batch.types import PartialItemFailureResponse
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger
from sqlalchemy import Engine, create_engine

from common.cache import DoSMetadataCache
from common.events import DMSEvent
from common.logbase import ServiceMigrationLogBase
from service_migration.config import ServiceMigrationConfig
from service_migration.constants import (
    LOGGER_SERVICE_NAME,
    METHOD_INSERT,
    METHOD_UPDATE,
    SourceDBTables,
)
from service_migration.dependencies import ServiceMigrationDependencies
from service_migration.exceptions import ServiceMigrationException
from service_migration.processor import ServiceMigrationProcessor


class ServiceMigrationApplication:
    """
    Main application class for handling service migration events.
    """

    def __init__(self, config: ServiceMigrationConfig | None = None) -> None:
        self.config = config or ServiceMigrationConfig()
        self.logger = self.create_logger(self.config)

        self.logger.log(ServiceMigrationLogBase.SM_APP_001, config=self.config)

        self.deps = self.create_dependencies(self.config)
        self.processor = ServiceMigrationProcessor(deps=self.deps)
        self.batch_processor = BatchProcessor(event_type=EventType.SQS)

        self.logger.log(ServiceMigrationLogBase.SM_APP_002)

    def handle_sqs_event(
        self,
        event: dict,
        context: LambdaContext,
    ) -> PartialItemFailureResponse:
        """
        Process the incoming event and run the correct processing logic for the change.
        """
        self.deps.logger.log(ServiceMigrationLogBase.SM_APP_003, event=event)
        self.processor.metrics.reset()

        try:
            result = process_partial_response(
                event=event,
                context=context,
                record_handler=self.handle_sqs_record,
                processor=self.batch_processor,
            )
        except BatchProcessingError as exc:
            self.deps.logger.log(
                ServiceMigrationLogBase.SM_APP_010,
                error=str(exc),
                metrics=self.processor.metrics.model_dump(),
            )
            raise ServiceMigrationException(
                message="Fatal error during batch processing"
            ) from exc

        if result["batchItemFailures"]:
            self.logger.log(
                ServiceMigrationLogBase.SM_APP_005,
                failures=result["batchItemFailures"],
            )

        self.deps.logger.log(
            ServiceMigrationLogBase.SM_APP_004,
            metrics=self.processor.metrics.model_dump(),
        )

        return result

    def handle_sqs_record(self, record: SQSRecord) -> None:
        """
        Handle an event from DMS
        This should be a single record change event.
        """

        start_time = perf_counter()

        try:
            event = self.parse_sqs_record(record)

            self.deps.logger.append_keys(sqs_message_id=record.message_id)
            self.deps.logger.log(ServiceMigrationLogBase.SM_APP_006, event=event)

            match event.table_name:
                case SourceDBTables.SERVICES:
                    return self.handle_service_event(event)

                case SourceDBTables.SERVICE_ENDPOINTS:
                    return self.handle_endpoint_event(event)

                case _:
                    raise ServiceMigrationException(  # noqa: TRY301
                        message=f"Unsupported table for migration: {event.table_name}",
                        should_requeue=False,
                    )

        except ServiceMigrationException as exc:
            if exc.should_requeue:
                self.deps.logger.log(
                    ServiceMigrationLogBase.SM_APP_008a,
                    error=str(exc),
                )
                raise  # Raise to trigger requeue

            self.deps.logger.log(
                ServiceMigrationLogBase.SM_APP_008b,
                error=str(exc),
            )

        except Exception as exc:
            self.deps.logger.log(
                ServiceMigrationLogBase.SM_APP_009,
                error=str(exc),
            )
            raise  # Raise to trigger requeue

        finally:
            duration = perf_counter() - start_time
            self.deps.logger.log(ServiceMigrationLogBase.SM_APP_007, duration=duration)
            self.deps.logger.remove_keys(["sqs_message_id"])

    def handle_service_event(self, event: DMSEvent) -> None:
        if event.method not in [METHOD_INSERT, METHOD_UPDATE]:
            raise ServiceMigrationException(
                message=f"Unsupported method for service migration: {event.method}",
                should_requeue=False,
            )

        return self.processor.sync_service(event.record_id, event.method)

    def handle_endpoint_event(self, event: DMSEvent) -> None:
        return self.processor.sync_service(event.service_id, METHOD_UPDATE)

    def parse_sqs_record(self, record: SQSRecord) -> DMSEvent:
        """
        Parse the SQS record into a DMSEvent
        """
        try:
            return DMSEvent.model_validate_json(record.body)
        except Exception as exc:
            self.deps.logger.log(
                ServiceMigrationLogBase.SM_APP_011,
                error=str(exc),
                record_body=record.body,
            )
            raise ServiceMigrationException(
                message="Failed to parse SQS record body into DMSEvent",
                should_requeue=False,
            ) from exc

    def create_dependencies(
        self,
        config: ServiceMigrationConfig | None = None,
    ) -> ServiceMigrationDependencies:
        """
        Create the dependencies required for the data migration application.
        """
        config = config or ServiceMigrationConfig()
        db_engine = self.create_db_engine(config)
        metadata_cache = DoSMetadataCache(db_engine)

        return ServiceMigrationDependencies(
            config=config,
            logger=self.logger,
            engine=db_engine,
            ddb_client=boto3.client("dynamodb", endpoint_url=config.dynamodb_endpoint),
            metadata=metadata_cache,
        )

    def create_db_engine(self, config: ServiceMigrationConfig) -> Engine:
        """
        Create a database engine using the provided configuration.
        """
        connection_string = config.db_config.connection_string
        if not connection_string.strip():
            raise ValueError(
                "Invalid DataMigrationConfig: db_config.connection_string must be a non-empty string"
            )

        return create_engine(connection_string, echo=False).execution_options(
            postgresql_readonly=True
        )

    def create_logger(self, config: ServiceMigrationConfig) -> Logger:
        """
        Create a logger for the application.
        Enables pretty-print JSON formatting for local development via POWERTOOLS_DEV.
        """
        logger = Logger.get(service=LOGGER_SERVICE_NAME)
        logger.append_keys(
            run_id=str(uuid4()),
            env=config.env,
            workspace=config.workspace,
        )

        return logger

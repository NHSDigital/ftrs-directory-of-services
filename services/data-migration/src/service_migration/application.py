from uuid import uuid4

from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    process_partial_response,
)
from aws_lambda_powertools.utilities.batch.types import PartialItemFailureResponse
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import DataMigrationLogBase

from common.events import DMSEvent
from service_migration.config import DataMigrationConfig
from service_migration.processor import DataMigrationProcessor


class DataMigrationApplication:
    def __init__(self, config: DataMigrationConfig | None = None) -> None:
        self.config = config or DataMigrationConfig()
        self.logger = self.create_logger()
        self.processor = self.create_processor()
        self.batch_processor = BatchProcessor(event_type=EventType.SQS)

    def handle_sqs_event(
        self,
        event: dict,
        context: LambdaContext,
    ) -> PartialItemFailureResponse:
        """
        Process the incoming event and run the correct processing logic for the change.
        """
        self.processor.metrics.reset()
        self.logger.log(DataMigrationLogBase.DM_ETL_000, event=event)

        result = process_partial_response(
            event=event,
            context=context,
            record_handler=self.handle_sqs_record,
            processor=self.batch_processor,
        )

        self.logger.log(
            DataMigrationLogBase.DM_ETL_999,
            metrics=self.processor.metrics.model_dump(),
            failures=result["batchItemFailures"],
        )

        return result

    def handle_sqs_record(self, record: SQSRecord) -> None:
        """
        Handle an event from DMS
        This should be a single record change event.
        """
        event = self.parse_event(record.json_body)

        if event.method.lower() not in ["insert", "update"]:
            self.logger.log(
                DataMigrationLogBase.DM_ETL_010,
                method=event.method,
                event=event.model_dump(),
            )
            return

        match event.table_name:
            case "services":
                return self.processor.sync_service(event.record_id, event.method)
            case "serviceendpoints":
                return self.handle_endpoint_event(event)

        self.logger.log(
            DataMigrationLogBase.DM_ETL_011,
            table_name=event.table_name,
            method=event.method,
            event=event.model_dump(),
        )

    def handle_full_sync_event(self) -> None:
        """
        Handle a full sync event.
        This should trigger the full sync process.
        """
        self.processor.sync_all_services()

    def parse_event(self, event: dict) -> DMSEvent:
        """
        Parse the incoming event into a DMSEvent object.
        Handles both direct events and nested Aurora trigger events.
        """
        try:
            # Unwrap nested Aurora trigger events from migration_copy_db_trigger_lambda_handler
            if (
                "source" in event
                and event.get("source") == "aurora_trigger"
                and "event" in event
            ):
                event = event["event"]

            return DMSEvent(**event)
        except Exception as e:
            self.logger.log(
                DataMigrationLogBase.DM_ETL_009,
                error=str(e),
                event=event,
            )
            raise ValueError("Invalid event format") from e

    def create_logger(self) -> Logger:
        """
        Set up the logger for the data migration application.
        """
        logger = Logger.get(service="data-migration")
        logger.append_keys(
            run_id=str(uuid4()),
            env=self.config.env,
            workspace=self.config.workspace,
        )
        return logger

    def create_processor(self) -> DataMigrationProcessor:
        """
        Create a DataMigrationProcessor instance with the configured database URI.
        """
        return DataMigrationProcessor(
            logger=self.logger,
            config=self.config,
        )

    def handle_endpoint_event(self, event: DMSEvent) -> None:
        return self.processor.sync_service(event.service_id, "update")

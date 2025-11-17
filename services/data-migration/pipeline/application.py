from typing import Literal
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
from pydantic import BaseModel

from pipeline.processor import DataMigrationProcessor
from pipeline.triagecode_processor import TriageCodeProcessor
from pipeline.utils.config import DataMigrationConfig


class DMSEvent(BaseModel):
    type: Literal["dms_event"] = "dms_event"
    record_id: int
    table_name: str
    method: str


class DataMigrationApplication:
    def __init__(self, config: DataMigrationConfig | None = None) -> None:
        self.config = config or DataMigrationConfig()
        self.logger = self.create_logger()
        self.processor = self.create_processor()
        self.triage_code_processor = self.create_triage_code_processor()
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
            response=result,
        )

        return result

    def handle_sqs_record(self, record: SQSRecord) -> None:
        """
        Handle an record from SQS
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
        self.triage_code_processor.sync_all_triage_codes()

    def parse_event(self, event: dict) -> DMSEvent:
        """
        Parse the incoming event into a DMSEvent object.
        """
        try:
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

    def create_triage_code_processor(self) -> TriageCodeProcessor:
        """
        Create a TriageCodeProcessor instance with the configured database URI.
        """
        return TriageCodeProcessor(
            logger=self.logger,
            config=self.config,
        )

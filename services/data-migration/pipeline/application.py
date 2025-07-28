from typing import Annotated, Literal
from uuid import uuid4

from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import DataMigrationLogBase
from pydantic import BaseModel, Field

from pipeline.processor import DataMigrationProcessor
from pipeline.utils.config import DataMigrationConfig


class DMSEvent(BaseModel):
    type: Literal["dms_event"]
    record_id: int
    table_name: str
    method: str


class FullSyncEvent(BaseModel):
    type: Literal["full_sync"]


LambdaTriggerEvent = Annotated[DMSEvent | FullSyncEvent, Field(discriminator="type")]


class DataMigrationEvent(BaseModel):
    event: LambdaTriggerEvent


class DataMigrationApplication:
    def __init__(self, config: DataMigrationConfig | None = None) -> None:
        self.config = config or DataMigrationConfig()
        self.logger = self.create_logger()
        self.processor = self.create_processor()

    def handle_event(self, event: dict) -> None:
        """
        Process the incoming event and run the correct processing logic for the change.
        """
        self.logger.log(DataMigrationLogBase.DM_ETL_000, event=event)
        parsed_event = self.parse_event(event)

        match parsed_event.__class__.__name__:
            case "DMSEvent":
                self.handle_dms_event(parsed_event)

            case "FullSyncEvent":
                self.handle_full_sync_event()

        self.logger.log(
            DataMigrationLogBase.DM_ETL_999,
            metrics=self.processor.metrics.model_dump(),
        )

    def handle_dms_event(self, event: DMSEvent) -> None:
        """
        Handle an event from DMS
        This should be a single record change event.
        """
        if event.method not in ["insert", "update"]:
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
        return self.processor.sync_all_services()

    def parse_event(self, event: dict) -> LambdaTriggerEvent:
        """
        Parse the incoming event into a LambdaTriggerEvent object.
        """
        try:
            return DataMigrationEvent(event=event).event
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

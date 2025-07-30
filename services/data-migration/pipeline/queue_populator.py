from typing import Iterable

import boto3
from ftrs_data_layer.domain.legacy import Service
from pydantic import BaseModel
from sqlmodel import Session, create_engine, select

from pipeline.application import DMSEvent
from pipeline.utils.config import DatabaseConfig, QueuePopulatorConfig


class QueuePopulatorEvent(BaseModel):
    type_ids: list[int] | None = None
    status_ids: list[int] | None = None


def get_record_ids(config: QueuePopulatorConfig) -> Iterable[int]:
    """
    Retrieve record IDs based on the provided type and status IDs.
    """
    engine = create_engine(config.db_config.connection_string)

    with Session(engine) as session:
        stmt = select(Service.id).execution_options(yield_per=1000)
        if config.type_ids:
            stmt = stmt.where(Service.typeid.in_(config.type_ids))

        if config.status_ids:
            stmt = stmt.where(Service.statusid.in_(config.status_ids))

        yield from session.scalars(stmt)


def get_dms_events(config: QueuePopulatorConfig) -> Iterable[DMSEvent]:
    """
    Populate the queue with legacy services based on type and status IDs.
    """
    for record_id in get_record_ids(config):
        yield DMSEvent(
            type="dms_event",
            record_id=record_id,
            table_name="services",
            method="insert",
        )


def populate_sqs_queue(config: QueuePopulatorConfig) -> None:
    """
    Populate the SQS queue with DMS events for legacy services.
    """
    sqs = boto3.client("sqs")

    for event in get_dms_events(config):
        sqs.send_message(
            QueueUrl=config.sqs_queue_url,
            MessageBody=event.model_dump_json(),
        )


def lambda_handler(event: dict, context: dict) -> None:
    """
    AWS Lambda entrypoint for populating the queue with legacy services.
    """
    parsed_event = QueuePopulatorEvent(**event)
    populate_sqs_queue(
        config=QueuePopulatorConfig(
            db_config=DatabaseConfig.from_secretsmanager(),
            type_ids=parsed_event.type_ids,
            status_ids=parsed_event.status_ids,
        )
    )

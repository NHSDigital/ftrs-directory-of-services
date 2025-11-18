from concurrent.futures import ThreadPoolExecutor
from itertools import batched
from typing import Iterable

import boto3
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger
from ftrs_data_layer.domain.legacy import Service
from ftrs_data_layer.logbase import DataMigrationLogBase
from pydantic import BaseModel
from sqlmodel import Session, create_engine, select

from pipeline.application import DMSEvent
from pipeline.utils.config import DatabaseConfig, QueuePopulatorConfig

SQS_BATCH_SIZE_LIMIT = 10
LOGGER = Logger.get(service="data-migration-queue-populator")
SQS_CLIENT = boto3.client("sqs")


class QueuePopulatorEvent(BaseModel):
    type_ids: list[int] | None = None
    status_ids: list[int] | None = None


def get_record_ids(config: QueuePopulatorConfig) -> Iterable[int]:
    """
    Retrieve record IDs based on the provided type and status IDs.
    """
    engine = create_engine(config.db_config.connection_string)

    with Session(engine) as session:
        stmt = select(Service.id)
        if config.type_ids is not None:
            stmt = stmt.where(Service.typeid.in_(config.type_ids))

        if config.status_ids is not None:
            stmt = stmt.where(Service.statusid.in_(config.status_ids))

        return session.exec(stmt).all()


def get_dms_event_batches(config: QueuePopulatorConfig) -> Iterable[list[dict]]:
    """
    Populate the queue with legacy services based on type and status IDs.
    """
    record_ids = get_record_ids(config)

    LOGGER.log(
        DataMigrationLogBase.DM_QP_001,
        count=len(record_ids),
        queue_url=config.sqs_queue_url,
    )

    for batch in batched(record_ids, SQS_BATCH_SIZE_LIMIT):
        sqs_messages = [
            {
                "Id": str(record_id),
                "MessageBody": DMSEvent(
                    type="dms_event",
                    record_id=record_id,
                    service_id=record_id,
                    table_name="services",
                    method="insert",
                ).model_dump_json(),
            }
            for record_id in batch
        ]

        yield {"QueueUrl": config.sqs_queue_url, "Entries": sqs_messages}


def send_message_batch(batch: dict) -> None:
    """
    Send a batch of messages to the SQS queue.
    """
    LOGGER.log(
        DataMigrationLogBase.DM_QP_002,
        count=len(batch["Entries"]),
        queue_url=batch["QueueUrl"],
    )

    response = SQS_CLIENT.send_message_batch(
        QueueUrl=batch["QueueUrl"],
        Entries=batch["Entries"],
    )

    if failed := response.get("Failed"):
        LOGGER.log(
            DataMigrationLogBase.DM_QP_003,
            count=len(failed),
            queue_url=batch["QueueUrl"],
            failed=failed,
        )

    if successful := response.get("Successful"):
        LOGGER.log(
            DataMigrationLogBase.DM_QP_004,
            count=len(successful),
            record_ids=[entry["Id"] for entry in successful],
            queue_url=batch["QueueUrl"],
        )


def populate_sqs_queue(config: QueuePopulatorConfig) -> None:
    """
    Populate the SQS queue with DMS events for legacy services.
    """
    LOGGER.log(
        DataMigrationLogBase.DM_QP_000,
        type_ids=config.type_ids,
        status_ids=config.status_ids,
    )

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(
            send_message_batch,
            get_dms_event_batches(config),
        )

    LOGGER.log(DataMigrationLogBase.DM_QP_999)


@LOGGER.inject_lambda_context
def lambda_handler(event: dict, context: LambdaContext) -> None:
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

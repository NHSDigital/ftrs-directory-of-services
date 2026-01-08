from concurrent.futures import ThreadPoolExecutor
from itertools import batched
from typing import Any, Dict, Iterable, List, Optional

import boto3
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger
from ftrs_data_layer.domain.legacy.db_models import Service
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from common.config import DatabaseConfig
from common.events import DMSEvent
from common.logbase import QueuePopulatorLogBase
from queue_populator.config import QueuePopulatorConfig

SQS_BATCH_SIZE_LIMIT = 10
LOGGER = Logger.get(service="data-migration-queue-populator")
SQS_CLIENT = boto3.client("sqs")


class QueuePopulatorEvent(BaseModel):
    table_name: str = "services"
    service_id: Optional[int] = None
    record_id: Optional[int] = None
    full_sync: bool = True
    type_ids: Optional[List[int]] = None
    status_ids: Optional[List[int]] = None


def get_record_ids(config: QueuePopulatorConfig) -> List[int]:
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

        result = session.execute(stmt).scalars().all()
        return [int(r) for r in result]


def get_dms_event_batches(config: QueuePopulatorConfig) -> Iterable[Dict[str, Any]]:
    """
    Populate the queue with legacy services based on type and status IDs.
    """
    record_ids = get_record_ids(config)

    LOGGER.log(
        QueuePopulatorLogBase.DM_QP_001,
        count=len(record_ids),
        queue_url=config.sqs_queue_url,
    )

    for batch in batched(record_ids, SQS_BATCH_SIZE_LIMIT):
        sqs_messages = [
            {
                "Id": str(record_id),
                "MessageBody": DMSEvent(
                    record_id=record_id,
                    service_id=record_id,
                    table_name="services",
                    method="insert",
                ).model_dump_json(),
            }
            for record_id in batch
        ]

        yield {"QueueUrl": config.sqs_queue_url, "Entries": sqs_messages}


def send_message_batch(batch: Dict[str, Any]) -> None:
    """
    Send a batch of messages to the SQS queue.
    """
    LOGGER.log(
        QueuePopulatorLogBase.DM_QP_002,
        count=len(batch["Entries"]),
        queue_url=batch["QueueUrl"],
    )

    response = SQS_CLIENT.send_message_batch(
        QueueUrl=batch["QueueUrl"],
        Entries=batch["Entries"],
    )

    failed = response.get("Failed")
    if failed:
        LOGGER.log(
            QueuePopulatorLogBase.DM_QP_003,
            count=len(failed),
            queue_url=batch["QueueUrl"],
            failed=failed,
        )

    successful = response.get("Successful")
    if successful:
        LOGGER.log(
            QueuePopulatorLogBase.DM_QP_004,
            count=len(successful),
            record_ids=[entry["Id"] for entry in successful],
            queue_url=batch["QueueUrl"],
        )


def populate_sqs_queue(config: QueuePopulatorConfig) -> None:
    """
    Populate the SQS queue with DMS events for legacy services.
    """
    LOGGER.log(
        QueuePopulatorLogBase.DM_QP_000,
        type_ids=config.type_ids,
        status_ids=config.status_ids,
    )
    if config.full_sync is True and config.record_id is None:
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(
                send_message_batch,
                get_dms_event_batches(config),
            )
    else:
        LOGGER.log(
            QueuePopulatorLogBase.DM_QP_005,
            service_id=config.service_id,
            record_id=config.record_id,
        )
        record_or_service_id = (
            config.record_id if config.record_id is not None else config.service_id
        )
        message = {
            "Id": str(record_or_service_id),
            "MessageBody": DMSEvent(
                record_id=record_or_service_id if record_or_service_id else 0,
                service_id=record_or_service_id if record_or_service_id else 0,
                table_name=config.table_name,
                method="insert",
            ).model_dump_json(),
        }
        send_message_batch({"QueueUrl": config.sqs_queue_url, "Entries": [message]})

    LOGGER.log(QueuePopulatorLogBase.DM_QP_999)


@LOGGER.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    """
    AWS Lambda entrypoint for populating the queue with legacy services.
    """
    parsed_event = QueuePopulatorEvent(**event)
    config = QueuePopulatorConfig(
        db_config=DatabaseConfig.from_secretsmanager(),
        type_ids=parsed_event.type_ids,
        status_ids=parsed_event.status_ids,
        service_id=parsed_event.service_id,
        record_id=parsed_event.record_id,
        full_sync=parsed_event.full_sync,
        table_name=parsed_event.table_name,
    )
    populate_sqs_queue(config=config)

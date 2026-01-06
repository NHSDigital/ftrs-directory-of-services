import json
import os
from typing import Any

import boto3
from botocore.client import BaseClient
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import get_correlation_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

ods_processor_logger = Logger.get(service="ods_processor")


def get_queue_name(
    env: str, workspace: str | None = None, queue_suffix: str = "queue"
) -> str:
    """
    Gets an SQS queue name based on the environment, workspace, and queue suffix.

    Args:
        env: Environment name (dev, test, prod)
        workspace: Optional workspace name
        queue_suffix: Queue type suffix (e.g., "queue", "extraction", "transform")
    """
    queue_name = f"ftrs-dos-{env}-etl-ods-{queue_suffix}"
    if workspace:
        queue_name = f"{queue_name}-{workspace}"
    return queue_name


def get_queue_url(queue_name: str, sqs: BaseClient) -> dict[str, Any]:
    """
    Gets an SQS queue url based on the queue name.
    """
    try:
        return sqs.get_queue_url(QueueName=queue_name)
    except Exception as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_EXTRACTOR_013,
            queue_name=queue_name,
            error_message=str(e),
        )
        raise


def send_messages_to_queue(
    messages: list[str | dict], queue_suffix: str = "queue", batch_size: int = 10
) -> None:
    """
    Send messages to SQS queue in batches.

    Args:
        messages: List of message bodies (strings or dicts)
        queue_suffix: Queue type suffix (e.g., "queue", "extraction", "transform")
        batch_size: Number of messages per batch (max 10 for SQS)
    """
    # Return early if no messages to send
    if not messages:
        return

    try:
        correlation_id = get_correlation_id()
        if correlation_id:
            ods_processor_logger.append_keys(correlation_id=correlation_id)

        sqs = boto3.client("sqs", region_name=os.environ["AWS_REGION"])
        queue_name = get_queue_name(
            os.environ["ENVIRONMENT"], os.environ.get("WORKSPACE"), queue_suffix
        )
        response_get_queue = get_queue_url(queue_name, sqs)
        queue_url = response_get_queue["QueueUrl"]

        total_messages = len(messages)

        # Process messages in batches
        for i in range(0, len(messages), batch_size):
            batch = messages[i : i + batch_size]
            batch_start = i + 1
            batch_end = min(i + len(batch), total_messages)
            _send_batch_to_sqs(
                sqs, queue_url, batch, (batch_start, batch_end, total_messages)
            )

    except Exception as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_EXTRACTOR_018,
            error_message=str(e),
        )
        raise


def _send_batch_to_sqs(
    sqs: BaseClient,
    queue_url: str,
    batch: list[str | dict],
    batch_info: tuple[int, int, int],  # (batch_start, batch_end, total_messages)
) -> None:
    """Send a single batch of messages to SQS with progress tracking."""
    batch_start, batch_end, total_messages = batch_info
    sqs_entries = []
    for index, message in enumerate(batch, start=batch_start):
        message_body = json.dumps(message) if isinstance(message, dict) else message
        sqs_entries.append({"Id": str(index), "MessageBody": message_body})

    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_EXTRACTOR_014,
        number=len(sqs_entries),
        batch_range=f"{batch_start}-{batch_end}",
        remaining=total_messages - batch_end,
    )

    response = sqs.send_message_batch(QueueUrl=queue_url, Entries=sqs_entries)

    successful = len(response.get("Successful", []))
    failed_messages = response.get("Failed", [])
    failed = len(failed_messages)

    if failed > 0:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_EXTRACTOR_015,
            failed=failed,
            batch_range=f"{batch_start}-{batch_end}",
        )

        for fail in failed_messages:
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_EXTRACTOR_016,
                id=fail.get("Id"),
                message=fail.get("Message"),
                code=fail.get("Code"),
            )

    if successful > 0:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_EXTRACTOR_017,
            successful=successful,
            batch_range=f"{batch_start}-{batch_end}",
            remaining=total_messages - batch_end,
        )


def load_data(transformed_data: list[str]) -> None:
    """
    Legacy function name for backward compatibility.
    Use send_messages_to_queue instead.
    """
    send_messages_to_queue(transformed_data, queue_suffix="queue")

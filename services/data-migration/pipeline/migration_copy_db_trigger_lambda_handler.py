import json

import boto3
from ftrs_common.logger import Logger

from pipeline.utils.secret_utils import get_dms_workspaces

LOGGER = Logger.get(service="migration-copy-db-trigger")
SQS_CLIENT = boto3.client("sqs")


def lambda_handler(event: dict, context: dict) -> None:
    LOGGER.info("Received event: %s", json.dumps(event))
    workspaces = get_dms_workspaces()

    for workspace_queue_url in workspaces:
        try:
            response = SQS_CLIENT.send_message(
                QueueUrl=workspace_queue_url, MessageBody=json.dumps(event)
            )

            LOGGER.info(
                "Message sent to SQS for workspace %s. Message ID: %s",
                workspace_queue_url,
                response.get("MessageId"),
            )
        except Exception:
            LOGGER.exception(
                "Failed to send message to SQS for workspace %s", workspace_queue_url
            )

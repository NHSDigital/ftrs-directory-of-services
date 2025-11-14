import json
import os

import boto3
from aws_lambda_powertools.utilities.parameters import get_parameters
from ftrs_common.logger import Logger

LOGGER = Logger.get(service="migration-copy-db-trigger")
SQS_CLIENT = boto3.client("sqs")


def get_dms_workspaces() -> list[str]:
    ssm_path = os.environ.get("SQS_SSM_PATH")
    if not ssm_path:
        raise ValueError("Missing required environment variable: SQS_SSM_PATH")

    params = get_parameters(
        ssm_path,
        recursive=True,
        decrypt=True,
        max_age=300,  # cache TTL = 300 seconds (5 minutes)
    )
    workspaces = list(params.values())
    return workspaces


def lambda_handler(event: dict, context: dict) -> None:
    message = get_message_from_event(event)
    workspaces = get_dms_workspaces()

    for workspace_queue_url in workspaces:
        try:
            response = SQS_CLIENT.send_message(
                QueueUrl=workspace_queue_url, MessageBody=json.dumps(message)
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


def get_message_from_event(event: dict) -> dict:
    LOGGER.info("Received event: %s", json.dumps(event))

    message = {"source": "aurora_trigger", "event": event}
    return message

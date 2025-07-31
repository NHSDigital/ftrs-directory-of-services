import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client("sqs")
ssm = boto3.client("ssm")
path = os.environ["SQS_SSM_PATH"]


def lambda_handler(event: dict, context: dict) -> None:

    message = get_message_from_event(event)

    workspaces = get_dms_workspaces()

    for workspace_queue_url in workspaces:
        try:
            response = sqs.send_message(
                QueueUrl=workspace_queue_url, MessageBody=json.dumps(message)
            )

            logger.info(
                "Message sent to SQS for workspace %s. Message ID: %s",
                workspace_queue_url,
                response.get("MessageId"),
            )
        except Exception:
            logger.exception(
                "Failed to send message to SQS for workspace %s", workspace_queue_url
            )


def get_message_from_event(event: dict) -> dict:
    logger.info("Received event: %s", json.dumps(event))

    message = {"source": "aurora_trigger", "event": event}
    return message


def get_dms_workspaces() -> list[str]:
    try:
        paginator = ssm.get_paginator("get_parameters_by_path")
        workspaces = []

        for page in paginator.paginate(Path=path, Recursive=True, WithDecryption=True):
            workspaces.extend([param["Value"] for param in page["Parameters"]])

        logger.info("Retrieved DMS workspaces: %s", workspaces)
    except Exception:
        logger.exception("Error retrieving DMS workspaces")
        raise
    else:
        return workspaces

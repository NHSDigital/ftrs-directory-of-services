import os
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client("sqs")
ssm = boto3.client("ssm")
path = os.environ["SQS_SSM_PATH"]


def lambda_handler(event, context):

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
        except Exception as e:
            logger.error(
                "Failed to send message to SQS for workspace %s. Error: %s",
                workspace_queue_url,
                str(e),
            )


def get_message_from_event(event):
    logger.info("Received event: %s", json.dumps(event))

    message = {"source": "aurora_trigger", "event": event}
    return message


def get_dms_workspaces():
    try:
        paginator = ssm.get_paginator("get_parameters_by_path")
        workspaces = []

        for page in paginator.paginate(Path=path, Recursive=True, WithDecryption=True):
            workspaces.extend([param["Value"] for param in page["Parameters"]])

        logger.info("Retrieved DMS workspaces: %s", workspaces)
        return workspaces
    except Exception as e:
        logger.error("Error retrieving DMS workspaces: %s", str(e))
        raise e

import os
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client("sqs")
queue_url = os.environ["SQS_QUEUE_URL"]


def lambda_handler(event, context):
    logger.info("Queue URL: %s", queue_url)
    logger.info("Received event: %s", json.dumps(event))

    message = {"source": "aurora_trigger", "event": event}

    response = sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))

    logger.info("Message sent to SQS. Message ID: %s", response.get("MessageId"))

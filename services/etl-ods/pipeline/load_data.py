import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_queue_name(env: str, workspace: str | None = None) -> str:
    """
    Gets an SQS queue name based on the environment, and optional workspace.
    """
    queue_name = f"ftrs-dos-{env}-etl-ods-queue"
    if workspace:
        queue_name = f"{queue_name}-{workspace}"
    return queue_name


def get_queue_url(queue_name: str, sqs: any) -> any:
    """
    Gets an SQS queue url based on the queue name.
    """
    try:
        return sqs.get_queue_url(QueueName=queue_name)
    except Exception as e:
        logging.warning(
            f"Error when requesting queue url with queue name: {queue_name} with error: {e}"
        )
        raise


def load_data(transformed_data: list[str]) -> None:
    try:
        batch = []
        for index, item in enumerate(transformed_data, start=1):
            batch.append({"Id": str(index), "MessageBody": json.dumps(item)})
        logging.info(f"Trying to send {len(transformed_data)} messages to sqs queue")

        sqs = boto3.client("sqs", region_name=os.environ["AWS_REGION"])
        queue_name = get_queue_name(os.environ["ENVIRONMENT"], os.environ["WORKSPACE"])
        response_get_queue = get_queue_url(queue_name, sqs)

        queue_url = response_get_queue["QueueUrl"]

        response = sqs.send_message_batch(QueueUrl=queue_url, Entries=batch)

        successful = len(response.get("Successful", []))
        failed = len(response.get("Failed", []))

        if failed > 0:
            logging.warning(f"Failed to send {failed} messages in batch")
            for fail in response.get("Failed", []):
                logging.warning(
                    f"  Message {fail.get('Id')}: {fail.get('Message')} - {fail.get('Code')}"
                )

        logging.info(f"Succeeded to send {successful} messages in batch")
    except Exception as e:
        logging.warning(f"Error sending data to queue with error: {e}")
        raise

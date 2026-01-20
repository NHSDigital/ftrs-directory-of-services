import time
from json import dumps
from typing import Any, Dict

from boto3 import client
from loguru import logger
from utilities.common.resource_name import get_resource_name

SQS_CLIENT = client("sqs", region_name="eu-west-2")


def send_message_to_sqs(queue_url: str, message_body: dict) -> dict:
    """
    Send a message to the specified SQS queue.

    Args:
        queue_url (str): The SQS queue URL.
        message_body (dict): The message payload as a dictionary.

    Returns:
        dict: Response from SQS send_message API.
    """
    try:
        response = SQS_CLIENT.send_message(
            QueueUrl=queue_url, MessageBody=dumps(message_body)
        )
        logger.info(f"Sent message to SQS: MessageId={response.get('MessageId')}")
        return response
    except Exception as e:
        logger.error(f"Failed to send message to SQS: {e}")
        raise


def generate_sqs_body(org_id: str, ods_code: str) -> dict:
    """Generate SQS body for Organization resource.

    Args:
        org_id (str): The Organization resource ID to set in the message.
        ods_code (str): The ODS code to set in the identifier value.

    Returns:
        dict: SQS body.
    """
    return {
        "path": org_id,
        "body": {
            "resourceType": "Organization",
            "id": org_id,
            "meta": {
                "profile": [
                    "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
                ]
            },
            "identifier": [
                {
                    "use": "official",
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": ods_code,
                }
            ],
            "active": True,
            "type": [
                {
                    "coding": [
                        {
                            "system": "TO-DO",
                            "code": "PRESCRIBING COST CENTRE",
                            "display": "PRESCRIBING COST CENTRE",
                        }
                    ],
                    "text": "PRESCRIBING COST CENTRE",
                }
            ],
            "name": "ADAM HOUSE MEDICAL CENTRE",
            "telecom": [{"system": "phone", "value": "0115 9496911"}],
        },
    }


def get_queue_url(
    project: str, workspace: str, env: str, service: str, queue_suffix: str
) -> str:
    """Get SQS queue URL by constructing queue name from resource naming convention.

    Args:
        project: Project name (e.g., 'ftrs-dos')
        workspace: Workspace name (empty string for default)
        env: Environment (e.g., 'dev', 'test')
        service: Service name (e.g., 'etl-ods')
        queue_suffix: Queue suffix (e.g., 'transform-queue', 'load-queue')

    Returns:
        str: The SQS queue URL
    """
    queue_name = get_resource_name(project, workspace, env, service, queue_suffix)
    response = SQS_CLIENT.get_queue_url(QueueName=queue_name)
    return response["QueueUrl"]


def purge_queue(queue_url: str, timeout: int = 30) -> None:
    """Purge all messages from a queue and wait for it to be empty.

    Args:
        queue_url: The SQS queue URL
        timeout: Maximum seconds to wait for queue to be empty after purge
    """
    try:
        SQS_CLIENT.purge_queue(QueueUrl=queue_url)
        logger.info(f"Purged queue: {queue_url}")
        poll_for_queue_empty(queue_url, timeout=timeout)
    except Exception as e:
        logger.warning(f"Could not purge queue {queue_url}: {e}")


def get_queue_attributes(queue_url: str) -> Dict[str, Any]:
    """Get queue attributes including message counts and visibility timeout.

    Args:
        queue_url: The SQS queue URL

    Returns:
        Dict containing queue attributes
    """
    response = SQS_CLIENT.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=[
            "ApproximateNumberOfMessages",
            "ApproximateNumberOfMessagesNotVisible",
            "ApproximateNumberOfMessagesDelayed",
            "VisibilityTimeout",
        ],
    )
    return response["Attributes"]


def set_visibility_timeout(queue_url: str, timeout_seconds: int) -> None:
    """Set the visibility timeout for a queue.

    Args:
        queue_url: The SQS queue URL
        timeout_seconds: Visibility timeout in seconds
    """
    SQS_CLIENT.set_queue_attributes(
        QueueUrl=queue_url, Attributes={"VisibilityTimeout": str(timeout_seconds)}
    )
    logger.info(f"Set visibility timeout to {timeout_seconds}s for queue: {queue_url}")


def restore_visibility_timeout(queue_url: str, original_timeout: int) -> None:
    """Restore the original visibility timeout for a queue.

    Args:
        queue_url: The SQS queue URL
        original_timeout: Original timeout value to restore
    """
    try:
        set_visibility_timeout(queue_url, original_timeout)
        logger.info(f"Restored visibility timeout to {original_timeout}s")
    except Exception as e:
        logger.warning(f"Could not restore visibility timeout: {e}")


def poll_for_queue_empty(
    queue_url: str, timeout: int = 10, poll_interval: int = 1
) -> bool:
    """Poll until queue is empty or timeout is reached.

    Args:
        queue_url: The SQS queue URL
        timeout: Maximum seconds to wait
        poll_interval: Seconds between poll attempts

    Returns:
        bool: True if queue is empty, False if timeout reached
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        attrs = get_queue_attributes(queue_url)
        total_messages = int(attrs.get("ApproximateNumberOfMessages", 0)) + int(
            attrs.get("ApproximateNumberOfMessagesNotVisible", 0)
        )
        if total_messages == 0:
            logger.info(f"Queue {queue_url} is empty")
            return True
        time.sleep(poll_interval)
    return False


def poll_for_messages_in_queue(
    queue_url: str, expected_count: int, timeout: int = 10, poll_interval: int = 1
) -> bool:
    """Poll until queue has expected message count or timeout is reached.

    Args:
        queue_url: The SQS queue URL
        expected_count: Expected number of messages
        timeout: Maximum seconds to wait
        poll_interval: Seconds between poll attempts

    Returns:
        bool: True if expected count reached, False if timeout reached
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        attrs = get_queue_attributes(queue_url)
        count = int(attrs.get("ApproximateNumberOfMessages", 0))
        if count >= expected_count:
            logger.info(f"Found {count} messages in queue")
            return True
        time.sleep(poll_interval)
    return False

from json import dumps
from boto3 import client
from loguru import logger

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
            QueueUrl=queue_url,
            MessageBody=dumps(message_body)
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
                "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
            },
            "identifier": [{
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": ods_code
            }],
            "active": True,
            "type": [{
                "coding": [{
                    "system": "TO-DO",
                    "code": "PRESCRIBING COST CENTRE",
                    "display": "PRESCRIBING COST CENTRE"
                }],
                "text": "PRESCRIBING COST CENTRE"
            }],
            "name": "ADAM HOUSE MEDICAL CENTRE",
            "telecom": [{
                "system": "phone",
                "value": "0115 9496911"
            }]
        }
    }


def get_queue_url(queue_name: str) -> str:
    """
    Get the URL for an SQS queue by name.

    Args:
        queue_name (str): The name of the SQS queue.

    Returns:
        str: The SQS queue URL.
    """
    try:
        response = SQS_CLIENT.get_queue_url(QueueName=queue_name)
        queue_url = response["QueueUrl"]
        logger.info(f"Retrieved queue URL for '{queue_name}': {queue_url}")
        return queue_url
    except Exception as e:
        logger.error(f"Failed to get queue URL for '{queue_name}': {e}")
        raise


def get_approximate_message_count(queue_url: str) -> int:
    """
    Get the approximate number of messages in an SQS queue.

    Args:
        queue_url (str): The SQS queue URL.

    Returns:
        int: Approximate number of messages in the queue.
    """
    try:
        response = SQS_CLIENT.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=["ApproximateNumberOfMessages"]
        )
        count = int(response["Attributes"]["ApproximateNumberOfMessages"])
        logger.info(f"Queue has approximately {count} message(s)")
        return count
    except Exception as e:
        logger.error(f"Failed to get message count for queue: {e}")
        raise


def purge_queue(queue_url: str) -> None:
    """
    Purge all messages from an SQS queue.

    Args:
        queue_url (str): The SQS queue URL.
    """
    try:
        SQS_CLIENT.purge_queue(QueueUrl=queue_url)
        logger.info(f"Purged all messages from queue: {queue_url}")
    except Exception as e:
        logger.error(f"Failed to purge queue: {e}")
        raise



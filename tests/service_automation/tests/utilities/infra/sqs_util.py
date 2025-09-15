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


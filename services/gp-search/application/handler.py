"""
Lambda handler entry point.
"""

import json
import logging
from typing import Any, Dict

from aws_lambda_powertools.utilities.typing import LambdaContext

from application.config import get_config
from application.services.fhir_mapper.fhir_mapper import FhirMapper
from application.services.repository.dynamo import DynamoRepository

config = get_config()

# Configure logging
logging.basicConfig(level=config.get("LOG_LEVEL"))
logger = logging.getLogger(__name__)
logging.getLogger("pydantic").setLevel(logging.DEBUG)
# Initialize services
repository = DynamoRepository(table_name=config.get("DYNAMODB_TABLE_NAME"))
mapper = FhirMapper(base_url=config.get("FHIR_BASE_URL"))


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler function that processes incoming requests.

    Args:
        event: The event raw_data
        context: The Lambda context

    Returns:
        API Gateway compatible response
    """
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Extract ODS code from event
        if (
            "pathParameters" in event
            and event["pathParameters"]
            and "ods_code" in event["pathParameters"]
        ):
            ods_code = event["pathParameters"]["ods_code"]
        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "ODS code is required"}),
            }

        logger.info(f"Looking up organization with ODS code: {ods_code}")

        # Look up organization in repository
        organization_data = repository.get_first_record_by_ods_code(ods_code)

        if not organization_data:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {"error": f"No organization found for ODS code: {ods_code}"}
                ),
            }

        # Map to FHIR Bundle with Organization and Endpoints
        fhir_bundle = mapper.map_to_fhir(organization_data, ods_code)

        # Convert the FHIR Bundle to JSON
        bundle_dump_json = fhir_bundle.model_dump_json()

    except Exception as e:
        logger.exception("Error processing request")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Error processing request: {str(e)}"}),
        }
    else:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/fhir+json"},
            "body": bundle_dump_json,
        }

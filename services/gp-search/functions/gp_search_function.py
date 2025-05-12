from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from functions.ftrs_service.ftrs_service import FtrsService

logger = Logger()


# noinspection PyUnusedLocal
@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    ods_code = event["odsCode"]
    logger.append_keys(ods_code=ods_code)

    ftrs_service = FtrsService()

    fhir_resource = ftrs_service.endpoints_by_ods(ods_code)
    fhir_resource_type = fhir_resource.get_resource_type()
    fhir_resource_json = fhir_resource.model_dump_json()

    if fhir_resource_type == "Bundle":
        logger.info("Successfully processed")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/fhir+json"},
            "body": fhir_resource_json,
        }

    elif fhir_resource_type == "OperationOutcome":
        logger.error("Error occurred while processing")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/fhir+json"},
            "body": fhir_resource_json,
        }

    else:
        logger.error(f"Unknown resource type: {fhir_resource_type}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/fhir+json"},
            "body": None,
        }

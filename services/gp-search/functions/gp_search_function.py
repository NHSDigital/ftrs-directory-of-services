import logging

from aws_lambda_powertools.utilities.typing import LambdaContext

from functions.ftrs_service.ftrs_service import FtrsService

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    ods_code = event["pathParameters"]["odsCode"]

    ftrs_service = FtrsService()

    fhir_resource = ftrs_service.endpoints_by_ods(ods_code=ods_code)
    fhir_resource_json = fhir_resource.model_dump_json()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/fhir+json"},
        "body": fhir_resource_json,
    }

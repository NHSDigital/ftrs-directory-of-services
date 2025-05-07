from typing import Any, Dict

from aws_lambda_powertools.utilities.typing import LambdaContext
from services.ftrs_service.ftrs_service import FtrsService


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    ftrs_service = FtrsService()

    ods_code = event["pathParameters"]["odsCode"]
    fhir_resource = ftrs_service.endpoints_by_ods(ods_code=ods_code)
    fhir_resource_json = fhir_resource.model_dump_json()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/fhir+json"},
        "body": fhir_resource_json,
    }

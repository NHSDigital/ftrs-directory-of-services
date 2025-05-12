from aws_lambda_powertools import Logger
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from fhir.resources.R4B.operationoutcome import OperationOutcome

from functions.ftrs_service.config import get_config
from functions.ftrs_service.fhir_mapper.bundle_mapper import BundleMapper
from functions.ftrs_service.repository.dynamo import DynamoRepository

logger = Logger()


class FtrsService:
    def __init__(self) -> None:
        table_name_ = get_config().get("DYNAMODB_TABLE_NAME")
        base_url_ = get_config().get("FHIR_BASE_URL")
        self.repository = DynamoRepository(table_name=table_name_)
        self.mapper = BundleMapper(base_url=base_url_)

    def endpoints_by_ods(self, ods_code: str) -> FHIRResourceModel:
        try:
            logger.info(f"Looking up organization with ODS code: {ods_code}")
            organization_record = self.repository.get_first_record_by_ods_code(ods_code)

            logger.info(
                f"Mapping to FHIR Bundle for organization_record: {organization_record.id}"
            )
            fhir_bundle = self.mapper.map_to_fhir(organization_record, ods_code)

        except Exception:
            logger.exception(f"Error occurred while processing ODS code: {ods_code}")
            return self._create_error_resource(ods_code)
        else:
            return fhir_bundle

    def _create_error_resource(self, ods_code: str) -> OperationOutcome:
        return OperationOutcome.model_validate(
            {
                "id": "internal-server-error",
                "issue": [
                    {
                        "severity": "error",
                        "code": "internal",
                        "details": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                                    "code": "INTERNAL_SERVER_ERROR",
                                    "display": f"Internal server error while processing ODS code '{ods_code}'",
                                },
                            ]
                        },
                    }
                ],
            }
        )

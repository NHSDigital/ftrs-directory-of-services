from aws_lambda_powertools import logging
from fhir.resources.R4B.operationoutcome import OperationOutcome
from fhir.resources.R4B.resource import Resource

from functions.ftrs_service.config import get_config
from functions.ftrs_service.fhir_mapper.bundle_mapper import BundleMapper
from functions.ftrs_service.repository.dynamo import DynamoRepository

logger = logging.Logger(service=__name__, level="INFO", child=True)


class FtrsService:
    def __init__(self) -> None:
        table_name_ = get_config().get("DYNAMODB_TABLE_NAME")
        base_url_ = get_config().get("FHIR_BASE_URL")
        self.repository = DynamoRepository(table_name=table_name_)
        self.mapper = BundleMapper(base_url=base_url_)

    def endpoints_by_ods(self, ods_code: str) -> Resource:
        try:
            logger.info(f"Looking up organization with ODS code: {ods_code}")

            organization_record = self.repository.get_first_record_by_ods_code(ods_code)

            if not organization_record:
                return self._create_error_resource(ods_code)

            fhir_bundle = self.mapper.map_to_fhir(organization_record)

        except Exception:
            return self._create_error_resource(ods_code)
        else:
            return fhir_bundle

    def _create_error_resource(self, ods_code: str) -> OperationOutcome:
        # TODO
        return OperationOutcome.model_construct(
            id="not-found",
            resourceType="OperationOutcome",
            issue=[
                {
                    "severity": "error",
                    "code": "not-found",
                    "details": {
                        "text": f"No organization found for ODS code: {ods_code}"
                    },
                }
            ],
        )

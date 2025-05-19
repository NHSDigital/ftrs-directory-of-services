from aws_lambda_powertools import Logger
from fhir.resources.R4B.bundle import Bundle

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

    def endpoints_by_ods(self, ods_code: str) -> Bundle:
        try:
            logger.info("Retrieving organization_record by ods_code")

            organization_record = self.repository.get_first_record_by_ods_code(ods_code)

            logger.append_keys(
                organization_id=organization_record.id
                if organization_record
                else "None"
            )

            logger.info("Mapping organization_record to fhir_bundle")

            fhir_bundle = self.mapper.map_to_fhir(organization_record, ods_code)

        except Exception:
            logger.exception("Error occurred while processing")
            raise

        else:
            return fhir_bundle

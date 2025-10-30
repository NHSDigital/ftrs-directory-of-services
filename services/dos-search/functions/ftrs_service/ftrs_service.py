from aws_lambda_powertools import Logger
from fhir.resources.R4B.bundle import Bundle
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import Organisation

from functions.ftrs_service.fhir_mapper.bundle_mapper import BundleMapper

logger = Logger()


class FtrsService:
    def __init__(self) -> None:
        self.repository = get_service_repository(Organisation, "organisation")
        self.mapper = BundleMapper()

    def endpoints_by_ods(self, ods_code: str) -> Bundle:
        try:
            logger.info("Retrieving organisation by ods_code")

            organisation = self.repository.get_first_record_by_ods_code(ods_code)

            logger.append_keys(
                organization_id=organisation.id if organisation else "None"
            )

            logger.info("Mapping organisation to fhir_bundle")

            fhir_bundle = self.mapper.map_to_fhir(organisation, ods_code)

        except Exception:
            logger.exception("Error occurred while processing")
            raise

        else:
            return fhir_bundle

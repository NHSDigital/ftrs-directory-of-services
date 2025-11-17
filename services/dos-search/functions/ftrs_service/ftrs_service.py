from fhir.resources.R4B.bundle import Bundle
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import Organisation

# Import instantiated logger from dos_search_ods_code_function to persist log context from beginning of Lambda execution
from functions.ftrs_logger import ftrs_logger
from functions.ftrs_service.fhir_mapper.bundle_mapper import BundleMapper


class FtrsService:
    def __init__(self) -> None:
        self.repository = get_service_repository(Organisation, "organisation")
        self.mapper = BundleMapper()

    def endpoints_by_ods(self, ods_code: str) -> Bundle:
        try:
            ftrs_logger.info("Retrieving organisation by ods_code")

            organisation = self.repository.get_first_record_by_ods_code(ods_code)

            ftrs_logger.info(
                "Mapping organisation to fhir_bundle",
                organization_id=organisation.id if organisation else "None",
            )

            fhir_bundle = self.mapper.map_to_fhir(organisation, ods_code)

        except Exception:
            ftrs_logger.exception("Error occurred while processing")
            raise

        else:
            return fhir_bundle

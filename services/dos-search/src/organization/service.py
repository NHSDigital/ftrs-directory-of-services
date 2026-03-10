from fhir.resources.R4B.bundle import Bundle
from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import Organisation

from src.common.fhir_mapper.bundle_mapper import BundleMapper
from src.common.logbase import DosSearchLogBase

logger = Logger.get(service="dos-search")


class OrganizationSearchService:
    def __init__(self) -> None:
        self.repository = get_service_repository(Organisation, "organisation")
        self.mapper = BundleMapper()

    def endpoints_by_ods(self, ods_code: str) -> Bundle:
        try:
            logger.log(DosSearchLogBase.DOS_SEARCH_007)

            organisation = self.repository.get_first_record_by_ods_code(ods_code)

            logger.log(
                DosSearchLogBase.DOS_SEARCH_008,
                organization_id=organisation.id if organisation else None,
            )

            fhir_bundle = self.mapper.map_to_fhir(organisation, ods_code)

        except Exception:
            logger.log(DosSearchLogBase.DOS_SEARCH_009)
            raise
        else:
            return fhir_bundle

from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from ftrs_common.logger import Logger
from ftrs_common.utils.api_url_util import get_fhir_url
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import Organisation

from src.common.constants import (
    ODS_ORG_CODE_IDENTIFIER_SYSTEM,
    REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
)
from src.common.fhir_mapper.bundle_mapper import BundleMapper
from src.common.fhir_mapper.endpoint_mapper import EndpointMapper
from src.common.fhir_mapper.organization_mapper import OrganizationMapper
from src.common.logbase import DosSearchLogBase

logger = Logger.get(service="dos-search")

API_NAME = "dos-search"
PRIMARY_RESOURCE_TYPE = "Organization"


class OrganizationSearchService:
    def __init__(self) -> None:
        self.repository = get_service_repository(Organisation, "organisation")
        self.organization_mapper = OrganizationMapper()
        self.endpoint_mapper = EndpointMapper()
        self.bundle_mapper = BundleMapper(API_NAME, PRIMARY_RESOURCE_TYPE)

    def endpoints_by_ods(self, ods_code: str) -> Bundle:
        try:
            logger.log(DosSearchLogBase.DOS_SEARCH_007)

            organisation = self.repository.get_first_record_by_ods_code(ods_code)

            logger.log(
                DosSearchLogBase.DOS_SEARCH_008,
                organization_id=organisation.id if organisation else None,
            )

            resources = self._create_resources(organisation)
            self_url = self._build_self_url(ods_code)
            fhir_bundle = self.bundle_mapper.map_to_fhir(resources, self_url)

        except Exception:
            logger.log(DosSearchLogBase.DOS_SEARCH_009)
            raise
        else:
            return fhir_bundle

    def _create_resources(
        self, organisation: Organisation | None
    ) -> list[FHIRResourceModel]:
        if organisation is None:
            return []

        organization_resource = self.organization_mapper.map_to_fhir_organization(
            organisation
        )
        endpoint_resources = self.endpoint_mapper.map_to_fhir_endpoints(organisation)

        return [organization_resource] + endpoint_resources

    @staticmethod
    def _build_self_url(ods_code: str) -> str:
        return (
            f"{get_fhir_url(API_NAME, PRIMARY_RESOURCE_TYPE)}"
            f"?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|{ods_code}"
            f"&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
        )

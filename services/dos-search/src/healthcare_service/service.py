from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from ftrs_common.logger import Logger
from ftrs_common.utils.api_url_util import get_fhir_url
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import HealthcareService
from ftrs_data_layer.domain.organisation import Organisation

from src.common.constants import ODS_ORG_CODE_IDENTIFIER_SYSTEM
from src.common.fhir_mapper.bundle_mapper import BundleMapper
from src.common.fhir_mapper.healthcare_service_mapper import HealthcareServiceMapper

logger = Logger.get(service="dos-search")

API_NAME = "dos-search"
PRIMARY_RESOURCE_TYPE = "HealthcareService"


class HealthcareServicesByOdsService:
    def __init__(self) -> None:
        self.repository = get_service_repository(Organisation, "organisation")
        self.healthcare_service_repository = get_service_repository(
            HealthcareService, "healthcare-service"
        )
        self.healthcare_service_mapper = HealthcareServiceMapper()
        self.bundle_mapper = BundleMapper(API_NAME, PRIMARY_RESOURCE_TYPE)

    def healthcare_services_by_ods(self, ods_code: str) -> Bundle:
        try:
            logger.info(
                "Retrieving organisations by ods_code for healthcare services lookup",
                ods_code=ods_code,
            )

            organisations = self.repository.get_by_ods_code(ods_code)

            if not organisations:
                logger.info(
                    "No organisations found for ods_code, returning empty bundle",
                    ods_code=ods_code,
                )
                self_url = self._build_self_url(ods_code)
                return self.bundle_mapper.map_to_fhir([], self_url)

            organization_ids = [str(org.id) for org in organisations]

            logger.info(
                "Retrieving healthcare services for organisations",
                organization_ids=organization_ids,
                ods_code=ods_code,
            )
            healthcare_services = []
            for organization_id in organization_ids:
                logger.info(
                    "Retrieving healthcare services for organisation",
                    organization_id=organization_id,
                )
                healthcare_services.extend(
                    self.healthcare_service_repository.get_records_by_provided_by(
                        str(organization_id)
                    )
                )

            logger.info(
                "Mapping healthcare services to fhir_bundle",
                healthcare_service_count=len(healthcare_services),
            )

            resources = self._create_resources(healthcare_services)
            self_url = self._build_self_url(ods_code)
            fhir_bundle = self.bundle_mapper.map_to_fhir(resources, self_url)

        except Exception:
            logger.exception(
                "Error occurred while processing healthcare services request"
            )
            raise

        else:
            return fhir_bundle

    def _create_resources(
        self, healthcare_services: list[HealthcareService]
    ) -> list[FHIRResourceModel]:
        return [
            self.healthcare_service_mapper.map_to_fhir_healthcare_service(
                healthcare_service
            )
            for healthcare_service in healthcare_services
        ]

    @staticmethod
    def _build_self_url(ods_code: str) -> str:
        return (
            f"{get_fhir_url(API_NAME, PRIMARY_RESOURCE_TYPE)}"
            f"?organization.identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|{ods_code}"
        )

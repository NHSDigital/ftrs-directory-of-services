from fhir.resources.R4B.bundle import Bundle
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import HealthcareService

from functions.ftrs_service.fhir_mapper.healthcare_service_bundle_mapper import (
    HealthcareServiceBundleMapper,
)
from functions.logger.dos_logger import DosLogger

dos_logger = DosLogger.get(service="dos-search")


class HealthcareServicesByOdsService:
    def __init__(self) -> None:
        self.healthcare_service_repository = get_service_repository(
            HealthcareService, "healthcare-service"
        )
        self.healthcare_service_mapper = HealthcareServiceBundleMapper()

    def healthcare_services_by_ods(self, ods_code: str) -> Bundle:
        try:
            dos_logger.info(
                "Retrieving organisations by ods_code for healthcare services lookup",
                ods_code=ods_code,
            )

            organisations = self.repository._get_records_by_ods_code(ods_code)

            if not organisations:
                dos_logger.info(
                    "No organisations found for ods_code, returning empty bundle",
                    ods_code=ods_code,
                )
                return self.healthcare_service_mapper.map_to_fhir([], ods_code)
            organization_ids = [str(org.id) for org in organisations]

            dos_logger.info(
                "Retrieving healthcare services for organisations",
                organization_ids=organization_ids,
                ods_code=ods_code,
            )
            healthcare_services = []
            for id in organization_ids:
                dos_logger.info(
                    "Retrieving healthcare services for organisation",
                    organization_id=id,
                )
                healthcare_services.extend(
                    self.healthcare_service_repository.get_records_by_provided_by(
                        str(id)
                    )
                )

            dos_logger.info(
                "Mapping healthcare services to fhir_bundle",
                healthcare_service_count=len(healthcare_services),
            )

            fhir_bundle = self.healthcare_service_mapper.map_to_fhir(
                healthcare_services, ods_code
            )

        except Exception:
            dos_logger.exception(
                "Error occurred while processing healthcare services request"
            )
            raise

        else:
            return fhir_bundle

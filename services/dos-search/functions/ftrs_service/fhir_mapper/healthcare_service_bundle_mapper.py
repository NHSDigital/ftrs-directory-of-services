from uuid import uuid4

from aws_lambda_powertools import Tracer
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from ftrs_common.utils.api_url_util import get_fhir_url
from ftrs_data_layer.domain import HealthcareService

from functions.ftrs_service.fhir_mapper.healthcare_service_mapper import (
    HealthcareServiceMapper,
)

tracer = Tracer()


class HealthcareServiceBundleMapper:
    """Maps a list of HealthcareService domain objects to a FHIR Bundle."""

    def __init__(self) -> None:
        self.healthcare_service_mapper = HealthcareServiceMapper()

    @tracer.capture_method
    def map_to_fhir(
        self, healthcare_services: list[HealthcareService], ods_code: str
    ) -> Bundle:
        """Map a list of HealthcareService objects to a FHIR Bundle.

        Args:
            healthcare_services: List of domain HealthcareService objects.
            ods_code: The ODS code used for the search.

        Returns:
            A FHIR Bundle containing HealthcareService resources.
        """
        resources = self._create_resources(healthcare_services)
        return self._create_bundle(resources, ods_code)

    def _create_resources(
        self, healthcare_services: list[HealthcareService]
    ) -> list[FHIRResourceModel]:
        """Convert domain HealthcareService objects to FHIR resources.

        Args:
            healthcare_services: List of domain HealthcareService objects.

        Returns:
            List of FHIR HealthcareService resources.
        """
        return [
            self.healthcare_service_mapper.map_to_fhir_healthcare_service(hs)
            for hs in healthcare_services
        ]

    def _create_bundle(
        self,
        resources: list[FHIRResourceModel],
        ods_code: str,
    ) -> Bundle:
        """Create a FHIR Bundle from resources.

        Args:
            resources: List of FHIR resources to include.
            ods_code: The ODS code used for the search.

        Returns:
            A FHIR Bundle.
        """
        bundle_type = "searchset"
        bundle_id = str(uuid4())
        url = (
            f"{get_fhir_url('dos-search', 'HealthcareService')}"
            f"?organization.identifier=odsOrganisationCode|{ods_code}"
        )
        bundle_link = [
            {
                "relation": "self",
                "url": url,
            }
        ]

        entries = [self._create_entry(resource) for resource in resources]

        bundle = Bundle.model_validate(
            {
                "type": bundle_type,
                "id": bundle_id,
                "total": len(resources),
                "link": bundle_link,
                "entry": entries,
            }
        )

        return bundle

    def _create_entry(self, resource: FHIRResourceModel) -> dict[str, object]:
        """Create a Bundle entry for a resource.

        Args:
            resource: The FHIR resource to wrap.

        Returns:
            A Bundle entry dict.
        """
        url = get_fhir_url("dos-search", "HealthcareService", resource.id)

        return {
            "fullUrl": url,
            "resource": resource,
            "search": {"mode": "match"},
        }

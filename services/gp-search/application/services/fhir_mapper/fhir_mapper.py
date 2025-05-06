"""
FHIR Mapper Service - Maps raw_data from repository to FHIR resources.
"""

#  amazonq-ignore-next-line
import uuid
from typing import Any, Dict, List

from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.resource import Resource

from application.services.fhir_mapper.endpoint_mapper import EndpointMapper
from application.services.fhir_mapper.organization_mapper import OrganizationMapper


class FhirMapper:
    """Service to map raw_data from repository to FHIR resources."""

    def __init__(self, base_url: str) -> None:
        """
        Initialize the FHIR mapper service.

        Args:
            base_url: Base URL for FHIR resources
        """
        self.base_url = base_url
        self.organization_mapper = OrganizationMapper()
        self.endpoint_mapper = EndpointMapper()

    def map_to_fhir(self, dynamo_data: Dict[str, Any], ods_code: str) -> Bundle:
        """
        Map the DynamoDB raw_data to FHIR Bundle containing Organization and Endpoints.

        Args:
            dynamo_data: The raw_data from DynamoDB
            ods_code: The ODS code used for the query

        Returns:
            A FHIR Bundle object
        """
        # Create organization resource
        org_resource = self.organization_mapper.map_to_organization(dynamo_data)

        # Create endpoint resources
        endpoint_resources = self.endpoint_mapper.map_to_endpoints(dynamo_data)

        # Create bundle and return it directly
        return self._create_bundle(org_resource, endpoint_resources, ods_code)

    def _create_bundle(
        self, organization: Organization, endpoints: List[Endpoint], ods_code: str
    ) -> Bundle:
        bundle_type = "searchset"
        bundle_id = str(uuid.uuid4())
        bundle_link = [
            {
                "relation": "self",
                "url": f"{self.base_url}/Endpoint"
                f"?organization.identifier=odsOrganisationCode|{ods_code}"
                f"&_include=Endpoint:organization",
            }
        ]

        entries = [
            self._create_entry("Endpoint", endpoint, "match") for endpoint in endpoints
        ]

        entries.append(self._create_entry("Organization", organization, "include"))

        bundle = Bundle.model_validate(
            {
                "type": bundle_type,
                "id": bundle_id,
                "link": bundle_link,
                "entry": entries,
            }
        )

        return bundle

    def _create_entry(
        self, resource_type: str, resource: Resource, search_mode: str
    ) -> Dict[str, Any]:
        return {
            "fullUrl": f"{self.base_url}/{resource_type}/{resource.id}",
            "resource": resource,
            "search": {"mode": search_mode},
        }

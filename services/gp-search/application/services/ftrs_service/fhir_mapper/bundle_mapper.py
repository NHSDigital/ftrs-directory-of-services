from typing import Any, Dict, List
from uuid import uuid4

from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.resource import Resource

from application.services.ftrs_service.fhir_mapper.endpoint_mapper import EndpointMapper
from application.services.ftrs_service.fhir_mapper.organization_mapper import (
    OrganizationMapper,
)
from application.services.ftrs_service.repository.dynamo import OrganizationRecord


class BundleMapper:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.organization_mapper = OrganizationMapper()
        self.endpoint_mapper = EndpointMapper()

    def map_to_fhir(self, organization_record: OrganizationRecord) -> Bundle:
        organization_resource = self.organization_mapper.map_to_organization_resource(
            organization_record
        )
        endpoint_resources = self.endpoint_mapper.map_to_endpoints(organization_record)

        return self._create_bundle(organization_resource, endpoint_resources)

    def _create_bundle(
        self, organization: Organization, endpoints: List[Endpoint]
    ) -> Bundle:
        ods_code = [
            identifier.value
            for identifier in organization.identifier
            if identifier.system == "https://fhir.nhs.uk/Id/ods-organization-code"
        ][0]

        bundle_type = "searchset"
        bundle_id = str(uuid4())
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

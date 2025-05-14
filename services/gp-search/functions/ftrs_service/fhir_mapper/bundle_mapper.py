from uuid import uuid4

from aws_lambda_powertools import Tracer
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel

from functions.ftrs_service.fhir_mapper.endpoint_mapper import EndpointMapper
from functions.ftrs_service.fhir_mapper.organization_mapper import (
    OrganizationMapper,
)
from functions.ftrs_service.repository.dynamo import OrganizationRecord

tracer = Tracer()


class BundleMapper:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.organization_mapper = OrganizationMapper()
        self.endpoint_mapper = EndpointMapper()

    @tracer.capture_method
    def map_to_fhir(
        self, organization_record: OrganizationRecord, ods_code: str
    ) -> Bundle:
        resources = (
            self._create_resources(organization_record) if organization_record else []
        )

        return self._create_bundle(resources, ods_code)

    def _create_resources(
        self, organization_record: OrganizationRecord
    ) -> list[FHIRResourceModel]:
        endpoint_resources = self.endpoint_mapper.map_to_endpoints(organization_record)
        organization_resource = self.organization_mapper.map_to_organization_resource(
            organization_record
        )

        return endpoint_resources + [organization_resource]

    def _create_bundle(
        self,
        resources: list[FHIRResourceModel],
        ods_code: str,
    ) -> Bundle:
        bundle_type = "searchset"
        bundle_id = str(uuid4())
        bundle_link = [
            {
                "relation": "self",
                "url": f"{self.base_url}/Organization"
                f"?identifier=odsOrganisationCode|{ods_code}"
                f"&_revinclude=Endpoint:organization",
            }
        ]

        entries = [self._create_entry(resource) for resource in resources]

        bundle = Bundle.model_validate(
            {
                "type": bundle_type,
                "id": bundle_id,
                "link": bundle_link,
                "entry": entries,
            }
        )

        return bundle

    def _create_entry(self, resource: FHIRResourceModel) -> dict[str, object]:
        resource_type = resource.get_resource_type()
        resource_id = resource.id
        search_mode = self._get_search_mode(resource)

        return {
            "fullUrl": f"{self.base_url}/{resource_type}/{resource_id}",
            "resource": resource,
            "search": {"mode": search_mode},
        }

    def _get_search_mode(self, resource: FHIRResourceModel) -> str:
        if resource.get_resource_type() == "Endpoint":
            return "match"
        else:
            return "include"

from uuid import uuid4

from aws_lambda_powertools import Tracer
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from ftrs_common.utils.api_url_util import get_fhir_url
from ftrs_data_layer.domain import Organisation

from functions.ftrs_service.fhir_mapper.endpoint_mapper import EndpointMapper
from functions.ftrs_service.fhir_mapper.organization_mapper import (
    OrganizationMapper,
)

tracer = Tracer()


class BundleMapper:
    def __init__(self) -> None:
        self.organization_mapper = OrganizationMapper()
        self.endpoint_mapper = EndpointMapper()

    @tracer.capture_method
    def map_to_fhir(self, organisation: Organisation, ods_code: str) -> Bundle:
        resources = self._create_resources(organisation) if organisation else []

        return self._create_bundle(resources, ods_code)

    def _create_resources(self, organisation: Organisation) -> list[FHIRResourceModel]:
        endpoint_resources = self.endpoint_mapper.map_to_fhir_endpoints(organisation)
        organization_resource = self.organization_mapper.map_to_fhir_organization(
            organisation
        )

        return [organization_resource] + endpoint_resources

    def _create_bundle(
        self,
        resources: list[FHIRResourceModel],
        ods_code: str,
    ) -> Bundle:
        bundle_type = "searchset"
        bundle_id = str(uuid4())
        url = (
            f"{get_fhir_url('dos-search', 'Organization')}"
            f"?identifier=odsOrganisationCode|{ods_code}"
            f"&_revinclude=Endpoint:organization"
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
                "link": bundle_link,
                "entry": entries,
            }
        )

        return bundle

    def _create_entry(self, resource: FHIRResourceModel) -> dict[str, object]:
        url = get_fhir_url("dos-search", resource.get_resource_type(), resource.id)
        search_mode = self._get_search_mode(resource)

        return {
            "fullUrl": url,
            "resource": resource,
            "search": {"mode": search_mode},
        }

    def _get_search_mode(self, resource: FHIRResourceModel) -> str:
        if resource.get_resource_type() == "Organization":
            return "match"
        else:
            return "include"

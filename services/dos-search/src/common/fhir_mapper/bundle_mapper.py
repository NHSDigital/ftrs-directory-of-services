from uuid import uuid4

from aws_lambda_powertools import Tracer
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from ftrs_common.utils.api_url_util import get_fhir_url

tracer = Tracer()


class BundleMapper:
    def __init__(self, api_name: str, primary_resource_type: str) -> None:
        self.api_name = api_name
        self.primary_resource_type = primary_resource_type

    @tracer.capture_method
    def map_to_fhir(self, resources: list[FHIRResourceModel], self_url: str) -> Bundle:
        return self._create_bundle(resources, self_url)

    def _create_bundle(
        self, resources: list[FHIRResourceModel], self_url: str
    ) -> Bundle:
        bundle_type = "searchset"
        bundle_id = str(uuid4())
        bundle_link = [
            {
                "relation": "self",
                "url": self_url,
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
        url = get_fhir_url(self.api_name, resource.get_resource_type(), resource.id)
        search_mode = self._get_search_mode(resource)

        return {
            "fullUrl": url,
            "resource": resource,
            "search": {"mode": search_mode},
        }

    def _get_search_mode(self, resource: FHIRResourceModel) -> str:
        if resource.get_resource_type() == self.primary_resource_type:
            return "match"
        else:
            return "include"

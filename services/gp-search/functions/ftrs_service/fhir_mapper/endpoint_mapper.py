from aws_lambda_powertools import Logger
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.endpoint import Endpoint as FhirEndpoint
from ftrs_data_layer.domain import Endpoint, Organisation

logger = Logger()


class EndpointMapper:
    BUSINESS_SCENARIO_MAP = {
        "Primary": "primary-recipient",
        "Copy": "copy-recipient",
    }

    def map_to_fhir_endpoints(self, organisation: Organisation) -> list[FhirEndpoint]:
        fhir_endpoints = []

        for endpoint in organisation.endpoints:
            fhir_endpoint = self._create_fhir_endpoint(endpoint)
            if fhir_endpoint:
                fhir_endpoints.append(fhir_endpoint)

        return fhir_endpoints

    def _create_fhir_endpoint(self, endpoint: Endpoint) -> FhirEndpoint | None:
        endpoint_id = str(endpoint.id)
        status = endpoint.status.value
        connection_type = self._create_connection_type(endpoint)
        managing_organization = self._create_managing_organization(endpoint)
        payload_type = self._create_payload_type(endpoint)
        payload_mime_type = self._create_payload_mime_type(endpoint)
        address = self._create_address(endpoint)
        extension = self._create_extensions(endpoint)

        endpoint = FhirEndpoint.model_validate(
            {
                "id": endpoint_id,
                "status": status,
                "connectionType": connection_type,
                "managingOrganization": managing_organization,
                "payloadType": payload_type,
                "payloadMimeType": payload_mime_type,
                "address": address,
                "extension": extension,
            }
        )

        return endpoint

    def _create_address(self, endpoint: Endpoint) -> str:
        return endpoint.address

    def _create_managing_organization(self, endpoint: Endpoint) -> dict[str, str]:
        org_id = str(endpoint.managedByOrganisation)
        managing_organization = {"reference": f"Organization/{org_id}"}
        return managing_organization

    def _create_payload_type(self, endpoint: Endpoint) -> list[CodeableConcept]:
        system = "http://hl7.org/fhir/ValueSet/endpoint-payload-type"
        code = endpoint.payloadType.value

        if not code:
            return []

        codeable_concept = CodeableConcept.model_validate(
            {
                "coding": [
                    {
                        "system": system,
                        "code": code,
                    },
                ],
            }
        )

        return [codeable_concept]

    def _create_payload_mime_type(self, endpoint: Endpoint) -> list[str]:
        payload_mime_type = str(endpoint.payloadMimeType.value)

        return [payload_mime_type]

    def _create_extensions(self, endpoint: Endpoint) -> list[dict]:
        extensions = []

        if endpoint.order:
            extensions.append(self._create_order_extension(endpoint.order))

        if endpoint.isCompressionEnabled is not None:
            extensions.append(
                self._create_compression_extension(endpoint.isCompressionEnabled)
            )

        if endpoint.description:
            if extension := self._create_business_scenario_extension(
                endpoint.description
            ):
                extensions.append(extension)

        return extensions

    def _create_order_extension(self, order: int) -> dict:
        return {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganizationEndpointOrder",
            "valueInteger": order,
        }

    def _create_compression_extension(self, is_compression_enabled: bool) -> dict:
        return {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-EndpointCompression",
            "valueBoolean": is_compression_enabled,
        }

    def _create_business_scenario_extension(
        self, business_scenario: str
    ) -> dict | None:
        business_scenario_code = self.BUSINESS_SCENARIO_MAP.get(business_scenario)

        if not business_scenario_code:
            logger.error(f"Unknown business scenario: {business_scenario}")
            return None

        return {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-EndpointBusinessScenario",
            "valueCode": business_scenario_code,
        }

    def _create_connection_type(self, endpoint: Endpoint) -> Coding | None:
        db_conn_type = endpoint.connectionType.lower()

        return Coding.model_validate(
            {
                "system": "https://fhir.nhs.uk/England/CodeSystem/England-EndpointConnection",
                "code": db_conn_type,
            }
        )

from aws_lambda_powertools import Logger
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.endpoint import Endpoint

from functions.ftrs_service.repository.dynamo import (
    EndpointValue,
    OrganizationRecord,
)

logger = Logger()


class EndpointMapper:
    PAYLOAD_MIME_TYPE_BY_FORMAT_MAP = {
        "PDF": "application/pdf",
        "CDA": "application/hl7-cda+xml",
        "FHIR": "application/fhir+json",
    }

    CONNECTION_TYPE_MAP = {
        "itk": "ihe-xcpd",
        "email": "direct-project",
        "fhir": "hl7-fhir-rest",
    }

    BUSINESS_SCENARIO_MAP = {
        "Primary": "primary-recipient",
        "Copy": "copy-recipient",
    }

    def map_to_endpoints(
        self, organization_record: OrganizationRecord
    ) -> list[Endpoint]:
        endpoints = []

        for endpoint_value in organization_record.value.endpoints:
            endpoint = self._create_endpoint(endpoint_value)
            if endpoint:
                endpoints.append(endpoint)

        return endpoints

    def _create_endpoint(self, endpoint_value: EndpointValue) -> Endpoint | None:
        endpoint_id = endpoint_value.id
        status = self._create_status()
        connection_type = self._create_connection_type(endpoint_value)
        managing_organization = self._create_managing_organization(endpoint_value)
        payload_type = self._create_payload_type(endpoint_value)
        payload_mime_type = self._create_payload_mime_type(endpoint_value)
        address = self._create_address(endpoint_value)
        extension = self._create_extensions(endpoint_value)

        endpoint = Endpoint.model_validate(
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

    def _create_address(self, endpoint_value: EndpointValue) -> str:
        return endpoint_value.address

    def _create_managing_organization(
        self, endpoint_value: EndpointValue
    ) -> dict[str, str]:
        org_id = endpoint_value.managedByOrganisation
        managing_organization = {"reference": f"Organization/{org_id}"}
        return managing_organization

    def _create_status(self) -> str:
        status = "active"
        return status

    def _create_payload_type(
        self, endpoint_value: EndpointValue
    ) -> list[CodeableConcept]:
        system = "http://hl7.org/fhir/ValueSet/endpoint-payload-type"
        code = endpoint_value.payloadType

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

    def _create_payload_mime_type(self, endpoint_value: EndpointValue) -> list[str]:
        format_value = endpoint_value.format.upper()

        if format_value not in self.PAYLOAD_MIME_TYPE_BY_FORMAT_MAP:
            logger.error(f"Unknown format: {format_value}")
            return []

        return [self.PAYLOAD_MIME_TYPE_BY_FORMAT_MAP[format_value]]

    def _create_extensions(self, endpoint_value: EndpointValue) -> list[dict]:
        extensions = []

        if endpoint_value.order:
            extensions.append(self._create_order_extension(endpoint_value.order))

        if endpoint_value.isCompressionEnabled:
            extensions.append(
                self._create_compression_extension(endpoint_value.isCompressionEnabled)
            )

        if endpoint_value.description:
            if extension := self._create_business_scenario_extension(
                endpoint_value.description
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

    def _create_connection_type(self, endpoint_value: EndpointValue) -> Coding | None:
        db_conn_type = endpoint_value.connectionType.lower()

        if db_conn_type not in self.CONNECTION_TYPE_MAP:
            logger.error(f"Unknown connection type: {db_conn_type}")
            return None

        return Coding.model_validate(
            {
                "system": "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                "code": self.CONNECTION_TYPE_MAP[db_conn_type],
            }
        )

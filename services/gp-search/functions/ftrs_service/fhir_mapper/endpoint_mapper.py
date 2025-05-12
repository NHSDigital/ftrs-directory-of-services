from typing import Dict, Optional

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

    def map_to_endpoints(
        self, organization_record: OrganizationRecord
    ) -> list[Endpoint]:
        endpoints = []

        for endpoint_value in organization_record.value.endpoints:
            endpoint = self._create_endpoint(endpoint_value)
            if endpoint:
                endpoints.append(endpoint)

        return endpoints

    def _create_endpoint(self, endpoint_value: EndpointValue) -> Optional[Endpoint]:
        endpoint_id = endpoint_value.id
        status = self._create_status()
        connection_type = self._create_connection_type(endpoint_value)
        managing_organization = self._create_managing_organization(endpoint_value)
        payload_type = self._create_payload_type(endpoint_value)
        payload_mime_type = self._create_payload_mime_type(endpoint_value)
        address = self._create_address(endpoint_value)
        header = self._create_header(endpoint_value)

        endpoint = Endpoint.model_validate(
            {
                "id": endpoint_id,
                "status": status,
                "connectionType": connection_type,
                "managingOrganization": managing_organization,
                "payloadType": payload_type,
                "payloadMimeType": payload_mime_type,
                "address": address,
                "header": header,
            }
        )

        return endpoint

    def _create_address(self, endpoint_value: EndpointValue) -> str:
        return endpoint_value.address

    def _create_managing_organization(
        self, endpoint_value: EndpointValue
    ) -> Dict[str, str]:
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

    def _create_header(self, endpoint_value: EndpointValue) -> list[str]:
        header_data = {
            "order": endpoint_value.order,
            "is_compression_enabled": endpoint_value.isCompressionEnabled,
            "business_scenario": endpoint_value.description,
        }

        headers = [
            f"header_{key} {value}"
            for key, value in header_data.items()
            if value is not None
        ]

        return headers

    def _create_connection_type(
        self, endpoint_value: EndpointValue
    ) -> Optional[Coding]:
        db_conn_type = endpoint_value.connectionType.lower()

        if db_conn_type not in self.CONNECTION_TYPE_MAP:
            return None

        return Coding.model_validate(
            {
                "system": "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                "code": self.CONNECTION_TYPE_MAP[db_conn_type],
            }
        )

"""
Endpoint Mapper Service - Maps endpoint raw_data to FHIR Endpoint resources.
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4

from aws_lambda_powertools import Logger
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.endpoint import Endpoint

logger = Logger(service="endpoint_mapper")


class EndpointMapper:
    """Service to map endpoint raw_data to FHIR Endpoint resources."""

    # Class-level constant for payload MIME type mapping
    PAYLOAD_MIME_TYPE_BY_FORMAT_MAP = {
        "PDF": "application/pdf",
        "CDA": "application/hl7-cda+xml",
        "FHIR": "application/fhir+json",
    }

    # Define connection_type_map as a class-level constant
    CONNECTION_TYPE_MAP = {
        "itk": "ihe-xcpd",
        "email": "direct-project",
        "fhir": "hl7-fhir-rest",
    }

    def map_to_endpoints(self, raw_data: Dict[str, Any]) -> List[Endpoint]:
        """
        Map endpoint raw_data from DynamoDB to FHIR Endpoint resources.

        Args:
            raw_data: The organization raw_data from DynamoDB containing endpoints

        Returns:
            A list of FHIR Endpoint resources
        """
        raw_endpoints = raw_data.get("value", {}).get("endpoints", [])
        if not raw_endpoints:
            return []

        endpoints = []
        for raw_endpoint in raw_endpoints:
            # Try to create the endpoint
            endpoint = self._create_endpoint(raw_endpoint)
            # If endpoint was successfully created (not None/False)
            if endpoint:
                endpoints.append(endpoint)
        return endpoints

    def _create_endpoint(self, endpoint_data: Dict[str, Any]) -> Optional[Endpoint]:
        try:
            default = str(uuid4())
            endpoint_id = endpoint_data.get("id", default)
            status = self._create_status()
            connection_type = self._create_connection_type(endpoint_data)
            managing_organization = self._create_managing_organization(endpoint_data)
            payload_type = self._create_payload_type(endpoint_data)
            payload_mime_type = self._determine_payload_mime_type(endpoint_data)
            address = self._create_address(endpoint_data)
            header = self._create_header(endpoint_data)

            endpoint = Endpoint(
                id=endpoint_id,
                status=status,
                connectionType=connection_type,
                managingOrganization=managing_organization,
                payloadType=payload_type,
                payloadMimeType=payload_mime_type,
                address=address,
                header=header,
            )
        except Exception as e:
            logger.exception(
                "Unexpected error while creating endpoint",
                extra={
                    "error": str(e),
                    "endpoint_data": endpoint_data,
                },
            )
            return None
        else:
            logger.info(
                "Successfully created endpoint",
                extra={
                    "endpoint_data": endpoint_data,
                },
            )
            return endpoint

    def _create_address(self, endpoint_data: Dict[str, Any]) -> str:
        address = endpoint_data.get("address")
        return address

    def _create_managing_organization(
        self, endpoint_data: Dict[str, Any]
    ) -> Dict[str, str]:
        org_id = endpoint_data.get("managedByOrganisation")
        managing_organization = {"reference": f"Organization/{org_id}"}
        return managing_organization

    def _create_status(self) -> str:
        status = "active"
        return status

    def _create_payload_type(
        self, endpoint_data: Dict[str, Any]
    ) -> List[CodeableConcept]:
        payload_type_str = endpoint_data.get("payloadType")

        if not payload_type_str:
            return []

        system = "http://hl7.org/fhir/ValueSet/endpoint-payload-type"
        code = payload_type_str

        coding = Coding.model_construct(
            system=system,
            code=code,
        )
        codeable_concept = CodeableConcept.model_construct(
            coding=[coding],
        )
        return [codeable_concept]

    def _determine_payload_mime_type(self, endpoint_data: Dict[str, Any]) -> List[str]:
        format_value = endpoint_data.get("format", "").upper()

        if format_value not in self.PAYLOAD_MIME_TYPE_BY_FORMAT_MAP:
            return []

        return [self.PAYLOAD_MIME_TYPE_BY_FORMAT_MAP[format_value]]

    def _create_header(self, endpoint_data: Dict[str, Any]) -> List[str]:
        header_data = {
            "order": endpoint_data.get("order"),
            "is_compression_enabled": endpoint_data.get("isCompressionEnabled", False),
            "business_scenario": endpoint_data.get("description"),
        }

        headers = [
            f"header_{key} {value}"
            for key, value in header_data.items()
            if value is not None
        ]

        return headers

    def _create_connection_type(
        self, endpoint_data: Dict[str, Any]
    ) -> Optional[Coding]:
        db_conn_type = endpoint_data.get("connectionType", "").lower()

        # If no mapping exists, return None
        if db_conn_type not in self.CONNECTION_TYPE_MAP:
            return None

        # Create and return the Coding object
        return Coding.model_construct(
            system="http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
            code=self.CONNECTION_TYPE_MAP[db_conn_type],
        )

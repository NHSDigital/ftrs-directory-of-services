"""
Shared pytest fixtures for all test files.
This module provides reusable fixtures that can be used across all test files.
"""

from datetime import datetime
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.endpoint import Endpoint as FhirEndpoint
from fhir.resources.R4B.organization import Organization
from ftrs_data_layer.domain import Endpoint, Organisation
from ftrs_data_layer.domain.auditevent import AuditEvent
from ftrs_data_layer.domain.enums import (
    EndpointBusinessScenario,
    EndpointConnectionType,
    EndpointPayloadMimeType,
    EndpointStatus,
)

from src.common.constants import (
    ODS_ORG_CODE_IDENTIFIER_SYSTEM,
    REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
)


@pytest.fixture
def create_endpoint():
    """Factory function to create Endpoint instances with customizable fields."""

    def _create_endpoint(
        endpoint_id: UUID | None = UUID("12345678123456781234567812345678"),
        identifier_old_dos_id: int = 123456,
        status: EndpointStatus = EndpointStatus.ACTIVE,
        connection_type: EndpointConnectionType = EndpointConnectionType.ITK,
        business_scenario: EndpointBusinessScenario = EndpointBusinessScenario.COPY,
        payload_mime_type: EndpointPayloadMimeType = EndpointPayloadMimeType.FHIR,
        is_compression_enabled: bool = True,
        managed_by_organisation=None,
        name: str = "Test Endpoint Name",
        payload_type: str = "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        service=None,
        address: str = "https://example.com/endpoint",
        order: int = 1,
    ) -> Endpoint:
        return Endpoint(
            id=endpoint_id or uuid4(),
            identifier_oldDoS_id=identifier_old_dos_id,
            status=status,
            connectionType=connection_type,
            businessScenario=business_scenario,
            payloadMimeType=payload_mime_type,
            isCompressionEnabled=is_compression_enabled,
            managedByOrganisation=managed_by_organisation or uuid4(),
            name=name,
            payloadType=payload_type,
            service=service,
            address=address,
            order=order,
        )

    return _create_endpoint


@pytest.fixture
def endpoint(create_endpoint):
    """Create a standard test Endpoint.
    Uses the create_endpoint factory function with default values."""
    return create_endpoint()


@pytest.fixture
def create_organisation():
    """Factory function to create Organisation instances with customizable fields."""

    def _create_organisation(
        org_id: UUID | None = None,
        identifier_ods_code: str = "123456",
        active: bool = True,
        name: str = "Test Organisation",
        org_type: str = "GP Practice",
        created_by: AuditEvent = {
            "type": "user",
            "value": "test_user",
            "display": "Test User",
        },
        created_date_time: datetime = datetime(2023, 10, 1),
        modified_by: AuditEvent = {
            "type": "user",
            "value": "test_user",
            "display": "Test User",
        },
        modified_date_time: datetime = datetime(2023, 10, 1),
        endpoints: list[Endpoint] | None = None,
    ) -> Organisation:
        return Organisation(
            id=org_id or uuid4(),
            identifier_ODS_ODSCode=identifier_ods_code,
            active=active,
            name=name,
            telecom=[],
            type=org_type,
            createdBy=created_by,
            created=created_date_time,
            lastUpdatedBy=modified_by,
            lastUpdated=modified_date_time,
            endpoints=endpoints or [],
        )

    return _create_organisation


@pytest.fixture
def organisation(create_organisation, endpoint):
    """Create a standard test Organisation with the default Endpoint.
    Uses the create_organisation factory function with default values."""
    return create_organisation(endpoints=[endpoint])


@pytest.fixture
def create_fhir_organization():
    """Factory function to create FHIR Organization resources with customizable fields."""

    def _create_fhir_organization(
        org_id: str = "org-123",
        name: str = "Test Organization",
        ods_code: str = "O123",
        active: bool = True,
        telecom: str = "01234567890",
    ) -> Organization:
        return Organization.model_validate(
            {
                "id": org_id,
                "name": name,
                "active": active,
                "identifier": [
                    {
                        "use": "official",
                        "system": ODS_ORG_CODE_IDENTIFIER_SYSTEM,
                        "value": ods_code,
                    }
                ],
                "telecom": [{"system": "phone", "value": telecom}],
                "address": [
                    {
                        "line": ["Dummy Medical Practice", "Dummy Street"],
                        "city": "Dummy City",
                        "postalCode": "DU00 0MY",
                        "country": "ENGLAND",
                    }
                ],
            }
        )

    return _create_fhir_organization


@pytest.fixture
def create_fhir_endpoint():
    """Factory function to create FHIR Endpoint resources with customizable fields."""

    def _create_fhir_endpoint(
        endpoint_id: str = "endpoint-123",
        status: str = "active",
        connection_type: str = "hl7-fhir-rest",
        managing_org_id: str = "org-123",
        payload_type: str = "document",
        address: str = "https://example.org/fhir",
    ) -> FhirEndpoint:
        return FhirEndpoint.model_validate(
            {
                "id": endpoint_id,
                "status": status,
                "connectionType": {
                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-EndpointConnection",
                    "code": connection_type,
                },
                "managingOrganization": {
                    "reference": f"Organization/{managing_org_id}"
                },
                "payloadType": [
                    {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                                "code": payload_type,
                            }
                        ]
                    }
                ],
                "address": address,
            }
        )

    return _create_fhir_endpoint


@pytest.fixture
def bundle():
    return Bundle.model_construct(id="bundle-id")


@pytest.fixture
def mock_setup_request():
    """Mock for the setup_request utility function."""
    with patch(
        "src.common.middleware.request_context_middleware.setup_request"
    ) as mock:
        yield mock


@pytest.fixture
def mock_get_response_size_and_duration(bundle):
    """Mock for the get_response_size_and_duration utility function."""
    with patch("src.organization.handler.get_response_size_and_duration") as mock:
        response_size = len(bundle.model_dump_json().encode("utf-8"))
        mock.return_value = (response_size, 1)
        yield mock


@pytest.fixture
def mock_logger():
    """Mock for the FTRS common Logger used for all log() calls."""
    with patch("src.organization.handler.logger") as mock:
        yield mock


@pytest.fixture
def ods_code():
    return "ABC123"


@pytest.fixture
def event(ods_code):
    return {
        "headers": {
            "Accept": "application/fhir+json",
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token",
            "Version": "1",
            "NHSD-Request-ID": "request_id",
            "NHSD-Correlation-ID": "request_id.correlation_id.message_id",
            "X-Correlation-ID": "test-x-correlation-id",
            "X-Request-ID": "request_id",
            "End-User-Role": "Clinician",
            "Application-ID": "application_id",
            "Application-Name": "dos_unit_tests",
            "Request-Start-Time": "2023-01-01T00:00:00Z",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US",
            "User-Agent": "test-user-agent",
            "Host": "test-host",
            "X-Amzn-Trace-Id": "test-trace-id",
            "X-Forwarded-For": "127.0.0.1",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https",
        },
        "path": "/Organization",
        "httpMethod": "GET",
        "queryStringParameters": {
            "identifier": f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|{ods_code}",
            "_revinclude": REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
        },
        "pathParameters": None,
        "requestContext": {
            "requestId": "796bdcd6-c5b0-4862-af98-9d2b1b853703",
        },
        "body": None,
    }


@pytest.fixture
def log_data():
    return {
        "dos_message_id": "message_id",
    }


@pytest.fixture
def details(event):
    return {
        "dos_environment": "Development",
        "dos_search_api_version": "1",
        "lambda_version": "0.0.1",
        "connecting_party_end_user_role": "Clinician",
        "connecting_party_application_id": "application_id",
        "connecting_party_application_name": "dos_unit_tests",
        "request_params": {
            "query_params": event.get("queryStringParameters") or {},
            "path_params": event.get("pathParameters") or {},
            "request_context": event.get("requestContext") or {},
        },
    }

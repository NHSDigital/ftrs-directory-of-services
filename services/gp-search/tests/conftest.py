"""
Shared pytest fixtures for all test files.
This module provides reusable fixtures that can be used across all test files.
"""

from datetime import datetime

import pytest
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.organization import Organization

from functions.ftrs_service.repository.dynamo import (
    EndpointValue,
    OrganizationRecord,
    OrganizationValue,
)


@pytest.fixture
def create_endpoint_value():
    """Factory function to create EndpointValue instances with customizable fields."""

    def _create_endpoint_value(
        endpoint_id: str = "endpoint-123",
        connection_type: str = "fhir",
        payload_type: str = "document",
        format_type: str = "PDF",
        address: str = "https://example.org/fhir",
        order: int = 1,
        is_compression_enabled: bool = True,
        description: str = "Primary",
        managed_by_organisation: str = "org-123",
    ) -> EndpointValue:
        return EndpointValue(
            id=endpoint_id,
            identifier_oldDoS_id=9876,
            connectionType=connection_type,
            managedByOrganisation=managed_by_organisation,
            payloadType=payload_type,
            format=format_type,
            address=address,
            order=order,
            isCompressionEnabled=is_compression_enabled,
            description=description,
            status="active",
            createdBy="test-user",
            modifiedBy="test-user",
            createdDateTime=datetime(2023, 1, 1),
            modifiedDateTime=datetime(2023, 1, 2),
            service="dummy-service",
            name="dummy-name",
        )

    return _create_endpoint_value


@pytest.fixture
def endpoint_value(create_endpoint_value):
    """Create a standard test endpoint value.
    Uses the create_endpoint_value factory function with default values."""
    return create_endpoint_value()


@pytest.fixture
def create_organization_value():
    """Factory function to create OrganizationValue instances with customizable fields."""

    def _create_organization_value(
        org_id: str = "org-123",
        name: str = "Test Organization",
        org_type: str = "prov",
        active: bool = True,
        ods_code: str = "O123",
        endpoints: list[EndpointValue] | None = None,
        telecom: str = "01234567890",
    ) -> OrganizationValue:
        return OrganizationValue(
            id=org_id,
            name=name,
            type=org_type,
            active=active,
            identifier_ODS_ODSCode=ods_code,
            telecom=telecom,
            endpoints=endpoints or [],
            createdBy="test-user",
            modifiedBy="test-user",
            createdDateTime=datetime(2023, 1, 1),
            modifiedDateTime=datetime(2023, 1, 2),
        )

    return _create_organization_value


@pytest.fixture
def organization_value(create_organization_value, endpoint_value):
    """Create a standard test organization value with the default endpoint.
    Uses the create_organization_value factory function with default values."""
    return create_organization_value(endpoints=[endpoint_value])


@pytest.fixture
def create_organization_record():
    """Factory function to create OrganizationRecord instances with customizable fields."""

    def _create_organization_record(
        org_id: str = "org-123",
        ods_code: str = "O123",
        org_value: OrganizationValue | None = None,
    ) -> OrganizationRecord:
        if org_value is None:
            # Create a minimal organization value if none provided
            org_value = OrganizationValue(
                id=org_id,
                name="Test Organization",
                type="prov",
                active=True,
                identifier_ODS_ODSCode=ods_code,
                telecom="01234567890",
                endpoints=[],
                createdBy="test-user",
                modifiedBy="test-user",
                createdDateTime=datetime(2023, 1, 1),
                modifiedDateTime=datetime(2023, 1, 2),
            )

        return OrganizationRecord(
            id=org_id,
            ods_code=ods_code,
            field="organization",
            value=org_value,
        )

    return _create_organization_record


@pytest.fixture
def organization_record(create_organization_record, organization_value):
    """Create a standard test organization record with the default organization value.
    Uses the create_organization_record factory function with default values."""
    return create_organization_record(org_value=organization_value)


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
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
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
    ) -> Endpoint:
        return Endpoint.model_validate(
            {
                "id": endpoint_id,
                "status": status,
                "connectionType": {
                    "system": "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
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

"""
Shared pytest fixtures for all test files.
This module provides reusable fixtures that can be used across all test files.
"""

from datetime import datetime

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.organization import Organization

from functions.ftrs_service.repository.dynamo import (
    EndpointValue,
    OrganizationRecord,
    OrganizationValue,
)


@pytest.fixture
def mock_environment():
    """Mock environment variables for testing."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DYNAMODB_TABLE_NAME", "test-table")
        mp.setenv("FHIR_BASE_URL", "https://test-fhir-url.org")
        mp.setenv("LOG_LEVEL", "DEBUG")
        yield mp


@pytest.fixture
def endpoint_value():
    """Create a standard test endpoint value."""
    return EndpointValue(
        id="endpoint-123",
        identifier_oldDoS_id=9876,
        connectionType="fhir",
        managedByOrganisation="org-123",
        payloadType="document",
        format="PDF",
        address="https://example.org/fhir",
        order=1,
        isCompressionEnabled=True,
        description="Test scenario",
        status="active",
        createdBy="test-user",
        modifiedBy="test-user",
        createdDateTime=datetime(2023, 1, 1),
        modifiedDateTime=datetime(2023, 1, 2),
    )


@pytest.fixture
def organization_value(endpoint_value):
    """Create a standard test organization value with the default endpoint."""
    return OrganizationValue(
        id="org-123",
        name="Test Organization",
        type="prov",
        active=True,
        identifier_ODS_ODSCode="O123",
        telecom="01234567890",
        endpoints=[endpoint_value],
        createdBy="test-user",
        modifiedBy="test-user",
        createdDateTime=datetime(2023, 1, 1),
        modifiedDateTime=datetime(2023, 1, 2),
    )


@pytest.fixture
def organization_record(organization_value):
    """Create a standard test organization record with the default organization value."""
    return OrganizationRecord(
        id="org-123",
        ods_code="O123",
        field="organization",
        value=organization_value,
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
        description: str = "Test scenario",
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
        )

    return _create_endpoint_value


@pytest.fixture
def create_organization_value(create_endpoint_value):
    """Factory function to create OrganizationValue instances with customizable fields."""

    def _create_organization_value(
        org_id: str = "org-123",
        name: str = "Test Organization",
        org_type: str = "prov",
        active: bool = True,
        ods_code: str = "O123",
        endpoints: list[EndpointValue] | None = None,
    ) -> OrganizationValue:
        if endpoints is None:
            endpoints = [create_endpoint_value()]

        return OrganizationValue(
            id=org_id,
            name=name,
            type=org_type,
            active=active,
            identifier_ODS_ODSCode=ods_code,
            telecom="01234567890",
            endpoints=endpoints,
            createdBy="test-user",
            modifiedBy="test-user",
            createdDateTime=datetime(2023, 1, 1),
            modifiedDateTime=datetime(2023, 1, 2),
        )

    return _create_organization_value


@pytest.fixture
def create_organization_record(create_organization_value):
    """Factory function to create OrganizationRecord instances with customizable fields."""

    def _create_organization_record(
        org_id: str = "org-123",
        ods_code: str = "O123",
        org_value: OrganizationValue | None = None,
    ) -> OrganizationRecord:
        if org_value is None:
            org_value = create_organization_value(org_id=org_id, ods_code=ods_code)

        return OrganizationRecord(
            id=org_id,
            ods_code=ods_code,
            field="organization",
            value=org_value,
        )

    return _create_organization_record


@pytest.fixture
def create_fhir_organization():
    """Factory function to create FHIR Organization resources with customizable fields."""

    def _create_fhir_organization(
        org_id: str = "org-123",
        name: str = "Test Organization",
        ods_code: str = "O123",
        active: bool = True,
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
                "telecom": [{"system": "phone", "value": "01234567890"}],
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


@pytest.fixture
def create_fhir_bundle(create_fhir_organization, create_fhir_endpoint):
    """Factory function to create FHIR Bundle resources with customizable fields."""

    def _create_fhir_bundle(
        base_url: str = "https://example.org",
        org_id: str = "org-123",
        ods_code: str = "O123",
        endpoints_count: int = 1,
    ) -> Bundle:
        # Create organization
        org = create_fhir_organization(org_id=org_id, ods_code=ods_code)

        # Create endpoints
        endpoints = [
            create_fhir_endpoint(endpoint_id=f"endpoint-{i}", managing_org_id=org_id)
            for i in range(endpoints_count)
        ]

        # Create entries
        entries = [
            {
                "fullUrl": f"{base_url}/Endpoint/{endpoint.id}",
                "resource": endpoint,
                "search": {"mode": "match"},
            }
            for endpoint in endpoints
        ]

        # Add organization entry
        entries.append(
            {
                "fullUrl": f"{base_url}/Organization/{org.id}",
                "resource": org,
                "search": {"mode": "include"},
            }
        )

        # Create bundle
        return Bundle.model_validate(
            {
                "resourceType": "Bundle",
                "type": "searchset",
                "id": f"bundle-{ods_code}",
                "link": [
                    {
                        "relation": "self",
                        "url": f"{base_url}/Endpoint"
                        f"?organization.identifier=odsOrganisationCode|{ods_code}"
                        f"&_include=Endpoint:organization",
                    }
                ],
                "entry": entries,
            }
        )

    return _create_fhir_bundle

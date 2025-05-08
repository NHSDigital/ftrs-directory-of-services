"""
Shared test utilities and fixtures for FTRS service tests.
This module provides reusable fixtures and helper functions for unit tests.
"""

from datetime import datetime
from typing import Dict, List, Optional

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
def create_organization_value():
    """Factory function to create OrganizationValue instances with customizable fields."""

    def _create_organization_value(
        org_id: str = "org-123",
        name: str = "Test Organization",
        org_type: str = "prov",
        active: bool = True,
        ods_code: str = "O123",
        endpoints: Optional[List[EndpointValue]] = None,
    ) -> OrganizationValue:
        return OrganizationValue(
            id=org_id,
            name=name,
            type=org_type,
            active=active,
            identifier_ODS_ODSCode=ods_code,
            telecom="01234567890",
            endpoints=endpoints or [],
            createdBy="test-user",
            modifiedBy="test-user",
            createdDateTime=datetime(2023, 1, 1),
            modifiedDateTime=datetime(2023, 1, 2),
        )

    return _create_organization_value


@pytest.fixture
def create_organization_record():
    """Factory function to create OrganizationRecord instances with customizable fields."""

    def _create_organization_record(
        org_id: str = "org-123",
        ods_code: str = "O123",
        org_value: Optional[OrganizationValue] = None,
    ) -> OrganizationRecord:
        if org_value is None:
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
def create_sample_dynamo_item():
    """Factory function to create sample DynamoDB items for testing."""

    def _create_sample_dynamo_item(
        org_id: str = "org-123",
        ods_code: str = "O123",
        org_name: str = "Test Organization",
        endpoints: Optional[List[Dict]] = None,
    ) -> Dict:
        if endpoints is None:
            endpoints = [
                {
                    "id": "endpoint-123",
                    "identifier_oldDoS_id": 9876,
                    "connectionType": "fhir",
                    "managedByOrganisation": org_id,
                    "payloadType": "document",
                    "format": "PDF",
                    "address": "https://example.org/fhir",
                    "order": 1,
                    "isCompressionEnabled": True,
                    "description": "Test scenario",
                    "status": "active",
                    "createdBy": "test-user",
                    "modifiedBy": "test-user",
                    "createdDateTime": "2023-01-01T00:00:00",
                    "modifiedDateTime": "2023-01-02T00:00:00",
                    "service": "dummy-service",
                    "name": "dummy-name",
                }
            ]

        return {
            "id": org_id,
            "ods-code": ods_code,
            "field": "organization",
            "value": {
                "id": org_id,
                "name": org_name,
                "type": "prov",
                "active": True,
                "identifier_ODS_ODSCode": ods_code,
                "telecom": "01234567890",
                "createdBy": "test-user",
                "modifiedBy": "test-user",
                "createdDateTime": "2023-01-01T00:00:00",
                "modifiedDateTime": "2023-01-02T00:00:00",
                "endpoints": endpoints,
            },
        }

    return _create_sample_dynamo_item


def create_test_bundle(
    org_resource: Organization,
    endpoint_resources: List[Endpoint],
    base_url: str = "https://example.org",
) -> Bundle:
    """
    Creates a FHIR Bundle resource for testing.

    Args:
        org_resource: The organization resource to include in the bundle
        endpoint_resources: List of endpoint resources to include in the bundle
        base_url: Base URL for the bundle

    Returns:
        A FHIR Bundle resource
    """
    # Extract ODS code from organization
    ods_code = [
        identifier.value
        for identifier in org_resource.identifier
        if identifier.system == "https://fhir.nhs.uk/Id/ods-organization-code"
    ][0]

    # Create entries for endpoints
    entries = [
        {
            "fullUrl": f"{base_url}/Endpoint/{endpoint.id}",
            "resource": endpoint,
            "search": {"mode": "match"},
        }
        for endpoint in endpoint_resources
    ]

    # Create entry for organization
    entries.append(
        {
            "fullUrl": f"{base_url}/Organization/{org_resource.id}",
            "resource": org_resource,
            "search": {"mode": "include"},
        }
    )

    # Create bundle
    bundle = Bundle.model_validate(
        {
            "type": "searchset",
            "id": "test-bundle-id",
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

    return bundle
